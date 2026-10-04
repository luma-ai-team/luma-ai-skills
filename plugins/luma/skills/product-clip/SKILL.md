---
name: product-clip
description: Use when the user wants short clips of a product for a shop, an ad or social media, from a photo of the product, or a product video changed for a season or a scene. Cleans the photo up, makes motion treatments in vertical and square, and can restage a clip.
title: Make a product clip
needs_shell: false
---

# Make a product clip

A product photo in; a small set of short clips out. First a clean still of the product (background,
light and clutter fixed with an image edit), one per shape, then a few motion treatments of each
still in vertical and square. Read [the tool cheat sheet](../_shared/luma-tools.md) first.

## The accuracy rule

The product in every still and every clip must be the product the user sells: the same shape,
colours, proportions, label and logo. Image edits can change small print, logos and colours, and a
turning product can warp its label. Check every result against the original photo and retake or
drop anything that changed the product. Never add text, features or claims the real product does
not have.

## 1. Ask only for what is missing, in one message

The product photo is the one thing only the user can give. Ask for it when the brief has no way to
reach it; for everything else, pick a default, state your picks in one line with the plan, and go
ahead.

- **The photo, and how it reaches Luma.** Luma cannot read a file attached to the chat. Ask for a
  direct https link to the image file, the path of a file on this computer (only with a shell), or
  one of their Luma pictures. It must be their own photo of the product, or one they may use.
- **What the product is**, and the one thing the clips must show (the label, the texture, the
  size). From the brief and the photo.
- **Where the clips will run**, which decides the shapes: vertical, square, or both (default both).
- **The setting**: a plain studio background (which colour), a scene (a kitchen counter, a desk,
  outdoors), or the original background tidied up. From the brief, otherwise a plain studio
  background in a soft neutral colour.
- **Brand colours**, if the brief gives any.
- **How many treatments**: the number the brief gives, otherwise three.
- **A video they already have**: a product clip of theirs (an `upload_id` from `upload_media`, or
  one of their Luma videos) can skip the stills and go straight to step 7b to be restaged for a
  season, a scene or a colourway.

Say up front that the clips come out silent. With a shell, music the user has the right to use
can go on afterwards, over a showreel per shape (step 8).

## 2. Bring the photo in

