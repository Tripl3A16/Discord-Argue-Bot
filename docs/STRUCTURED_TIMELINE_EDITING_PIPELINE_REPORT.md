# Structured Timeline Editing Pipeline

## Design report for a distinct montage-asset training pipeline

**Status:** Proposed  
**Proposed pipeline names:** `timeline-editing`, `roughcut-edl`  
**Target task group:** video-editing or a dedicated timeline-editing group  
**Primary output:** editable timeline JSON plus a trusted rendered preview

## Executive summary

The existing PipeV2 video-editing pipeline already covers end-to-end creative
editing. A solver receives one `montage-output.mp4` containing supplied images,
audio, and video, then creates a complete publish-ready MP4. Its responsibilities
already include source selection, narrative structure, pacing, typography,
transitions, audio integration, aspect-ratio delivery, and a resolved ending.

Consequently, proposed categories such as trailers, promotional spots, social
ads, music-led highlights, product reels, and documentary teasers are not new
pipelines. They are genres within the current pipeline.

The recommended genuinely distinct task family is **structured timeline
editing**. Instead of asking the solver to directly produce an arbitrary final
MP4, it asks the solver to produce an editable timeline that references bounded
regions of the supplied montage. A fixed, trusted renderer converts that
timeline into a preview video. The timeline exposes every editorial decision:
shot selection, source in/out points, order, duration, crop, speed, transition,
audio placement, gain, fades, and title timing.

Existing edited golden videos remain useful. An offline alignment process maps
the hidden golden back to regions of the montage and creates a hidden golden
timeline. Tasks are admitted only when that reconstruction is sufficiently
confident and the trusted renderer can reproduce a valid oracle result.

This pipeline trains a different capability from PipeV2: explicit nonlinear
editor timeline construction rather than unconstrained render implementation.
It is also faster and cheaper to validate because most scoring can be
deterministic. The target is no more than 8-12 semantic judge calls per complete
task evaluation, while preserving the existing acceptance contract: oracle
score at least 0.85, NOP exactly zero, three valid solver outputs, and final
solver average at or below 0.65.

## 1. Current PipeV2 baseline

### 1.1 Input and hidden reference

PipeV2 stages exactly two media representations:

- Solver-visible `environment/resources/source_pack/montage-output.mp4`
- Hidden edited golden `solution/final_video.mp4`, mirrored as
  `tests/reference.mp4`

The montage is the only source file presented to the solver. It serializes the
available images, sounds, and videos into one video container.

### 1.2 Existing solver goal

The current builder creates an instruction that asks the solver to produce
`/app/output/final_video.mp4`. The instruction defines:

- Subject and editorial goal
- Duration range
- Resolution and aspect ratio
- Audio requirements
- No-external-media requirement

The solver is free to implement the entire edit. Accepted tasks demonstrate
that PipeV2 already evaluates:

- Visual source selection and product or subject communication
- Narrative progression and structure
- Shot pacing and continuity
- Transitions and repetition
- Typography and title treatment
- Music, dialogue, ambience, and effects
- Audio-video integration
- Opening hook and resolved ending

### 1.3 Acceptance contract

The current production contract includes:

- Frozen, versioned verifier runtime
- Oracle score `>= 0.85`
- NOP score exactly `0.0` with zero judge requests
- Three valid saved solver artifacts
- Untouched holdout until rubric freeze
- Final saved-solver average `<= 0.65`
- Valid, byte-identical rubric copies
- Final trace packaging and deployment only after acceptance

The structured timeline pipeline should retain these operational properties,
but use a fixed timeline rubric and deterministic metrics instead of generating
a new semantic rubric for every task.

## 2. Evidence from representative assets

Representative inspected assets have the following shapes:

| Asset | Montage | Golden | Format |
|---|---:|---:|---|
| `asset-576` | 40 s | 27 s | 1080x1920 portrait |
| `asset-591` | 201 s | 33 s | 1920x1080 landscape |
| `asset-447` | 401 s | 77 s | 1920x1080 landscape |
| `asset-462` | 487 s | 48 s | 1080x1920 portrait |
| `asset-482` | 1089 s | 56 s | 1920x1080 landscape |
| `asset-487` | 73 s | 59 s | 1080x1920 portrait |

