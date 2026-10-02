# Assembling the film with ffmpeg

Commands for the short-film finish, and for any workflow that joins clips. They were run on real
Luma output and on a build of ffmpeg without `drawtext`. Run them in one project folder, in bash or
zsh. Numbers shown as examples (sizes, seconds, volumes) are edit choices, not catalog values:
set them from `ffprobe` and from the shot list.

Shell note: always write a variable in braces when a `[`, a `:` or a letter follows it:
`${V}[v]`, `d=${LEN}:r=48000`. zsh reads `$V[v]` as a subscript (ffmpeg then fails with "No such
filter: ''") and `$LEN:r` as a history modifier.

## 1. Check the tools

```sh
ffmpeg -hide_banner -version | head -1
ffmpeg -hide_banner -filters | grep -wE "xfade|acrossfade|loudnorm|drawtext"
python3 -c "import PIL; print('PIL', PIL.__version__)"
```

- No `xfade` (a very old ffmpeg): use hard cuts (step 9b) instead of crossfades.
- No `drawtext` (common): render titles as PNG with PIL (step 8). If PIL is missing,
  `python3 -m venv .venv && .venv/bin/pip install pillow`, then run the title script with
  `.venv/bin/python title.py` in place of `python3 title.py`; or skip titles and say so.

## 2. Download and inspect

Download each clip as soon as `get_generation` gives its `media_url` (links last one hour). Quote
the link, it contains `&`. Name files by shot number so they sort: clips `s01.mp4`, `s02.mp4`,
and stills `k01.jpg`, `k02.jpg` in shot order. A link has no file extension: Luma's stills are
JPEG, so save them as `.jpg`.

```sh
curl -sSL -o k01.jpg "<media_url of still 1>"
curl -sSL -o s01.mp4 "<media_url of shot 1>"
for f in s*.mp4; do printf "%s " "$f"; ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,duration -of csv=p=0 "$f" | tr '\n' ' '; echo; done
```

A clip with no `audio` entry has no audio track at all. Every image-to-video clip is like that.
Pictures and clips come in slightly different sizes even in one shape (text and edit stills differ,
and so do image-to-video, frames and effect clips made from the same still), and in different frame
rates, so everything is normalised (steps 4 and 6).

`ffprobe` shows a phone photo's stored pixels, not the upright picture: a photo with a rotate flag
reads as landscape when it looks portrait. Read the upright size with
`python3 -c "from PIL import Image, ImageOps; print(ImageOps.exif_transpose(Image.open('p01.jpg')).size)"`.
Luma applies the flag itself, and ffmpeg 8 does too when it scales a photo (an older build may
show it sideways in a contact sheet).

## 3. Contact sheets (check before you cut, and before you animate)

Scale every picture to one cell first, then tile the cells. Tiling pictures of different sizes
directly makes ffmpeg drop tiles without a message, and Luma's tools make slightly different sizes.
`COLS` is how many cells per row; the rows are computed so every picture gets a cell:

```sh
CELL="scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:-1:-1:color=black"
COLS=4
mkdir -p thumbs
for f in k*.jpg; do ffmpeg -loglevel error -y -i "$f" -vf "${CELL}" "thumbs/$f"; done
N=$(ls thumbs/k*.jpg | wc -l); ROWS=$(( (N + COLS - 1) / COLS ))
ffmpeg -loglevel error -y -pattern_type glob -i 'thumbs/k*.jpg' -vf "tile=${COLS}x${ROWS}" -frames:v 1 sheet-stills.jpg
```

First and last frame of every clip, one row per clip:

```sh
for f in s*.mp4; do b=${f%.mp4}
  ffmpeg -loglevel error -y -ss 0.5 -i "$f" -frames:v 1 -vf "${CELL}" "thumbs/${b}_first.jpg"
  ffmpeg -loglevel error -y -sseof -0.5 -i "$f" -frames:v 1 -vf "${CELL}" "thumbs/${b}_last.jpg"
done
N=$(ls thumbs/s*_*.jpg | wc -l)
ffmpeg -loglevel error -y -pattern_type glob -i 'thumbs/s*_[fl]*.jpg' -vf "tile=2x$(( (N + 1) / 2 ))" -frames:v 1 sheet-clips.jpg
```

For a vertical film swap the cell size in `CELL` (`270:480` in both places). Count the tiles on
the sheet against the files: one missing means a picture did not go through the cell step. Look at
the sheet yourself, then show it to the user.

A cut hidden inside a clip (the model sometimes changes the shot halfway) shows as a jump in the
picture. This lists where one happens; nothing printed means none:

```sh
ffmpeg -hide_banner -nostats -i s03.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*'
```

## 4. Pick one size, rate and audio format, and define the helper

The frame comes from the piece's shape, not from any one clip: clips of one shape come out close to
their ratio but not on it, and at different sizes by route. Set `R` to the frame's shape: the
film's `aspect_ratio`, such as `16:9`; `vertical` for a phone reel, story or hook (`9:16`),
`landscape` for a screen (`16:9`) or `square` (`1:1`); or, for clips made from one photo, the
photo's own width and height (`784:1172`). The short side is 1080 when any clip is about that
sharp, otherwise 720, and the frame rate is the one most clips share:

```sh
R=16:9   # the frame's shape: a width:height, or vertical, landscape or square
S=$(for f in s*.mp4; do ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$f"; done \
  | awk -F x '{ m = ($1 < $2 ? $1 : $2); if (m > s) s = m } END { print (s >= 1000 ? 1080 : 720) }')
read W H < <(awk -v r="$R" -v s="$S" 'BEGIN { if (r == "vertical") r = "9:16"; if (r == "landscape") r = "16:9"; if (r == "square") r = "1:1"
  split(r, a, ":"); if (a[1] + 0 >= a[2] + 0) { h = s; w = s * a[1] / a[2] } else { w = s; h = s * a[2] / a[1] }
  printf "%d %d\n", int(w / 2 + 0.5) * 2, int(h / 2 + 0.5) * 2 }')
FPS=$(for f in s*.mp4; do ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$f"; done | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
echo "$W x $H at $FPS"
```

The crop to fill in `V` below absorbs the small differences, and a clip smaller than the frame is
scaled up. For a smaller file, or to keep the smaller clips at their own sharpness, set `S=720`
before the `read` line. A loop is delivered as its own file, never joined to other clips: the join
would put a cut in the loop.

Then define the filters and one helper. It scales and crops to fill the frame, and it always
produces a stereo 48 kHz audio track: the clip's own, one borrowed from another file, or silence.
The crossfades in step 9a fail on a clip without audio, so never skip this.

```sh
V="scale=${W}:${H}:force_original_aspect_ratio=increase:flags=lanczos,crop=${W}:${H},setsar=1,fps=${FPS},format=yuv420p"
A="aresample=48000,aformat=channel_layouts=stereo"
has_audio() { ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$1" | grep -q .; }

# norm SRC OUT SECONDS [AUDIO_FROM] [AUDIO_FILTERS]; SECONDS is capped at the clip's own length
norm() {
  local src="$1" out="$2" secs="$3" asrc="${4:-$1}" afilt="${5:-anull}"
  local vdur=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 "$src")
  secs=$(awk -v s="$secs" -v d="$vdur" 'BEGIN { print (d ~ /^[0-9.]+$/ && d + 0 < s + 0) ? d : s }')
  if has_audio "$asrc"; then
    ffmpeg -loglevel error -y -t "$secs" -i "$src" -i "$asrc" -filter_complex \
      "[0:v]${V}[v];[1:a]${A},${afilt},apad,atrim=0:${secs}[a]" \
      -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 17 -c:a aac -b:a 192k -t "$secs" "$out"
  else
    ffmpeg -loglevel error -y -t "$secs" -i "$src" -f lavfi -t "$secs" -i "anullsrc=r=48000:cl=stereo" \
      -filter_complex "[0:v]${V}[v]" \
      -map "[v]" -map 1:a -c:v libx264 -preset medium -crf 17 -c:a aac -b:a 192k -t "$secs" "$out"
  fi
}
```

## 5. A sound bed from a clip's own audio

When most shots are silent (image-to-video), cut the bed from a shot that has sound. Find where its
audio is quiet but present, then loop that stretch with soft seams:

```sh
ffmpeg -hide_banner -nostats -i s05.mp4 -af silencedetect=noise=-45dB:d=0.5 -f null - 2>&1 | grep -E "silence_(start|end)"
ffmpeg -loglevel error -y -ss 5.2 -t 4.8 -i s05.mp4 -vn -af "${A}" amb.wav
ffmpeg -loglevel error -y -i amb.wav -i amb.wav -i amb.wav -filter_complex \
  "[0][1]acrossfade=d=1:c1=tri:c2=tri[x];[x][2]acrossfade=d=1:c1=tri:c2=tri,highpass=f=100[o]" -map "[o]" bed.wav
ffprobe -v error -show_entries format=duration -of csv=p=0 bed.wav
```

Three copies give about three times the stretch minus the overlaps; add inputs and `acrossfade`
steps for a longer bed. Then use it with `norm` (step 6) or mix it (step 7).

A user's own music never goes through `norm` or this loop: `norm` restarts it on every shot. Lay
it under the finished cut with [reel edit R4](../../memory-reel/references/reel-edit.md), with
`IN=film.mp4`, `OUTFILE=film-music.mp4` and `GRADE=null`, then `mv film-music.mp4 film.mp4` before
step 10. Only music the user has the right to use.

## 6. Normalise every shot

Run `norm` once per shot (the seconds come from your shot list; `norm` cuts them to the clip's own
length if the list asks for more):

```sh
norm s01.mp4 c01.mp4 10                                        # its own sound
norm s02.mp4 c02.mp4 10 s01.mp4 "lowpass=f=900,volume=0.55"    # silent shot, borrows shot 1's storm, muffled for an interior
norm s06.mp4 c06.mp4 8  bed.wav "volume=0.75"                  # silent shot over the sound bed (step 5)
norm s07.mp4 c07.mp4 5  s07.mp4 "volume=0.35"                  # an effect clip's own soundtrack, kept low
norm s03.mp4 c03.mp4 10                                        # silent shot, silent track
```

For an extended shot, normalise the extend output only; it already contains the original.

When the donor is shorter than the shot, or several shots in a row borrow the same sound, borrow
from a bed instead, so the sound carries on across the cuts rather than restarting. Make one bed
long enough for all of them (step 5), then give each shot the next slice: start each slice where
the previous one ended, less the transition between the two shots (0 for a hard cut):

```sh
ffmpeg -loglevel error -y -ss 0 -t 5 -i bed.wav slice_06.wav
norm s06.mp4 c06.mp4 5 slice_06.wav "volume=0.75"
ffmpeg -loglevel error -y -ss 4.4 -t 5 -i bed.wav slice_07.wav    # 5 seconds on, less a 0.6 crossfade
norm s07.mp4 c07.mp4 5 slice_07.wav "volume=0.75"
```

## 7. Mix a sound bed under a clip that has partial sound

An extend with audio on a silent original comes back silent in its first part. Lay the bed under
the clip's own audio and fade the bed out where the clip's sound starts:

```sh
ffmpeg -loglevel error -y -t 10 -i s05.mp4 -i bed.wav -filter_complex \
  "[0:v]${V}[v];[0:a]${A},apad,atrim=0:10[o];[1:a]atrim=0:10,volume=0.8,afade=t=out:st=5:d=1.5[b];[o][b]amix=inputs=2:normalize=0[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 17 -c:a aac -b:a 192k c05.mp4
```

## 8. Titles and an end card as PNG overlays

Save as `title.py`. It picks a system serif font (Georgia, DejaVu Serif, Times, Arial, in that
order), shrinks a line until it fits the width, so it works for vertical frames too, and puts a
soft dark shadow under overlay text so it reads over a bright picture.

```python
# python3 title.py W H OUT.png "Main line" ["Second line"] [--card] [--at=0.40]
# Transparent overlay by default; --card draws a full dark end card instead.
# --at sets where the first line starts, as a fraction of the height from the top.
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

flags = [a for a in sys.argv[1:] if a.startswith("--")]
args = [a for a in sys.argv[1:] if not a.startswith("--")]
card = "--card" in flags
at = next((float(a.split("=", 1)[1]) for a in flags if a.startswith("--at=")), 0.40)
W, H, out, lines = int(args[0]), int(args[1]), args[2], args[3:]

def font(size):
    for name in ("Georgia.ttf", "DejaVuSerif.ttf", "Times New Roman.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

def fitted(text, size, draw):
    f = font(size)
    while draw.textlength(text, font=f) > W * 0.9 and size > 10:
        size = int(size * 0.9)
        f = font(size)
    return f

img = Image.new("RGBA" if not card else "RGB", (W, H), (0, 0, 0, 0) if not card else (8, 9, 11))
d = ImageDraw.Draw(img)
sizes = [int(H * 0.09), int(H * 0.035)]
colors = [(245, 238, 225, 235), (220, 210, 190, 210)]
y = H * at
for i, text in enumerate(lines[:2]):
    f = fitted(text, sizes[i], d)
    w = d.textlength(text, font=f)
    if not card:
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).text(((W - w) / 2 + 2, y + 3), text, font=f, fill=(0, 0, 0, 255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(3, int(H * 0.006))))
        shadow.putalpha(shadow.getchannel("A").point(lambda v: min(255, int(v * 1.8))))
        img = Image.alpha_composite(img, shadow)
        d = ImageDraw.Draw(img)
    d.text(((W - w) / 2, y), text, font=f, fill=colors[i] if not card else colors[i][:3])
    y += getattr(f, "size", sizes[i]) * 1.6
img.save(out)
print(out)
```

Opening title over the first normalised clip. The fades scale with the clip: in from a tenth of
its length, and gone just before the transition into the next clip starts (with nothing after it,
a hard cut or a clip on its own, one second before its end). `X` is that transition's length in
step 9a, `0` for a hard cut; the overlay input runs for the clip's length:

```sh
L=$(ffprobe -v error -show_entries format=duration -of csv=p=0 c01.mp4)
X=0.6
read TIN TOUT F < <(awk -v l="$L" -v x="$X" 'BEGIN { f = (l / 10 < 0.8 ? l / 10 : 0.8); g = (x > 0 ? l - x - 0.1 : l - 1)
  printf "%.2f %.2f %.2f\n", l / 10, g - f, f }')
python3 title.py "$W" "$H" title_open.png "THE FILM'S TITLE" "a short film"
ffmpeg -loglevel error -y -i c01.mp4 -loop 1 -t "$L" -i title_open.png -filter_complex \
  "[1:v]format=rgba,fade=t=in:st=${TIN}:d=${F}:alpha=1,fade=t=out:st=${TOUT}:d=${F}:alpha=1[t];[0:v][t]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map "0:a?" -c:v libx264 -preset medium -crf 17 -c:a copy c01t.mp4
ffmpeg -loglevel error -y -ss "$(awk -v l="$L" 'BEGIN { print l / 2 }')" -i c01t.mp4 -frames:v 1 title-check.jpg
```

Look at `title-check.jpg`, a frame from the middle with the words on it. If they sit over the
subject, render the PNG again with `--at=0.15` (near the top) or `--at=0.70` (near the bottom) and
run the overlay again.

End card, five seconds, carrying the tail of a clip's sound (drop the second input and use
`-f lavfi -t 5 -i "anullsrc=r=48000:cl=stereo"` with `-map 1:a` for silence):

