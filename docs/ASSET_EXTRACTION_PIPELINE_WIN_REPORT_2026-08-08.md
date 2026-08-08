# Asset Recovery and Editorial Reconstruction Pipeline

## Pipeline Technique Reading Group win report

**Date:** 2026-08-08
**Pipeline area:** montage-to-assets recovery and video editing
**Reference task:** `004-cb5ccd`
**Source bundle:** [Google Drive source folder](https://drive.google.com/drive/folders/16P0XRPDyYqxtA50VHGfbQ79s_awCAuuD?usp=share_link)
**Related repository:** [Discord-Argue-Bot](https://github.com/Tripl3A16/Discord-Argue-Bot)

## 1. Executive summary

The original task asked an agent to separate usable assets from a montage. The
first interpretation treated the montage as if it were the expected asset
output, which made it easy to confuse defects in the montage packaging with
defects in the recovered assets. The corrected interpretation is:

- The individual files supplied in the original bundle are the hidden golden
  source.
- The solver sees only `montage-output.mp4`.
- The solver must recover an editor-ready asset package.
- The solver must also produce a meaningful playable `final_video.mp4`, not
  just a directory of extracted files.

The resulting pipeline has a deterministic package gate followed by a
golden-aware semantic judge. This separates objective failures such as missing
files or wrong media types from subjective or causal questions such as whether
the solver cut a speaker off mid-sentence.

For the reference bundle, the hidden golden contains 14 logical assets: four
static PNG images, nine moving video clips, and one complete audio-only file.
The hidden editorial reference is assembled from those original golden assets.
The fixture passes 73/73 checks, including 59 deterministic gate checks.

This is a meaningful improvement, but it is not yet a production-wired
replacement for the generic final-video runner. A six-sample end-to-end run is
still required before claiming generalization.

## 2. Initial state and problem

The solver-facing montage was intended to be a bundle of usable media that an
editor could separate into individual assets. In practice, the observed
output had several failure modes:

- Too many still images were created, including frames taken from the middle
  of dialogue.
- Moving clips were sometimes represented as movies made from static frames.
- The woman speaking was split into too many clips.
- Some speaking clips appeared to end in the middle of a sentence.
- The audio was treated as one assembled song incorrectly, including effects
  at the end.
- The montage itself contained a long black tail after the visible video.

The central diagnosis was initially easy to get wrong: the solver output is
the extracted asset package, while the original supplied individual files are
the golden reference. The montage is the input to be interpreted, not the
golden output.

## 3. Ground truth discovered for `004-cb5ccd`

### Original supplied bundle

| Category | Count | Golden treatment |
|---|---:|---|
| Static visual source items | 4 | Individual `.png` files |
| Moving video source items | 9 | Individual video files |
| Audio-only source | 1 | Complete audio file |
| Total logical assets | **14** | Manifest entry per asset |

The audio-only source has a duration of approximately **152.849 seconds**.

### Solver-facing montage

The montage is 1280×720 and approximately **339.134 seconds** long. Its
visible video ends at approximately **186.238 seconds**. From there it remains
black for approximately **152.833 seconds**, or **45.1%** of the montage
duration, while the container continues to carry audio.

That black tail is a packaging defect in the solver input. It is not an asset
that the solver should extract, and it must not be treated as proof that the
original audio source is wrong.

## 4. Key design correction

The task was changed from “extract files and hope the file list is useful” to
an editor-facing reconstruction task:

```text
original supplied bundle
          |
          v
hidden golden assets + hidden golden reconstruction
          |
          v
montage only --> solver --> manifest + assets + final_video.mp4
                                      |
                                      v
                             deterministic gate
                                      |
                                      v
                         semantic judge against golden
```

The final video makes the solver output meaningful in the same way that the
previous video-editing tasks were meaningful: a reviewer can play it, inspect
its editorial result, and then open the recovered assets to revise it.

The package remains important because a final render alone does not prove that
the solver recovered reusable source assets.

## 5. New output contract

The solver must write:

```text
/app/output/
  manifest.json
  assets/
    01_social_media_intro.png
    ...
  final_video.mp4
```

The requested reconstruction must:

1. Preserve each moving take as an individual video.
2. Represent the four static visual assets as individual PNG files.
3. Preserve the complete audio-only source as an independent audio asset.
4. Assemble a clean playable video in montage order using the recovered visual
   assets.
5. Avoid emitting the montage itself as an output asset.
6. Avoid reproducing the montage's long black/audio-only packaging tail.

The audio policy is deliberately source-grounded. Effects at the end are not
removed merely because they sound unexpected. If they are part of the original
golden audio file, they are part of the asset and should be preserved. The
judge compares the submitted audio against that source.

## 6. Implementation

The specialized implementation lives in the pipeline checkout under
`pipelines/pipev2/asset_extraction/`.

### Golden preparation

`prepare_golden.py` reads the original supplied bundle and creates:

- canonical asset names;
- static PNG conversions;
- copied video and audio assets;
- media durations and SHA-256 advisory oracle values;
- a hidden `manifest.json`.

Static IDs can be explicitly forced because a very short clip should not be
classified as a still based only on a motion heuristic.

### Meaningful reconstruction

`assemble_reconstruction.py` builds the hidden reference `final_video.mp4`
from the golden asset package itself. It normalizes visual segments, holds
static PNGs for their source durations, preserves audio from moving clips, and
concatenates the recovered visual sequence without the montage's black tail.

### Orchestration

`pipeline.py build` creates a task root with:

- only the montage under the solver-visible input;
- the hidden golden manifest and assets;
- the hidden golden final video;
- a task contract describing the output artifacts.

`pipeline.py verify` invokes the deterministic verifier against a solver
submission.

### Deterministic gate

`verify.py` checks:

- output directory presence;
- exact expected logical asset set;
- missing and unexpected files;
- PNG extension and actual PNG type;
- expected video/audio stream type;
- ffmpeg decodability;
- per-asset duration within tolerance;
- final video presence, video stream, decodability, and reference duration.

Exact source bytes are recorded as advisory oracle signals, not hard gate
requirements. A valid solver may re-encode a video or render a PNG with
different bytes. This allows a semantically valid result to reach the judge.

### Semantic judge

The semantic rubric runs only after the deterministic gate. It evaluates:

- whether static assets were incorrectly emitted as movies;
- whether moving clips remain moving videos;
- whether takes remain separate;
- whether endpoints differ from the golden source in a way that causes a
  mid-speech cut;
- whether the complete audio asset was preserved;
- whether `final_video.mp4` is a coherent reconstruction using recovered
  assets;
- whether the final video avoids the black packaging tail.

The causal condition is important: a speaker's mouth being open at the golden
endpoint is not itself a defect. A mid-sentence failure is only a failure when
the submitted endpoint differs from the golden endpoint.

## 7. Validation results

### Deterministic fixture validation

| Test | Result |
|---|---|
| Golden package and final video | **73/73 checks passed** |
| Deterministic gate subset | **59/59 passed** |
| Golden logical assets | 4 images + 9 videos + 1 audio = 14 |
| Hidden reconstructed video | Approximately 186.288 seconds |
| Renamed PNG and missing final video | Correctly rejected |
| Valid altered PNG with different bytes | Gate passed; advisory oracle mismatch surfaced |

The altered-PNG test is important. It proves that the system does not confuse
“different encoding bytes” with “invalid deliverable,” while the renamed-file
test proves that type and output-contract failures are still blocked.

### Judge calibration observations

Repeated baseline judge votes found the following patterns:

| Judge question | Baseline result |
|---|---:|
| Static source represented as a movie | 6/6 detected |
| Audio tail pattern visible in the montage | 6/6 detected |
| Golden endpoint visually has an open mouth | 6/6 detected |
| Incorrectly attributed a mid-sentence cut to extraction | 6/6 false attribution |
| JPG-versus-PNG distinction | 4/6 detected |
| Woman-clip fragmentation | 4/6 detected |

The baseline results showed that the judge could notice visual patterns but
could not reliably determine causality from a single montage view.

After introducing the explicit golden-endpoint and source-tail conditions, the
revised rubric behaved correctly across three calibration votes:

- static-as-movie failure: 3/3 true;
- PNG modality failure: 3/3 true;
- audio-tail presence: 3/3 true;
- audio-tail “wrongness” asserted without a golden comparison: 3/3 false;
- extraction-caused mid-sentence cut when endpoints matched golden: 3/3 false;
- unsupported claim that a golden comparison was impossible: 3/3 false.

The three-vote calibration is evidence that the rubric design improved the
judge, but it is not a Rule-of-6 generalization result yet.

## 8. Pipeline Technique Reading Group and Rule of 6 analysis

The Reading Group's central requirement is a quantifiable win. This work
provides one at the task-contract and verification layers:

### Win 1: ambiguity removed from the gold/output relationship

Before the change, the montage, the extracted assets, and the final video were
easy to conflate. After the change, the hidden source, solver input, expected
package, and meaningful final deliverable are separate named artifacts.

### Win 2: semantic judging is causally constrained

The judge no longer treats every visible oddity as an extraction failure. It
must compare submitted endpoints and audio against the hidden golden source,
and it must ignore the known black tail in the solver input.

### Win 3: a solver can produce a meaningful artifact

The solver now has to produce a playable `final_video.mp4`, not merely satisfy
a file inventory. The package is still evaluated because it is what makes the
result useful to an editor.

### Rule-of-6 status

The process followed the Rule of 6 for the first calibration pass by repeating
the baseline judge questions six times. It also scanned five other local
montages and found no equivalent trailing black run in those controls.

However, the complete end-to-end behavior has **not** yet been tested across
six independent golden extraction tasks. The next validation run should use at
least six distinct montage/source-bundle pairs and assess:

1. builder ability to construct a correct hidden package;
2. solver ability to recover assets;
3. solver ability to create a meaningful reconstruction video;
4. gate rejection of malformed packages;
5. judge discrimination between valid and defective reconstructions;
6. variance across different montage layouts and media types.

No SVM was trained in this iteration. The current approach uses deterministic
media predicates plus a frozen semantic rubric, which is the safer first
version because it makes the failure modes directly inspectable. RG4-style
holdout rubric freezing can be added after the six-task calibration set exists.

## 9. Reproduction guide

From the pipeline checkout, build a task from the original source bundle:

```bash
python3 pipelines/pipev2/asset_extraction/pipeline.py build \
  --source-root /path/to/original-bundle \
  --task-root /tmp/004-cb5ccd-task \
  --task-id 004-cb5ccd \
  --static-id 01_social_media_intro \
  --static-id 08_afrizone_outro_card \
  --static-id 09_confused_reaction_meme \
  --static-id 12_dog_reaction
```

After the solver writes the three required output artifacts:

```bash
python3 pipelines/pipev2/asset_extraction/pipeline.py verify \
  --task-root /tmp/004-cb5ccd-task \
  --submission /app/output/manifest.json
```

The semantic judge should be invoked only when the deterministic report has
passed. Its input should include the hidden golden manifest, sampled golden
assets, sampled submitted assets, both final videos, and the causal rubric.

## 10. Quantified before/after summary

| Dimension | Before | After |
|---|---|---|
| Solver output | Ambiguous extraction result | 14-asset package plus playable reconstruction |
| Golden relationship | Easily confused with montage | Original supplied bundle is hidden golden |
| Static modality | Judge-only or implicit | Deterministic PNG type gate |
| Missing/extra assets | Not contractually blocked | Deterministically rejected |
| Audio interpretation | Could be judged from tail appearance | Compared against complete hidden audio source |
| Black tail | Could be mistaken for an asset defect | Classified as input packaging; excluded from output |
| Meaningful artifact | Not guaranteed | Required `final_video.mp4` |
| Fixture validation | No specialized contract | 73/73 checks passed |
| Exact bytes | Could incorrectly block re-encoded media | Advisory signal only |

The most concrete measured improvement is contract coverage: the fixture now
checks the complete editorial output through **59 deterministic gate checks**,
while retaining **14 advisory exact-byte comparisons** for diagnostic use.

## 11. Remaining risks and next steps

1. Run the complete pipeline across six independent source bundles before
   claiming generalization.
2. Add a formal timeline or OTIO-style project file if editor handoff needs
   non-linear editing interoperability beyond the manifest.
3. Add a deterministic check that the final video is not entirely black and
   does not contain a long trailing black run; semantic review should remain
   responsible for proving asset identity and causal endpoint quality.
4. Wire this specialized directory into the production task launcher. It is
   currently deliberately separate from the generic runner because the generic
   runner assumes one `final_video.mp4`, while this task has a package plus a
   final video.
5. Freeze the semantic rubric on training examples and evaluate a held-out
   sixth sample in an RG4-style run.

## Conclusion

The pipeline now has the right abstraction boundary: the original asset bundle
is the hidden truth, the montage is the imperfect solver input, the recovered
package is the editor-facing library, and `final_video.mp4` is the meaningful
solver result. Deterministic checks protect the artifact contract, while the
golden-aware semantic judge handles the genuinely visual questions without
mistaking packaging defects for solver failures.