All six inspected montages contain stereo audio. Their goldens are materially
shorter than the longer montage containers, demonstrating that shot selection,
ordering, and trimming decisions can potentially be recovered as structured
timeline supervision.

The large montage-to-golden duration ratios are particularly useful for an
editorial-decision task: the model cannot succeed by copying the complete
montage and must select appropriate source ranges.

## 3. Alternatives considered

### 3.1 Rejected as overlapping with PipeV2

The following ideas change the genre but not the capability:

- Promotional spot
- Product advertisement
- Trailer or teaser
- Music-driven highlight
- Social-media cut
- Documentary teaser
- Sound-led brand film
- Motion photo story rendered directly as an MP4

They all still ask the model to select assets and produce a polished flattened
video. PipeV2 already does this.

### 3.2 Distinct but unsuitable as the primary pipeline

**Thumbnail or key-art generation** is distinct, but the current asset inflow
does not reliably include human-authored thumbnail goldens.

**Audio-only mastering** is distinct and inexpensive, but not every montage
contains suitable isolated audio or a standalone golden mix.

**Asset cataloging** is useful and deterministic, but primarily trains media
organization rather than editing.

**Multi-format adaptation** produces useful deliverables, but remains
end-to-end video editing and substantially overlaps PipeV2.

### 3.3 Recommended direction

Structured timeline generation changes the solver artifact, model behavior,
verification method, and training signal while continuing to use the existing
montage and edited golden assets.

## 4. Proposed task contract

### 4.1 Solver-visible files

```text
/app/data/source_pack/montage-output.mp4
/app/data/source_pack/asset-index.json
```

The asset index is generated deterministically from the montage and contains no
hidden golden information. It makes montage regions addressable without
exposing the original un-concatenated files.

Example:

```json
{
  "version": "timeline-assets/1.0",
  "montage": "montage-output.mp4",
  "segments": [
    {
      "id": "visual-001",
      "source_in": 0.0,
      "source_out": 4.82,
      "kind": "video",
      "has_audio": true,
      "width": 1920,
      "height": 1080
    },
    {
      "id": "still-002",
      "source_in": 4.82,
      "source_out": 9.10,
      "kind": "image",
      "has_audio": false,
      "width": 1920,
      "height": 1080
    },
    {
      "id": "audio-001",
      "source_in": 92.40,
      "source_out": 124.80,
      "kind": "audio",
      "has_audio": true
    }
  ]
}
```

### 4.2 Required solver output

```text
/app/output/timeline.json
```

The solver may also produce a local preview for debugging, but only the trusted
renderer's preview is scored.

Example timeline:

```json
{
  "version": "timeline-edit/1.0",
  "format": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration_seconds": 28.0
  },
  "video_tracks": [
    {
      "clips": [
        {
          "asset_id": "visual-001",
          "source_in": 0.40,
          "source_out": 2.80,
          "timeline_in": 0.0,
          "speed": 1.0,
          "crop": {"mode": "center-fill"},
          "transition_out": {"type": "cut", "duration": 0.0}
        }
      ]
    }
  ],
  "audio_tracks": [
    {
      "clips": [
        {
          "asset_id": "audio-001",
          "source_in": 4.0,
          "source_out": 26.0,
          "timeline_in": 0.0,
          "gain_db": -8.0,
          "fade_in": 0.5,
          "fade_out": 1.0
        }
      ]
    }
  ],
  "titles": [
    {
      "text": "Approved task-specific title",
      "start": 0.5,
      "end": 2.5,
      "position": "lower-third"
    }
  ]
}
```

### 4.3 Version-one feature set

The first renderer should deliberately support a constrained edit language:

- Hard cuts
- Crossfades
- Source in/out points
- Timeline placement
- One or more video and audio tracks
- Playback speed within a safe range
- Center-fill, fit, and bounded custom crops
- Audio gain and linear fades
- Simple titles using bundled fonts and fixed style tokens

