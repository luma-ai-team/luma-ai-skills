---
name: memory-reel
description: Use when the user has five to ten photos from a trip, a birthday or a family event and wants one short recap video of them. Animates every photo in one shared look, then joins them with transitions and music; without ffmpeg, hands over the clips in order with an edit plan.
title: Turn photos into a memory reel
needs_shell: true
---

# Turn photos into a memory reel

Five to ten photos in; one short recap out: each photo gently brought to life in one shared look,
in the user's order, joined with soft transitions, a title and a music bed. Joining needs ffmpeg on
the user's machine; without it the user gets every clip in order with an edit plan for their own
video app. Read [the tool cheat sheet](../_shared/luma-tools.md) first.

## 1. Check the finish before anything else

Run `ffmpeg -version` and `python3 -c "import PIL"`.

- **ffmpeg present**: you will deliver one reel file, plus a smaller copy for phones.
- **No shell or no ffmpeg**: tell the user now that you will make one
  clip per photo and hand them over in order with an edit plan, and that the joining, the music and
  the title happen in the app they edit or post with. Then carry on.

## 2. Ask only for what is missing, in one message

The photos are the one thing only the user can give. Ask for them when the brief has no way to
reach them; for everything else, pick a default, state your picks in one line, and go ahead.

- **The photos, and how they reach Luma.** Luma cannot read files attached to the chat. Ask for a
  direct https link to each image file, the paths of files on this computer (only with a shell), or
  their Luma pictures. If they attached photos, say plainly that you cannot pass them to Luma from
  the chat.
- **The occasion and the mood**: a birthday, a trip, a wedding; joyful, calm, nostalgic. From the
  brief, otherwise warm and gentle.
- **The order**: as given, or a story order you propose (arrival, the day, the evening) when the
  brief asks for one.
- **The shape and where it goes**: vertical for a phone status, story or reel, landscape for a TV
  or a laptop, and any length limit of the place they will post it. When the brief does not say,
  vertical.
- **Music**: a song file they have the right to use (with a shell), when the brief gives one.
  Otherwise the reel is left ready for their own song, and you say in one line that a quiet
  ambient bed ([reel edit R5](references/reel-edit.md)) can go under it; these tools do not make
  songs. If they want silence, or a song added later in their app, skip it.
- **Words**: a title for the start (such as a place and a date) and an end line, when the brief
  gives them; otherwise none.
- **Rights**: the photos must be theirs or ones they may use, and the people in them must have
  agreed. Say so in one line.

## 3. Bring the photos in

