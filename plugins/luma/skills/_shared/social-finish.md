# Finishing a video for social feeds and shop pages

The last pass that turns finished clips into something people stop for and a shop can use: the
right frame for each place it runs, captions timed to the speech, music that drops under the voice,
a few sound effects on the cuts, one loudness, and a check of every file before it is handed over.
It builds on [the short-film ffmpeg reference](../short-film/references/ffmpeg.md) (steps 1 to 4
set `W`, `H`, `FPS`, `V`, `A` and `norm`) and its `title.py` (step 8). Run it in one project
folder, in bash or zsh, with ffmpeg and python3 with Pillow. Numbers shown (sizes, seconds,
volumes, loudness) are edit choices, not catalog values; the catalog's own values still come from
`list_models`.

The order is always: the cut with its own sound, then captions (F3), music (F5), sound effects
(F6), the loudness and the copies (F7), the checks (F8). Each step reads the file the one before
wrote. Below, `master-<shape>.mp4` (`master-vertical.mp4`) is the finished cut of one shape with
its music and effects; copy your workflow's last file to that name before F7.

## F1. Where it runs decides the frame

| Where | Frame (edit choice) | What matters there |
|---|---|---|
| Reels, TikTok, Shorts, stories | vertical, 1080x1920 | The first second; the app covers the edges (F2); most people watch with sound, many without |
| Instagram or Facebook feed | 4:5, 1080x1350, or square | Muted autoplay: the picture and the words carry the message |
| Shop product page, marketplace listing | square or landscape | Muted, looping, no captions over the product; the product whole and sharp from the first frame |
| YouTube, a website, a presentation | landscape, 1920x1080 | Sound on; titles and an end card |

Set `R` in film step 4 to the frame's shape (`vertical`, `square`, `landscape`, or `4:5`) and
make one master per shape. Film step 4 makes the short side 1080 when the clips are that sharp and
720 otherwise; every app takes both. For a 1080 master from smaller clips, enhance them first
(`edit_video` `mode: "enhance"`). To get another shape from a finished clip there are four ways;
in testing they ranked like this for a product:

1. **A moved crop** (film step 4's `V`, with [reel edit R2](../memory-reel/references/reel-edit.md)'s
   `CX` and `CY` to put it where the subject is): free and exact, and the subject gets bigger, not
   smaller. Try `CX` from 0.3 to 0.7 on frames at the start, middle and end, because the subject
   moves; take the one that keeps it whole in all three. Enhance the crop when it is small.
2. **Made again in the new shape**, for a clip Luma made from a still: an edit of the still with
   the new `aspect_ratio`, animated with the same prompt. The best quality, at the price of a new
   clip, and the motion is new.
3. **`edit_video` `mode: "reframe"`** with that `aspect_ratio` from `list_models` feature
   `reframe`. It takes no prompt, keeps the whole source at its own size and invents everything
   around it. For a small change (vertical to 4:5 or 3:4) that is a thin strip; from landscape to
   vertical it is about two thirds of the frame: the subject ends up small in the middle, and the
   model draws what it guesses is there, which in testing included a realistic face for a person
   whose head the source never showed, different on every take, and a garbled shop sign. Check
   every reframe for invented people, faces, text and props before it is used, and never put an
   invented face in an ad without telling the user. A new job with a new key, made when asked.
