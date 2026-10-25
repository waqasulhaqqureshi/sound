# MASTER PROMPT — Drama Episode → 8-Min Fair-Use Summary Video (Urdu TTS)

> HOW TO USE: Start a NEW Arena Agent session on this repo (or any repo containing
> your episode clips), paste everything between the === lines below, fill in the
> [bracketed] parts, and paste your transcript where indicated. The agent will
> reproduce the exact Mitti De Baway Ep10 workflow end-to-end.

===
You are my video-production agent. Make me a YouTube fair-use SUMMARY + REVIEW video
of approximately [8 minutes] from the full episode clips I provide, following this
EXACT proven workflow. Do not improvise steps away; if a step fails, apply the
documented fix.

## MY INPUTS
- Drama: [DRAMA NAME], Episode: [EPISODE NUMBER], Channel: [CHANNEL NAME]
- Episode video: split into 10-minute parts in the `clips/` folder as
  part_000.mp4, part_001.mp4, ... (made with
  `ffmpeg -i input.mp4 -c copy -map 0 -segment_time 600 -f segment -reset_timestamps 1 clips/part_%03d.mp4`)
  TIMESTAMP MATH: global time T (seconds) lives in file number floor(T/600),
  at local offset T mod 600.
- Transcript with timestamps: [PASTE TRANSCRIPT HERE]
- Narration language: URDU (اردو script). Voice: FEMININE. Style: HOOK-FIRST RECAP + REVIEW.
- Target: finished video in `output/` folder, then COMMIT + PUSH it to my current
  git branch so I can `git fetch` it in VSCode.

## STEP 1 — RESEARCH (fair use + story context)
1.1 Web-search "YouTube fair use guidelines" and confirm you understand the 4 factors
    (transformative purpose, nature of work, amount used, market effect).
1.2 Web-search the drama + this episode (plot, cast names/spellings, what moment went
    viral) so narration uses correct context and the audience's language.

## STEP 2 — TOOL SETUP (sandbox has NO ffmpeg — install it via PyPI)
2.1 Run: pip3 install --break-system-packages imageio imageio-ffmpeg Pillow arabic-reshaper python-bidi
2.2 ffmpeg path = python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
    (static ffmpeg 7.x; use this binary for ALL ffmpeg work).
2.3 Verify every clip's duration/resolution with `ffmpeg -i`.
2.4 Urdu fonts: direct font downloads are BLOCKED; get them via git:
    cd /tmp && git clone --depth 1 --filter=blob:none --sparse https://github.com/googlefonts/noto-fonts.git notofonts
    cd notofonts && git sparse-checkout set hinted/ttf/NotoNastaliqUrdu hinted/ttf/NotoNaskhArabic
    Copy NotoNaskhArabic-Regular.ttf and -Bold.ttf to work/fonts/.
    *** CRITICAL: use NASKH for on-screen Urdu, NOT Nastaliq. Nastaliq renders as
    tofu boxes because arabic_reshaper outputs presentation-form codepoints that
    NotoNastaliqUrdu lacks (needs HarfBuzz/raqm, unavailable). Naskh works perfectly
    with arabic_reshaper + python-bidi in Pillow.
    Latin/English overlay text: /usr/share/fonts/truetype/dejavu/DejaVuSans(-Bold).ttf.
    NOTE: the em-dash character renders as tofu in Naskh — use ":" instead. ***

## STEP 3 — ANALYZE HOOKS (transcript + frames)
3.1 Read the full transcript. Identify 5-7 hook beats (shocking dialogue, twists,
    emotional peaks). Note their global timestamps.
3.2 Scout frames: extract 6-8 stills per hook window with
    ffmpeg -ss <local_offset> -i clips/part_XXX.mp4 -frames:v 1 -vf scale=480:-1 frame.jpg
    tile them with ImageMagick `montage ... -tile 4x2 sheet.jpg`, then VIEW the sheets
    (read_file) and pick the strongest emotional close-ups. Avoid blurry/transition frames.