```sh
python3 title.py "$W" "$H" title_end.png "The end line." "Credit line" --card
ffmpeg -loglevel error -y -loop 1 -t 5 -i title_end.png -ss 2.5 -i c07.mp4 \
  -filter_complex "[0:v]${V}[v];[1:a]${A},volume=0.3,apad,atrim=0:5,afade=t=out:st=2:d=3[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 17 -c:a aac -b:a 192k -t 5 c99.mp4
```

Use the words the user gave for the title and end card, or the ones you chose and named in the
plan; do not add a credit line they did not ask for.

## 9a. Join with crossfades, and set the loudness

Save as `join.py`. Clips alternate with transitions written `name:seconds` (any `xfade` transition:
`fade`, `fadeblack`, `dissolve`, `wipeleft`, ...). It computes every offset from the real clip
lengths and normalises the loudness for online playback.

```python
# python3 join.py OUT.mp4 c01.mp4 fade:0.6 c02.mp4 fadeblack:0.5 c03.mp4 ...
# Clips alternate with transitions (xfade name:seconds). Every clip must be normalised first.
import subprocess, sys

def dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(out.decode())

out, items = sys.argv[1], sys.argv[2:]
clips, trans = items[0::2], [t.split(":") for t in items[1::2]]
cmd = ["ffmpeg", "-y", "-loglevel", "error"]
for c in clips:
    cmd += ["-i", c]
graph, v, a, length = [], "[0:v]", "[0:a]", dur(clips[0])
for i in range(1, len(clips)):
    name, d = trans[i - 1][0], float(trans[i - 1][1])
    graph.append(f"{v}[{i}:v]xfade=transition={name}:duration={d}:offset={length - d:.3f}[v{i}]")
    graph.append(f"{a}[{i}:a]acrossfade=d={d}:c1=tri:c2=tri[a{i}]")
    v, a, length = f"[v{i}]", f"[a{i}]", length + dur(clips[i]) - d
graph.append(f"{a}loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
cmd += ["-filter_complex", ";".join(graph), "-map", v, "-map", "[aout]",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    sys.exit(r.stderr[-2000:])
print(f"expected {length:.2f}s, got {dur(out):.2f}s")
```

