//! gateway — thin OpenAI-compatible front end over llama-server backends.
//!
//! * Routes `POST /v1/chat/completions` + `/v1/completions` by the request's
//!   `model` field (substring match against each upstream's model id),
//!   round-robins when no model matches, fails over on errors.
//! * `GET /v1/models` merges upstream model lists. `GET /health` reports
//!   per-upstream health (background-probed every 15 s).
//! * Streaming (`"stream": true` SSE) is relayed, never buffered.
//!
//! Usage:
//!   gateway --listen 127.0.0.1:18080 \
//!           --upstream http://127.0.0.1:18090 \
//!           --upstream http://127.0.0.1:18091

use axum::{
    body::Body,
    extract::State,
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde_json::Value;
use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};
use std::time::Duration;
use tokio::sync::RwLock;

struct Upstream {
    url: String,
    model: RwLock<String>,
    healthy: RwLock<bool>,
}

struct AppState {
    upstreams: Vec<Upstream>,
    rr: AtomicUsize,
    client: reqwest::Client,
}

async fn probe(st: &AppState) {
    for u in &st.upstreams {
        let health = st
            .client
            .get(format!("{}/health", u.url))
            .timeout(Duration::from_secs(5))
            .send()
            .await
            .map(|r| r.status().is_success())
            .unwrap_or(false);
        *u.healthy.write().await = health;
        if health {
            if let Ok(resp) = st
                .client
                .get(format!("{}/v1/models", u.url))
                .timeout(Duration::from_secs(5))
                .send()
                .await
            {
                if let Ok(v) = resp.json::<Value>().await {
                    let name = v
                        .get("data")
                        .and_then(|d| d.as_array())
                        .and_then(|a| a.first())
                        .and_then(|m| m.get("id"))
                        .and_then(|i| i.as_str())
                        .unwrap_or("")
                        .to_string();
                    if !name.is_empty() {
                        *u.model.write().await = name;
                    }
                }
            }
        }
    }
}

async fn health_loop(st: Arc<AppState>) {
    loop {
        probe(&st).await;
        tokio::time::sleep(Duration::from_secs(15)).await;
    }
}

/// Pick an upstream index: model-substring match first, else round-robin
/// over healthy ones (any upstream if all are marked down).
async fn pick(st: &AppState, want: Option<&str>) -> Option<usize> {
    if let Some(w) = want {
        let w = w.to_lowercase();
        for (i, u) in st.upstreams.iter().enumerate() {
            if *u.healthy.read().await && u.model.read().await.to_lowercase().contains(&w) {
                return Some(i);
            }
        }
    }
    let mut healthy: Vec<usize> = Vec::new();
    for (i, u) in st.upstreams.iter().enumerate() {
        if *u.healthy.read().await {
            healthy.push(i);
        }
    }
    if healthy.is_empty() {
        return (0..st.upstreams.len()).next();
    }
    let n = st.rr.fetch_add(1, Ordering::Relaxed);
    Some(healthy[n % healthy.len()])
}

