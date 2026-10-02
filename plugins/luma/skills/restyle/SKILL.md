---
name: restyle
description: Use when the user wants a photo, or one of their own Luma videos, redrawn in a different look such as anime, watercolour, clay or film noir, and wants to compare a few looks. Finds matching Luma styles, makes each variant and shows them side by side.
title: Restyle a photo or video
needs_shell: false
---

# Restyle a photo or video

One photo or one of the user's Luma videos in; the same picture or clip redrawn in a few looks,
shown side by side so the user can pick. The looks are ready-made styles from Luma's catalog; for a
photo, a look described in words is a second route. Read [the tool cheat sheet](../_shared/luma-tools.md)
first.

## Two inputs, three routes

| Input | Call |
|---|---|
| A photo, a ready-made style | `generate_image` `mode: "style"` with `image` and `style` |
| A photo, a look written in words | `generate_image` `mode: "edit"` with `image` and `prompt` |
| One of their Luma videos, a ready-made style | `apply_template` `kind: "style"` with `key`, `video`, optional `tier` |

- **One style catalog serves both.** `list_templates` `{"kind": "style"}` lists each style once; its
  `key` goes in `style` for a photo and in `key` for a video.
- **A style's `credits` in `list_templates` is the video restyle's price** (`credits` for the
  `"fast"` tier, `credits_max` for `"max"`), never a photo's. When the user asks what a look
  costs, `estimate_cost` answers for either.
- **A video must be one of the user's own finished Luma video generations.** An uploaded or linked
  video cannot be restyled; say so up front if they mention one. Check the result's length and
  sound; do not promise either.
- A style takes no prompt: the template is the prompt. An edit takes a prompt and no style.

## 1. Ask only for what is missing, in one message

What to restyle is the one thing only the user can give. Ask for it when the brief does not say;
for everything else, pick a default, state your picks in one line, and go ahead.

- **What to restyle.** A photo: a direct https link to the image file, the path of a file on this
  computer (only with a shell), or one of their Luma pictures. Luma cannot read a file attached to
  the chat; if they attached one, say so and ask for a link or a path. A video: which of their
  Luma videos.
- **The looks** to compare, in their words ("anime", "oil painting", "1950s noir"), from the brief.
  When the brief names none, see step 3.
- **How many variants**: one per look the brief names; otherwise three for a photo, and for a video
  the one or two looks the user picks in step 3.
- **For a video, the tier**: `"fast"` (default) for comparing, `"max"` when the brief asks for the
  best quality or the final version.
- **Rights**: the photo must be theirs or one they may use, and anyone in it must have agreed. Say
  so in one line.

## 2. Bring the input in