- **Links**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`, one photo per call,
  one after another. Each answer has a ready `upload_id`.
- **Files here, with a shell**: `upload_media` `{"action": "start", "content_type": "<its MIME
  type, from file --mime-type -b <file>>", "size": <bytes from wc -c>}`, run the `curl -X PUT` from the answer, then
  `{"action": "confirm", "upload_id": "<id>"}`. Finish each photo before starting the next: an
  account can have only three uploads in progress, and a fourth `start` is refused with "You
  already have 3 uploads in progress".
- **Luma pictures**: `list_generations` `{"kind": "image"}` and their `generation_id`s.

Keep a manifest as you go (with a shell, `reel.md` in the project folder): position, what the
photo shows, portrait or landscape or square, and its `upload_id`. Look at each photo if you can:
who is in it, faces, how it is framed. If you cannot see them, ask for one line per photo.

Phone photos can carry a rotate flag, so `ffprobe` shows the stored pixels, not the upright
picture. Read the true shape with
`python3 -c "from PIL import Image, ImageOps; print(ImageOps.exif_transpose(Image.open('p01.jpg')).size)"`.
Luma applies the flag itself.

## 4. Choose one look for the whole reel

A reel feels like one piece when every clip moves the same way. Use the natural look unless the
brief asks for accents or an illustrated look, and name the look in the plan line:

| Look | How | Generations |
|---|---|---|
| **Natural** (default) | Every photo animated with `generate_video` `mode: "image"`, with the same camera move in every prompt | one per photo |
| **Natural with accents** | As natural, plus a one-photo effect (`apply_template` `kind: "effect"`, `input_count` 1) on one or two key photos, all from one `list_templates` category | one per photo (the effect replaces the animation for those photos) |
| **Illustrated** | Every photo first redrawn with the same style key (`generate_image` `mode: "style"`, key from `list_templates` `kind: "style"`), then the styled still animated | two per photo |

- **The motion prompt** names what moves in this photo, then the same camera line every time:
  "Hair and dresses stir in the breeze, the candles flicker, people laugh and lean in a little. Slow
  push-in, gentle and steady." Keep people's motion small; big actions bend faces.
- **The illustrated look** turns faces into the style. Style one photo first and check it
  yourself: when the faces still read as the same people, style the rest; when they do not, stop,
  show it, and offer the natural look instead.
- **Sound**: image-to-video clips are silent; an effect may bring its own soundtrack, which goes
  low under the music. With a shell, one colour grade over the finished reel also helps photos from
  different phones match ([reel edit step R4](references/reel-edit.md)).
- Choose accents and the illustrated style by their `preview_url`. When the brief asks for an
  illustrated look but names no style, show the user three styles with their `preview_url` and let
  them pick: a choice of look only they can make.

## 5. Shape and length

- **Image-to-video takes no `aspect_ratio`**: each clip keeps its photo's shape, and phone photos
  mix portrait and landscape. With ffmpeg, the edit fits each clip into the reel's shape, either
  cropped to fill or whole over a blurred copy of itself ([R2](references/reel-edit.md)). This
  needs no generation and changes nothing in the people.
- **Only if the user wants every clip full-frame without cropping**, first make a still per photo
  in the reel's shape: `generate_image` `mode: "edit"` with `aspect_ratio` and "Same photo, the
  same people with the same faces and clothes, unchanged; extend the scene to fill the frame." An
  edit redraws the whole picture, so faces can change: compare each with the original. It doubles
  the generation count; say so in the plan line. Take the ratio from the `image-edit` row of
  `list_models`, or the `text-to-image` row when that one lists none. The rows are the only check
  on a shape: an unlisted one fails only after the call starts, as a provider refusal that returns
  the credits.
- **Length**: use one `image-to-video` duration from `list_models` for every clip (a recap moves
  quickly, so the shortest listed usually fits). The reel is the clips' sum minus the transitions,
  and clips can be trimmed in the edit. Say the length that gives in the plan line. For a status
  or a story keep it short: trim each clip in the edit (`norm ... <seconds>`) and check the app's
  current limit.

## 6. Plan in one line

1. `get_account` (consent). `list_models` `{"feature": "image-to-video"}`, plus `image-edit` if you
   reshape the photos.
2. Say the plan in one line: the look, how many clips, how many effects, how many stills, and the
   reel's length.
3. Then make the clips. See "Credits and account status" in the cheat sheet.

## 7. Make the clips

Keys: `<reel>-<run>-p<nn>-<what>`, such as `lisbon-reel-k7f2-p03-animate`, where `<run>` is four
random characters chosen once for this reel (see the cheat sheet); a retake is `...-t2`.

```
generate_video {"mode": "image", "image": {"upload_id": "<photo 3>"}, "prompt": "<what moves>. Slow push-in, gentle and steady.",
  "model": "<from list_models>", "duration": <the clip duration you chose>, "client_request_id": "lisbon-reel-k7f2-p03-animate"}
apply_template {"kind": "effect", "key": "<key>", "images": [{"upload_id": "<photo 5>"}], "client_request_id": "lisbon-reel-k7f2-p05-fx"}
generate_image {"mode": "style", "image": {"upload_id": "<photo 3>"}, "style": "<key>", "client_request_id": "lisbon-reel-k7f2-p03-style"}
```

- Stills first (illustrated or reshaped): wait for each `media_url`, check it, then animate the
  still instead of the photo, `"image": {"generation_id": "<the still>"}`.
- Start clips in batches of about five, then poll each with `get_generation` (`wait_seconds` up
  to 25) until `poll_after_seconds` is null. Ten generation calls in one burst can hit "Too many
  requests"; wait the seconds it names and retry that call with the same key.
- Fill the manifest with each clip's `generation_id` as it arrives. Do not narrate the polling.

## 8. Check every clip

- With ffmpeg: download each clip as soon as its link arrives (links last one hour), named by
  position (`s01.mp4`, `s02.mp4`), and make a contact sheet of first and last frames
  ([ffmpeg steps 2 and 3](../short-film/references/ffmpeg.md)). Look at it yourself first.
- Look for a face that changed or warped, extra or melted fingers, a person appearing or vanishing,
  motion that fights the photo. A warped face of someone the user loves is worse than no motion.
- For a bad clip, say which and why, and offer a retake with calmer motion (a new key), made when
  the user asks, or, with a shell, the photo itself with a slow zoom, which needs no generation
  ([R3](references/reel-edit.md)).

## 9. Cut the reel (with ffmpeg)

Follow [the ffmpeg reference](../short-film/references/ffmpeg.md) and
[the reel edit steps](references/reel-edit.md) in this order:

1. Check the tools (ffmpeg step 1), then size and frame rate for the reel's shape (R1: ffmpeg
   step 4 with `R` set to the reel's shape).
2. Normalise each clip to its planned seconds (ffmpeg step 6). Look at each under the plain crop
   first; move the crop or fit the whole picture where the crop cuts a face (R2). An effect's own
   soundtrack goes low or silent.
3. The title over the first clip and a silent end card, with the user's words (ffmpeg step 8).
4. Join with soft crossfades such as `fade` or `dissolve` (ffmpeg step 9a) into `reel-cut.mp4`.
5. One grade and the music, or the quiet ambient bed, under the whole reel (R4, R5).
6. Check the length, loudness and a contact sheet (ffmpeg step 10), then the phone copy (step 11).
   For a reel going to Instagram or TikTok, set `LUFS=-14` in R4 and add the posting copies and
   the cover frame from [the social finish](../_shared/social-finish.md) (F7, F8).

Hand over: the paths of both files, the running time, and the manifest with every
`generation_id`. Offer changes: a new order, title, transition or song is only a re-cut; a new
clip is a new job with a new key, made when the user asks.

## 10. Without a shell: the edit plan

Say plainly that the reel is not joined here, then deliver, in reel order:

| # | Photo | Clip | generation_id | Link (valid one hour) | Use from/to | Transition into the next |
|---|---|---|---|---|---|---|

Then the title and end card text with where they go, and the music: their song under the whole
reel, starting on the first clip and fading out on the last. Tell them to download the clips now,
and that `get_generation` or `list_generations` gives fresh links later.

## When something goes wrong

- **"You already have 3 uploads in progress"**: confirm or finish the pending uploads before the
  next `start`. **"Upload limit reached. Try again in an hour."**: stop and tell the user; the
  photos already uploaded stay usable.
- **A link is refused**: a web page instead of the file needs the direct link; a file too big for
  `from_url` needs a shell and `action: "start"`.
- **Moderation refused a photo or a prompt**: final for that input. Tell the user which photo; the
  reel goes on without it. Do not crop, edit or reword to get it through.
- **Credits run out midway** (`insufficient_credits`): stop and do not retry. Hand over the clips
  made so far (ids and links), say once that the balance does not cover the rest, give the account
  link from the refusal, and list the photos still to animate. Offer a shorter reel from fewer
  photos. Resume later from the manifest or `list_generations`.
- **A clip failed**: read `error.message`, `retryable` and `refunded`. When `retryable` is true, run
  it once more as a new job with a new key, and tell the user only if that one fails too.
- **A session dropped**: `list_generations` `{"kind": "video"}` and match the prompts to the
  manifest.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
