# PipeV2 Next-15 Final Report

Generated: 2026-08-02T05:37Z

## Summary

- Supervisor: finished all 15 canonical indices.
- Outcomes: 5 accepted, 8 needs-review, 2 infrastructure failures.
- Accepted PRs: all 5 have local validation comments, Sapphire format-check trace triggers, and PASS bot comments.
- Remaining librarian inventory: not recorded in `logs/pipev2-prepared-assets-20260802.json`; the local artifact only records the 15 selected assets as loaned.

## Selected Assets

| Index | Asset | Task | Outcome | PR |
|---:|---|---|---|---|
| 0 | asset-90 | 000-dd7c98 | accepted | https://github.com/Parsewave-internal/mm-sapphire/pull/1790 |
| 1 | asset-67 | 000-545102 | needs_review_model_contract | - |
| 2 | asset-150 | 000-d1e263 | needs_review_quality | - |
| 3 | asset-142 | 000-50f0db | accepted | https://github.com/Parsewave-internal/mm-sapphire/pull/1792 |
| 4 | asset-135 | 000-f7ef19 | needs_review_quality | - |
| 5 | asset-40 | 000-9ad46d | needs_review_quality | - |
| 6 | asset-140 | 000-863365 | infrastructure_failed | - |
| 7 | asset-51 | 000-abbb17 | accepted | https://github.com/Parsewave-internal/mm-sapphire/pull/1793 |
| 8 | asset-53 | 000-281b6a | needs_review_quality | - |
| 9 | asset-36 | 000-e7c5fa | needs_review_discrimination | - |
| 10 | asset-133 | 000-5ae558 | accepted | https://github.com/Parsewave-internal/mm-sapphire/pull/1794 |
| 11 | asset-100 | 000-c8b062 | needs_review_quality | - |
| 12 | asset-102 | 000-4eb6f9 | infrastructure_failed | - |
| 13 | asset-123 | 000-a1a82e | needs_review_quality | - |
| 14 | asset-62 | 000-2bb416 | accepted | https://github.com/Parsewave-internal/mm-sapphire/pull/1803 |

## Accepted PRs

| Index | Asset | Task | PR | Local validation | Trace-check trigger | PASS |
|---:|---|---|---|---|---|---|
| 0 | asset-90 | 000-dd7c98 | https://github.com/Parsewave-internal/mm-sapphire/pull/1790 | https://github.com/Parsewave-internal/mm-sapphire/pull/1790#issuecomment-5154762562 | https://github.com/Parsewave-internal/mm-sapphire/pull/1790#issuecomment-5154762601 | https://github.com/Parsewave-internal/mm-sapphire/pull/1790#issuecomment-5154765621 |
| 3 | asset-142 | 000-50f0db | https://github.com/Parsewave-internal/mm-sapphire/pull/1792 | https://github.com/Parsewave-internal/mm-sapphire/pull/1792#issuecomment-5154929806 | https://github.com/Parsewave-internal/mm-sapphire/pull/1792#issuecomment-5154929850 | https://github.com/Parsewave-internal/mm-sapphire/pull/1792#issuecomment-5154932380 |
| 7 | asset-51 | 000-abbb17 | https://github.com/Parsewave-internal/mm-sapphire/pull/1793 | https://github.com/Parsewave-internal/mm-sapphire/pull/1793#issuecomment-5155368948 | https://github.com/Parsewave-internal/mm-sapphire/pull/1793#issuecomment-5155369001 | https://github.com/Parsewave-internal/mm-sapphire/pull/1793#issuecomment-5155373244 |
| 10 | asset-133 | 000-5ae558 | https://github.com/Parsewave-internal/mm-sapphire/pull/1794 | https://github.com/Parsewave-internal/mm-sapphire/pull/1794#issuecomment-5155476664 | https://github.com/Parsewave-internal/mm-sapphire/pull/1794#issuecomment-5155476708 | https://github.com/Parsewave-internal/mm-sapphire/pull/1794#issuecomment-5155480289 |
| 14 | asset-62 | 000-2bb416 | https://github.com/Parsewave-internal/mm-sapphire/pull/1803 | https://github.com/Parsewave-internal/mm-sapphire/pull/1803#issuecomment-5155687714 | https://github.com/Parsewave-internal/mm-sapphire/pull/1803#issuecomment-5155687753 | https://github.com/Parsewave-internal/mm-sapphire/pull/1803#issuecomment-5155690268 |