Arbitrary shell commands, arbitrary shaders, downloaded assets, generated
media, plugins, and executable project files are out of scope.

## 5. Montage indexing

The indexing stage should run before task construction and should be fully
deterministic.

### 5.1 Visual boundary detection

Use a combination of:

- Hard-cut detection
- Sustained black-frame or slate detection
- Perceptual-hash discontinuity
- Motion discontinuity
- Resolution or aspect-ratio changes inside the montage
- Detection of effectively static image regions

### 5.2 Audio boundary detection

Use:

- Silence boundaries
- Audio fingerprint changes
- Codec or channel-layout changes
- Sustained music-versus-speech classification
- Alignment with visual segment boundaries

### 5.3 Index validation

Every indexed segment must:

- Stay inside montage duration
- Decode independently over its declared bounds
- Have a stable unique identifier
- Include source timing with millisecond precision
- Record whether visual and audio streams are usable
- Avoid hidden-golden-derived annotations

## 6. Hidden golden timeline extraction

The existing golden MP4 should be converted into a hidden timeline before the
task is admitted.

### 6.1 Alignment process

1. Sample golden and montage frames.
2. Generate robust visual fingerprints or embeddings.
3. Generate acoustic fingerprints for both audio streams.
4. Produce candidate montage matches for each golden interval.
5. Use dynamic programming or Viterbi alignment to recover a coherent source
   path through the montage.
6. Detect repeated source use, crop changes, speed changes, and transitions.
7. Convert the recovered path into `golden-timeline.json`.
8. Render it with the same fixed renderer used for solver timelines.
9. Compare the trusted render against the original golden.

### 6.2 Admission requirements

Initial suggested requirements:

- At least 90% of golden duration aligned to montage content
- At least 85% high-confidence visual coverage
- At least 90% audio coverage when audio is required
- No source references outside indexed bounds
- No unsupported effect covering a material portion of the golden
- Trusted-render oracle score at least 0.85 on two fresh runs
- Full decode and valid output format

These are starting points. Phase-zero measurements should set the final values.

### 6.3 Handling unsupported golden effects

The extractor must not pretend to recover effects it cannot represent. It
should either:

- Express the effect using a supported timeline primitive;
- Mark a small unmatched interval as an allowed overlay region; or
- Reject the asset pack for this pipeline.

Filtering is preferable to creating misleading supervision.

## 7. Trusted renderer

The renderer is part of the immutable verifier/runtime boundary.

Requirements:

- Reads only validated timeline JSON and the staged montage
- Resolves all asset IDs through `asset-index.json`
- Rejects direct filesystem paths in the solver timeline
- Rejects unknown fields and unsupported transitions
- Uses fixed FFmpeg filters and bundled fonts
- Produces deterministic output for the same inputs
- Records renderer version and hashes
- Emits a render manifest containing resolved source ranges
- Enforces CPU, memory, duration, and file-size limits

The renderer should never execute solver-provided commands.

## 8. Scoring design

The score should be primarily deterministic.

### 8.1 Timeline validity: 20%

- Exact schema version
- Valid asset identifiers
- Source bounds contained within indexed segments
- Valid track ordering
- No illegal overlaps on exclusive tracks
- Valid duration, speeds, gains, crops, fades, and transitions
- No external media references

### 8.2 Editorial construction: 30%

- Required subject or concept assets selected
- Required narrative beats represented
- Meaningful source diversity
- No accidental duplicate ranges
- Shot durations within profile-specific bounds
- No cuts inside protected speech spans
- Required title or identity included
- Audio bed and dialogue placed coherently

### 8.3 Hidden golden agreement: 25%

This must use tolerances rather than exact timeline equality:

- Important source-region recall
- Relative shot ordering
- Required-content preservation
- Approximate pacing
- Audio-bed selection
- Broad crop and framing agreement
- Timing tolerance, initially approximately +/-1.5 seconds

Alternative valid edits should remain possible. Task metadata should distinguish
mandatory golden-derived beats from optional editorial choices.

