# PipeV2 11-Asset Run Failure Report

## Run summary

- Run ID: `20260804-092656-868e5a`
- Run date: 2026-08-04 (UTC)
- Requested tasks: 11
- Engine result: 11 tasks reached terminal states, 0 engine failures
- Accepted tasks: 2
- Review outcomes: 9
- Accepted PRs:
  - [`asset-282` / task `001-63af75` / PR #2042](https://github.com/Parsewave-internal/mm-sapphire/pull/2042)
  - [`asset-143` / task `005-4fc94c` / PR #2045](https://github.com/Parsewave-internal/mm-sapphire/pull/2045)

The engine's `success=11 failed=0` result means all tasks completed the pipeline without an infrastructure exception. It does **not** mean all tasks passed the semantic quality gates. Nine tasks ended in explicit `needs_review_*` outcomes and therefore did not deploy or open PRs.

## Non-accepted tasks

| Index | Task | Asset | Outcome | Oracle | Agent 1 | Agent 2 | Agent 3 | Terminal stage | Evidence |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 0 | `000-cc0b44` | `asset-277` | `needs_review_discrimination` | `1.0000` | `0.9143` | `0.2286` | N/E | `pipev2.run_rg4` | `INSUFFICIENT_DISCRIMINATION`: the oracle-safe training pool could not satisfy RG4's discrimination contract after all regeneration rounds. Holdout evaluation was correctly skipped. |
| 2 | `002-30d137` | `asset-284` | `needs_review_quality` | `0.8182` | `0.3636` | `0.4545` | `0.6682` | `pipev2.run_rg4` | `ORACLE_PROTECTION_FAILURE`: RG4 could not freeze a discriminative rubric without violating oracle protection. |
| 3 | `003-653fbd` | `asset-285` | `needs_review_quality` | `0.6532` | `0.4194` | `0.4194` | `0.4565` | `pipev2.run_rg4` | `ORACLE_PROTECTION_FAILURE`: RG4 could not freeze a discriminative rubric without violating oracle protection. |
| 4 | `004-f1148a` | `asset-297` | `needs_review_quality` | `0.8286` | `0.4857` | `0.4857` | `0.0000` | `pipev2.run_rg4` | `ORACLE_PROTECTION_FAILURE`: RG4 could not freeze a discriminative rubric without violating oracle protection. |
| 6 | `006-9da516` | `asset-171` | `needs_review_discrimination` | `1.0000` | `0.3514` | `0.1892` | `0.7568` | `pipev2.run_rg4` | `HOLDOUT_GENERALIZATION_FAILURE`: the frozen rubric failed the holdout generalization/discrimination contract. |
| 7 | `007-0b3462` | `asset-201` | `needs_review_quality` | `0.7273` | `0.3636` | `0.3636` | `0.0000` | `pipev2.run_rg4` | `ORACLE_PROTECTION_FAILURE`: RG4 could not freeze a discriminative rubric without violating oracle protection. |
| 8 | `008-2e5adb` | `asset-21` | `needs_review_quality` | `1.0000` | `1.0000` | N/E | `1.0000` | `difficulty.pipev2_solver_split` | Agent 2 failed before producing a saved MP4, so the required two-training/one-holdout split could not proceed safely. |
| 9 | `009-827710` | `asset-23` | `needs_review_quality` | `0.6667` | N/E | N/E | N/E | `oracle.pipev2_score_golden.bootstrap` | Bootstrap oracle score was `0.666667`, below the required `0.750000` early-quality floor. |
| 10 | `010-477f07` | `asset-267` | `needs_review_quality` | `0.7037` | N/E | N/E | N/E | `oracle.pipev2_score_golden.bootstrap` | Bootstrap oracle score was `0.703704`, below the required `0.750000` early-quality floor. |

`N/E` means the role was not evaluated. Scores for RG4-stage outcomes are the rubric-stage oracle/training/holdout scores recorded by RG4: Agent 1 and Agent 2 are the two training solvers, and Agent 3 is the deferred holdout solver. Task `000-cc0b44` never evaluated its holdout, so Agent 3 has no score. Scores for tasks `008–010` come from the bootstrap verifier stage because those tasks stopped before RG4. These are not final deployed-rubric rescores.

## Failure-class breakdown

### RG4 discrimination and generalization failures (2)

- `asset-277` exhausted all candidate-regeneration rounds without producing an oracle-safe rubric that discriminated sufficiently between oracle and training outputs.
- `asset-171` reached frozen-rubric holdout evaluation, but the result failed the holdout generalization/discrimination contract.

These outcomes are resumable review states, not transport or runtime failures. Follow-up should inspect solver similarity, source/golden separability, and the retained RG4 candidate/vote evidence before deciding whether to revise the task or rerun it.

### RG4 oracle-protection failures (4)

- `asset-284`
- `asset-285`
- `asset-297`
- `asset-201`

For each task, candidate generation and validation ran, but RG4 could not freeze a sufficiently discriminative rubric while preserving the oracle-protection constraints. These tasks should be reviewed for golden quality, instruction/golden alignment, and whether the solver outputs expose enough task-specific failure modes for a safe rubric.

### Invalid solver artifact (1)

- `asset-21` had one solver trial with an invalid saved MP4. Agent 2 failed during setup when `nvm install 22` could not resolve a Node 22 release, so no agent output or verifier score exists for that lane.

Before rerunning, inspect the failed solver trial's artifact manifest, agent log, FFmpeg/ffprobe output, and final output path. A rerun is reasonable only after determining whether the artifact failure was transient or caused by the task contract/edit strategy.

### Bootstrap oracle below the early floor (2)

- `asset-23`: `0.666667` vs. required `0.750000`
- `asset-267`: `0.703704` vs. required `0.750000`

The pipeline stopped these tasks before solver/RG4-heavy stages, as intended. Review the prepared golden, bootstrap rubric fit, source/golden staging, and task requirements. Do not lower the threshold merely to force deployment; the final oracle gate is stricter (`0.85`).

## Operational incident during the run

The host filesystem briefly reached 100% usage while the first solver trials were running. Disposable Docker build cache, historical pipeline logs, and a duplicate old-worktree asset cache were removed, restoring approximately 28 GB of free space at that point. The active run recovered and ultimately completed with no infrastructure-failed tasks. This incident is therefore not recorded as the cause of any terminal review outcome above.

For future runs, keep at least 20–30 GB free before launch and retain only the current run's logs while it is active.

## Deployment disposition

Only tasks that pass final acceptance are packaged and deployed. The nine tasks in this report correctly produced no PRs. The two accepted tasks each produced an open, mergeable PR with the large-file guard passing at the time of verification:

- [PR #2042](https://github.com/Parsewave-internal/mm-sapphire/pull/2042)
- [PR #2045](https://github.com/Parsewave-internal/mm-sapphire/pull/2045)

## Evidence source

This report was generated from the retained run directory:

`/home/ubuntu/mm-sapphire-pipelines-pr49-current/pipelines/pipev2/logs/20260804-092656-868e5a`

Authoritative inputs included `events.jsonl`, each task's `pipev2/<task-id>/task_outcome.json`, RG4 reports/checkpoints, and exact GitHub PR queries by deployment branch.