4. **A blurred fill** (R2's `FIT`): the whole picture over a soft copy of itself. Fine for a story,
   weak for an ad.

## F2. Keep words and faces where the app does not cover them

On a vertical feed the app puts its own buttons and text over the top eighth, the bottom fifth and
the right eighth. Faces, the product and every word belong in what is left. Every workflow in this
bundle means these bands when it says "the parts the app covers". Draw those bands on a
middle frame and look at it:

```sh
ffmpeg -loglevel error -y -ss 2 -i master-vertical.mp4 -frames:v 1 -vf \
  "drawbox=y=0:w=iw:h=ih*0.125:color=red@0.35:t=fill,drawbox=y=ih*0.8:w=iw:h=ih*0.2:color=red@0.35:t=fill,drawbox=x=iw*0.875:y=0:w=iw*0.125:h=ih:color=red@0.35:t=fill" \
  safe-check.jpg
```

Anything that matters under red moves (a new crop, a new caption position) or is accepted with
the user. In a 4:5 feed post the app covers about a seventh at the top and the bottom instead.

## F3. Captions from the speech

Most viewers in a feed start muted, so a clip with speech gets burned-in captions: two to four
words at a time, big, bold, white with a dark outline, in the band between the face and the
bottom fifth. Word timings come from one of two places:

- **A transcription with word times**, when `whisper` or `mlx_whisper` is installed (check with
  `command -v whisper mlx_whisper`): `whisper voice.wav --word_timestamps True --output_format json`,
  or `mlx_whisper voice.wav --word-timestamps True -f json -o .`. Both write `voice.json`. Read
  it against the script and fix any misheard word or spelling (British or American, as the user
  writes) in the JSON before rendering. The first word's start is often early: when the speech
  starts later (`silencedetect`, film step 5), set that word's `start` to where it does.
- **The script itself**, when there is no transcriber: the words are spread over the speech from
  where it starts to where it ends, longer words longer, with a pause at each full stop. Good
  enough for a short ad read at an even pace; check it with the frames below and move a line
  that drifts.

Mark one word per line to stand out by writing it `*like this*` in the script (or in the JSON's
word). Save as `captions.py`:

```python
# python3 captions.py W H SOURCE OUTDIR [--start=S] [--end=E] [--at=0.66] [--max=3]
# SOURCE is a whisper JSON (segments with words) or a plain text script spread from --start to --end.
# With a JSON, --end drops the words said after it (to stop captions where an on-screen ask begins).
# Writes OUTDIR/cap01.png ..., OUTDIR/overlay.txt (a filter for: ffmpeg -i IN -i cap01.png ...)
# and OUTDIR/captions.srt, the same lines as text for an editing app.
import json, re, sys
from PIL import Image, ImageDraw, ImageFont

flags = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--"))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
W, H, src, outdir = int(args[0]), int(args[1]), args[2], args[3]
at, most = float(flags.get("at", 0.66)), int(flags.get("max", 3))

if src.endswith(".json"):
    data = json.load(open(src))
    words = [(w["word"].strip(), w["start"], w["end"]) for s in data["segments"] for w in s.get("words", [])]
    if "end" in flags:
        words = [w for w in words if w[1] < float(flags["end"])]
else:
    text = open(src).read().split()
    start, end = float(flags["start"]), float(flags["end"])
    weights = [len(t.strip("*")) + 2 + (6 if re.search(r"[.!?]$", t) else 0) for t in text]
    step, t, words = (end - start) / sum(weights), start, []
    for tok, wt in zip(text, weights):
        words.append((tok, t, t + step * (len(tok.strip("*")) + 2)))
        t += step * wt

groups, cur = [], []
for i, w in enumerate(words):
    cur.append(w)
    gap = words[i + 1][1] - w[2] if i + 1 < len(words) else 9
    if len(cur) >= most or gap > 0.55 or re.search(r"[.!?,;:]$", w[0].strip("*")):
        groups.append(cur); cur = []
if cur: groups.append(cur)

def font(size):
    for name in ("Arial Black.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "Helvetica.ttc", "Arial.ttf"):
        try: return ImageFont.truetype(name, size)
        except OSError: pass
    return ImageFont.load_default(size=size)

size, stroke, lines = int(H * 0.058 if H > W else H * 0.07), max(3, int(H * 0.006)), []
for n, g in enumerate(groups, 1):
    toks = [w[0] for w in g]
    f = font(size)
    while sum(f.getlength(t.strip("*") + " ") for t in toks) > W * 0.72 and f.size > 12:
        f = font(int(f.size * 0.92))
    words_px = [(t.strip("*"), f.getlength(t.strip("*") + (" " if i < len(toks) - 1 else "")), t.startswith("*"))
                for i, t in enumerate(toks)]
    tw = int(sum(p for _, p, _ in words_px)) + stroke * 4
    th = int(f.size * 1.35) + stroke * 4
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d, x = ImageDraw.Draw(img), stroke * 2
    for word, px, hot in words_px:
        d.text((x, stroke * 2), word, font=f, fill=(255, 214, 10) if hot else (255, 255, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += px
    img.save(f"{outdir}/cap{n:02d}.png")
    end = min(g[-1][2] + 0.15, groups[n][0][1] - 0.01) if n < len(groups) else g[-1][2] + 0.3
    lines.append((n, g[0][1], end))

# Centred in the part the app leaves free (F2): left of the right eighth.
chain, last = [], "[0:v]"
for n, s, e in lines:
    chain.append(f"{last}[{n}:v]overlay=x=(W*0.875-w)/2:y=H*{at}-h/2:enable='between(t,{s:.2f},{e:.2f})'[c{n}]")
    last = f"[c{n}]"
open(f"{outdir}/overlay.txt", "w").write(";".join(chain) + f";{last}format=yuv420p[v]\n")
ts = lambda v: f"{int(v // 3600):02d}:{int(v % 3600 // 60):02d}:{int(v % 60):02d},{int(round(v * 1000)) % 1000:03d}"
with open(f"{outdir}/captions.srt", "w") as srt:
    for (n, s, e), g in zip(lines, groups):
        srt.write(f"{n}\n{ts(s)} --> {ts(e)}\n{' '.join(w[0].strip('*') for w in g)}\n\n")
print(f"{len(lines)} captions; first {lines[0][1]:.2f}s, last ends {lines[-1][2]:.2f}s")
```

Then burn them in. The clip is normalised first (film steps 4 and 6), so `W` and `H` are the
master's:

```sh
mkdir -p caps
python3 captions.py "$W" "$H" voice.json caps                      # or: script.txt caps --start=0.3 --end=8.6
ffmpeg -loglevel error -y -i c01.mp4 $(for p in caps/cap*.png; do printf -- '-i %s ' "$p"; done) \
  -/filter_complex caps/overlay.txt -map "[v]" -map "0:a?" -c:v libx264 -preset medium -crf 17 -c:a copy c01cap.mp4
for t in 1 3 5; do ffmpeg -loglevel error -y -ss $t -i c01cap.mp4 -frames:v 1 "cap-check-$t.jpg"; done
```

An ffmpeg older than 7 reads `-filter_complex_script caps/overlay.txt` instead of
`-/filter_complex caps/overlay.txt`. For `--start` and `--end` with a script, take where the
speech starts and stops from `silencedetect` (film step 5). Look at the check frames: the line
under the face and above the bottom fifth, readable when the frame is shrunk to a phone thumbnail.
If it covers the face, run `captions.py` again with `--at=0.75`; on a product shot, keep it off the
product. Never put captions on a shop page copy.

## F4. A voice that sounds finished

A voice the user recorded on a phone gets a light clean-up before anything else, and before it goes
to `lip_sync`, because the lip-sync clip carries the audio it was given. First trim the silence at
both ends, keeping about a fifth of a second before the first word and a third after the last
(`silencedetect` in film step 5 shows where speech starts and stops; cut with `-ss` and `-t`):
every second of silence is a second of video to make and to watch. Then clean it, with `IN` set to
the trimmed recording:

```sh
IN=my-voice-trimmed.m4a
ffmpeg -loglevel error -y -i "$IN" -af \
  "highpass=f=80,lowpass=f=16000,acompressor=threshold=-18dB:ratio=2.5:attack=12:release=180:makeup=1.4,loudnorm=I=-16:TP=-1.5:LRA=7" \
  -ar 48000 -ac 2 voice.wav
```

Use only a voice the user has the right to use.

## F5. Music that drops under the voice

The music sits well under the speech and dips further whenever someone talks (ducking), then comes
back up in the gaps. `IN` is the finished cut with the speech as its audio, `MUSIC` a track the
user has the right to use. The track is levelled first, so `MUSIC_GAIN` means the same for a quiet
track and a loud one:

```sh
IN=cut.mp4; OUTFILE=cut-music.mp4; MUSIC=music.mp3
MUSIC_GAIN=0.3                                   # the bed before ducking; 0.2 for a busy track
ffmpeg -loglevel error -y -i "$MUSIC" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 music-level.wav   # every track starts equal
MUSIC=music-level.wav
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
FADE_AT=$(awk -v d="$D" 'BEGIN { printf "%.2f", d - 1.5 }')
ffmpeg -loglevel error -y -i "$IN" -stream_loop -1 -i "$MUSIC" -filter_complex \
  "[0:a]${A},asplit=2[vo][key];[1:a]${A},atrim=0:${D},volume=${MUSIC_GAIN},afade=t=in:d=0.5,afade=t=out:st=${FADE_AT}:d=1.5[m];[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[duck];[vo][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUTFILE"
```

With no speech in the clip, use [reel edit R4](../memory-reel/references/reel-edit.md) instead,
with `LUFS=-14` and `GRADE=null`. Listen to the result on a phone speaker: the music must be heard in the gaps and
must never cover a word. Too loud under the voice: lower `MUSIC_GAIN`. Lost in the gaps: raise it.

Cutting on the beat: when the user knows the track's tempo (most music libraries list it), one beat
is `60 / BPM` seconds; make each shot a whole number of beats long (two or four for a fast edit,
eight for a slow one) and start the music on a beat.

## F6. A few sound effects on the cuts

Sound effects make cuts feel deliberate. They go on after the music (F5 or R4), over the mixed
sound, so their level is set against it. Use the user's own licensed effects when they have them;
otherwise make two soft ones (the hit carries a short click as well as its low thump, because a
phone speaker plays nothing as low as the thump). `peak_to` sets an effect's loudest point, so the same numbers work
for any source: a whoosh at -9 dBFS and a hit at -6 dBFS sit clearly but not loudly over a mix at
-14 LUFS.

```sh
peak_to() {   # peak_to FILE DBFS
  local m=$(ffmpeg -hide_banner -nostats -i "$1" -af volumedetect -f null - 2>&1 | awk '/max_volume/ { print $5 }')
  ffmpeg -loglevel error -y -i "$1" -af "volume=$(awk -v t="$2" -v m="$m" 'BEGIN { print t - m }')dB" "lvl-$1" && mv "lvl-$1" "$1"
}
ffmpeg -loglevel error -y -f lavfi -i "anoisesrc=color=pink:d=0.45:amplitude=0.7" -af \
  "highpass=f=500,lowpass=f=7000,afade=t=in:d=0.3:curve=exp,afade=t=out:st=0.3:d=0.15,aformat=channel_layouts=stereo,aresample=48000" whoosh.wav
ffmpeg -loglevel error -y -f lavfi -i "sine=f=70:d=0.45" -f lavfi -i "anoisesrc=color=pink:d=0.15:amplitude=1" -filter_complex \
  "[0]afade=t=out:d=0.45:curve=exp[l];[1]lowpass=f=2500,highpass=f=150,afade=t=out:d=0.15:curve=exp[c];[l][c]amix=inputs=2:normalize=0,aformat=channel_layouts=stereo,aresample=48000" hit.wav
peak_to whoosh.wav -9; peak_to hit.wav -6
```

Place each one with `adelay` (milliseconds, the same for both channels) and mix them over the
music master. A whoosh starts a quarter second before a cut; a hit lands on it. A single clip with
no cuts gets one hit on its first frame (`adelay=0|0`) or on the moment the product lands, not a
whoosh into nothing:

```sh
ffmpeg -loglevel error -y -i cut-music.mp4 -i whoosh.wav -i hit.wav -filter_complex \
  "[1:a]adelay=2750|2750[w];[2:a]adelay=6000|6000[h];[0:a][w][h]amix=inputs=3:normalize=0:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 master-vertical.mp4
ffmpeg -hide_banner -nostats -ss 2.75 -t 0.45 -i master-vertical.mp4 -af "highpass=f=3000,volumedetect" -f null - 2>&1 | grep mean_volume
ffmpeg -hide_banner -nostats -ss 2.75 -t 0.45 -i cut-music.mp4 -af "highpass=f=3000,volumedetect" -f null - 2>&1 | grep mean_volume
```

The two last lines prove the whoosh is there: over the effect's window the high band should rise
by a few dB. No rise, raise the peak by 3 dB; a rise of more than about 10 dB is too loud. Two to
six effects in a short clip, at most one whoosh per cut, never over a spoken word, and no game
sounds (plucks, bloops, coins).

## F7. One loudness, and a copy for each place

Most apps and players turn loud uploads down to about -14 LUFS, so a finished social master lands
there with its peaks at or under -1.5 dBTP. Measure it with film step 10's loudness line (on
`master-vertical.mp4`). More than half a unit off: on a film, step 10's second pass with
`LUFS=-14`. On a clip under about ten seconds, that pass can overshoot (loudnorm measures short
files differently from the `ebur128` check), so apply the difference as a plain gain instead, then
measure again:

