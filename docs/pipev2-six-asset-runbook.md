# PipeV2 six-asset runbook

This document describes how to prepare the six-asset PipeV2 rollout from
[`mm-sapphire-pipelines` PR 49](https://github.com/Parsewave-internal/mm-sapphire-pipelines/pull/49).
It does not start or authorize a pipeline run.

## Server

| Role | Public IP | Pipeline state |
| --- | --- | --- |
| Existing runner | `2.28.20.231` | PipeV2 not started |

No additional servers were provisioned. The available AWS identity is scoped
to S3 artifacts and cannot enumerate EC2, so this is not a complete inventory
of the cloud account.

## Repositories and revisions

Use a dedicated clean checkout:

```bash
git clone git@github.com:Parsewave-internal/mm-sapphire-pipelines.git
cd mm-sapphire-pipelines
gh pr checkout 49
test "$(git rev-parse HEAD)" = aa43d9eb0f9da24494dd9569f91d57e719543d54
```

PR 49 pins:

- Yggdrasil: `codex/audio-traces-optional-nop`
- pw-harness: `/home/ubuntu/pw-harness`
- pw-harness commit: `652f230b4619c1d0932bac714e5c2a27b7ae2afe`

Install Git, Git LFS, GitHub CLI, Docker, `uv`, Python 3.12+, `ffmpeg`, and
`ffprobe`. The runner needs enough disk for six source/golden pairs and solver
artifacts.

> **Deployment blocker:** PR 49 currently sets `deploy.pr_base: accepted`.
> Do not run it until that field is changed and reviewed as `main`, as required
> for task PRs to target mm-sapphire `main`.

## Credentials and environment

Create `pipelines/pipev2/.credentials.yaml`, set mode `0600`, and obtain values
from the approved Parsewave secret store. Never commit the file.

```yaml
AWS_ACCESS_KEY_ID: "<S3 uploader key>"
AWS_SECRET_ACCESS_KEY: "<S3 uploader secret>"
AWS_REGION: "us-east-1"
GH_TOKEN: "<internal-repository and PR token>"
CLAUDE_OAUTH_TOKEN: "<Parsewave proxy bearer>"
CLAUDE_PROXY_URL: "<Parsewave proxy URL>"
OPENROUTER_API_KEY: "<judge key>"
LLM_JUDGE_API_KEY: "<judge key, if required>"
LLM_JUDGE_API_URL: "<judge endpoint, if overridden>"
```

PipeV2 pins the judge to `google/gemini-3.6-flash`; ambient
`LLM_JUDGE_MODEL` does not override it. Solver traffic uses the Parsewave proxy,
while judge credentials are forwarded only to verifier containers.

AWS credentials are required. Accepted tasks upload final oracle, NOP, and
agent trace bundles to `s3://mm-sapphire/video-editing-pipev2/`, then synchronize
the final URLs into both trace tables in `task.toml`.

## Six-asset selection

PR 49 uses `pipelines/pipev2/ideas1.yaml`, not `idea18.yaml`. Select six ideas
sequentially without replacement. Each idea pairs a solver-visible
`montage-output.mp4` with a hidden `output-video.mp4` golden solution. Sequential
selection prevents duplicate assets and keeps oracle comparisons repeatable.

Do not expose golden assets to solvers or randomly sample with replacement. If
an independently reviewed `idea18.yaml` is later required, update both
`ideation.source` and `ideation.idea_file_pick.params.file`, and ensure every
source name contains the exact `asset-NNN` ID.

## Rubric consistency requirements

Keep PR 49's immutable controls enabled:

- builders cannot edit verifier Python;
- rubric files are schema-validated and written atomically;
- predicates are related yes/no questions under 350 characters, avoiding
  excessive prose and multi-criterion comma lists;
- the final rubric has exactly 15 positive items and no more than three signed
  penalties with valid integer weights;
- RG4 trains on two solver outputs, freezes the rubric, and only then evaluates
  the third solver as a holdout;
- accepted tasks require oracle `>= 0.85`, NOP exactly `0` with zero judge
  calls, byte-identical rubrics, successful rescoring, and the locked verifier
  hash.

Never manually repair generated rubric JSON or verifier code. Preserve the
pipeline's classified review, protocol, budget, and quality outcomes so trials
remain comparable.

## Preflight without running tasks

```bash
PYTHONPATH=pipelines/pipev2 \
  python3 -m unittest discover -s pipelines/pipev2/tests -v

PYTHONPATH=pipelines/pipev2 \
  python3 pipelines/pipev2/backtest.py \
  --output pipelines/pipev2/backtest-archived.json

/home/ubuntu/.cache/yggdrasil/codex/audio-traces-optional-nop/.venv/bin/python \
  -m yggdrasil.cli validate --config pipelines/pipev2/config.yaml

git lfs env
docker info >/dev/null
aws sts get-caller-identity >/dev/null
aws s3api head-bucket --bucket mm-sapphire
gh auth status
```

Stop if validation fails, S3 is inaccessible, the PR head differs, the PR-base
blocker remains, or another process is using the checkout.

## Intended tmux command

Do not execute this until the PR-base blocker is reviewed and cleared:

```bash
tmux new-session -d -s pipev2-c2-t6 \
  "cd /home/ubuntu/mm-sapphire-pipelines-pr49 && \
   ./run.sh --config pipelines/pipev2/config.yaml \
     --credentials pipelines/pipev2/.credentials.yaml \
     --count 6 --concurrency 2 --conc-trials 6 \
     --logs-dir logs 2>&1 | tee pipev2-c2-t6.log"
```

Attach with `tmux attach -t pipev2-c2-t6`. `--concurrency 2` caps simultaneous
tasks and `--conc-trials 6` caps solver trials across the run. Do not launch a
second session from the same checkout.

## Completion checks

Confirm that the run manifest contains six unique asset IDs, every task has a
classified terminal outcome, and no run-owned containers remain. For each
accepted task, verify that:

- oracle, NOP, and agent trace bundles exist under the configured S3 prefix;
- both `task.toml` trace tables contain the final S3 URLs;
- rubric files are byte-identical and pass audit;
- the verifier hash matches the locked template;
- a task PR was opened against mm-sapphire `main`.

Missing S3 objects or missing trace URLs are deployment failures, even when
local trial artifacts exist.
