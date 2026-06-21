# coding: utf-8
"""Update test_cross_domain_integration.py to use canonical cd3_exporter module."""
import os

with open("tests/test_cross_domain_integration.py", "r", encoding="utf-8") as f:
    content = f.read()

fixes = []

# Fix 1: Add import for cd3_exporter
old_import = "from CORE.cd2_verifier import SMTVerifier, serialize_solver_result"
new_import = "from CORE.cd2_verifier import SMTVerifier, serialize_solver_result\nfrom CORE.cd3_exporter import SQLiteSpanExporter, OTEL_SPANS_SCHEMA, configure_otel_tracing"
if old_import in content:
    content = content.replace(old_import, new_import, 1)
    fixes.append("Added cd3_exporter import")

# Fix 2: Replace the entire inline SQLiteSpanExporter class + OTel setup with canonical import
old_inline = """    # --- Build SQLiteSpanExporter from CD3 spec ---
    OTEL_SPANS_SCHEMA = \"\"\"
    CREATE TABLE IF NOT EXISTS otel_spans (
        trace_id        TEXT NOT NULL,
        span_id         TEXT NOT NULL,
        parent_span_id  TEXT,
        name            TEXT NOT NULL,
        kind            TEXT NOT NULL DEFAULT 'INTERNAL',
        start_time      INTEGER NOT NULL,
        end_time        INTEGER NOT NULL,
        status_code     INTEGER NOT NULL DEFAULT 0,
        attributes      TEXT NOT NULL DEFAULT '{}',
        correlation_id  TEXT,
        session_id      TEXT,
        PRIMARY KEY (trace_id, span_id)
    );
    CREATE INDEX IF NOT EXISTS idx_otel_trace_id ON otel_spans(trace_id);
    CREATE INDEX IF NOT EXISTS idx_otel_start_time ON otel_spans(start_time);
    CREATE INDEX IF NOT EXISTS idx_otel_session ON otel_spans(session_id);
    CREATE INDEX IF NOT EXISTS idx_otel_correlation ON otel_spans(correlation_id);
    \"\"\"
    \x0d
    class SQLiteSpanExporter:
        \"\"\"Exports OTel spans to memory_store.db for unified trace analysis.\"\"\"
        \x0d
        def __init__(self, db_path: str):
            self.db_path = db_path
            self._init_schema()
            self.export_count = 0
        \x0d
        def _init_schema(self):
            conn = sqlite3.connect(self.db_path, timeout=5)
            conn.execute(\"PRAGMA journal_mode=WAL\")
            conn.executescript(OTEL_SPANS_SCHEMA)
            conn.commit()
            conn.close()
        \x0d
        def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
            conn = sqlite3.connect(self.db_path, timeout=5)
            conn.execute(\"BEGIN TRANSACTION\")
            try:
                for span in spans:
                    ctx = span.get_span_context()
                    parent_ctx = span.parent
                    parent_id = format(parent_ctx.span_id, \"016x\") if parent_ctx and hasattr(parent_ctx, 'span_id') else None
                    attrs = dict(span.attributes) if span.attributes else {}
                    conn.execute(
                        \"INSERT OR REPLACE INTO otel_spans \"
                        \"(trace_id, span_id, parent_span_id, name, kind, \"
                        \" start_time, end_time, status_code, attributes, \"
                        \" correlation_id, session_id) \"
                        \"VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\",
                        (
                            format(ctx.trace_id, \"032x\"),
                            format(ctx.span_id, \"016x\"),
                            parent_id,
                            span.name,
                            str(span.kind),
                            span.start_time,
                            span.end_time,
                            span.status.status_code.value,
                            json.dumps(attrs),
                            attrs.get(\"correlation_id\"),
                            attrs.get(\"session_id\"),
                        )
                    )
                    self.export_count += 1
                conn.commit()
                return SpanExportResult.SUCCESS
            except Exception as e:
                print(f\"    [CD3] Export error: {e}\")
                return SpanExportResult.FAILURE
            finally:
                conn.close()
        \x0d
        def shutdown(self):
            pass
    \x0d
    # --- Determine DB path (same as DirectMemory) ---"""

new_inline = """    # --- Use canonical SQLiteSpanExporter from cd3_exporter module ---"""

if old_inline in content:
    content = content.replace(old_inline, new_inline, 1)
    fixes.append("Replaced inline SQLiteSpanExporter class with canonical import")
else:
    fixes.append("WARNING: Inline class pattern not found - checking alternative...")
    # Try alternative pattern without the import line
    alt_pattern = """    OTEL_SPANS_SCHEMA = \"\"\"
    CREATE TABLE IF NOT EXISTS otel_spans ("""
    if alt_pattern in content:
        fixes.append("  Found alternative pattern but replacement failed")
        fixes.append(f"  Pattern found at index: {content.find(alt_pattern)}")

# Fix 3: Replace the OTel setup section
old_setup = """    # --- Configure OTel with SQLite exporter ---
    exporter = SQLiteSpanExporter(str(memory_db_path))
    \x0d
    resource = Resource.create({
        \"service.name\": \"cd_integration_test\",
        \"service.version\": \"1.0.0\",
    })
    \x0d
    provider = TracerProvider(resource=resource)
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    \x0d
    # Set as global tracer provider
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)"""

new_setup = """    # --- Configure OTel with canonical SQLiteSpanExporter ---
    exporter = SQLiteSpanExporter(db_path=str(memory_db_path), batch_size=64)

    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider

    resource = Resource.create({
        \"service.name\": \"cd_integration_test\",
        \"service.version\": \"1.0.0\",
    })

    provider = TracerProvider(resource=resource)
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)"""

if old_setup in content:
    content = content.replace(old_setup, new_setup, 1)
    fixes.append("Replaced OTel setup with canonical exporter")
else:
    fixes.append("WARNING: OTel setup pattern not found")

# Fix 4: Clean up unused imports in CD3 function (OTEL_SPANS_SCHEMA, sqlite3)
# Don't remove sqlite3 import here - it's used for trace queries

with open("tests/test_cross_domain_integration.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixes applied:")
for f in fixes:
    print(f"  {f}")
