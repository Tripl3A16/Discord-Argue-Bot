# Asset-recovery pipeline preparation findings

Date: 2026-08-08

Status: five task packages saved locally; none deployed; no PR opened.
Publication disposition: publish the task ideas and findings directly to the
report repository; do not create a PR from this run.

## Scope

Five available Librarian bulk assets were loaned, materialized, converted into
hidden golden packages, and returned after validation:

| Task | Editorial brief | Golden assets | Video / image / audio | Gate |
| --- | --- | ---: | --- | --- |
| `asset-recovery-507` | Temple / tricolor / flight portrait opener | 46 | 26 / 16 / 4 | 175/175 |
| `asset-recovery-512` | Beauty creator UGC portrait demo | 36 | 26 / 2 / 8 | 149/149 |
| `asset-recovery-517` | Creator social-promo portrait reel | 18 | 9 / 9 / 0 | 70/70 |
| `asset-recovery-527` | Network-led landscape business explainer | 29 | 7 / 3 / 19 | 120/120 |
| `asset-recovery-532` | Sai Silks / market-cap landscape explainer | 46 | 4 / 40 / 2 | 151/151 |

The existing `004-cb5ccd` fixture was also gated as the sixth R6 packaging
sample: 14 assets and 59/59 gate checks. All six hidden golden packages passed.
This is an R6 construction and gate result, not a solver-model success rate:
the solver and semantic judge have not been run on these five saved tasks.

## What the new pipeline does

```text
Librarian bulk bundle
        |
        +--> source manifest + media --> hidden typed golden package
        |
        +--> montage-output.mp4 ------> solver-visible input only
                                           |
                         manifest + assets + final_video.mp4
                                           |
                               deterministic package gate
                                           |
                              semantic judge against hidden gold
```

The task asks the solver to recover one file per usable source asset, retain
stills as PNGs, keep video and audio separate, and produce a human-viewable
editorial reconstruction. The hidden golden retains source provenance, media
kind, duration, and SHA-256. Exact bytes are advisory; type, decodability,
duration, missing/extra paths, and final-video playability are gates.

## Findings and fixes

1. The first Librarian attempt failed because the older resolver expected an
   immediate `*-sub` directory. The current bulk assets are flat. The new
   adapter reads `bundle-manifest.json` and materializes `media/` directly.
2. Asset 507 contained 97 nominal media objects, but 51 were generated
   Premiere preview or prior `FINAL_OUTPUT` material. Those were not fair
   solver targets, so the repaired golden keeps 46 recoverable source assets
   and records all 51 exclusions in the audit manifest.
3. Temporary source downloads are processed one at a time and removed after
   the hidden golden is built. S3 downloads retry with bounded backoff and
   validate object size.
4. The previous reference videos for 512, 517, and 532 contained trailing
   black padding. Only that padding was normalized in the hidden reference;
   the source asset package was not altered. The final reference durations are
   28.57s, 56.30s, and 104.60s respectively.
5. The montage remains input-only. The black tail is not copied into the
   solver's final-video target. For 004, the known montage defect is about
   152.8s of black after roughly 186.2s of visible content; it is packaging
   noise, not a golden asset.
6. All five Librarian loans were returned and independently recorded as
   `available`. No task deployment or PR mutation occurred.

## Difference from the previous final-video pipeline

The previous pipeline primarily judged one creative `final_video.mp4` against
an output-video reference. It was simpler and cheaper, but it could not tell
whether the solver had recovered the underlying editor assets, whether a still
had been made into a movie, whether audio had been merged incorrectly, or
whether a clip boundary cut speech.

The new pipeline adds an explicit, auditable asset contract before semantic
judging. It catches missing/extra assets and modality errors cheaply, preserves
audio as independent reusable files, retains source provenance, and gives the
judge evidence for asset-level comparisons as well as a meaningful final
video. It is therefore better for this extraction problem and safer against
the exact failures observed in the montage review.

The tradeoff is real: hidden storage and deterministic validation are larger,
and semantic solver quality is still unmeasured. The old pipeline remains
better for a pure short-form creative-edit benchmark where only the final
video matters.

## Recommended asymmetry improvements

- Keep the solver view limited to the montage; keep raw media, source
  manifest, prior output, and normalized golden reference hidden.
- Let the builder derive exact asset inventory, media type, durations, and
  provenance from the source manifest. Do not reveal those counts or paths to
  the solver unless the task explicitly requires them.
- Gate manifest shape and playable media before spending semantic-judge
  budget. The judge should then compare the final video and asset-level
  evidence against the hidden package.
- Add semantic checks for “static image emitted as a movie”, “sound effects
  merged into the song”, “speaker cut mid-utterance”, “black filler tail”, and
  “unsupported captions”. These are judge criteria, not byte checks.
- Use the normalized hidden reference only as an editorial oracle; require
  the solver's final video to be independently playable, source-grounded,
  complete in audio, and free of padding.
- For the next six-run solver evaluation, use the aggregate mean judge score
  across the six tasks, with the existing solver criterion of average <= 0.65;
  do not accept/reject on an individual task score.

## Approval gate

The recommended first PR candidate is `asset-recovery-512`: it is a moderate
28.6-second portrait task with 36 assets, including eight independent audio
files, so reviewers can inspect the new manifest/audio asymmetry without the
17-minute montage size of 527. It is saved at
`prepared-runs/asset-recovery-20260808/tasks/asset-recovery-512/` and remains
marked `preparation_only: true` and `deployment_status: not_deployed`.

I have not opened the PR. Approval is required before adapting and PR-ing this
one task to `Parsewave-internal/mm-sapphire`.