```sh
python3 join.py film.mp4 c01t.mp4 fade:0.6 c02.mp4 fade:0.6 c03.mp4 fadeblack:0.5 c04.mp4 fadeblack:1.0 c99.mp4
```

The film is the sum of the clips minus every transition (a tenth of a second more than expected is
normal). Keep transitions shorter than the shorter of the two clips they join.

## 9b. Join with hard cuts

Use 9a or 9b, not both: each writes `film.mp4`. This works because step 6 made every clip
identical in format:

```sh
printf "file '%s'\n" c01t.mp4 c02.mp4 c03.mp4 c99.mp4 > cuts.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i cuts.txt -c copy cuts-raw.mp4
ffmpeg -loglevel error -y -i cuts-raw.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart film.mp4
```

When no clip has sound and none is wanted (a silent showreel), make a file with no audio track in
place of the last command, so players do not show a sound control for nothing:

```sh
ffmpeg -loglevel error -y -i cuts-raw.mp4 -c:v copy -an -movflags +faststart film.mp4
```

## 10. Check the cut

```sh
ffprobe -v error -show_entries format=duration -of csv=p=0 film.mp4
ffmpeg -hide_banner -nostats -i film.mp4 -af ebur128=framelog=quiet -f null - 2>&1 | grep -E " I:"
ffmpeg -hide_banner -nostats -i film.mp4 -af silencedetect=noise=-45dB:d=1 -f null - 2>&1 | grep -E "silence_(start|end)" || echo "no silent gaps"
ffmpeg -loglevel error -y -i film.mp4 \
  -vf "fps=1/5,scale=384:216:force_original_aspect_ratio=decrease,pad=384:216:-1:-1:color=black,tile=4x3" \
  -frames:v 1 final-sheet.jpg
```