3.3 Write work/shot_plan.md: one row per narration segment = topic, Urdu chapter title,
    3 source shots (file + start second), and why each shot was chosen.

## STEP 4 — WRITE THE NARRATION SCRIPT (this is the fair-use core)
Rules that keep the video transformative:
- 100% ORIGINAL new Urdu voiceover; NEVER copy drama dialogue verbatim beyond a
  3-4 word quote. Original episode audio will be COMPLETELY REMOVED in editing.
- Structure (12 segments of ~600-700 Urdu characters each):
  S1 cold-open HOOK (the biggest twist, asked as a question), then backstory/context,
  chronological recap in chapters, each with CRITIQUE ("میری رائے میں..."),
  social commentary, rhetorical questions to viewers, ending with PREDICTION +
  verdict + comment question + "watch the full episode on the official channel".
- TIMING FACT: the built-in Urdu TTS reads ~650 chars in ~38-45 seconds
  (~1000 chars/min). For 8 minutes you need ~12 segments (~7,800 chars total),
  NOT 7. Our Ep10 video needed 5 extra analysis segments added after measuring.
- Save the script as work/script_urdu.txt BEFORE generating any audio.

## STEP 5 — TTS WITH THE BUILT-IN ARENA VOICE (NO Gemini key exists in repo)
Background: there is NO key.txt/Gemini API key available and Google APIs are not
reachable from the sandbox. Use Arena's built-in speech tools EXACTLY like this:
5.1 Call add_voice FIRST (mandatory before any speech):
    - language: "ur"   (NOT "ur-PK" — a region tag is a hard constraint and can fail)
    - voice_identity: gender="feminine", use_case="narration"
    - text: ~35 words of Urdu taken from the S1 hook opening, e.g.
      "کیا بلقیس بانو نے واقعی پیر صاحب سے شادی کی پیشکش کر دی؟ جی ہاں! ..."
    The tool plays 2 audition voices; I (the user) pick one; the tool returns a
    voice_id (in the Ep10 session it was "voice-00").
    *** NEW-SESSION WARNING: voice_ids do not carry across sessions. In a new
    session you MUST call add_voice again with the same parameters and let me pick
    the closest-matching voice. Same voice_id WITHIN one session always = same
    voice, so all 12 clips stay consistent. ***
5.2 Then call generate_speech once per script segment:
    - max 1500 characters per call (our ~650-char segments are safely under)
    - save to work/audio/segN.mp3, all with the SAME voice_id
    - send the calls in PARALLEL (multiple calls in one response)
    - HARD LIMIT: 10 speech clips per turn. With 12 segments, generate 7+3, tell me
      "reply continue", then generate the last 2 next turn. (Proven workaround.)
5.3 Probe every mp3 duration (ffmpeg -i) and confirm the total ≈ target length.
    TTS output format: 24 kHz MONO mp3 — remember this for Step 7!

## STEP 6 — OVERLAYS WITH PILLOW (work/make_overlays.py — reuse from Ep10 repo if present)
Generate PNGs at 1280x720:
- title.png: drama name (gold, Naskh Bold ~96px), "قسط نمبر X : مکمل خلاصہ و تبصرہ",
  a curiosity question line, English subtitle.
- badge.png (520x56, semi-transparent black, gold underline): "خلاصہ و تبصرہ" +
  "SUMMARY & REVIEW" — shown the WHOLE video (review framing = fair use evidence).
- chapter_01..12.png: lower-third bar (black alpha + gold edge), Urdu chapter title
  right-aligned (reshape + bidi, anchor right), "PART n/12" left in DejaVu Bold.
- end.png: "مکمل قسط ضرور دیکھیں" + official channel + comment CTA + English
  Fair Use (17 U.S.C. §107) paragraph crediting the channel/rights owners.
- output/thumbnail.jpg: best hook frame + dark bottom band + big Urdu question +
  red "EP X TWIST!" tag.

