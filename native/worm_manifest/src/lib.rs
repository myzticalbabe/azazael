use pyo3::prelude::*;

use pyo3::types::PyDict;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Single worm entry as stored in the manifest JSON.
#[derive(Debug, Clone, Serialize, Deserialize)]
struct WormEntry {
    module: String,
    category: String,
    priority: u8,
    cooldown_seconds: f64,
    description: String,
    registered_at: String,
    spawn_count: u64,
    last_spawned: Option<String>,
    version: String,
    source_file: String,
}

/// Full manifest structure: worm_name -> WormEntry.
type Manifest = HashMap<String, WormEntry>;

/// Parse the embedded manifest JSON once at load time.
fn load_manifest() -> Manifest {
    let json = include_str!("../../../src/CORE/worm_manifest.json");
    serde_json::from_str(json).expect("worm_manifest.json must be valid JSON")
}

/// Get a lazily-loaded singleton manifest.
fn manifest() -> &'static Manifest {
    static MANIFEST: std::sync::OnceLock<Manifest> = std::sync::OnceLock::new();
    MANIFEST.get_or_init(load_manifest)
}

// ---------------------------------------------------------------------------
// Helper: convert a &WormEntry into a Python dict using PyO3 0.29 Bound API
// ---------------------------------------------------------------------------

fn entry_to_dict<'py>(entry: &WormEntry, py: Python<'py>) -> Bound<'py, PyDict> {
    let d = PyDict::new(py);
    let _ = d.set_item("module", &entry.module);
    let _ = d.set_item("category", &entry.category);
    let _ = d.set_item("priority", entry.priority);
    let _ = d.set_item("cooldown_seconds", entry.cooldown_seconds);
    let _ = d.set_item("description", &entry.description);
    let _ = d.set_item("registered_at", &entry.registered_at);
    let _ = d.set_item("spawn_count", entry.spawn_count);
    let _ = d.set_item("version", &entry.version);
    let _ = d.set_item("source_file", &entry.source_file);
    if let Some(ref last) = entry.last_spawned {
        let _ = d.set_item("last_spawned", last);
    } else {
        let _ = d.set_item("last_spawned", py.None());
    }
    d
}

/// Build a Python dict list of dicts with priority sorting.
fn build_sorted_results<'py>(
    py: Python<'py>,
    entries: impl Iterator<Item = (&'py String, &'py WormEntry)>,
    condition: impl Fn(&str, &WormEntry) -> bool,
) -> Vec<Bound<'py, PyDict>> {
    let mut results: Vec<(&str, Bound<'py, PyDict>)> = Vec::new();
    for (name, entry) in entries {
        if condition(name, entry) {
            let d = entry_to_dict(entry, py);
            let _ = d.set_item("name", name.as_str());
            results.push((name.as_str(), d));
        }
    }
    results.sort_by(|a, b| {
        let pa = a.1.get_item("priority")
            .ok().flatten()
            .and_then(|v| v.extract::<u8>().ok())
            .unwrap_or(0);
        let pb = b.1.get_item("priority")
            .ok().flatten()
            .and_then(|v| v.extract::<u8>().ok())
            .unwrap_or(0);
        pb.cmp(&pa)
    });
    results.into_iter().map(|(_, d)| d).collect()
}

// ---------------------------------------------------------------------------
// Python module
// ---------------------------------------------------------------------------

/// Fast worm manifest lookup - Rust-powered replacement for the 38s Python
/// cold-start import chain.
#[pymodule]
fn worm_manifest(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_worm, m)?)?;
    m.add_function(wrap_pyfunction!(get_worms_by_category, m)?)?;
    m.add_function(wrap_pyfunction!(get_worms_by_priority_range, m)?)?;
    m.add_function(wrap_pyfunction!(get_all_categories, m)?)?;
    m.add_function(wrap_pyfunction!(get_worm_count, m)?)?;
    m.add_function(wrap_pyfunction!(get_all_worms, m)?)?;
    m.add_function(wrap_pyfunction!(search_worms, m)?)?;
    m.add_function(wrap_pyfunction!(get_statistics, m)?)?;
    Ok(())
}

