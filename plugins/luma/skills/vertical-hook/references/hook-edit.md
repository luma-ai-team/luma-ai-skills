# Finishing a hook clip with ffmpeg

Commands for the vertical-hook finish: words on screen, a copy for posting, the loop's seam check
and the mirror loop, which needs no new generation. They build on
[the short-film ffmpeg reference](../../short-film/references/ffmpeg.md) and use its `title.py`
(step 8). Run them in one project folder, in bash or zsh. Numbers shown
(seconds, fades, positions) are edit choices, not catalog values.

## H1. Words on screen, and a copy for posting

Copy the clip to `s01.mp4`, run film step 4 with `R=vertical` (it sets `W`, `H`, `V` and `A` and
defines `norm`), then normalise it at its exact length, so a loop keeps its last frame:

```sh
L=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 s01.mp4)
norm s01.mp4 c01.mp4 "$L"
```

A hook's words come in fast and leave early: in from 0.3 s over half a second, out over one second
so they are gone one second before the clip ends. The overlay input runs for the clip's length. On
a loop keep both fades, so the first and last frames carry no words and the seam stays clean:

```sh
python3 title.py "$W" "$H" hook_words.png "THE HOOK LINE"
OUT_AT=$(awk -v l="$L" 'BEGIN { printf "%.2f", l - 2 }')
ffmpeg -loglevel error -y -i c01.mp4 -loop 1 -t "$L" -i hook_words.png -filter_complex \
  "[1:v]format=rgba,fade=t=in:st=0.3:d=0.5:alpha=1,fade=t=out:st=${OUT_AT}:d=1:alpha=1[t];[0:v][t]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map "0:a?" -c:v libx264 -preset medium -crf 17 -c:a copy c01t.mp4
ffmpeg -loglevel error -y -ss "$(awk -v l="$L" 'BEGIN { print l / 2 }')" -i c01t.mp4 -frames:v 1 words-check.jpg
```

Look at `words-check.jpg`. The feed covers the top and bottom edges and the right side with its
own buttons and captions, so the words belong in the middle band, clear of the subject. If they
sit over the hook, render the PNG again with `--at=0.15` (higher) or `--at=0.60` (lower).

Most creators add the sound in the posting app. For that, a copy with no audio track, small
enough to send to a phone:

```sh
ffmpeg -loglevel error -y -i c01t.mp4 -an -c:v libx264 -preset slow -crf 25 -movflags +faststart hook-post.mp4
```

With sound made with the clip, use film step 11's phone copy instead, which keeps it.

## H2. Check a loop's seam

Copy the loop (the frames clip, or H3's `hook-v1-loop.mp4`) to `hook-loop.mp4`. Put the last frame
beside the first, measure how alike they are, measure two neighbouring frames
from the middle of the clip for comparison, and make a copy that plays three times in a row:

```sh
ffmpeg -loglevel error -y -i hook-loop.mp4 -frames:v 1 seam-first.png
ffmpeg -loglevel error -y -sseof -0.1 -i hook-loop.mp4 -update 1 seam-last.png
ffmpeg -loglevel error -y -i seam-last.png -i seam-first.png -filter_complex "[0:v][1:v]hstack=inputs=2,scale=-2:480" seam.jpg
ffmpeg -hide_banner -nostats -i seam-last.png -i seam-first.png -lavfi ssim -f null - 2>&1 | grep -o 'All:[0-9.]*'
MID=$(ffprobe -v error -show_entries format=duration -of csv=p=0 hook-loop.mp4 | awk '{ print $1 / 2 }')
ffmpeg -loglevel error -y -ss "$MID" -i hook-loop.mp4 -frames:v 2 mid-%d.png
ffmpeg -hide_banner -nostats -i mid-1.png -i mid-2.png -lavfi ssim -f null - 2>&1 | grep -o 'All:[0-9.]*'
ffmpeg -loglevel error -y -stream_loop 2 -i hook-loop.mp4 -c copy hook-loop-x3.mp4
```

The seam (the first `All:` number, 1 means identical) should score about as high as the two
neighbouring frames (the second) or higher; clearly lower is a jump the eye will catch. Then watch
`seam.jpg` and the three-times copy: the numbers do not see a colour shift or an object that pops.

## H3. The mirror loop (no new generation)

The clip forward, then backward, with no seam by construction. The backward half drops its first
and last frames, which are the same frames the forward half ends and starts on, so it plays
without a stall at the turnaround or at the wrap. `reverse` holds the whole clip in memory, which
is fine for a hook of a few seconds:

```sh
N=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of csv=p=0 hook-v1.mp4)
ffmpeg -loglevel error -y -i hook-v1.mp4 -filter_complex \
  "[0:v]split[fw][bw0];[bw0]reverse,trim=start_frame=1:end_frame=$((N - 1)),setpts=PTS-STARTPTS[bw];[fw][bw]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -preset medium -crf 18 -movflags +faststart hook-v1-loop.mp4
```

It suits a camera push or drift and slow ambient motion (hair, water, smoke, light). Anything with
a visible cause and effect reads as a rewind: steam sinking back into bread, a tear that mends, a
pour, a step, speech. Prefer the variant whose motion is camera-led, and watch the backward half
before offering it.