## Failed / Review Report

| Index | Asset | Task | Outcome | Stage | Reason | RG4 status | RG4 oracle | RG4 solver | RG4 gap |
|---:|---|---|---|---|---|---|---:|---:|---:|
| 1 | asset-67 | 000-545102 | needs_review_model_contract | pipev2.run_rg4 | OpenRouterFailure: OpenRouter model content is not valid JSON | - | - | - | - |
| 2 | asset-150 | 000-d1e263 | needs_review_quality | pipev2.run_rg4 | RG4 could not freeze a discriminative rubric | ORACLE_PROTECTION_FAILURE | 0.918919 | 0.163514 | 0.755405 |
| 4 | asset-135 | 000-f7ef19 | needs_review_quality | pipev2.run_rg4 | RG4 could not freeze a discriminative rubric | ORACLE_PROTECTION_FAILURE | 0.870968 | 0.316129 | 0.554839 |
| 5 | asset-40 | 000-9ad46d | needs_review_quality | oracle.pipev2_score_golden.final | oracle score 0.775000 is below required 0.850000 | PASS | 0.914286 | 0.035714 | 0.878571 |
| 8 | asset-53 | 000-281b6a | needs_review_quality | difficulty.pipev2_solver_split | 1 solver trials produced invalid saved MP4 artifacts | - | - | - | - |
| 9 | asset-36 | 000-e7c5fa | needs_review_discrimination | pipev2.run_rg4 | RG4 could not freeze a discriminative rubric | HOLDOUT_GENERALIZATION_FAILURE | 1.000000 | 0.818182 | 0.181818 |
| 11 | asset-100 | 000-c8b062 | needs_review_quality | pipev2.run_rg4 | RG4 could not freeze a discriminative rubric | ORACLE_PROTECTION_FAILURE | 0.850000 | 0.000000 | 0.850000 |
| 13 | asset-123 | 000-a1a82e | needs_review_quality | pipev2.run_rg4 | RG4 could not freeze a discriminative rubric | ORACLE_PROTECTION_FAILURE | 0.850000 | 0.606452 | 0.243548 |
| 6 | asset-140 | 000-863365 | infrastructure_failed | pipev2.run_rg4 | RuntimeError: Judge proxy remains over 5.0 MiB: /home/ubuntu/mm-sapphire-pipelines-sparse/logs/20260802-034935-632027/pipev2/000-863365/rg4/media/design/oracle.judge.mp4 (6.22 MiB) | - | - | - | - |
| 12 | asset-102 | 000-4eb6f9 | infrastructure_failed | oracle.pipev2_score_golden.final | verifier failure: ValueError: judge response contains no JSON object; oracle score 0.000000 is below required 0.850000 | PASS | 1.000000 | 0.000000 | 1.000000 |

## Accepted Metrics

| Index | Task | RG4 oracle | RG4 solver | RG4 gap | Final oracle | Final NOP | Saved solver rescores |
|---:|---|---:|---:|---:|---:|---:|---|
| 0 | 000-dd7c98 | 1.000000 | 0.259091 | 0.740909 | 1.000000 | 0.000000 | 0.000000, 0.034211, 0.034211 |
| 3 | 000-50f0db | 0.885714 | 0.085714 | 0.800000 | 1.000000 | 0.000000 | 0.000000, 0.075000, 0.150000 |
| 7 | 000-abbb17 | 0.914286 | 0.300000 | 0.614286 | 1.000000 | 0.000000 | 0.020000, 0.645000, 0.375000 |
| 10 | 000-5ae558 | 0.914286 | 0.228571 | 0.685714 | 1.000000 | 0.000000 | 0.625000, 0.475000, 0.625000 |
| 14 | 000-2bb416 | 1.000000 | 0.250000 | 0.750000 | 1.000000 | 0.000000 | 0.350000, 0.125000, 0.550000 |