```sh
I=$(ffmpeg -hide_banner -nostats -i master-vertical.mp4 -af ebur128 -f null - 2>&1 | awk '/ I:/ { v = $2 } END { print v }')
ffmpeg -loglevel error -y -i master-vertical.mp4 -c:v copy -af "volume=$(awk -v i="$I" 'BEGIN { print -14 - i }')dB,alimiter=limit=0.84:level=false" \
  -c:a aac -b:a 192k -ar 48000 master-level.mp4 && mv master-level.mp4 master-vertical.mp4
```

Then, per master:

```sh
ffmpeg -loglevel error -y -i master-vertical.mp4 -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart post-vertical.mp4
ffmpeg -loglevel error -y -i master-vertical.mp4 -an -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -movflags +faststart post-vertical-silent.mp4
for t in 0.3 0.6 1.0 1.5; do ffmpeg -loglevel error -y -ss $t -i master-vertical.mp4 -frames:v 1 -q:v 2 "cover-$t.jpg"; done
```

- **With sound** for a feed that plays it; **silent** for the user to add a trending sound in the
  app, and for a shop page.
- **The cover** is the best of those four frames: the hook at its strongest, sharp (no motion
  blur on the face or the product), nothing under F2's red bands. Keep it as `cover-vertical.jpg`.
