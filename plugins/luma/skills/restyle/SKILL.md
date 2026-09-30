---
name: restyle
description: Use when the user wants a photo, or one of their own Luma videos, redrawn in a different look such as anime, watercolour, clay or film noir, and wants to compare a few looks. Finds matching Luma styles, quotes each variant, runs them and shows them side by side.
title: Restyle a photo or video
needs_shell: false
---

# Restyle a photo or video

One photo or one of the user's Luma videos in; the same picture or clip redrawn in a few looks,
shown side by side so the user can pick. The looks are ready-made styles from Luma's catalog; for a
photo, a look described in words is a second route. Read [the tool cheat sheet](../_shared/luma-tools.md)
first.

## Two inputs, three routes, two kinds of price

| Input | Call | Priced |
|---|---|---|
| A photo, a ready-made style | `generate_image` `mode: "style"` with `image` and `style` | per picture |
| A photo, a look written in words | `generate_image` `mode: "edit"` with `image` and `prompt` | per picture |
| One of their Luma videos, a ready-made style | `apply_template` `kind: "style"` with `key`, `video`, optional `tier` | per second of the source video, by tier |

- **One style catalog serves both.** `list_templates` `{"kind": "style"}` lists each style once; its
  `key` goes in `style` for a photo and in `key` for a video.
- **A style's `credits` in `list_templates` is the video price** per unit of `per` (`credits` for
  the `"fast"` tier, `credits_max` for `"max"`). It does not price a photo. Every number you tell
  the user comes from `estimate_cost`.
- **A video must be one of the user's own finished Luma video generations.** An uploaded or linked
  video cannot be restyled; say so up front if they mention one. It is priced per second of the
  source, so a longer clip costs more. Check the result's length and sound; do not promise either.
- A style takes no prompt: the template is the prompt. An edit takes a prompt and no style.

## 1. Ask first, in one message

- **What to restyle.** A photo: a direct https link to the image file, the path of a file on this
  computer (only with a shell), or one of their Luma pictures. Luma cannot read a file attached to
  the chat; if they attached one, say so and ask for a link or a path. A video: which of their
  Luma videos.
- **The looks** they want to compare, in their words ("anime", "oil painting", "1950s noir"), or
  "show me some".
- **How many variants**: default three.
- **For a video, the tier**: `"fast"` (default) for comparing, `"max"` for the final.
- **Rights**: the photo is theirs or they may use it, and anyone in it agreed.

## 2. Bring the input in

- **A photo from a link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`.
- **A photo on this computer, with a shell**: `upload_media` `{"action": "start", "content_type":
  "<its MIME type, from file --mime-type -b <file>>", "size": <bytes from wc -c>}`, run the `curl -X PUT` from the answer, then
  `{"action": "confirm", "upload_id": "<id>"}`.
- **A Luma picture**: `list_generations` `{"kind": "image"}` and its `generation_id`.
- **A Luma video**: `list_generations` `{"kind": "video", "limit": 10}`. Show each with its prompt,
  `duration_seconds` and link; the user picks one. It must be `completed` with a `media_url`.

## 3. Find the looks

1. `list_templates` `{"kind": "style", "limit": 5}` to read the full `categories` list.
2. Search with `query` (a word of the look: "anime", "noir", "clay", "paint"; try both spellings of
   words like "watercolour") or `category` (exact, from the list).
3. Pick three to five that match and show each with its name and `preview_url` (`preview_kind` says
   whether the sample is a picture or a clip). Previews are free.
4. **For a photo, when no style fits** a look the user named, offer the edit route with the look
   written out: "Redraw this picture as <medium and look: a watercolour painting on textured paper,
   soft washes, visible brush edges>. Keep the same composition, the same people with the same
   faces and poses, and the same <key details>." Describe the medium, palette, era and light.
5. The user picks the variants.

## 4. For a video: try the looks on a still first (optional, cheaper)

A video restyle is priced per second, once per variant. To compare looks for less, restyle one
still in each candidate style first, then restyle the video only in the look the user picks:

- If the video was animated from one of their pictures (its `feature` in `list_generations` is
  `image-to-video`), restyle that picture with `generate_image` `mode: "style"`. The listing does
  not name a clip's input: ask the user which picture it was, or match one in `list_generations`
  `{"kind": "image"}` by prompt and date. When unsure, use a frame of the video instead.
- Otherwise, with a shell: download the video, take a frame
  (`ffmpeg -loglevel error -ss 1 -i source.mp4 -frames:v 1 -q:v 2 frame.jpg`), upload it with
  `action: "start"`, and restyle the frame.
- Without a shell, and when the video was not animated from one of their pictures, skip the still
  test and quote the video variants.

Say that a still shows the look, not the motion, and that the video result can differ. Quote the
stills and the video restyle together so the user sees both.

## 5. Quote and confirm

`get_account` (balance, consent). Then `estimate_cost` once per variant, with exactly the arguments
the call will take:

```
estimate_cost {"tool": "generate_image", "mode": "style", "image": {"upload_id": "<id>"}, "style": "<key>"}
estimate_cost {"tool": "generate_image", "mode": "edit", "image": {"upload_id": "<id>"}, "prompt": "Redraw this picture as ..."}
estimate_cost {"tool": "apply_template", "kind": "style", "key": "<key>", "video": {"generation_id": "<id>"}, "tier": "fast"}
```

For a video, `priced_seconds` in the answer is the source's length. The quote refuses a video
whose length Luma does not know, for free; a clip the provider cannot take (too long, too large) is
refused only once the restyle starts, and those credits come back. Show one short list: each variant and its price, the
total, the number of generations and the balance. Say that a retake, or the max tier later, is a
new generation with its own price. Wait for the user's yes.

## 6. Run

Keys: `<subject>-<run>-style-<look>`, such as `dog-photo-0930a-style-anime`, where `<run>` is a run
tag chosen once for this conversation (see the cheat sheet); a retake is `...-t2`.

```
generate_image {"mode": "style", "image": {"upload_id": "<id>"}, "style": "<key>", "client_request_id": "dog-photo-0930a-style-anime"}
generate_image {"mode": "edit", "image": {"upload_id": "<id>"}, "prompt": "Redraw this picture as ...", "client_request_id": "dog-photo-0930a-look-watercolour"}
apply_template {"kind": "style", "key": "<key>", "video": {"generation_id": "<id>"}, "tier": "fast", "client_request_id": "surf-clip-0930a-style-noir-fast"}
```

- `generate_image` usually answers with the finished `media_url`; if it answers with
  `poll_after_seconds`, wait with `get_generation`.
- `apply_template` answers with a `generation_id` at once. Start the variants in batches of about five, then poll each with
  `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is null. Do not narrate the
  polling; say that videos take minutes.

