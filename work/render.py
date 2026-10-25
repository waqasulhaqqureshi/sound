"""Assemble the 8-min fair-use summary: muted short shots + Urdu TTS + overlays."""
import os, re, subprocess, sys, imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SEG_DIR, VID_DIR = "work/segments", "work/audio"
os.makedirs(SEG_DIR, exist_ok=True)

# (audio file, [(source, start_sec) x3])
PLAN = [
    ("seg1.mp3",               [("clips/part_000.mp4", 385), ("clips/part_000.mp4", 505), ("clips/part_000.mp4", 565)]),
    ("seg8_backstory.mp3",     [("clips/part_000.mp4", 260), ("clips/part_001.mp4", 480), ("clips/part_000.mp4", 480)]),
    ("seg2.mp3",               [("clips/part_000.mp4", 195), ("clips/part_000.mp4", 250), ("clips/part_000.mp4", 320)]),
    ("seg3.mp3",               [("clips/part_000.mp4", 400), ("clips/part_000.mp4", 470), ("clips/part_000.mp4", 540)]),
    ("seg4.mp3",               [("clips/part_001.mp4", 180), ("clips/part_001.mp4", 230), ("clips/part_001.mp4", 300)]),
    ("seg9_household.mp3",     [("clips/part_001.mp4", 215), ("clips/part_001.mp4", 275), ("clips/part_001.mp4", 340)]),
    ("seg10_underworld.mp3",   [("clips/part_001.mp4", 395), ("clips/part_001.mp4", 440), ("clips/part_001.mp4", 470)]),
    ("seg5.mp3",               [("clips/part_001.mp4", 500), ("clips/part_001.mp4", 545), ("clips/part_001.mp4", 572)]),
    ("seg6.mp3",               [("clips/part_002.mp4", 30),  ("clips/part_002.mp4", 95),  ("clips/part_002.mp4", 180)]),
    ("seg11_qamar_marriage.mp3",[("clips/part_002.mp4", 230),("clips/part_002.mp4", 300), ("clips/part_002.mp4", 380)]),
    ("seg7.mp3",               [("clips/part_002.mp4", 460), ("clips/part_002.mp4", 530), ("clips/part_003.mp4", 230)]),
    ("seg12_verdict.mp3",      [("clips/part_003.mp4", 260), ("clips/part_003.mp4", 295), ("clips/part_003.mp4", 312)]),
]
TITLE_DUR, END_DUR, GAP = 5.0, 7.0, 0.35

def dur(path):
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2500:]); sys.exit(1)

def build_segment(idx, audio, shots, test_one=False):
    a = os.path.join(VID_DIR, audio)
    if not os.path.exists(a):
        print(f"SKIP seg{idx}: {audio} missing"); return None
    total = dur(a) + GAP
    each = total / len(shots)
    parts = []
    for j, (src, start) in enumerate(shots):
        p = f"{SEG_DIR}/s{idx:02d}_{j}.mp4"
        vf = ("scale=1344:756,crop=1280:720:(in_w-1280)/2:(in_h-720)/2,"
              f"trim=duration={each:.2f},setpts=PTS-STARTPTS,fps=25,"
              f"fade=t=in:st=0:d=0.35,fade=t=out:st={each-0.35:.2f}:d=0.35,format=yuv420p")
        run([FF, "-y", "-ss", str(start), "-i", src, "-an", "-vf", vf,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", p])
        parts.append(p)
    lst = f"{SEG_DIR}/s{idx:02d}.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    raw = f"{SEG_DIR}/s{idx:02d}_raw.mp4"
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", raw])
    out = f"{SEG_DIR}/s{idx:02d}.mp4"
    fc = (f"[0:v][1:v]overlay=(W-w)/2:12[v1];"
          f"[v1][2:v]overlay=0:H-110:enable='lt(t,5)'[v]")
    run([FF, "-y", "-i", raw, "-i", "work/overlays/badge.png",
         "-i", f"work/overlays/chapter_{idx:02d}.png", "-filter_complex", fc,
         "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", out])
    print(f"seg{idx:02d} done ({total:.1f}s)")
    return out, a, total

if __name__ == "__main__":
    test = "--test" in sys.argv
    built = []
    for i, (audio, shots) in enumerate(PLAN, 1):
        r = build_segment(i, audio, shots)
        if r: built.append(r)
        if test: break
    if test:
        print("TEST segment rendered OK"); sys.exit(0)
    if len(built) != len(PLAN):
        print(f"ABORT: {len(built)}/{len(PLAN)} segments ready — generate missing TTS first"); sys.exit(2)
    # title + end cards as video
    for name, d in [("title", TITLE_DUR), ("end", END_DUR)]:
        run([FF, "-y", "-loop", "1", "-t", str(d), "-i", f"work/overlays/{name}.png",
             "-vf", "fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
             "-crf", "20", f"{SEG_DIR}/{name}.mp4"])
    vids = [f"{SEG_DIR}/title.mp4"] + [b[0] for b in built] + [f"{SEG_DIR}/end.mp4"]
    lst = "work/final_video.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(v)}'\n" for v in vids))
    # audio: FIRST normalise every clip to 48kHz stereo WAV (TTS mp3s are 24kHz mono;
    # mixing formats in concat demuxer collapses timestamps), then concat.
    os.makedirs("work/audio48", exist_ok=True)
    conv = []
    for _, a, _ in built:
        w = "work/audio48/" + os.path.basename(a).replace(".mp3", ".wav")
        run([FF, "-y", "-i", a, "-ar", "48000", "-ac", "2", w]); conv.append(w)
    gapf = "work/audio48/_gap.wav"
    sil_t, sil_e = "work/audio48/_sil_t.wav", "work/audio48/_sil_e.wav"
    for path, t in [(gapf, GAP), (sil_t, TITLE_DUR), (sil_e, END_DUR)]:
        run([FF, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", str(t), path])
    alst = "work/final_audio48.txt"
    with open(alst, "w") as fh:
        fh.write(f"file '{os.path.abspath(sil_t)}'\n")
        for w in conv:
            fh.write(f"file '{os.path.abspath(w)}'\nfile '{os.path.abspath(gapf)}'\n")
        fh.write(f"file '{os.path.abspath(sil_e)}'\n")
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", alst, "-c:a", "pcm_s16le", "work/narration48.wav"])
    os.makedirs("output", exist_ok=True)
    final = "output/Mitti_De_Baway_Ep10_Urdu_Summary_8min.mp4"
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", "work/narration48.wav",
         "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", final])
    print("FINAL:", final, f"{dur(final):.1f}s")
