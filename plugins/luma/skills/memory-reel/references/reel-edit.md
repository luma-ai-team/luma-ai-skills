# Cutting the memory reel with ffmpeg

The reel uses [the short-film ffmpeg reference](../../short-film/references/ffmpeg.md) for
everything it shares with a film: checking the tools (step 1), downloading and probing (step 2),
contact sheets (step 3), the `norm` helper (step 4), normalising (step 6), titles (step 8), the
crossfade join (step 9a), the checks (step 10) and the phone copy (step 11). This page adds the
five things a reel of phone photos needs on top. Run it in the same project folder, in bash or
zsh. Numbers shown as examples (seconds, blur, grade, volumes) are edit choices, not catalog
values.

Name the downloaded clips by reel position so they sort: `s01.mp4`, `s02.mp4`, and so on.

## R1. The reel's size and frame rate

Run film step 4 with `R=vertical` for a phone reel, story or status, or `R=landscape` for a TV or a
laptop. The frame comes from that shape, whatever mix of portrait, landscape and square photos went
in, and `V` is built on it: a reel for a phone gets the tall frame phone feeds want even when every
photo is landscape. Step 4 picks the short side `S` itself; image-to-video clips are about one
megapixel, so a reel usually lands on 720. Set `S=720` by hand before step 4's `read` line only
when one sharper clip (an effect, say) pushed the frame to 1080 and you want the smaller file.
Define `V`, `A` and `FIT` (R2) only after `W` and `H` are final.

## R2. Fit a clip of the other orientation

Step 4's `V` crops every clip to fill the frame, which cuts the sides off a landscape photo in a
vertical reel (and heads off a portrait photo in a landscape one). `FIT` keeps the whole picture
and fills the rest of the frame with a soft, blurred copy of it. Define it after R1 and step 4,
once `W` and `H` are final:

```sh
FIT="split[fg0][bg0];[bg0]scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},boxblur=30:2[bg];[fg0]scale=${W}:${H}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=${FPS},format=yuv420p"
```

Look at a middle frame of each clip under the plain crop before choosing:

```sh
ffmpeg -loglevel error -y -ss 2 -i s04.mp4 -frames:v 1 -vf "${V}" crop-check.jpg
```

Use `FIT` only when the crop would cut off a face or the whole width matters. When the subject is
off centre, move the crop instead of fitting: `CX` and `CY` place it (0 is the left or top edge, 1
the right or bottom, 0.5 the centre).

Use either for one clip by setting `V` in front of the call. The change lasts for that call only, in
bash and in zsh:

```sh
norm s01.mp4 c01.mp4 4                            # already the reel's shape: crop to fill
V="$FIT" norm s02.mp4 c02.mp4 4                   # other orientation: whole photo over a blurred fill
V="$FIT" norm s03.mp4 c03.mp4 4 s03.mp4 "volume=0.3"   # an effect clip, its own soundtrack kept low
CX=0.75; CY=0.5
V="scale=${W}:${H}:force_original_aspect_ratio=increase:flags=lanczos,crop=${W}:${H}:(iw-${W})*${CX}:(ih-${H})*${CY},setsar=1,fps=${FPS},format=yuv420p" norm s04.mp4 c04.mp4 4
```

Look at the first frame of each fitted clip: a crop that cuts a face off is the reason to fit
instead.

## R3. A photo that should not move

When a clip warped a face, or the user wants one photo kept exactly as it is, turn the photo
itself into a clip with a slow zoom. It costs nothing and changes nothing in the picture. Download
the photo first (`curl -sSL -o p04.jpg "<link>"`, or the file the user gave; on a Mac, convert a
HEIC photo with `sips -s format jpeg p04.heic --out p04.jpg`).

```sh
SECS=4
FRAMES=$(awk -v s="$SECS" -v f="$FPS" 'BEGIN { n = split(f, r, "/"); printf "%d", s * r[1] / (n > 1 ? r[2] : 1) + 0.999 }')
ffmpeg -loglevel error -y -i p04.jpg -vf "scale=${W}:${H}:force_original_aspect_ratio=increase,crop=${W}:${H},scale=$((W*4)):$((H*4))" -frames:v 1 p04-big.png
ffmpeg -loglevel error -y -i p04-big.png -vf "zoompan=z='min(zoom+0.0006,1.08)':d=${FRAMES}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=${W}x${H}:fps=${FPS},format=yuv420p" \
  -c:v libx264 -preset medium -crf 17 s04.mp4
norm s04.mp4 c04.mp4 "$SECS"
```