### 8.4 Render health and craft: 15%

- Full decode
- Correct resolution, aspect ratio, and FPS
- No black or flash frames introduced by the timeline
- No frozen or truncated tail
- Safe integrated loudness and true peak
- No clipped title safe areas
- No malformed transition frames
- Audible audio when required

### 8.5 Fixed semantic review: 10%

Use only two stable questions:

1. Does the rendered timeline communicate the requested progression
   coherently?
2. Do the shot, timing, and audio choices appear deliberate rather than
   mechanically assembled?

Batch both questions into one request. Use two initial votes and issue a third
request only when the first two disagree.

## 9. Judge-call and cost budget

This pipeline should not run RG4 candidate generation, candidate regeneration,
semantic rubric selection, or per-task rubric freezing.

For one oracle and three solver videos:

- One request containing both fixed questions per vote
- Two initial votes per video
- Optional third vote only on disagreement
- Expected total: 8 requests per task
- Hard maximum: 12 requests per task

NOP should return zero before any media encoding or judge lookup.

The fixed rubric, renderer, schema, and deterministic metric versions must be
hash-pinned in task provenance.

## 10. Difficulty and acceptance

Retain the production acceptance contract:

- Oracle `>= 0.85`
- NOP exactly `0.0`
- NOP judge requests exactly zero
- Three solver timelines render and decode successfully
- Final solver average `<= 0.65`
- Hidden holdout not examined before the scoring contract is frozen
- Fixed renderer, schema, and verifier hashes unchanged
- Trace bundles contain timeline JSON, resolved render manifest, preview video,
  and verifier result
- Deployment occurs only after every required gate passes

Difficulty should come from editorial reasoning, not schema confusion. The
timeline format and renderer documentation should be visible and precise.

## 11. Generating more tasks per asset

Structured timelines allow meaningful task multiplication.

### 11.1 Full-sequence task

Reconstruct a complete editorial sequence from the montage according to the
task brief.

### 11.2 Subsequence tasks

Split a longer golden at high-confidence editorial boundaries:

- Opening construction
- Explanatory middle sequence
- Product demonstration sequence
- Dialogue continuity sequence
- B-roll placement sequence
- Closing sequence
- Audio-bed and cue-placement sequence

### 11.3 Minimum quality requirements

Each generated task should:

- Cover at least 8-15 seconds
- Use at least three meaningful source regions
- Represent a coherent editorial beat
- Have a human-readable task instruction
- Render independently from its hidden golden timeline
- Avoid being only a single trim or transcode operation
- Avoid excessive source-range overlap with another task

Start with no more than three tasks per asset pack. Increase only after a
deduplication audit.

## 12. Pipeline architecture

```text
Librarian asset package
        |
        v
montage-output.mp4 + edited golden
        |
        +--> deterministic montage indexer
        |         |
        |         v
        |    asset-index.json
        |
        +--> hidden golden aligner
                  |
                  v
          golden-timeline.json
                  |
                  v
          trusted renderer audit
                  |
                  v
             task admission
                  |
                  v
       three solver timeline trials
                  |
                  v
     deterministic + fixed semantic scoring
                  |
                  v
 oracle/NOP/difficulty/trace/deployment gates
```

## 13. Proposed repository layout

```text
pipelines/timeline-editing/
  config.yaml
  instructions.txt
  ideas.yaml
  timeline-schema.json
  asset-index-schema.json
  renderer-policy.json
  fixed-rubric.json
  index_montage.py
  align_golden.py
  render_timeline.py
  verifier.py
  example-task/
    instruction.md
    task.toml
    environment/
    solution/
    tests/
```

The production implementation should factor immutable runtime files into
versioned templates and lock their hashes, following PipeV2's existing runtime
guard pattern.

## 14. Rollout plan

### Phase 0: feasibility audit

Audit 30-50 existing montage/golden pairs and record:

- Visual alignment coverage
- Audio alignment coverage
- Recoverable cut count
- Crop and speed-change frequency
- Unsupported effect duration
- Render similarity
- Estimated number of viable subtask boundaries

