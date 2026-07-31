# Librarian video pipeline runbook

This document describes the validated video-editing pipeline on the current runner. It prepares a second random batch of 15 assets but does not start it.

## Runner

- Hostname: `aditi0522-pipe-server-runner`
- Public IPv4 / primary host address: `65.109.8.102`
- Public IPv6 assigned to the host: `2a01:4f9:c014:b8f::1`
- Pipeline checkout: `/home/ubuntu/mm-sapphire-pipelines`
- Pipeline checkout commit at preparation time: `c7cb65d48dcd`
- Harness checkout: `/home/ubuntu/pw-harness`
- Pipeline config: `pipelines/videoediting_pipeline/config-librarian.yaml`
- Librarian collection: `video-edit-assets-final`
- Librarian endpoint: `https://alexandria.parsewave.ai`

The many `172.16.*.1` addresses on the runner are transient container bridges and should not be used as server addresses.

## Prepared batch 02

Availability was checked at `2026-07-31T20:50:12Z`. The sample was drawn from 36 available assets that had both a local solver montage and hidden golden, excluding the previous 15-asset batch.

- Count: `15`
- Batch concurrency: `3`
- Per-pipeline count: `1`
- Per-pipeline concurrency: `1`
- Concurrent trials per task: `1`
- Random seed: `24fba2f2474237627b7f1a408a665dfb9782b7a5e8ffd736448ab23357601f7b`
- Assets, in launch order: `244 248 176 239 205 25 234 162 243 57 250 165 4 171 84`
- Prepared seed file: `docs/video-pipeline-batch-02.yaml`

Librarian status is authoritative at launch time. If any exact asset is no longer available, do not substitute it silently; reselect the batch and update the seed file and launch list together.

## Credentials

Store credentials only on the runner at `/home/ubuntu/mm-sapphire-pipelines/.credentials.yaml`. Never commit the file or paste its values into tickets, logs, or this repository.

The runner's current credential schema contains these keys:

```yaml
AWS_ACCESS_KEY_ID: "..."
AWS_SECRET_ACCESS_KEY: "..."
AWS_REGION: "..."
GH_TOKEN: "..."
LIBRARIAN_API_KEY: "..."
PROXY_TOKEN: "..."
HETZNER_API_KEY: "..."
llm_judge_api_key: "..."
llm_judge_api_url: "..."
llm_judge_base_url: "..."
llm_judge_model: "..."
openrouter_api_key: "..."
```

The essential values for this pipeline are the Librarian key, AWS credentials and region, GitHub token, and configured judge credentials. Use a secret manager or a mode-`0600` file.

```bash
chmod 600 /home/ubuntu/mm-sapphire-pipelines/.credentials.yaml
```

## Install batch 02 on the runner

The checked-in pipeline config currently names `ideas18.yaml`. Preserve that file and create a batch-specific config so parallel or later work cannot overwrite it.

```bash
export PIPELINE_ROOT=/home/ubuntu/mm-sapphire-pipelines
export RUNBOOK_REPO=/home/ubuntu/Discord-Argue-Bot

cp "$RUNBOOK_REPO/docs/video-pipeline-batch-02.yaml" \
  "$PIPELINE_ROOT/pipelines/videoediting_pipeline/ideas18-batch-02.yaml"

cp "$PIPELINE_ROOT/pipelines/videoediting_pipeline/config-librarian.yaml" \
  "$PIPELINE_ROOT/pipelines/videoediting_pipeline/config-librarian-batch-02.yaml"

sed -i 's/idea_file: ideas18.yaml/idea_file: ideas18-batch-02.yaml/' \
  "$PIPELINE_ROOT/pipelines/videoediting_pipeline/config-librarian-batch-02.yaml"
```

Confirm that the substitution changed exactly one line:

```bash
rg -n 'idea_file:' \
  "$PIPELINE_ROOT/pipelines/videoediting_pipeline/config-librarian-batch-02.yaml"
```

## Environment variables

Set these non-secret values for the batch launcher:

```bash
export LIBRARIAN_CREDENTIALS=/home/ubuntu/mm-sapphire-pipelines/.credentials.yaml
export LIBRARIAN_CONFIG=/home/ubuntu/mm-sapphire-pipelines/pipelines/videoediting_pipeline/config-librarian-batch-02.yaml
export LIBRARIAN_LOGS_ROOT=/home/ubuntu/mm-sapphire-pipelines/logs/librarian-ideas18-random15-batch02
export LIBRARIAN_BATCH_CONCURRENCY=3
export LLM_JUDGE_REPETITIONS=3
export LLM_JUDGE_CONCURRENCY=3
export LLM_JUDGE_TEMPERATURE=0
```

Each exact-asset child sets its own value:

```bash
LIBRARIAN_ASSET_PREFIX="s3://mm-sapphire/clean-uploads/asset-${asset_number}/"
```

Do not export secret values globally unless necessary. `run.sh --credentials` reads them from the protected YAML file.

## Preflight without launching

From the pipeline checkout, validate files, credentials, tools, GitHub authentication, and free space:

```bash
cd /home/ubuntu/mm-sapphire-pipelines

test -r "$LIBRARIAN_CREDENTIALS"
test -r "$LIBRARIAN_CONFIG"
command -v uv
command -v docker
command -v gh
gh auth status
docker info >/dev/null
df -h /home/ubuntu
```

Use Librarian's read-only `/list` response to reconfirm all 15 assets are still `available`. Do not call `/loan` merely as a preflight check because it changes state.

## Launch

Run each exact asset as one pipeline and allow three child pipelines at a time:

```bash
cd /home/ubuntu/mm-sapphire-pipelines

assets=(244 248 176 239 205 25 234 162 243 57 250 165 4 171 84)
export pipeline_root="$PWD"
export credentials_path="$LIBRARIAN_CREDENTIALS"
export config_path="$LIBRARIAN_CONFIG"
export logs_root="$LIBRARIAN_LOGS_ROOT"
mkdir -p "$logs_root"

printf '%s\n' "${assets[@]}" | xargs -P "$LIBRARIAN_BATCH_CONCURRENCY" -n 1 bash -c '
  set -euo pipefail
  asset_number="$1"
  asset_logs="${logs_root}/asset-${asset_number}"
  mkdir -p "$asset_logs"

  env \
    -u LLM_JUDGE_BASE_URL -u LLM_JUDGE_API_URL -u LLM_JUDGE_MODEL \
    -u ATHENA_JUDGE_BASE_URL -u ATHENA_JUDGE_MODEL -u ATHENA_JUDGE_API_KEY \
    -u LLM_JUDGE_REASONING_EFFORT \
    -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy \
    -u ALL_PROXY -u all_proxy \
    GIT_CONFIG_COUNT=1 \
    GIT_CONFIG_KEY_0=credential.helper \
    GIT_CONFIG_VALUE_0="!gh auth git-credential" \
    LIBRARIAN_ASSET_PREFIX="s3://mm-sapphire/clean-uploads/asset-${asset_number}/" \
    "${pipeline_root}/run.sh" \
      --credentials "${credentials_path}" \
      --config "${config_path}" \
      -- --count 1 --concurrency 1 --conc-trials 1 --logs-dir "${asset_logs}" \
    2>&1 | tee "${asset_logs}/launcher.log"
' _
```

For unattended operation, place that command in a reviewed launcher script and start it in a named `tmux` session. Do not start a second copy with the same log root.

## Monitor and reconcile

```bash
ps -eo pid,ppid,etime,stat,args | rg 'yggdrasil\.cli run'
tail -f "$LIBRARIAN_LOGS_ROOT"/asset-*/launcher.log
rg -H 'engine_done|task_failed' "$LIBRARIAN_LOGS_ROOT"/asset-*/launcher.log
```

Loan lifecycle rules:

- A failed or cancelled pre-PR run returns its loan.
- A run with an open PR retains the loan in `awaiting_review`.
- A merged PR steals/finalizes the asset.
- A closed or rejected PR returns the asset.
- If a return or steal result is ambiguous, query `/status`; never repeat the mutation blindly.
- Durable state is under `pipelines/videoediting_pipeline/.librarian-state/`.

The pipeline's generated task PRs target `Parsewave-internal/mm-sapphire` on `main`. This documentation repository does not receive generated tasks or secrets.
