# Running the Idea 14 video-editing pipeline

This run builds 15 video-editing tasks from the downloaded Librarian sample in
`assets/`. Each entry in `ideas14.yaml` exposes a montage to the solver and
keeps its paired `output-video.mp4` as the hidden golden reference.

## Prerequisites

- Linux with Bash, Python 3, Git, Docker, and `uv` on `PATH`.
- SSH access to `git@github.com:Parsewave-internal/yggdrasil.git`.
- Access to `/home/ubuntu/pw-harness`, as configured in `config.yaml`.
- The 15 `assets/idea18-asset-*` directories already present in this pipeline.
- Enough local disk for Docker images, task worktrees, solver outputs, and
  traces. The checked-in sample media itself is approximately 660 MB.

Run all commands from the repository root:

```bash
cd /home/ubuntu/mm-sapphire-pipelines
```

## Credentials

Create a YAML credentials file outside version control. The launcher defaults
to the repository-root `.credentials.yaml` and copies it into the pipeline
directory with mode `0600`.

```yaml
# Required for Codex build, repair, and calibration agents.
proxy_token: "<parsewave-proxy-token>"

# Required by deploy.videoediting_gh_push and deploy.open_pr.
github_token: "<github-token-with-repo-and-pr-access>"

# Required to upload traces to s3://mm-sapphire/video-editing.
aws_access_key_id: "<aws-access-key-id>"
aws_secret_access_key: "<aws-secret-access-key>"
aws_region: "us-east-1"

# Required if the harsh artifact audit runs through OpenRouter.
openrouter_api_key: "<openrouter-api-key>"
```

Instead of `openrouter_api_key`, a custom judge endpoint can be configured
with all of the following:

```yaml
llm_judge_api_key: "<judge-api-key>"
llm_judge_api_url: "<chat-completions-url>"
llm_judge_model: "<model-name>"
```

The AWS principal needs write access to the configured trace prefix. The
GitHub token needs clone, branch-push, and pull-request permissions for
`Parsewave-internal/mm-sapphire`.

Do not commit either `.credentials.yaml`. Both the root and pipeline-local
credential files are ignored and are removed from generated task packages.

`LIBRARIAN_API_KEY` and `LIBRARIAN_ASSET_PREFIX` are not needed for this run:
the selected Librarian assets have already been downloaded and are referenced
locally by `ideas14.yaml`.

## Environment variables

No environment variables are required when all credentials are in the YAML
file. Avoid stale judge/provider overrides, because they take precedence over
or can conflict with credential-file settings. A clean launch is:

```bash
env \
  -u LLM_JUDGE_BASE_URL \
  -u LLM_JUDGE_API_URL \
  -u LLM_JUDGE_API_KEY \
  -u LLM_JUDGE_MODEL \
  -u OPENROUTER_API_KEY \
  -u ATHENA_JUDGE_BASE_URL \
  -u ATHENA_JUDGE_API_KEY \
  -u ATHENA_JUDGE_MODEL \
  -u LIBRARIAN_API_KEY \
  -u LIBRARIAN_ASSET_PREFIX \
  ./run.sh \
    --credentials .credentials.yaml \
    --config pipelines/videoediting_pipeline/config.yaml \
    -- \
    --count 15 \
    --concurrency 5
```

The launcher itself unsets `HTTPS_PROXY`, `https_proxy`, and
`NODE_TLS_REJECT_UNAUTHORIZED`. Authentication and agent routing come from
`proxy_token`; do not manually set provider tokens in generated solver
containers.

## Pre-run checks

Confirm the config selects the required idea file:

```bash
grep -n 'ideas14.yaml' pipelines/videoediting_pipeline/config.yaml
```

Confirm all 30 source/golden media files exist:

```bash
find pipelines/videoediting_pipeline/assets \
  -path '*/idea18-asset-*/*.mp4' -type f | wc -l
```

The expected result is `30`: two MP4 files for each of 15 ideas. Do not rename
the asset directories; `ideas14.yaml` intentionally points to their existing
`idea18-asset-*` sampling names.

Optionally verify setup without launching task generation:

```bash
./run.sh \
  --credentials .credentials.yaml \
  --config pipelines/videoediting_pipeline/config.yaml \
  --smoke-test
```

## Run the pipeline

```bash
./run.sh \
  --credentials .credentials.yaml \
  --config pipelines/videoediting_pipeline/config.yaml \
  -- \
  --count 15 \
  --concurrency 5
```

`strategy: sequential` consumes all 15 entries in `ideas14.yaml` exactly once
for a 15-task run. Concurrency `5` limits the run to five active tasks at a
time; lower it if CPU, memory, Docker capacity, or judge rate limits are tight.

The first launch may take longer because `run.sh` clones the configured
Yggdrasil revision, prepares the `pw-harness` environment, and downloads
dependencies. A full run is expensive: every task can perform multiple build,
oracle, NOP, solver-calibration, audit, repair, trace, and deployment steps.

## Expected behavior and outputs

- Task generation uses `pipelines/videoediting_pipeline/ideas14.yaml`.
- Solver-visible input is each `montage-output.mp4`.
- Hidden oracle input is the corresponding `output-video.mp4`.
- The required task deliverable is `/app/output/final_video.mp4`.
- Sanitized traces upload under `s3://mm-sapphire/video-editing/`.
- Successful tasks push branches named `video-editing-task-{id}` and open PRs
  against the `accepted` branch of `Parsewave-internal/mm-sapphire`.

The terminal summary reports total, successful, and failed task counts. Keep
the complete run log when diagnosing failures; each task also writes
phase-specific diagnostics under its run directory.

## Useful reduced run

To verify one asset before committing resources to all 15:

```bash
./run.sh \
  --credentials .credentials.yaml \
  --config pipelines/videoediting_pipeline/config.yaml \
  -- \
  --count 1 \
  --concurrency 1
```

This is a real run and can deploy/open a PR if it reaches the final steps; the
smoke test is the non-task-generating setup check.