async fn forward(
    st: &AppState,
    path: &str,
    headers: HeaderMap,
    body: bytes::Bytes,
) -> Response {
    let want = serde_json::from_slice::<Value>(&body)
        .ok()
        .and_then(|v| v.get("model").and_then(|m| m.as_str()).map(str::to_string));
    let ct = headers
        .get(axum::http::header::CONTENT_TYPE)
        .cloned()
        .unwrap_or_else(|| axum::http::HeaderValue::from_static("application/json"));

    let mut tried = vec![false; st.upstreams.len()];
    for _ in 0..st.upstreams.len() {
        let idx = match pick(st, want.as_deref()).await {
            Some(i) if !tried[i] => i,
            Some(_) => continue,
            None => break,
        };
        tried[idx] = true;
        let url = format!("{}{}", st.upstreams[idx].url, path);
        let t0 = std::time::Instant::now();
        match st
            .client
            .post(&url)
            .header(axum::http::header::CONTENT_TYPE, ct.clone())
            .body(body.clone())
            .send()
            .await
        {
            Ok(resp) if resp.status().is_success() => {
                let status = resp.status();
                println!(
                    "POST {} -> {} {} ({} ms)",
                    path,
                    st.upstreams[idx].url,
                    status.as_u16(),
                    t0.elapsed().as_millis()
                );
                let stream = resp.bytes_stream();
                return (status, [(axum::http::header::CONTENT_TYPE, ct)],
                        Body::from_stream(stream))
                    .into_response();
            }
            Ok(resp) => {
                println!("POST {} -> {} error {}, trying next", path, st.upstreams[idx].url,
                         resp.status().as_u16());
                continue;
            }
            Err(e) => {
                println!("POST {} -> {} unreachable ({e}), trying next", path, st.upstreams[idx].url);
                *st.upstreams[idx].healthy.write().await = false;
                continue;
            }
        }
    }
    (
        StatusCode::BAD_GATEWAY,
        Json(serde_json::json!({"error": "no healthy upstream"})),
    )
        .into_response()
}

async fn chat(State(st): State<Arc<AppState>>, headers: HeaderMap, body: bytes::Bytes) -> Response {
    forward(&st, "/v1/chat/completions", headers, body).await
}

async fn completions(State(st): State<Arc<AppState>>, headers: HeaderMap, body: bytes::Bytes) -> Response {
    forward(&st, "/v1/completions", headers, body).await
}

async fn health(State(st): State<Arc<AppState>>) -> impl IntoResponse {
    let mut ups = Vec::new();
    for u in &st.upstreams {
        ups.push(serde_json::json!({
            "url": u.url,
            "model": *u.model.read().await,
            "healthy": *u.healthy.read().await,
        }));
    }
    Json(serde_json::json!({"status": "ok", "upstreams": ups}))
}

async fn models(State(st): State<Arc<AppState>>) -> impl IntoResponse {
    let mut data = Vec::new();
    for u in &st.upstreams {
        if !*u.healthy.read().await {
            continue;
        }
        if let Ok(resp) = st
            .client
            .get(format!("{}/v1/models", u.url))
            .timeout(Duration::from_secs(10))
            .send()
            .await
        {
            if let Ok(v) = resp.json::<Value>().await {
                if let Some(arr) = v.get("data").and_then(|d| d.as_array()) {
                    data.extend(arr.clone());
                }
            }
        }
    }
    Json(serde_json::json!({"object": "list", "data": data}))
}

fn parse_args() -> (String, Vec<String>) {
    let mut listen = "127.0.0.1:18080".to_string();
    let mut ups = Vec::new();
    let mut it = std::env::args().skip(1).peekable();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--listen" => {
                if let Some(v) = it.next() {
                    listen = v;
                }
            }
            "--upstream" => {
                if let Some(v) = it.next() {
                    ups.push(v.trim_end_matches('/').to_string());
                }
            }
            _ => {}
        }
    }
    if ups.is_empty() {
        ups.push("http://127.0.0.1:18090".to_string());
        ups.push("http://127.0.0.1:18091".to_string());
    }
    (listen, ups)
}

#[tokio::main]
async fn main() {
    let (listen, ups) = parse_args();
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(600))
        .build()
        .expect("client");
    let state = Arc::new(AppState {
        upstreams: ups
            .into_iter()
            .map(|url| Upstream {
                url,
                model: RwLock::new(String::new()),
                healthy: RwLock::new(false),
            })
            .collect(),
        rr: AtomicUsize::new(0),
        client,
    });
    probe(&state).await;
    tokio::spawn(health_loop(state.clone()));

    let app = Router::new()
        .route("/health", get(health))
        .route("/v1/models", get(models))
        .route("/v1/chat/completions", post(chat))
        .route("/v1/completions", post(completions))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(&listen)
        .await
        .expect("bind");
    println!("gateway listening on http://{listen}");
    axum::serve(listener, app).await.expect("serve");
}
