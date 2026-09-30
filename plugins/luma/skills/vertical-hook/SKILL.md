---
name: vertical-hook
description: Use when the user wants a short vertical clip for Reels, TikTok or Shorts that grabs attention in the first second, from an idea, a photo or a Luma picture, optionally as a loop. Writes the hook first, makes a few variants in the vertical shape, quotes each and shows them.
title: Make a vertical hook clip
needs_shell: false
---

# Make a vertical hook clip

One short vertical clip built so the first second does the work: the subject big in the frame,
something already happening in frame one, no slow build-up. Usually two or three variants of the
opening, so the user can test which one holds people. Optionally a loop. Read
[the tool cheat sheet](../_shared/luma-tools.md) first.

## 1. Ask first, in one message

- **What the clip is for**: the product, the message or the account, and where it will run.
- **The hook**: the one thing that must happen in the first second. If they do not have one,
  offer three and let them pick.
- **The starting point**: an idea only; a photo (a direct https link to the image file, or a file
  path when you have a shell; Luma cannot read a file attached to the chat); or one of their Luma
  pictures, such as a still from the `character-sheet` or `product-clip` workflows.
- **Sound**: sound made with the clip, or silent with a sound added in the posting app (often what
  creators want, since the app offers its own library).
- **Loop or not.** Say that the loop is an experiment (section 5).
- **Words on screen**, if any. They go on in the edit or the app, not in the generated picture.
- **How many variants**: default two or three.

## 2. Find the vertical shape in the catalog

Never type a ratio from memory. `get_account` (balance, consent), then `list_models` for
`text-to-image` (for a still), `text-to-video` (for a clip from words), and `image-to-video` and
`frames` (models and durations for clips made from stills).

- In a row's `aspect_ratios`, read each value as width:height and take the portrait one (height
  greater than width). If a row lists more than one, full-screen phone feeds want the tallest; ask
  when unsure. Use that exact string as `aspect_ratio`.
- A model whose row lists no portrait value cannot make this clip from words; pick another model,
  or go through a still.
- **Image and frames modes take no `aspect_ratio`**: the clip takes the shape of its picture. So
  any clip made from a picture needs a vertical picture first.

A photo: bring it in with `upload_media` as the cheat sheet shows ("Getting the user's photo into
Luma").

## 3. Choose the route

| Route | When | Calls |
|---|---|---|
| **A. Still, then animate** (default) | A person, a character or a product must look exactly right | a vertical still (`generate_image` text, or edit of their photo), then `generate_video` `mode: "image"` (silent) |
| **B. Straight from words** | Speed, or sound made with the clip | `generate_video` `mode: "text"` with the portrait `aspect_ratio`, and for sound `audio: true` with the model of a row that has the audio variant |
| **C. Two stills** | A before and after, a reveal, a transformation | two vertical stills (the second an edit of the first), then `generate_video` `mode: "frames"` |
| **D. Loop** | The user wants it to repeat without a visible cut | section 5 |

- **A photo in the wrong shape**: `generate_image` `mode: "edit"` with the portrait `aspect_ratio`
  and "The same <subject>, unchanged. The whole subject in frame, with space above and below."
  Check it did not cut off or change the subject. Take the value from the `image-edit` row, or the
  `text-to-image` row when that one lists none; `estimate_cost` does not check shapes, so an
  unlisted value can fail only after the call starts, as a provider refusal that returns the credits.
- **Route A's still is the first frame**, so make it the hook itself: the moment of most tension or
  surprise, not the calm before it. Say where the subject sits, such as "the loaf centred in the
  frame, its top at the middle of the picture, empty space above". Then look at the still with the
  bottom fifth and the right sixth covered, the parts a feed hides: the hook must still read.
- Frames model values differ from text-to-video ones; read the `frames` row for route C and D.

## 4. Write the hook

Prompt pattern for the motion (routes A, C and D), or after the picture description (route B):

```
Opens mid-action: <the striking thing, already happening in the first frame>. <What escalates
next>. <Camera: fast push-in, whip pan, handheld close-up>. <The payoff, before the end>.
```

- The first frame already shows the subject, big and centred. No empty establishing frame, no fade
  in.
- One idea per clip. The payoff lands before the clip ends.
- Keep faces, the product and any later text in the middle of the frame: vertical feeds cover the
  top and bottom edges and the right side with buttons and captions.
- Do not ask the model for words on screen; they often come out garbled.
- **Variants change the opening, not everything**: the same subject and look, two or three
  different first seconds.
- With sound on (route B or C), end the prompt with a sound line: "Sound: <three or four concrete
  sounds>". More patterns: [the prompt patterns](../generate/references/prompting.md).

## 5. The loop (an experiment)

> Tried once in testing: a still used as both frames of a `frames` clip, with a camera orbit and
> rising steam, gave a clip that moved, ended on its first frame and wrapped with no visible jump.
> One sample, so keep it an experiment: quote it on its own line, check the seam every time, and
> keep the fallback ready. It costs more than an ordinary clip of the same length.

With a shell, the mirror loop in the fallback below is free and has no seam by construction, so
offer it beside the experiment and let the user choose.

- **The call**: `generate_video` `mode: "frames"` with the vertical still as both `start_image` and
  `end_image`, and motion that leaves and comes back: "The camera drifts around her and returns to
  where it started; her hair lifts in the wind and settles back." Model and duration from the
  `frames` row.
- **No generated sound on a loop**: the sound would jump where the clip restarts. Sound goes on in
  the app.
- **Check the seam.** With a shell, follow [hook edit H2](references/hook-edit.md): the last frame
  beside the first, a number for how alike they are against two neighbouring frames, and a copy
  that plays three times. Without a shell, ask the user to watch it on repeat.
- **A loop is its own file.** Never join it to other clips; the join would put a cut in it.
- **Fallback when the clip barely moves, the seam jumps, or the call is refused** (a provider
  refusal returns the credits):
  1. **With a shell, a mirror loop, free**: the best route A clip forward, then backward
     ([hook edit H3](references/hook-edit.md)). It suits a camera push or drift and slow ambient
     motion. Anything with a visible cause and effect reads as a rewind (steam sinking back, a pour,
     a step, speech), so prefer the variant whose motion is camera-led, and watch the backward half
     before offering it.
  2. **No loop**: post the best variant; the app replays it with a visible cut.

## 6. Plan and quote

1. Say the plan in one line: how many stills, how many clips, and the loop attempt if any.
2. **Stills first** (routes A, C, D): one quote per still mode used, with the portrait
   `aspect_ratio`: a text call, and an edit with the uploaded photo (or the first still, once made)
   as `image`. On route A a variant with a different first second is its own still: two clips from
   one still differ only after frame one, so quote a still for every variant. Multiply by the
   stills, show it and ask for a yes.
3. **Then the clips**, once the stills are approved: `estimate_cost` once per distinct call shape
   with a real still's `generation_id` as input (image mode, frames with and without audio, the
   loop). Route B has only this step.
