---
name: product-clip
description: Use when the user wants short clips of a product for a shop, an ad or social media, starting from a photo of the product. Cleans the photo up with an image edit, then makes a few motion treatments in vertical and square, each quoted first.
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

## 1. Ask first, in one message

- **The photo, and how it reaches Luma.** Luma cannot read a file attached to the chat. Ask for a
  direct https link to the image file, the path of a file on this computer (only with a shell), or
  one of their Luma pictures. It must be their own photo of the product, or one they may use.
- **What the product is**, and the one thing the clips must show (the label, the texture, the size).
- **Where the clips will run**, which decides the shapes: vertical, square, or both (default both).
- **The setting**: a plain studio background (which colour), a scene (a kitchen counter, a desk,
  outdoors), or the original background tidied up.
- **Brand colours**, if any.
- **How many treatments**: default three.

Say up front that the clips come out silent. With a shell, music the user has the right to use
can go on afterwards: join one showreel per shape
([ffmpeg steps 4, 6 and 9b](../short-film/references/ffmpeg.md)), then add music over each with
[reel edit R4](../memory-reel/references/reel-edit.md).

## 2. Bring the photo in

- **A link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`.
- **A file here, with a shell**: `upload_media` `{"action": "start", "content_type": "<its MIME
  type, from file --mime-type -b <file>>", "size": <bytes from wc -c>}`, run the `curl -X PUT` from
  the answer, then `{"action": "confirm", "upload_id": "<id>"}`.
- **A Luma picture**: `list_generations` `{"kind": "image"}` and its `generation_id`.

## 3. Read the catalog

- `get_account` for the balance and consent.
- `list_models` `{"feature": "image-edit"}`: pick the vertical and the square value from the
  row's `aspect_ratios`. If that row lists none, take them from the `text-to-image` row.
  `estimate_cost` does not check shapes: a value no row lists fails only after the call starts, as
  a provider refusal that returns the credits. Never use a ratio that is listed nowhere.
- `list_models` `{"feature": "image-to-video"}`: models and durations; `{"feature": "frames"}` too
  if a Reveal is planned.
- Optional: `list_templates` `{"kind": "effect"}` and look in `categories` for one aimed at
  products or ads. A one-photo effect (`input_count` 1) can be an extra treatment; show its
  `preview_url` first.

Image-to-video takes no `aspect_ratio`: each clip takes the shape of its still. That is why the
stills are made once per shape.

## 4. Plan the treatments

Offer three that fit the product and let the user choose:

| Treatment | Motion prompt to adapt |
|---|---|
| Slow turn | "The camera orbits slowly around the product; soft reflections move across its surface." |
| Push-in with light | "Slow push-in toward the product while a soft band of light sweeps across it." |
| Float | "The product lifts a little and floats, turning gently, a soft shadow below it." |
| In use | "A hand enters the frame and picks up the product." Hands can come out wrong; check. |
| Reveal | Two edits of the clean still (for example far and close, or closed and open) joined with `generate_video` `mode: "frames"`. |

Say the plan with its count: one still per shape, plus treatments times shapes. For two shapes and
three treatments that is two stills and six clips. A Reveal adds two edits and one `frames` clip per
shape; an effect adds one `apply_template` per shape.

## 5. Quote and confirm

- `get_account` (balance, consent) if not read in step 3.
- `estimate_cost` for the edit in each shape, one image-to-video clip per model and duration (the
  uploaded photo as `image`), one `frames` clip per Reveal (the photo as both frames), and each
  chosen effect key.
- Multiply, show the total, the number of stills and clips, and the balance. Offer to start with one
  shape and one treatment as a test when the budget is tight. Ask for a yes.

## 6. Make the clean stills

```
generate_image {"mode": "edit", "image": {"upload_id": "<id>"},
  "prompt": "The same <product>, unchanged: same shape, colours, label and logo. <setting>. Soft studio light from <side>. The whole product in frame, centred, with space around it.",
  "aspect_ratio": "<the vertical value from list_models>", "client_request_id": "<product>-<run>-still-vertical"}
```

Then the same with the square value and `<product>-<run>-still-square`. `<run>` is a run tag chosen
once for this conversation (see the cheat sheet), such as `0930a`.

- Wait for each `media_url`, then compare it with the original: label text, logo, colours,
  proportions. Say what changed, if anything.
- If the new shape cuts the product off, retake once with the "whole product in frame" line
  stressed; if it still fails, tell the user and offer the shape that works. Whether an edit with a
  different `aspect_ratio` reframes the product cleanly depends on the photo; check, do not assume.
- Show the approved stills before any video spend.

## 7. Animate

```
generate_video {"mode": "image", "image": {"generation_id": "<approved still>"}, "prompt": "<treatment>",
  "model": "<from list_models>", "duration": <a listed duration>, "client_request_id": "<product>-<run>-<treatment>-<shape>"}
generate_image {"mode": "edit", "image": {"generation_id": "<approved still>"}, "prompt": "The same <product>, unchanged. <the reveal's first or last state>.",
  "aspect_ratio": "<the same value>", "client_request_id": "<product>-<run>-reveal-a-<shape>"}
generate_video {"mode": "frames", "start_image": {"generation_id": "<reveal a>"}, "end_image": {"generation_id": "<reveal b>"},
  "prompt": "<the move between them>", "model": "<frames model>", "duration": <a listed duration>, "client_request_id": "<product>-<run>-reveal-<shape>"}
apply_template {"kind": "effect", "key": "<key>", "images": [{"generation_id": "<approved still>"}], "client_request_id": "<product>-<run>-fx-<shape>"}
```

A Reveal's two edits (`reveal-a`, `reveal-b`) must have their `media_url` before the `frames` call.
Check the effect clip's shape; it may not follow the still. Start clips in batches of about five,
then poll each with `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is null. A retake gets a new key (`...-t2`) and the user's yes.

## 8. Check and deliver

- Watch each clip for the product changing as it moves: the label warping, the colour shifting,
  the shape bending. Drop or retake those, with the user's yes.
- **With a shell**: download the clips into one folder per shape (`vertical/`, `square/`), named
  `s01.mp4`, `s02.mp4` in showreel order (links last one hour). Make one showreel per shape, never
  one mixing shapes: in each folder run [ffmpeg steps 4, 6 and 9b](../short-film/references/ffmpeg.md)
  with `O` set to that shape, then rename `film.mp4` to `<product>-<shape>.mp4`. Add music over
  each showreel with [reel edit R4](../memory-reel/references/reel-edit.md).
- **Without a shell**: list the clips grouped by shape: treatment, `media_url`, `generation_id`.
  Say the links expire in an hour and `list_generations` finds them later.

## When something goes wrong

- **The link is refused**: a web page instead of the file needs the direct link; too big for
  `from_url` needs a shell and `action: "start"`.
- **Moderation refused a photo or a prompt**: final for that input. Tell the user; do not reword to
  get around it.
- **A clip failed**: show `error.message` and `refunded`; a retry is a new job, quoted, new key.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer clips at once.
- **Not enough credits**: stop, show the account link from the refusal, offer fewer variants.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