**Go/no-go condition:** at least 60-70% of audited asset packs should yield a
usable hidden timeline. If this fails, do not build the production pipeline.

### Phase 1: timeline schema and renderer

- Freeze timeline schema v1
- Implement strict validation
- Implement fixed renderer
- Add renderer determinism and security tests
- Build hand-authored fixture timelines

### Phase 2: indexing and golden extraction

- Implement deterministic montage indexer
- Implement visual and acoustic alignment
- Generate hidden golden timelines
- Add confidence reports and rejection reasons
- Compare trusted renders with original goldens

### Phase 3: verifier

- Implement deterministic metric suite
- Add fixed two-question semantic review
- Enforce oracle, NOP, and solver-average gates
- Package timeline and render evidence into traces

### Phase 4: canary

Run ten asset packs with three solvers each.

Required results:

- Zero renderer crashes
- Zero schema ambiguity failures
- Oracle at least 0.85 on two fresh runs
- NOP zero with zero calls
- Solver average at or below 0.65 for admitted tasks
- No more than 12 judge requests per task
- No external-media or path-escape violations

### Phase 5: small batch

- Run 25-50 asset packs
- Enable up to three tasks per qualifying asset
- Audit task overlap and golden alignment manually
- Measure average solver time and judge cost

### Phase 6: production

- Increase task multiplication only after deduplication is reliable
- Publish versioned schema and renderer documentation
- Monitor oracle stability, solver distribution, alignment confidence, and
  judge disagreement

## 15. Risks and mitigations

### Golden cannot be reconstructed

**Risk:** The golden uses generated overlays, effects, or media not present in
the montage.

**Mitigation:** Reject low-coverage packs. Do not fabricate hidden source
mappings.

### Exact-match scoring penalizes valid edits

**Risk:** A solver produces a good alternative timeline that differs from the
golden.

**Mitigation:** Score mandatory content coverage and relative order with broad
timing tolerances. Keep golden agreement to a minority of the total score.

### Solver exploits the renderer

**Risk:** Timeline fields trigger arbitrary file reads or command execution.

**Mitigation:** Strict JSON schema, asset IDs instead of paths, fixed filter
construction, no shell interpolation, bounded numeric fields, and container
isolation.

### Task fragments become trivial

**Risk:** Multiplication produces single-cut or simple trim tasks.

**Mitigation:** Enforce minimum duration, source diversity, editorial beats,
and solver difficulty before admission.

### Hidden alignment leaks into solver input

**Risk:** Golden-derived source choices are accidentally included in the
visible asset index.

**Mitigation:** Build the asset index from the montage alone. Generate and store
golden alignment in verifier-only paths.

### Deterministic metrics dominate craft

**Risk:** Models optimize timeline statistics without making coherent edits.

**Mitigation:** Retain the two fixed semantic questions and require mandatory
content progression, while keeping the judge budget bounded.

## 16. Success metrics

The first production milestone should target:

- At least 65% of audited asset packs usable
- Median golden alignment coverage at least 90%
- Oracle stability spread below 0.05 across fresh runs
- NOP zero-call success rate of 100%
- Renderer success rate of 100% on validated timelines
- Judge usage median no greater than 8 calls per task
- Judge usage maximum no greater than 12 calls per task
- Median solver runtime below 20 minutes
- At least three nontrivial tasks per long qualifying asset
- No task pair with excessive hidden source-range overlap

## 17. Final recommendation

Build a phase-zero prototype before committing to a production pipeline. Its
only purpose should be to answer whether existing goldens can be aligned back to
the concatenated montage with enough confidence to create editable timeline
supervision.

If the audit passes, implement `timeline-editing` as:

> montage asset container -> explicit editable timeline -> trusted renderer ->
> deterministic editorial verification -> bounded semantic review

This is materially different from PipeV2, uses the assets already available,
creates inspectable training signals, supports multiple meaningful tasks per
asset pack, and sharply reduces judge calls without lowering the oracle, NOP,
solver-difficulty, or deployment standards.