4. Show the count of each kind, the total and the balance. Say that each variant and each retake is
   its own generation and its own charge. Wait for the user's yes.

## 7. Make it

Keys: `<hook>-<run>-<what>-v<n>`, such as `coffee-hook-k7f2-still-v1`, where `<run>` is four random
characters chosen once for this conversation (see the cheat sheet); a retake is `...-t2`.

```
generate_image {"mode": "text", "prompt": "...", "aspect_ratio": "<portrait value from list_models>", "client_request_id": "coffee-hook-k7f2-still-v1"}
generate_video {"mode": "image", "image": {"generation_id": "<still v1>"}, "prompt": "Opens mid-action: ...",
  "model": "<image-to-video model>", "duration": <a listed duration>, "client_request_id": "coffee-hook-k7f2-clip-v1"}
generate_video {"mode": "text", "prompt": "... Sound: ...", "aspect_ratio": "<portrait value>", "model": "<a model with an audio row>",
  "duration": <from durations_with_audio>, "audio": true, "client_request_id": "coffee-hook-k7f2-text-v2"}
generate_video {"mode": "frames", "start_image": {"generation_id": "<still v1>"}, "end_image": {"generation_id": "<still v1>"},
  "prompt": "<motion that leaves and returns>", "model": "<frames model>", "duration": <a listed duration>, "client_request_id": "coffee-hook-k7f2-loop-v1"}
```

- `generate_image` usually answers with the `media_url`; a still used as input must have one.
- Start the clips in batches of about five, then poll each with `get_generation` (`wait_seconds` up to 25) until
  `poll_after_seconds` is null. Do not narrate the polling.

## 8. Check and deliver

- **Check the first frame of every variant**: it is the hook and often the thumbnail. The subject
  visible, sharp and big; nothing important under the edges the app covers. Check the clip is
  vertical (with a shell, `ffprobe` shows width smaller than height).
- **With a shell**: download each as `<hook>-v<n>.mp4` (links last one hour). Words on screen go on
  as a PNG overlay: [hook edit H1](references/hook-edit.md) sizes the clip, keeps its exact length
  (a loop keeps its last frame), fades the words in fast and out before the end, checks a middle
  frame for words over the hook, and makes a copy for posting with no audio track for the app to
  fill. Clips from different routes come out at different sizes; finish each variant on its own.
- **Without a shell**: list the variants, each with what its opening does, `media_url` and
  `generation_id`, which one to post first, and the words and sound to add in the app. Say the
  links expire in an hour and `list_generations` finds them later.
- Next steps, each a new job with its own quote and key: extend the winner (`generate_video`
  `mode: "extend"`; it takes no `aspect_ratio`, so check the result is still vertical), another
  opening, a restyle (`restyle`).

## When something goes wrong

- **"aspect_ratio is not used when mode is 'image'"** (or `'frames'`): remove it; the still sets
  the shape. New key.
- **No portrait value in any text-to-video row**: go through a still (route A).
- **Audio refused without a model**: pass the model the message names.
- **The loop call was refused or came back wrong**: use the fallback in section 5. A refusal
  returned the credits; a finished clip that does not loop was charged, so say so before retrying.
- **Moderation refused a prompt or a photo**: final for that input. Tell the user; do not reword
  to get around it.
- **A clip failed**: show `error.message` and `refunded`; a retry is a new job, quoted, new key.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key.
- **Not enough credits**: stop, show the account link from the refusal, offer fewer variants.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
