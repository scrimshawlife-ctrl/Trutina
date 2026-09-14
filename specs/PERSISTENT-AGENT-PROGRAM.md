# Trutina participation in persistent-agent research

Program: `ABX-NOEMA-REP-001`  
Status: proposed / SHADOW / ADVISORY_ONLY  
Date: 2026-09-14  
Scope: specification review only; no runtime or permission change.

[Shared program draft](https://github.com/scrimshawlife-ctrl/Abraxas/blob/codex/persistent-agent-program-20260914/docs/research/persistent-agent-program/spec.md) owns cross-repository experiment coordination, workflows WF-P01 through WF-P05, acceptance AC-P01 through AC-P10, and the candidate sidecar. This document owns only this repository's participation mapping. The program is not a new specialist or a replacement for existing contracts. Draft branch links are review links; pin the accepted commit when adopted.

## Existing authority

[Constitution](../constitution.md), [bind receipt](BIND.md), [score spec](001-score/spec.md), and [spine](000-trutina-spine/spec.md) retain authority. Specialist id abx.brier, function trutina.score, packet brier.score.v0, home yggdrasil.replay remain unchanged. No hard import or replacement of outcome_brier is introduced.

## Contribution and contract

Trutina provides the calibration measurement for eligible externally settled forecasts about registered experimental outcomes. It does not forecast, settle outcomes, infer semantics or govern promotion. A lexical confidence, Semion class score, Noesis similarity, latency or action-validity rate is not automatically a Brier probability/outcome pair.

The external adapter must reference the forecast identity, probability, target event, issue/cutoff time, horizon, preregistered resolution rule, settlement authority/evidence and resolved binary outcome. Those references belong in the shared sidecar or existing producer objects, not new fields silently added to brier.score.v0. Resolve compatibility with current SCORE/BATCH contracts before implementation.

## Workflow and acceptance

J-P04 -> WF-P04 -> eligible external settlement -> existing SCORE contract -> AC-P07 -> T-TRU-P01. Actors are forecast producer, authorized settlement owner and scorer, with separate authority. A probability must be registered before the outcome is observed; post-outcome assignment cannot count as prospective calibration evidence.

T-TRU-P01: define a permitted adapter field mapping and accepted/denied fixtures. For synthetic p=0.8,y=1, BRIER_BINARY_V1=(p-y)^2 yields 0.04 under declared floating tolerance. Label this a test, never a real forecast. A missing, VOID, malformed, unresolved, out-of-range or wrong-lane input must follow the existing contract's failure/NOT_COMPUTABLE behavior. No automatic conversion of missing y to zero.

J-P04 -> WF-P04 -> REVIEWED_RESULT/INCONCLUSIVE -> batch/decomposition evidence -> AC-P08 -> T-TRU-P02: preserve explicit cohorts, exclusions, dependence units and baseline definitions. Brier measures probabilistic forecast accuracy; calibration and resolution analysis are distinct. Neither a low single score nor a small batch proves calibration. Batch, decomposition and uncertainty modes remain subject to their existing support and sample-size conditions.

## Resource and governance boundaries

Deterministic score arithmetic is CPU baseline work. Do not propose training a Trutina model or consuming GPUs to justify NVIDIA eligibility. Its contribution is trustworthy evaluation of the GPU-backed system. No new mode, packet schema, learned head, Hub upload, router bind, ledger finalization or forecast authority is opened here.

## Verification and unresolved evidence

Run existing Trutina tests and local link/diff checks. Cross-component forecast/settlement source mapping remains proposed; actual settled experimental outcomes are NOT_COMPUTABLE. Existing output and bind tests can establish component conformance only, not end-to-end Noema forecast validity.