- **A photo from a link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`.
- **A photo on this computer, with a shell**: `upload_media` `{"action": "start", "content_type":
  "<its MIME type, from file --mime-type -b <file>>", "size": <bytes from wc -c>}`, run the `curl -X PUT` from the answer, then
  `{"action": "confirm", "upload_id": "<id>"}`.
- **A Luma picture**: `list_generations` `{"kind": "image"}` and its `generation_id`.
- **A Luma video**: `list_generations` `{"kind": "video", "limit": 10}`. Show each with its prompt,
  `duration_seconds` and link; the user picks one. It must be `completed` with a `media_url`; skip
  failed and pending rows. If the clip the user means is not in the ten, list more (`limit` up to
  50) or ask for a word from its prompt.

## 3. Find the looks

1. `list_templates` `{"kind": "style", "limit": 50}` lists every style, each with a plain name;
   pick by name. `categories` can be empty for styles.
2. `query` matches only a style's name or key: "clay" finds a clay style, while "hand-drawn",
   "cartoon" or "poster" can find nothing. Use it for a word likely in a name, and try both
   spellings of words like watercolor and watercolour.
3. Find three to five that match, by name and `preview_url` (`preview_kind` says whether the
   sample is a picture or a clip). Previews are free samples. A look is not always safe for the
   subject: styles built around faces can invent a face on an object (one gave a mug eyes and
   arms), comic looks can add sound-effect lettering and a panel border, and line-art looks drop
   colour. Say what each is likely to add; a product or an object shows it most, so check those
   results closely.
4. **For a photo, when no style fits** a look the user named, use the edit route with the look
   written out: "Redraw this picture as <medium and look: a watercolour painting on textured paper,
   soft washes, visible brush edges>. Keep the same composition, the same people with the same
   faces and poses, and the same <key details>." Describe the medium, palette, era and light.
   Looks that come with typography (a poster, a magazine cover, a stamp, a postcard, a label) make
   the model invent lettering, and it comes out garbled or mirrored. Unless the user wants words,
   end the prompt with "No text, no lettering, no captions and no signs anywhere in the picture."
   Do not say "hand-lettered", which asks for lettering. If the user wants words, suggest adding
   them in an editor afterwards.
5. **Choose the variants.** Looks the brief names: use them. For a photo with none named, choose
   three that suit the subject and name them in the plan line. For a video with none named, show
   the user three to five with their name and `preview_url` and let them pick one or two: a choice
   of look only they can make.

## 4. For a video: the looks on a still, when the user asks

When the user wants to see the looks on their own clip before picking, restyle one still in each
candidate look, show them, then restyle the video in the one or two looks the user picks:

- If the video was animated from one of their pictures (its `feature` in `list_generations` is
  `image-to-video`), restyle that picture with `generate_image` `mode: "style"`. The listing does
  not name a clip's input, and a user can have several near-identical pictures, so do not guess
  from prompts and dates: ask the user which picture it was, and when they cannot say, use a frame
  of the video (next bullet).
- Otherwise, with a shell: download the video, take a frame
  (`ffmpeg -loglevel error -ss 1 -i source.mp4 -frames:v 1 -q:v 2 frame.jpg`), upload it with
  `action: "start"`, and restyle the frame.
- Without a shell, and when the video was not animated from one of their pictures, there is no
  still to restyle: say so, and let the previews guide the pick.

Say that a still shows the look, not the motion, and that the video result can differ.

## 5. Plan in one line

`get_account` (consent). Say the plan in one line: the input, each look by name, and for a video
the tier. Then run it. See Credits in the cheat sheet: the request is the go-ahead.

`apply_template` refuses a video whose length Luma does not know, and a clip outside the length or
size the catalog accepts for a restyle, before anything is charged; say which limit it named and
pick another clip with the user. A clip the provider still cannot take is refused only once the
restyle starts, and those credits come back.

## 6. Run

Keys: `<subject>-<run>-style-<look>`, such as `dog-photo-k7f2-style-anime`, where `<run>` is four
random characters chosen once for this conversation (see the cheat sheet); a retake is `...-t2`.

```
generate_image {"mode": "style", "image": {"upload_id": "<id>"}, "style": "<key>", "client_request_id": "dog-photo-k7f2-style-anime"}
generate_image {"mode": "edit", "image": {"upload_id": "<id>"}, "prompt": "Redraw this picture as ...", "client_request_id": "dog-photo-k7f2-look-watercolour"}
apply_template {"kind": "style", "key": "<key>", "video": {"generation_id": "<id>"}, "tier": "fast", "client_request_id": "surf-clip-k7f2-style-noir-fast"}
```

- `generate_image` usually answers with the finished `media_url`; if it answers with
  `poll_after_seconds`, wait with `get_generation`.
- `apply_template` answers with a `generation_id` at once. Start the variants in batches of about five, then poll each with
  `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is null. Do not narrate the
  polling; say that a video restyle takes a few minutes.

## 7. Show them side by side

- Show the original first, then each variant with its style name and `media_url`, in the same
  order every time. Links last one hour.
- Check each against the original: the same composition, people still recognisable, hands and
  faces intact, and nothing added: no invented faces, hands, lettering or objects. For a video: its
  length against the source's, the motion kept, and whether its sound survived (check the file; do
  not promise either). A clip made from a photo has no audio to keep, and its restyle has none
  either (ffprobe shows one video stream): tell the user, and offer a soft ambient bed
  ([reel edit R5](../memory-reel/references/reel-edit.md), laid under with R4 and `GRADE=null`), or
  their own music with R4. R4 needs an audio track, so first run
  [ffmpeg steps 4 and 6](../short-film/references/ffmpeg.md) on the clip, which give it a silent
  one. Say too that the video
  look can differ from the still: a clay still can show fingerprints and dents where the clay
  video is smoother, and the background can change colour.
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

- Next steps, each a new job with a new key, made when the user asks: the favourite in the
  `"max"` tier, the same look on more photos or clips, animate a restyled photo (`generate_video`
  `mode: "image"`, or the `photo-to-video` workflow).

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
- **A variant failed**: read `error.message`, `retryable` and `refunded`. When `retryable` is true,
  run it once more as a new job with a new key, and tell the user only if that one fails too.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer variants at once.
- **Not enough credits**: stop and do not retry. Hand over the variants made so far (ids and
  links), say once that the balance does not cover the rest, show the account link from the
  refusal, say which looks are left to make, and offer fewer variants (or the `"fast"` tier).
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