The first command crops the photo to the reel's shape. To keep a photo of the other orientation
whole, run this in its place (R2's `FIT` defined), then the zoom and `norm` as above:

```sh
ffmpeg -loglevel error -y -i p04.jpg -filter_complex "[0:v]${FIT},scale=$((W*4)):$((H*4))" -frames:v 1 p04-big.png
```

The four-times upscale keeps the zoom smooth.

## R4. One grade and one music bed over the whole reel

Join the normalised clips first with film step 9a, writing `reel-cut.mp4` (soft `fade` or
`dissolve` transitions suit a reel). Make the end card silent (the step 8 variant with
`anullsrc`), because the music runs under it.

Then lay the music under the whole reel, fading in at the start and out over the last seconds,
looped if the song is shorter than the reel, mixed over any sound the clips kept. The same pass
applies one colour grade to every clip, which makes photos from different phones feel like one
set:

```sh
IN=reel-cut.mp4; OUTFILE=reel.mp4; MUSIC=music.mp3
GRADE="eq=contrast=1.04:saturation=1.08"          # keep it subtle; "null" for no grade
LUFS=-16                                          # -20 or lower for a quiet ambient bed (R5)
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
FADE_AT=$(awk -v d="$D" 'BEGIN { printf "%.2f", d - 3 }')
ffmpeg -loglevel error -y -i "$IN" -stream_loop -1 -i "$MUSIC" -filter_complex \
  "[0:v]${GRADE},format=yuv420p[v];[1:a]${A},atrim=0:${D},afade=t=in:d=1,afade=t=out:st=${FADE_AT}:d=3[m];[0:a]${A},volume=0.4[o];[m][o]amix=inputs=2:normalize=0:duration=first,loudnorm=I=${LUFS}:TP=-1.5:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUTFILE"
```

The short film uses the same step for a user's own song: `IN=film.mp4`, `OUTFILE=film-music.mp4`,
`GRADE=null`.

- `volume=0.4` is the clips' own sound under the music; `0` mutes it.
- `IN` must have an audio track (a silent one is enough): film step 6 gives every normalised clip
  one. A file with none, such as a single image-to-video or restyled clip straight from Luma, goes
  through film steps 4 and 6 first, or this step fails with "matches no streams".
- For a warmer look add `,colorbalance=rs=0.03:bs=-0.03` to `GRADE`.
- Use only music the user has the right to use. With no music file and no wish for sound, skip
  this step and rename `reel-cut.mp4` to `reel.mp4`; the reel carries whatever sound the clips
  have. With no music file but a wish for a soft sound, make the bed in R5 and run this step with
  `MUSIC=music.wav` and a lower `LUFS`.

Then run film step 10 on `reel.mp4` (length, loudness, contact sheet) and step 11 for the phone
copy.

## R5. A quiet ambient bed, when there is no music

When the user has no song but wants something soft under the reel, synthesise a slow drone: a few
sine voices of one chord, each breathing at its own slow rate, over filtered pink noise, with a
little echo and width. It is a soft drone, not a song: say so to the user. Make it a little longer
than the reel (R4 loops it otherwise), then run R4 with `MUSIC=music.wav`:

```sh
BEDLEN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 reel-cut.mp4 | awk '{ print int($1) + 2 }')
ffmpeg -loglevel error -y \
  -f lavfi -i "sine=f=146.83:d=${BEDLEN}" -f lavfi -i "sine=f=147.4:d=${BEDLEN}" -f lavfi -i "sine=f=220.0:d=${BEDLEN}" \
  -f lavfi -i "sine=f=220.7:d=${BEDLEN}" -f lavfi -i "sine=f=293.66:d=${BEDLEN}" -f lavfi -i "sine=f=369.99:d=${BEDLEN}" \
  -f lavfi -i "sine=f=659.25:d=${BEDLEN}" -f lavfi -i "anoisesrc=color=pink:amplitude=0.05:d=${BEDLEN}:r=48000" \
  -filter_complex "[0]volume=0.5,tremolo=f=0.11:d=0.35[a0];[1]volume=0.4,tremolo=f=0.13:d=0.35[a1];[2]volume=0.4,tremolo=f=0.1:d=0.4[a2];[3]volume=0.3,tremolo=f=0.12:d=0.4[a3];[4]volume=0.25,tremolo=f=0.17:d=0.5[a4];[5]volume=0.18,tremolo=f=0.14:d=0.5[a5];[6]volume=0.05,tremolo=f=0.2:d=0.6[a6];[7]lowpass=f=700,highpass=f=120,volume=0.5[n];[a0][a1][a2][a3][a4][a5][a6][n]amix=inputs=8:normalize=0,lowpass=f=1400,aecho=0.8:0.6:180|360:0.35|0.22,aresample=48000,aformat=channel_layouts=stereo,stereotools=mlev=1:slev=1.6[o]" \
  -map "[o]" -c:a pcm_s16le music.wav
```

`tremolo` refuses a rate under 0.1 Hz; keep every `f=` at 0.1 or above.
