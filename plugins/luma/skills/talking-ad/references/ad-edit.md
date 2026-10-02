# Cutting the talking ad with ffmpeg

The ad's edit: the talking clip is the spine and its voice never stops, product shots cover it on
the lines marked for a cutaway, captions run under the face, the ask comes up on screen at the end,
and music sits under it all. It uses [the short-film ffmpeg reference](../../short-film/references/ffmpeg.md)
(steps 1 to 4, and `title.py` from step 8) and [the social finish](../../_shared/social-finish.md).
Run it in one project folder, in bash or zsh. Numbers shown (seconds, positions, volumes) are edit
choices, not catalog values.

## A1. Lay down the spine

Download the talking clip as `s01.mp4` (or `s01.mp4`, `s02.mp4` for a voice split in parts) and the
product shots as `b01.mp4`, `b02.mp4` in script order. Run film step 4 with `R=vertical` (or the
ad's shape); it sets `W`, `H`, `FPS`, `V`, `A` and `norm`. Step 4 sizes the frame from the
talking clip; a lip-sync clip is usually 720 wide, so the ad is 720x1280, which every app takes.
For a 1080 ad, enhance the talking clip first (`edit_video` `mode: "enhance"`), a new job made when
the user asks. Then normalise the talking clip at its
own length, which keeps its voice:

```sh
L=$(ffprobe -v error -select_streams v:0 -show_entries stream=duration -of csv=p=0 s01.mp4)
norm s01.mp4 talk.mp4 "$L"
```

For a voice in parts, normalise each the same way and join them with hard cuts (film step 9b, its
first two lines only, writing `talk.mp4`): the cut lands on the sentence break where the voice was
split.

Check that the talking clip starts where the voice starts: compare the first speech in
`silencedetect` on `talk.mp4` and on `voice.wav`, which should agree within a few frames. A clip a
little longer than the voice ends on the face at rest; trim it with `-t` at the voice's length
plus half a second. A clip a few frames shorter than the voice is fine: the edit follows the
clip, and the loudness and copy steps end the audio with it.

## A2. Find when each line is said

The captions and the cutaways both hang on when words are said. Transcribe the voice once, as
[social finish F3](../../_shared/social-finish.md) shows (`whisper` or `mlx_whisper`, writing
`voice.json`), then print each word with its start:

```sh
python3 -c "
import json
for s in json.load(open('voice.json'))['segments']:
    for w in s.get('words', []): print(f\"{w['start']:6.2f} {w['word'].strip()}\")"
```

Without a transcriber, find the pauses with `silencedetect` (film step 5) and count sentences: each
pause longer than a third of a second is usually a full stop.

## A3. Cut to the product while the voice runs on

List each cutaway as file, the second it starts on the ad's timeline, how long it holds, and the
second of the product shot to start from. It starts at the A2 start of its line's first word and
holds until the end of that line's last word plus a tenth of a second; the in-point picks the part
of the shot with the action (a hand reaching in may only arrive two seconds in). Never cover the
hook: the first two seconds show the face.

```sh
CUTS=("b01.mp4 2.6 1.9 0" "b02.mp4 4.8 1.6 2.0")   # file, start (s), length (s), from (s)
INPUTS=(-i talk.mp4); G=""; LAST="[0:v]"; n=1
for c in "${CUTS[@]}"; do set -- $(echo $c)
  INPUTS+=(-i "$1")
  G+="[${n}:v]trim=start=$4:duration=$3,setpts=PTS-STARTPTS+$2/TB,${V}[b${n}];${LAST}[b${n}]overlay=eof_action=pass:enable='between(t,$2,$2+$3)'[v${n}];"
  LAST="[v${n}]"; n=$((n+1))
done
G+="${LAST}format=yuv420p[v]"
ffmpeg -loglevel error -y "${INPUTS[@]}" -filter_complex "$G" -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 17 -c:a copy ad-cut.mp4
```

The voice is the talking clip's own, untouched; only the picture changes. A product shot shorter
than its line leaves the face showing for the rest of the line, which is fine. Look at a frame in
the middle of each cutaway and one just after it.

## A4. Captions, then the ask on screen

`S` is the A2 start of the ask line's first word. Burn the captions in with
[social finish F3](../../_shared/social-finish.md) on `ad-cut.mp4`, from `voice.json` with
`--end=$S`, so they stop where the ask comes up on screen instead of repeating it, writing
`ad-cap.mp4`. One height serves the face and the product shots: `--at=0.74` sits under the chin
and below most products. Look at a caption frame inside each cutaway; if a line covers the
product, lower it to `--at=0.78`.

The ask goes on screen over the last line, high in the frame so it does not fight the captions,
and narrower than the frame so it stays clear of the app's right-hand buttons: it is rendered at
seven eighths of the width and laid on the left. `E` is the end of the ad:

```sh
S=7.4; E=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ad-cut.mp4)
python3 title.py "$((W * 7 / 8))" "$H" ask.png "Tap the link" "Pick your colour" --at=0.16
ffmpeg -loglevel error -y -i ad-cap.mp4 -loop 1 -t "$E" -i ask.png -filter_complex \
  "[1:v]format=rgba,fade=t=in:st=${S}:d=0.3:alpha=1[t];[0:v][t]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset medium -crf 17 -c:a copy ad-ask.mp4
```

Use the user's exact ask and offer; never add a discount, a deadline or a claim they did not give.

## A5. Sound, loudness and the copies

In the social finish's order:

1. The music under the voice, ducked ([social finish F5](../../_shared/social-finish.md)), with
   `IN=ad-ask.mp4; OUTFILE=cut-music.mp4`. With no music, `cp ad-ask.mp4 cut-music.mp4`.
2. A whoosh a quarter second before each cutaway starts, nothing else: the voice is the show
   ([F6](../../_shared/social-finish.md), on `cut-music.mp4`, writing `master-vertical.mp4`). Place
   it in a pause, never over a word; when a cutaway starts mid-sentence, leave its whoosh out.
3. The loudness, the posting copies, the silent copy and the cover
   ([F7](../../_shared/social-finish.md)), then the checks ([F8](../../_shared/social-finish.md)),
   with one more: the mouth against the words at three word times spread over the ad (lips shut on
   an "m", open on a long vowel). A drift that grows towards the end means the clip and the voice
   differ in length; trim to the voice (A1).

The captions as text, for an editing app, are `caps/captions.srt`: the same lines as the burned
ones. Hand it over with the ad.