/// Return metadata for a single worm as a dict, or None.
#[pyfunction]
fn find_worm(py: Python<'_>, name: String) -> Option<Bound<'_, PyDict>> {
    let m = manifest();
    m.get(&name).map(|entry| entry_to_dict(entry, py))
}

/// Return all worms in a given category.
#[pyfunction]
fn get_worms_by_category(py: Python<'_>, category: String) -> Vec<Bound<'_, PyDict>> {
    build_sorted_results(py, manifest().iter(), |_, e| e.category == category)
}

/// Return all worms whose priority falls within [min, max] (inclusive).
#[pyfunction]
fn get_worms_by_priority_range(py: Python<'_>, min_priority: u8, max_priority: u8) -> Vec<Bound<'_, PyDict>> {
    if max_priority < min_priority {
        return Vec::new();
    }
    build_sorted_results(py, manifest().iter(), |_, e| {
        e.priority >= min_priority && e.priority <= max_priority
    })
}

/// Return all unique category names.
#[pyfunction]
fn get_all_categories() -> Vec<String> {
    let m = manifest();
    let mut cats: Vec<String> = m.values().map(|e| e.category.clone()).collect();
    cats.sort();
    cats.dedup();
    cats
}

/// Return the total number of worms in the manifest.
#[pyfunction]
fn get_worm_count() -> usize {
    manifest().len()
}

/// Return ALL worms as a list of dicts.
#[pyfunction]
fn get_all_worms(py: Python<'_>) -> Vec<Bound<'_, PyDict>> {
    build_sorted_results(py, manifest().iter(), |_, _| true)
}

/// Search worms by name or description substring (case-insensitive).
#[pyfunction]
fn search_worms(py: Python<'_>, query: String) -> Vec<Bound<'_, PyDict>> {
    let query_lower = query.to_lowercase();
    let mut results = Vec::new();
    for (name, entry) in manifest().iter() {
        let name_lower = name.to_lowercase();
        let desc_lower = entry.description.to_lowercase();
        if name_lower.contains(&query_lower) || desc_lower.contains(&query_lower) {
            let d = entry_to_dict(entry, py);
            let _ = d.set_item("name", name.as_str());
            results.push(d);
        }
    }
    results
}

/// Return aggregate statistics about the worm ecosystem.
#[pyfunction]
fn get_statistics(py: Python<'_>) -> Bound<'_, PyDict> {
    let m = manifest();
    let total = m.len();
    let mut cat_counts: HashMap<&str, usize> = HashMap::new();
    let mut prio_counts: HashMap<u8, usize> = HashMap::new();
    let mut unspawned: usize = 0;

    for entry in m.values() {
        *cat_counts.entry(&entry.category).or_insert(0) += 1;
        *prio_counts.entry(entry.priority).or_insert(0) += 1;
        if entry.spawn_count == 0 {
            unspawned += 1;
        }
    }

    let stats = PyDict::new(py);
    let _ = stats.set_item("total_worms", total);
    let _ = stats.set_item("total_categories", cat_counts.len());
    let _ = stats.set_item("total_unspawned", unspawned);
    let _ = stats.set_item("total_spawned", total - unspawned);

    // Build nested dicts for category and priority distributions
    let cat_dict = PyDict::new(py);
    for (cat, count) in &cat_counts {
        let _ = cat_dict.set_item(*cat, *count);
    }
    let _ = stats.set_item("category_counts", cat_dict);

    let prio_dict = PyDict::new(py);
    for (prio, count) in &prio_counts {
        let _ = prio_dict.set_item(*prio, *count);
    }
    let _ = stats.set_item("priority_distribution", prio_dict);

    stats
}