- **A link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`.
- **A file here, with a shell**: `upload_media` `{"action": "start", "content_type": "<its MIME
  type, from file --mime-type -b <file>>", "size": <bytes from wc -c>}`, run the `curl -X PUT` from
  the answer, then `{"action": "confirm", "upload_id": "<id>"}`.
- **A Luma picture**: `list_generations` `{"kind": "image"}` and its `generation_id`.

## 3. Read the catalog

- `get_account` for consent.
- `list_models` `{"feature": "image-edit"}`: pick the vertical and the square value from the
  row's `aspect_ratios`. If that row lists none, take them from the `text-to-image` row.
  The rows are the only check on a shape: a value no row lists fails only after the call starts,
  as a provider refusal that returns the credits. Never use a ratio that is listed nowhere.
- `list_models` `{"feature": "image-to-video"}`: models and durations; `{"feature": "frames"}` too
  if a Reveal is planned.
- Optional: `list_templates` `{"kind": "effect"}`, find a category aimed at products or ads in
  `categories`, then list that category with `category`. A one-photo effect (`input_count` 1) can
  be an extra treatment when the brief asks for an effect; judge it by its `preview_url`, a free
  sample.

Image-to-video takes no `aspect_ratio`: each clip takes the shape of its still. That is why the
stills are made once per shape.

When every shape must show the same motion (one ad set across feeds), there is a second route:
animate the stills of one shape only, then turn each checked clip into the other shape with
`edit_video` `mode: "reframe"`, which redraws the clip in the new shape instead of cutting it. Read
`list_models` `{"feature": "reframe"}` for its `aspect_ratios` and `source_limits`. Reframe takes
no prompt, keeps the clip at its own size and invents the rest of the new shape: from vertical to
square that is the sides, and on a plain studio background it tends to add props (in testing, a
vase of flowers and a ledge). For a studio look, keep the default route. Say which route you took in the plan line,
and check the reframed edges for anything added as well as for the product itself.

## 4. Plan the treatments

Choose the treatments that fit the product, as many as step 1 settled, and name them in the
plan line:

| Treatment | Motion prompt to adapt |
|---|---|
| Slow turn | "The camera orbits slowly around the product; soft reflections move across its surface." See the note below. |
| Push-in with light | "Slow push-in toward the product while a soft band of light sweeps across it." The push-in enlarges the product, so its still needs wide side margins (step 6). |
| Float | "The product lifts a little and floats, turning gently, a soft shadow below it." |
| In use | "A hand enters the frame and picks up the product." Hands can come out wrong; check. |
| Reveal | One edit of the checked still (for example a close-up, or the product open) as one end and the checked still as the other, joined with `generate_video` `mode: "frames"`. Ending on the checked still lands the clip on the same framing as the others. |

A turn shows sides the photo never showed, so the far side is invented (a rim colour can drop out,
a handle can move). Choose Slow turn only for a product that looks the same all round, tell the
user the back is generated, and check the last frames against the photo. Otherwise prefer Push-in
or Reveal.

## 5. Plan in one line, then run

- `get_account` (consent) if not read in step 3.
- Say the plan in one line with its count: one still per shape, plus treatments times shapes. For
  two shapes and three treatments that is two stills and six clips. A Reveal adds one edit and one
  `frames` clip per shape; an effect adds one `apply_template` per shape. On the reframe route it
  is one still, the treatments, and one reframe per treatment per extra shape.
- Then run it: the clean stills, your check of them, then the clips, without stopping between. See "Credits and account status" in the cheat sheet.

## 6. Make the clean stills

```
generate_image {"mode": "edit", "image": {"upload_id": "<id>"},   # or {"generation_id": "<id>"} for a Luma picture
  "prompt": "The same <product>, unchanged: same shape, colours and proportions, and the same <its label, logo, pattern or handle: name each visible feature>. <setting>. Soft studio light from <side>. The whole product in frame, centred, with space around it.",
  "aspect_ratio": "<the vertical value from list_models>", "client_request_id": "<product>-<run>-still-vertical"}
```

Then the same with the square value and `<product>-<run>-still-square`. For a Push-in, ask for
the product to fill no more than half the frame's width: by the end of the move it is half as big
again, and on a vertical feed the right edge is under the app's buttons. `<run>` is four random
characters chosen once for this conversation (see the cheat sheet), such as `k7f2`.

- Wait for each `media_url`, then compare it with the original: label text, logo, colours,
  proportions. Say what changed, if anything. Also compare the two stills with each other: if the
  colour or shape of the product differs between them, say so and offer a retake of the weaker one
  (a new key); make it when the user asks.
- If the new shape cuts the product off, do not animate that still: say so and offer a retake with
  the "whole product in frame" line stressed (a new key), made when the user asks; if that fails
  too, offer the shape that works. Whether an edit with a different `aspect_ratio` reframes the
  product cleanly depends on the photo; check, do not assume.
- Show the stills that pass, then animate them straight away. A still that changed the product is
  not animated.

## 7. Animate

```
generate_video {"mode": "image", "image": {"generation_id": "<checked still>"}, "prompt": "<treatment>",
  "model": "<from list_models>", "duration": <a listed duration>, "client_request_id": "<product>-<run>-<treatment>-<shape>"}
generate_image {"mode": "edit", "image": {"generation_id": "<checked still>"}, "prompt": "The same <product>, unchanged. <the reveal's other end, such as a close-up>.",
  "aspect_ratio": "<the same value>", "client_request_id": "<product>-<run>-reveal-a-<shape>"}
generate_video {"mode": "frames", "start_image": {"generation_id": "<reveal a>"}, "end_image": {"generation_id": "<checked still>"},
  "prompt": "<the move between them>", "model": "<frames model>", "duration": <a listed duration>, "client_request_id": "<product>-<run>-reveal-<shape>"}
apply_template {"kind": "effect", "key": "<key>", "images": [{"generation_id": "<checked still>"}], "client_request_id": "<product>-<run>-fx-<shape>"}
```

```
edit_video {"mode": "reframe", "video": {"generation_id": "<checked clip>"}, "aspect_ratio": "<the other shape, from list_models feature reframe>",
  "client_request_id": "<product>-<run>-<treatment>-reframe-<shape>"}
```

A Reveal's edit (`reveal-a`) must have its `media_url` before the `frames` call, and a reframe or
a restage (step 7b) starts only once its clip has its `media_url`.
Check the effect clip's shape; it may not follow the still. Start clips in batches of about five,
then poll each with `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is null.
A retake, when the user asks for one, gets a new key (`...-t2`).

## 7b. Restage a clip: a season, a scene, a colourway

When the user wants the same product clip in another setting (a holiday table, a beach, a
night-time version for a campaign, a background in their brand colour), change the finished clip
instead of making a new one: the motion stays, the scene changes. One job per variant, as many as
they ask for:

```
edit_video {"mode": "edit", "video": {"generation_id": "<checked clip>"},
  "prompt": "The same <product>, unchanged: same shape, colours, label and logo, and the same movement. Only the setting changes: <the new scene, its light and colours>.",
  "client_request_id": "<product>-<run>-<treatment>-<variant>"}
```

`model` is optional; read `list_models` `{"feature": "edit"}` for the models and the
`source_limits` the clip must fit. The clip can also be the user's own video, as
`{"upload_id": "..."}`. Hold each variant to the accuracy rule: an edit that redraws the label or
changes a colour of the product is not used. Warm or cool light changes how a colour reads; judge
the product's colour in its own highlights and shadows against the original, and tell the user
when the new light makes it look different, so they decide whether it still sells the right one. Variants that differ only in the setting are what an
ad test needs, so keep everything else the same.

## 8. Check and deliver

- Watch each clip for the product changing as it moves: the label warping, the colour shifting,
  the shape bending. Leave those out of the showreel, say which and why, and offer a retake; make
  it when the user asks.
- **With a shell**: download the clips into one folder per shape (`vertical/`, `square/`), named
  `s01.mp4`, `s02.mp4` in showreel order (links last one hour). Put the Reveal first or last, and
  end it on the framing the next clip starts with. Make one showreel per shape, never one mixing
  shapes: in each folder run [ffmpeg steps 4, 6 and 9b](../short-film/references/ffmpeg.md) with
  `R` set to that shape (`vertical` or `square`), then rename `film.mp4` to
  `<product>-<shape>.mp4`. Clips of one shape still differ in size by route (a `frames` clip is
  larger than an image-to-video one); step 4 sizes them to one frame. Each clip's seconds for step
  6 are its own length (`ffprobe`), trimmed only where it drifts at the end.
- If the user has music they may use, add it over each showreel with
  [reel edit R4](../memory-reel/references/reel-edit.md), in the same shell as step 4, with R4's
  first lines set to `IN=<product>-<shape>.mp4; OUTFILE=<product>-<shape>-music.mp4;
  MUSIC=<their file>`, `GRADE=null` and `LUFS=-14`. For an ad, [the social finish](../_shared/social-finish.md)
  adds what makes it look finished, in its order: copy the music file to `master-<shape>.mp4`,
  then a few sound effects (F6), a cover frame and a silent copy for the shop page (F7), and the
  check of every file (F8), including the safe area (F2).
  If not, deliver the silent showreels as
  they are, made with step 9b's no-audio variant; step 10's loudness and silence checks then have
  nothing to measure, so run only its length and sheet lines.
- **Without a shell**: list the clips grouped by shape: treatment, `media_url`, `generation_id`.
  Say the links expire in an hour and `list_generations` finds them later.
- **For a product page or a paid ad**, offer a sharper copy of the chosen clips with
  `edit_video` `mode: "enhance"` (`resolution` and `frame_rate` from `list_models`
  `{"feature": "upscale"}`, or neither for the default quality); make it when the user asks, a new
  key per clip. Enhance the chosen clips, not every take.

## When something goes wrong

- **The link is refused**: a web page instead of the file needs the direct link; too big for
  `from_url` needs a shell and `action: "start"`.
- **Moderation refused a photo or a prompt**: final for that input. Tell the user; do not reword to
  get around it.
- **A clip failed**: read `error.message`, `retryable` and `refunded`. When `retryable` is true, run
  it once more as a new job with a new key, and tell the user only if that one fails too.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer clips at once.
- **Not enough credits**: stop and do not retry. Hand over what is made (ids and links), say once
  that the balance does not cover the rest, and list what
  is left to make. Offer fewer treatments or one shape.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
