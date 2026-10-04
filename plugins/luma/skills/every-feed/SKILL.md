---
name: every-feed
description: Use when the user has one video and wants it in other shapes or sharper for Reels, TikTok, Shorts, a feed post, YouTube or a shop page. Finds the crop that keeps the subject whole in each shape, sharpens it with enhance, and checks every copy.
title: Fit a video to every feed
needs_shell: false
---

# Fit a video to every feed

One finished video in; one copy per place it will run out, each with the subject whole and big in
its frame, sharp enough for where it runs. Read [the tool cheat sheet](../_shared/luma-tools.md)
first. What each place needs, and the four ways to change a shape, are in
[the social finish](../_shared/social-finish.md) (F1 and F2). In testing they ranked this way for a
product, and this workflow follows that order:

1. **A moved crop**, then `edit_video` `mode: "enhance"` when the crop is small. Free to cut, and
   the subject gets bigger.
2. **Made again in the new shape**, for a clip Luma made from a still.
3. **`edit_video` `mode: "reframe"`**, for a small change of shape only. It keeps the whole source
   at its own size and invents everything around it: from landscape to vertical it drew two thirds
   of the frame, shrank the product and added a realistic face that changed on every take.

## 1. Ask only for what is missing, in one message

- **The video**: one of their Luma videos, a direct https link to the file, or a file on this
  computer (with a shell). The user's own footage or footage they may use.
- **Where it will run**: decides the shapes. Without an answer: vertical for Reels, TikTok and
  Shorts, 4:5 for a feed post, landscape for YouTube or a website. Make only the shapes that differ
  from the video's own.
- **Sharper or not**: enhance when the brief says high quality, an ad, a shop page or a big screen.
  Otherwise make the copies and offer enhance in one line.

## 2. Bring the video in, look at it, read the catalog

- **A Luma video**: `list_generations` `{"kind": "video"}` and its `generation_id`. Ask whether it
  was made from a still (`list_generations` `{"kind": "image"}` shows their stills), which opens
  route 2.
- **A link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`. **A file here**:
  `upload_media` `start`, the PUT, then `confirm`.
- Read the source's shape (`output_width` and `output_height` in `get_generation`, or `ffprobe`).
  With a shell, download it and take frames at the start, the middle and the end
  ([ffmpeg step 3](../short-film/references/ffmpeg.md)): where the subject is, and whether it
  moves across the frame.
- `get_account`, and `list_models` for `upscale` (its rows' `variant` values are the orderable
  quality pairs, the null one the default) and, if route 3 may be needed, `reframe`
  (`aspect_ratios`, `source_limits`).

## 3. Choose the route per shape

**With a shell, try the crop first, always.** For each shape, crop frames at the start, middle and
end with film step 4's `V` and [reel edit R2](../memory-reel/references/reel-edit.md)'s `CX` and
`CY` moved across the subject (`CX` from 0.3 to 0.7 in steps of 0.1 for a vertical cut of a
landscape clip). Put the candidates side by side and look: the right crop keeps the subject whole,
and on a vertical feed out of the parts the app covers (social finish F2), in all three frames.

- **A crop holds it**: route 1. Cut it (step 5), and enhance it when its short side is under
  about 1080 and the brief wants it sharp.
- **No crop holds it, and the video is a Luma clip made from a still**: route 2. `generate_image`
  `mode: "edit"` of that still with the shape's `aspect_ratio` and "The same scene, unchanged: the
  same <subject>, the whole <subject> in frame", checked, then animated with the same mode and
  prompt as the original (its parameters are in `get_generation` or the user's history).
- **No crop holds it, and the change is small** (vertical to 4:5 or 3:4, landscape to square at
  most): route 3, reframe, and check it hard (step 6).
- **No crop holds it and the change is large**: tell the user the choices in one message: the
  closest crop (and what it cuts), a blurred fill (social finish F1), or a reframe with its risk
  (an invented scene around a small subject). Make the one they pick.

**Without a shell**: you cannot crop. Reframe a small change; for a large one, explain the
choices above and offer route 2 for a Luma clip, or a crop the user makes in an editing app (give
the exact crop: which side and how much to keep).

## 4. Plan in one line, then run

Say the plan in one line: each shape and its route, and which copies get enhanced. Then run it. See "Credits and account status" in the cheat sheet. `<run>` is four random characters chosen
once for this conversation.

```
edit_video {"mode": "enhance", "video": {"upload_id": "<the uploaded crop>"}, "client_request_id": "<name>-<run>-enhance-<shape>"}
edit_video {"mode": "enhance", "video": {"generation_id": "<a copy>"}, "resolution": "<from a variant>",
  "frame_rate": <from the same variant>, "client_request_id": "<name>-<run>-enhance-<shape>"}