## STEP 7 — EDIT & RENDER (work/render.py — reuse from Ep10 repo if present)
Per segment (video duration = its mp3 duration + 0.35s breathing gap):
- Cut its 3 planned shots (equal thirds, each ~12-16s, NEVER a long continuous scene):
  ffmpeg -ss START -i SRC -an  (*** -an = original audio deleted — mandatory ***)
  filter: scale=1344:756,crop=1280:720 center (slight punch-in vs source 1280x676,
  fills 720p), trim, fps=25, fade in/out 0.35s, libx264 veryfast CRF20.
- Concat the 3 shots, overlay badge at top-center (y=12) and chapter PNG at bottom
  (y=H-110) visible only first 5s: overlay=enable='lt(t,5)'.
Assemble: title card 5s (silent) + 12 segments + end card 7s (silent).
*** AUDIO GOTCHA (cost us a broken first render): NEVER concat the 24kHz-mono mp3s
together with 48kHz-stereo silence wavs via the concat demuxer — mixed formats
collapse timestamps into a ~30s file. FIX: first convert EVERY audio piece to
48kHz stereo WAV (ffmpeg -ar 48000 -ac 2), then concat to one narration wav.
Also NEVER use -shortest on the final mux (it amputates the video to the broken
audio). ***
Final mux: video concat -c copy + narration with
-af "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000" -c:a aac -b:a 160k -movflags +faststart
(YouTube loudness target -14 LUFS; aresample after loudnorm because loudnorm
upsamples to 192k internally.)

## STEP 8 — QA (do not skip)
- ffmpeg -i final.mp4 → Duration must be ~08:00-08:30, 1280x720, AAC 48000 stereo.
- Full decode test: ffmpeg -v error -i final.mp4 -f null -  → no errors.
- Volume: ffmpeg -ss 60 -t 60 -i final.mp4 -af volumedetect -f null - →
  mean ≈ -17 dB, max ≈ -1.5 dB.
- Extract QA frames at 6 chapter boundaries, montage, VIEW them: Urdu text must be
  clean (no tofu), badge visible, GREEN/channel logo still visible (credit).

## STEP 9 — DELIVERABLES + GITHUB DELIVERY
- output/[Drama]_Ep[N]_Urdu_Summary_8min.mp4  (final video)
- output/thumbnail.jpg
- output/YouTube_title_description.txt: 3 title options, Urdu description,
  chapter timestamps computed from ACTUAL segment durations (title offset +5s,
  cumulative), fair-use disclaimer, tags.
- .gitignore the heavy intermediates (work/segments/, work/audio48/, narration wav).
- git add .gitignore output/ work/script_urdu.txt work/shot_plan.md work/render.py
  work/make_overlays.py  →  commit  →  git push origin <MY CURRENT BRANCH>
  (64MB video pushes fine; GitHub warns >50MB, hard-blocks only >100MB.)
- Present the final video file and tell me the fetch commands:
  git fetch origin && git checkout <branch>   (fetch alone does not write files!)

## FAIR-USE CHECKLIST (re-verify every time)
[ ] Original audio 100% removed; new narration covers 100% of runtime
[ ] No continuous source shot longer than ~20s; shots re-ordered (hook first)
[ ] Every chapter adds criticism, context, or questions — not just retelling
[ ] On-screen "Summary & Review" framing + end-card credit + description disclaimer
[ ] Video cannot substitute for the full episode (no OST, no full scenes/dialogue)
[ ] Tell me honestly: a Content ID claim is still possible; fair use is a
    case-by-case legal defense, not a guarantee.

My transcript for this episode:
[PASTE FULL TRANSCRIPT WITH TIMESTAMPS HERE]
===

## Reference — how Ep10 turned out (proof this prompt works)
- Input: 4 clips, 35:36 total (1280x676) → Output: 8:19, 1280x720, 64 MB
- Voice: Arena built-in TTS, `add_voice(language="ur", gender="feminine",
  use_case="narration")`, session voice_id `voice-00`, 12 clips (37-48s each)
- Files: output/Mitti_De_Baway_Ep10_Urdu_Summary_8min.mp4, thumbnail.jpg,
  YouTube_title_description.txt; pipeline in work/render.py + work/make_overlays.py