## 7. Show them side by side

- Show the original first, then each variant with its style name and `media_url`, in the same
  order every time. Links last one hour.
- Check each against the original: the same composition, people still recognisable, hands and
  faces intact, nothing added. For a video: its length against the source's, the motion kept, and
  whether its sound survived (check the file; do not promise either).
- **Without a shell**: a list, original first, each with the style name, `generation_id` and
  `media_url`. Say the links expire in an hour and `list_generations` finds them later.
- **With a shell**: download them and build one comparison the user can open, original first. Add
  one `-i` and one `[xN]` per extra variant and raise `inputs`. A HEIC original may not decode;
  convert it first (`sips -s format jpeg original.heic --out original.jpg` on a Mac):

```sh
ffmpeg -loglevel error -y -i original.jpg -i style-a.jpg -i style-b.jpg -filter_complex \
  "[0:v]scale=-2:640,setsar=1[x0];[1:v]scale=-2:640,setsar=1[x1];[2:v]scale=-2:640,setsar=1[x2];[x0][x1][x2]hstack=inputs=3" \
  -frames:v 1 compare.jpg
ffmpeg -loglevel error -y -i original.mp4 -i style-a.mp4 -i style-b.mp4 -filter_complex \
  "[0:v]scale=-2:640,setsar=1[x0];[1:v]scale=-2:640,setsar=1[x1];[2:v]scale=-2:640,setsar=1[x2];[x0][x1][x2]hstack=inputs=3:shortest=1,format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -crf 20 compare.mp4
```

- Next steps, each a new job with its own quote and key: the favourite in the `"max"` tier, the same
  look on more photos or clips, animate a restyled photo (`generate_video` `mode: "image"`, or the
  `photo-to-video` workflow).

## When something goes wrong

- **"Luma does not know that video's length"** (`unknown_length`): that video cannot be restyled;
  pick another.
- **"The provider refused this request; your credits were returned."** (`provider_refused`) on a
  video restyle: often a source the provider cannot take, such as one too long. The same call fails
  again; pick a shorter clip or another style with the user.
- **"that upload is a ..., but this needs a ..."** (`wrong_media_kind`): a photo went where a video
  belongs, or the reverse. `generate_image` restyles photos, `apply_template` videos.
- **"That model, setting or template is not available right now."**: re-read `list_templates` and
  pick an available style.
- **Moderation refused a photo or the edit prompt**: final for that input. Tell the user; do not
  reword or crop to get it through.
- **A variant failed**: show `error.message` and `refunded`; a retry is a new job, quoted, new key.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer variants at once.
- **Not enough credits**: stop, show the account link from the refusal, offer fewer variants.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
