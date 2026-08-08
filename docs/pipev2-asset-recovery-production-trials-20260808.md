# PipeV2 asset-recovery production-trial report

Date: 2026-08-08

Disposition: no deployment and no PR. The task ideas and preparation findings
are published as report-repository documentation only.

## What was run

The no-deploy production configuration selected the first five asset-recovery
seeds and kept the configured solver rule:

- three solver trials per task;
- aggregation by arithmetic mean;
- acceptance threshold: aggregate mean `<= 0.65`;
- `PIPEV2_JUDGE_MODEL=google/gemini-3.6-flash`;
- `--concurrency 1 --conc-trials 1` after the parallel run exhausted disk.

The deployment steps `pipev2.deploy_gh_push` and `pipev2.deploy_open_pr` were
removed from this trial configuration.

## Production result

The run was intentionally stopped after the first task had completed its
three required solver trials and frozen-rubric rescore. The remaining four
tasks were not scored, so this is a production sanity trial, not an R6 or
five-task success claim.

| Task | Solver trials | Aggregate mean | Threshold result |
| --- | --- | ---: | --- |
| `temple-tricolor-flight-opener` / task `000-5e68ab` | `0.564516`, `0.000000`, `0.758065` | `0.440860` | passes aggregate `<= 0.65` |
| four remaining selected seeds | not reached | — | no claim |

The individual `0.758065` trial is above the threshold, but that does not
fail this criterion: the configured rule is on the mean across the three
trials. The first task's bootstrap golden-oracle diagnostic was `0.564516`
against an expected `0.85`; it was non-terminal and correctly allowed the
trial to continue.

The successful solver output was a human-viewable 9.53-second, 1080x1920
H.264 portrait MP4 with full decode verification. It had no audio track. The
production-generated instruction allowed that, even though the preparation
brief requested audible sound; this is a task-generation mismatch and should
be fixed before using the opener as an audio-sensitive benchmark. It is not
evidence that the new extraction/audio contract works.

## Infrastructure findings and fixes

1. The first attempt exhausted disk while installing CUDA dependencies. The
   disposable UV cache and idle temporary trial artifacts were reclaimed.
2. The next attempt exposed model-policy drift: the ambient judge was not the
   permitted Gemini judge. The trial was rerun with the judge model pinned.
3. The provider smoke initially timed out on all five tasks. The live-smoke
   structured-vote timeout was increased from 45 seconds to 120 seconds while
   retaining three bounded retries. Two independent smokes then passed.
4. A parallel three-sandbox solver run filled the machine during its first
   solver phase. Serializing the three trials with `--conc-trials 1` kept disk
   use stable and produced the valid three-score result above.

## Interpretation

This proves that the production harness can reach the builder, verifier, and
three-trial aggregate gate for one selected seed after the infrastructure
adjustments. It does not yet prove the full five-task or six-sample behavior,
and it does not measure the specialized hidden manifest/package gate. That
full evaluation remains the next run once enough disk and runtime budget are
reserved.

Related documents:

- `pipev2-asset-recovery-task-ideas-20260808.yaml`
- `pipev2-asset-recovery-20260808-findings.md`