edit_video {"mode": "reframe", "video": {"generation_id": "<source>"}, "aspect_ratio": "<value from the reframe row>",
  "client_request_id": "<name>-<run>-reframe-<shape>"}
```

- Omit `resolution` and `frame_rate` for the default quality; pass a pair only when an `upscale`
  row's `variant` names it.
- A source that is the user's upload stays `{"upload_id": "..."}` in every call.
- A retake is a new job with a new key, made when the user asks. A reframe takes no prompt, so a
  retake is a new roll of the same dice, not a correction.

## 5. Cut a crop (with a shell)

```sh
CX=0.45; CY=0.5            # the position chosen in step 3
read CW CH < <(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x source.mp4 \
  | awk -F x -v r=9/16 '{ split(r, a, "/"); t = a[1] / a[2]; if ($1 / $2 > t) { h = $2; w = int(h * t / 2) * 2 } else { w = $1; h = int(w / t / 2) * 2 }; print w, h }')
ffmpeg -loglevel error -y -i source.mp4 -t 5 -vf "crop=${CW}:${CH}:(iw-${CW})*${CX}:(ih-${CH})*${CY},setsar=1" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -an crop-vertical.mp4
```

Set `r` to the shape (`9/16`, `4/5`, `1/1`, `16/9`) and `-t` to the source's length cut to a whole
second: an uploaded file is priced on its measured length, rounded up. Keep the audio (drop `-an`)
when the source has sound. A crop to enhance is uploaded (`upload_media` `start`) and enhanced by
`upload_id`; a crop that stays as it is goes straight to step 7.

## 6. Check every copy

- **Nothing invented.** Compare each copy with the source frame by frame at the start, middle and
  end. A reframe or a route 2 still can add a person, a face, a hand, a sign with garbled letters
  or a prop. An invented face is never used in an ad without the user's knowing yes; a changed
  product is never used.
- **The subject is whole and big**: not cut at any point of the clip, not shrunk to a strip, and
  on a vertical feed clear of the parts the app covers (social finish F2).
- **An enhance changed only the sharpness**: same framing and length (it may come back at another
  frame rate, which is fine).

## 7. Deliver

- **With a shell**: download each copy (links last one hour), size it to an exact frame with film
  step 4 (`R` set to its shape), and make the posting copies with social finish F7, with
  `master-<shape>.mp4` as the input (a clip with no sound gives two silent copies; keep one). Run
  F8, then
  name the files by where they go: `<name>-reels.mp4` (also TikTok and Shorts),
  `<name>-feed-4x5.mp4`, `<name>-youtube.mp4`, `<name>-shop.mp4`.
- **Without a shell**: list each copy with where it goes, its `media_url` and `generation_id`, and
  for a crop the user makes, the exact crop. Say the links expire in an hour and
  `list_generations` finds them later.

Offer the next step, made when the user asks: captions and music for the vertical copy (social
finish F3 and F5), a hook at the start (`vertical-hook`), or a talking ad around it (`talking-ad`).

## When something goes wrong

- **"This tool needs a clip between ..."** (`source_length_unsupported`): trim the source to fit,
  or pick another part with the user.
- **"Luma could not read how long that video is"** (`unknown_length`): save it again as a standard
  MP4 (`ffmpeg -i in.mov -c:v libx264 -c:a aac out.mp4`) and upload again.
- **A shape is not in the reframe row**: crop to it, or route 2.
- **Moderation refused the video**: final. Tell the user; do not trim or recolour it to get past.
- **Not enough credits**: stop and do not retry. Hand over the copies made, say once that the
  balance does not cover the rest, and offer crops for the
  rest, which cost nothing.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