Integrated loudness should land near -16 LUFS (or the target you set in reel edit R4); long quiet
stretches pull it lower. A silent gap you did not plan means a shot lost its sound: fix it with a
bed (steps 5 and 7) and cut again. Look at the sheet before handing over.

A film made of silent clips with a silent track (no sound bed, no music) reads as silent from start
to end, near -70 LUFS: that is expected, not a fault. A file made with `-an` has no audio to
measure; run only the length and sheet lines on it.

If the loudness lands more than 1 LU from the target, measure it and apply the measurement in a
second pass, which lands within a fraction of a unit. `LUFS` is the target, -16 unless you set
another (reel edit R4):

```sh
eval "$(ffmpeg -hide_banner -nostats -i film.mp4 -af loudnorm=I=${LUFS:--16}:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 \
  | awk -F'"' '/"(input_i|input_tp|input_lra|input_thresh|target_offset)"/ { printf "%s=%s\n", $2, $4 }')"
ffmpeg -loglevel error -y -i film.mp4 -c:v copy -af \
  "loudnorm=I=${LUFS:--16}:TP=-1.5:LRA=11:measured_I=${input_i}:measured_TP=${input_tp}:measured_LRA=${input_lra}:measured_thresh=${input_thresh}:offset=${target_offset}:linear=true" \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart film-level.mp4 && mv film-level.mp4 film.mp4
```

## 11. A smaller copy for phones and messaging, or for a web page

```sh
ffmpeg -loglevel error -y -i film.mp4 -c:v libx264 -preset slow -crf 25 -c:a copy -movflags +faststart film-phone.mp4
```

For an even smaller file, halve the size as well: add `-vf "scale=-2:trunc(ih/4)*2"`. Report both
files with their sizes and paths.

A muted web copy, for a clip that plays on a page (a header, a product page), works for one
downloaded clip as well as a film. It starts playing before it has fully loaded:

```sh
ffmpeg -loglevel error -y -i in.mp4 -an -vf "scale='min(1280,iw)':-2" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart web.mp4
```
