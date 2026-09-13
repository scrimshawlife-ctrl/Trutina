# Spec 000: Brier Spine

Historical derivative precursor, preserved for provenance. The implementation-ready module specification is [the Trutina spine](../000-trutina-spine/spec.md), with atomic behavior in [Spec 001](../001-score/spec.md). The packet shapes, integration claims, file list and CLI examples below are historical proposals, not evidence of implemented interfaces. VOID is unscorable; binary range [0,1] is not the unscaled multiclass range. This does not govern or activate.

**Owns**: Brier score computation (atomic, series, BSS, Murphy, Yates), performance ledger emission, skill evolution telemetry
**Honesty**: OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE
**Shape**: T0 rules now. Encoder name-gated. Not a chatbot.
**Lane**: SHADOW - classify live - train/Hub gated

## Overview

The Brier spine provides telemetry-grade accuracy scoring for Abraxas model surfaces. It does not produce forecasts; it scores settled outcomes against predicted probabilities. All Brier values are null until explicit human settlement via /hyperlex-settle or equivalent operator decision.

This spec defines the core Brier functions and their integration with the Abraxas skill evolution system (abx-hermes-skill-evolution).

## Key Concepts

- **Brier Score**: Mean squared error between predicted probabilities and observed outcomes (0 = perfect, 1 = worst).
- **Settlement Requirement**: Brier is only computed after operator-settled forecast outcomes (TRUE/FALSE/VOID).
- **Telemetry Use**: Feeds abx-hermes-skill-evolution to build performance ledgers and detect skill drift.
- **Honesty**: Output includes OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE labels per Provenance Kit.

## Output Shapes

### Atomic Brier Packet (brier.packet.v0)
{
  "schema": "brier.packet.v0",
  "forecast_id": "string", // Hyperlex forecast ID or Abraxas OperationTrace ID
  "expected_probability": "number [0,1]", // Model's predicted probability
  "observed_outcome": "0 | 1", // Settled outcome (0 = false, 1 = true)
  "brier_score": "number [0,1] | null", // Null until settled
  "honesty": "OBSERVED | INFERRED | SPECULATIVE | NOT_COMPUTABLE",
  "provenance": {
    "source": "string", // e.g., "hyperlex", "holler-sports", "abx-neon-genie"
    "ingest_source": "string | null", // e.g., "real", "reddit", "moltbook"
    "settled_by": "string | null", // Operator ID or "human"
    "settled_at": "string (ISO 8601) | null"
  },
  "forecast_eligible": "boolean" // False for Brier packets (they are scores, not forecasts)
}

### Series Brier (brier.series.v0)
{
  "schema": "brier.series.v0",
  "series_id": "string", // Group of related forecasts (e.g., skill version, model)
  "members": ["forecast_id1", "forecast_id2", ...],
  "series_brier": "number [0,1] | null", // Mean Brier of settled members
  "member_count": "integer",
  "settled_count": "integer",
  "honesty": "OBSERVED | INFERRED | SPECULATIVE | NOT_COMPUTABLE",
  "provenance": {
    "source": "string",
    "settled_by": "string | null",
    "settled_at": "string (ISO 8601) | null"
  }
}

## Integration Points

### With Hyperlex
- Hyperlex emits score pairs (expected_probability, observed_outcome) only after settlement via hyperlex.calibrate.
- Brier spine consumes these via hyperlex.compat.abraxas.brier_score.to_brier_score_packet.

### With abx-hermes-skill-evolution
- Consumes OperationTraces from skilled surfaces.
- Converts traces to Brier packets when settled outcomes are available.
- Builds performance ledgers over time to detect skill degradation or improvement.

### With Holler-Sports
- Holler-Calibrate produces settled sports forecasts with Brier-aware scoring.
- Brier spine provides the underlying score computation and ledger emission.

## Rules

1. **Never Invent Brier**: All open analysis keeps brier: null and provenance.brier: null.
2. **Settlement Gate**: Brier scores require explicit operator decision (TRUE/FALSE/VOID).
3. **Determinism**: Serialization must be deterministic; no wall-clock, UUID, or randomness in Brier computation.
4. **SHADOW Lane**: Brier spine is advisory only; never mutates active skills or triggers promotion without operator approval.
5. **Provenance**: Strict provenance tracking; all inputs must be traceable to source.

## Files

- src/brier/__init__.py: Public API (compute_atomic_brier, to_brier_score_packet, to_brier_ledger_entry)
- src/brier/core.py: Core computation logic (Brier, BSS, Murphy, Yates)
- src/brier/ledger.py: Performance ledger emission for skill evolution
- src/brier/compat/: Abraxas-specific shape mappers (to BrierLedgerEntry.v1, etc.)
- tests/: Unit tests for all functions
- fixtures/seed/: Settled series examples for validation

## Quickstart

```bash
pip install -e ".[dev]"
python -m brier --version
python -m brier compute 0.7 1 --settled-by human
# Output: brier.packet.v0 with brier_score=0.09
pytest -q
```

Provenance: scrimshawlife-ctrl/Trutina + specs/BIND.md + Hash: 2724c9baf6e5837441f65e569347c8e713a2a32e (observed repository baseline; historical body preserved).
