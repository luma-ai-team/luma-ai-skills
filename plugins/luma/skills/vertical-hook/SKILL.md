---
name: vertical-hook
description: Use when the user wants a short vertical clip for Reels, TikTok or Shorts that grabs attention in the first second: from an idea or a photo, as a loop, a character doing a trend's movement, or their own video made vertical. Writes the hook first, then makes it.
title: Make a vertical hook clip
needs_shell: false
---

# Make a vertical hook clip

One short vertical clip built so the first second does the work: the subject big in the frame,
something already happening in frame one, no slow build-up. Usually two or three variants of the
opening, so the user can test which one holds people. Optionally a loop. Read
[the tool cheat sheet](../_shared/luma-tools.md) first.

## 1. Ask only for what is missing, in one message

Ask only for what the brief leaves out and you cannot choose yourself: what the clip is for, when
the brief does not say, and the photo, when the brief mentions one you do not have. For everything
else, pick a default, state your picks in one line with the plan, and go ahead.

- **What the clip is for**: the product, the message or the account, and where it will run.
- **The hook**: the one thing that must happen in the first second. From the brief; when it gives
  none, write one per variant yourself, each a different first second.
- **The starting point**: an idea only (the default); a photo (a direct https link to the image
  file, or a file path when you have a shell; Luma cannot read a file attached to the chat); or one
  of their Luma pictures, such as a still from the `character-sheet` or `product-clip` workflows;
  a video of theirs to make vertical (route F); or a photo of a character plus a video of the
  movement it should copy (route E).
- **Sound**: sound made with the clip, or silent with a sound added in the posting app (often what
  creators want, since the app offers its own library). Silent, unless the brief asks for sound;
  say in one line that a version with sound can be made.
- **Loop or not**: only when the brief asks for one. Say that the loop is an experiment
  (section 5).
- **Words on screen**, if the brief gives any. They go on in the edit or the app, not in the
  generated picture.
- **How many variants**: the number the brief gives, otherwise two, so the user can test which
  opening holds people.

## 2. Find the vertical shape in the catalog

Never type a ratio from memory. `get_account` (consent), then `list_models` for the features the
route uses: `text-to-image` (for a still), `text-to-video` (for a clip from words), `image-to-video`
and `frames` (models and durations for clips made from stills), `motion-control` (route E) and
`reframe` (route F).

- In a row's `aspect_ratios`, read each value as width:height and take the portrait one (height
  greater than width). If a row lists more than one, full-screen phone feeds want the tallest; use
  it unless the brief says where else the clip runs. Use that exact string as `aspect_ratio`.
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
| **E. Copy a movement** | A mascot, a model or a character doing a dance, a gesture or a trend | a vertical photo of the character, then `edit_video` `mode: "motion"` with the movement video (section 5b) |
| **F. Their own video, made vertical** | A landscape or square clip they already have | `edit_video` `mode: "reframe"` with the portrait `aspect_ratio` from `list_models` `{"feature": "reframe"}` |

- **A photo in the wrong shape**: `generate_image` `mode: "edit"` with the portrait `aspect_ratio`
  and "The same <subject>, unchanged. The whole subject in frame, with space above and below."
  Check it did not cut off or change the subject. Take the value from the `image-edit` row, or the
  `text-to-image` row when that one lists none. The rows are the only check on a shape: an
  unlisted value fails only after the call starts, as a provider refusal that returns the credits.
- **Route A's still is the first frame**, so make it the hook itself: the moment of most tension or
  surprise, not the calm before it. Say where the subject sits, such as "the loaf centred in the
  frame, its top at the middle of the picture, empty space above". Then look at the still with the
  parts the app covers blanked out ([social finish F2](../_shared/social-finish.md): the top
  eighth, the bottom fifth and the right eighth): the hook must still read.
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
- Keep faces, the product and any later text out of the parts the app covers (social finish F2).
- Do not ask the model for words on screen; they often come out garbled.
- **Variants change the opening, not everything**: the same subject and look, two or three
  different first seconds.
- With sound on (route B or C), end the prompt with a sound line: "Sound: <three or four concrete
  sounds>". More patterns: [the prompt patterns](../generate/references/prompting.md).

## 5. The loop (an experiment)

> Tried once in testing: a still used as both frames of a `frames` clip, with a camera orbit and
> rising steam, gave a clip that moved, ended on its first frame and wrapped with no visible jump.
> One sample, so keep it an experiment: name it as one in the plan line, check the seam every
> time, and keep the fallback ready.

Pick the loop from the planned motion and the shell. With a shell, the mirror loop in the
fallback below needs nothing beyond the route A clip and has no seam by construction: choose it
when the motion is camera-led (a push, a drift, slow ambient movement). Choose the `frames` loop
when the motion has a visible cause and effect, which reads as a rewind when mirrored, or when
there is no shell. Name the choice in the plan line.

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
  1. **With a shell, a mirror loop, no new generation**: the best route A clip forward, then
     backward ([hook edit H3](references/hook-edit.md)). It suits a camera push or drift and slow ambient
     motion. Anything with a visible cause and effect reads as a rewind (steam sinking back, a pour,
     a step, speech), so prefer the variant whose motion is camera-led, and watch the backward half
     before offering it.
  2. **No loop**: post the best variant; the app replays it with a visible cut.

