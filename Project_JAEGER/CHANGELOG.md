# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-03

### Added

- **Decision (jaeger-000)**: Jaeger accepted as *tracer of this tree* (consumes AOA `DelegationSpec` + `ArmResult` → spans within AOA). Rejected: Jaeger as thin OTLP client.
- **Grimorie v0.1.0** — The Spellbook: Incantations (API), Wards (validation), Rituals (workflows), Runes (configuration), Wards (protection spells), Runes (configuration runes).
- **Core Types**: `JaegerTracer`, `Span`, `DelegationSpec`, `ArmResult`, `SpanEvent`, `SpanStatus`, `SpanKind`, `ArmProvenance`.
- **Wards**: Span creation validation, span freeze protection, export validation, configuration validation.
- **Rituals**: Daily trace, freshness check, export rite, freshness audit.
- **Protection Spells**: `SpanFrozenError`, `SpanCreationError`, `StalenessWarning`, `ExportError`.
- **Configuration Runes**: Tracer runes, Exporter runes, Span runes with full schema.
- **Configuration**: YAML-based config with tracer, exporter, span sections.
- **Span Format**: JSON with required `delegation.*` and `arm.*` attributes.
- **Project Structure**: `src/jaeger/`, `tests/`, `tools/`, `grimorie/`.

### Decided

- **jaeger-000**: Jaeger is the *tracer of this tree* (consumes AOA `DelegationSpec` + `ArmResult` → spans within AOA). Rejected: Jaeger as thin OTLP client.

### Planned

- **jaeger-001**: Scaffold `Project_JAEGER/` to `Project_CRADLE` shape
- **jaeger-002**: AOA-ARM integration (`BaseArm` + `@register_arm` + `_ARM_MODULES`)
- **jaeger-003**: OTLP Export (transport AOA lacks; trace correlation field `DelegationSpec` lacks)

### License

Changed from Apache-2.0 to **CDDL-1.1** (Common Development and Distribution License 1.1).

---

## [Unreleased]

- jaeger-001: Scaffold `Project_JAEGER/` to `Project_CRADLE` shape
- jaeger-002: AOA-ARM integration (`BaseArm` + `@register_arm` + `_ARM_MODULES`)
- jaeger-003: OTLP Export transport

---

*Grimorie version 0.1.0 — Updated 2026-11-03*