- A shop page copy is landscape or square, silent, and starts on the product whole and sharp.
  Make it with film step 11's muted web copy.

## F8. Check every file before handing it over

```sh
for f in post-*.mp4; do
  echo "== $f"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of compact=p=0 "$f"
  ffmpeg -hide_banner -nostats -i "$f" -vf blackdetect=d=0.15:pix_th=0.02 -f null - 2>&1 | grep black_start || echo "no black frames"
  if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$f" | grep -q .; then
    ffmpeg -hide_banner -nostats -i "$f" -af silencedetect=noise=-40dB:d=1 -f null - 2>&1 | grep silence_start || echo "no silent gaps"
    ffmpeg -hide_banner -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 | grep -E " I:| Peak:" | tail -2
  else echo "no audio track (a silent copy)"; fi
done
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 post-vertical.mp4)
ffmpeg -loglevel error -y -i post-vertical.mp4 -vf "fps=12/${D},scale=270:-2,tile=6x2" -frames:v 1 post-sheet.jpg
for t in 0 1; do ffmpeg -loglevel error -y -ss $t -i post-vertical.mp4 -frames:v 1 "frame-$t.jpg"; done
ffmpeg -loglevel error -y -sseof -0.2 -i post-vertical.mp4 -frames:v 1 frame-last.jpg
```

The sheet holds twelve frames spread over the whole file, however short. Then look at
the first frame, a frame at one second, every cut, the last frame, `safe-check.jpg` and the caption
checks yourself, against the brief:

- The hook is visible in the first frame, with no fade from black and no logo first.
- The product or the person is the same in every shot: label, colours, face. A shot that drifted
  is cut or retaken, never hidden under a caption or a crop.
- Every caption matches what is said, on time, inside the safe area.
- The music is heard in the gaps and never covers a word.

If you can start a helper with a fresh context, give it the brief and
the frames and let it find what is wrong before the user sees it. Report the files with their
paths, sizes and what each one is for.