## 5b. Copy a movement (route E) and make a video vertical (route F)

- **The movement** comes from a video: the user's own recording of the move, or one they have the
  right to use. Upload it (`upload_media`; it may be an `upload_id`) or take one of their Luma
  videos. Its length and size must fit `list_models` `{"feature": "motion-control"}`
  `source_limits`; trim it first with a shell when it is longer. The result runs about as long as
  it. The hook rule holds: the move must already be happening in its first frame, so trim any
  wind-up off the source. A good source has a static camera, the whole body in frame all the way
  through, one clear move, a plain background and no one else in it. When the user has no such
  video and wants one made, make it with route B (`generate_video` `mode: "text"`, the portrait
  `aspect_ratio`) and those words in the prompt, not the hook's fast camera.
- **The character** is a photo: one person or character, whole body when the move uses the whole
  body, in the vertical shape (make it with route A's still if it is not), on a plain background.
  The result starts in the photo's pose, so pose the character like the movement video's first
  frame (arms up if its arms are up), not standing still. Only a real person who agreed to it.
- **The call** takes no prompt: `edit_video {"mode": "motion", "video": {...}, "image": {...},
  "client_request_id": "..."}`, with `model` optional from that feature's rows. `audio` is optional
  too; left out, the result came back silent in testing. A dance's music goes on in the edit
  (social finish F5) or in the app.
- **Check the face and hands** on a contact sheet of the result ([ffmpeg step 3](../short-film/references/ffmpeg.md))
  and on a full frame at the fastest moment of the move: the face stays the character's, the hands
  stay hands, no extra limbs. Hands blurring into soft fists in a fast swing is normal; a drifted
  face or a melted limb is retaken or dropped, not posted.
- **Route F** keeps their footage and redraws the edges into the new shape: `edit_video
  {"mode": "reframe", "video": {...}, "aspect_ratio": "<portrait value>", "client_request_id":
  "..."}`. Check that nothing new appeared at the edges that the brief would not want. When the
  first second of their video is not a hook, say so and suggest trimming it to start on the action.

## 6. Plan in one line, then run

1. Say the plan in one line: the route, how many stills, how many clips, sound or silent, and the
   loop attempt if any. Then run it. See "Credits and account status" in the cheat sheet.
2. **Stills first** (routes A, C, D), with the portrait `aspect_ratio`: a text call, or an edit
   with the uploaded photo (or the first still, once made) as `image`. On route A a variant with a
   different first second is its own still: two clips from one still differ only after frame one,
   so make a still for every variant.
3. **Check each still yourself** (section 3: the hook reads with the edges a feed hides covered,
   the subject whole and unchanged), then go straight on to the clips from the stills that pass.
   A still that fails is not animated: name it, say why, and offer a retake (a new key); make it
   when the user asks.
4. **Route B** has no stills: make the clips straight from the plan line.

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
  When the hook also gets music, effects or captions from the social finish, its F7 copies replace
  H1's posting copy.
- **Without a shell**: list the variants, each with what its opening does, `media_url` and
  `generation_id`, which one to post first, and the words and sound to add in the app. Say the
  links expire in an hour and `list_generations` finds them later.
- **Speech, music and captions**: a hook with someone talking gets captions, and any hook can get
  music under it and a sound effect on its first cut, with [the social finish](../_shared/social-finish.md)
  (F3, F5, F6). It also makes the posting copies and the cover frame (F7) and checks them (F8).
- Next steps, each a new job with a new key, made when the user asks: extend the winner
  (`generate_video` `mode: "extend"`; it takes no `aspect_ratio`, so check the result is still
  vertical), another opening, a restyle (`restyle`), a sharper copy of the winner (`edit_video`
  `mode: "enhance"`).

## When something goes wrong

- **"aspect_ratio is not used when mode is 'image'"** (or `'frames'`): remove it; the still sets
  the shape. New key.
- **No portrait value in any text-to-video row**: go through a still (route A).
- **Audio refused without a model**: pass the model the message names.
- **The loop call was refused or came back wrong**: use the fallback in section 5. A finished clip
  that does not loop is still a clip: show it beside the fallback, and make another loop attempt
  when the user asks.
- **Moderation refused a prompt or a photo**: final for that input. Tell the user; do not reword
  to get around it.
- **A clip failed**: read `error.message`, `retryable` and `refunded`. When `retryable` is true, run
  it once more as a new job with a new key, and tell the user only if that one fails too.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key.
- **Not enough credits**: stop and do not retry. Hand over what is made so far (ids and links),
  say once that the balance does not cover the rest, say
  which stills and clips are left to make, and offer fewer variants.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
