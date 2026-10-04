---
name: short-film
description: Use when the user wants a short film, a trailer or a story told in several shots with Luma, from script and shot list to matching stills, animated shots and one cut with titles and sound. The final cut needs ffmpeg on the user's machine; without it, deliver the shots in order.
title: Make a short film
needs_shell: true
---

# Make a short film

Turns a story idea into a finished film: a logline, a short script, a shot list, one still per
shot in a single locked look, each still animated, long shots extended, then one cut with
crossfades, titles and a sound bed. This is the method behind a real film whose every shot came
from these tools, cut with ffmpeg. Read [the tool cheat sheet](../_shared/luma-tools.md) first.

## 1. Check the finish before anything else

Run `ffmpeg -version` and `python3 -c "import PIL"`.

- **ffmpeg present**: you will deliver one film file, plus a smaller copy for phones.
- **No shell or no ffmpeg**: tell the user now that you will make every
  shot and hand over the shots in order with an edit list, and that joining them happens in a
  video editor on their side. Then carry on.

## 2. Ask only for what is missing, in one message

Ask only for what the brief leaves out and you cannot choose yourself: the story, when there is no
idea at all, and the photo or the character sheet, when the brief mentions one you do not have.
For everything else, pick a default, state your picks in one line with the plan, and go ahead.

- **Story**: the idea or a logline, the mood, how it ends. The user's to give; you can shape a
  bare idea into a logline yourself.
- **Length**: from the brief, otherwise short, a handful of shots.
- **Shape**: from the brief or where it will be shown, otherwise landscape.
- **Look**: from the brief, otherwise one that suits the story.
- **Characters**: invented, based on a photo they own or have the right to use (see "Getting the
  user's photo into Luma" in the cheat sheet), or a sheet from the `character-sheet` workflow (use
  its anchor and character line). Invented, unless the brief says otherwise.
- **Sound**: sound made with the shots (the default), their own music file, or silent.
- **Titles**: the words the brief gives, otherwise a short title you write from the story and no
  end card line.

## 3. Read the catalog

`get_account` (consent). Then `list_models` for `text-to-image`, `image-edit`,
`image-to-video`, `frames`, `extend` and `text-to-video`. For each, note the models, `durations`,
`durations_with_audio`, which rows have the audio variant, and `aspect_ratios`. Choose the film's
`aspect_ratio` to match the shape: a value the `text-to-image` and `image-edit` rows both list (and
`text-to-video`, for text shots); the rows are the only check, so use a listed value. Model values
are per feature; do not reuse one feature's model value in another.

## 4. Plan the sound before the shots

Image-to-video clips are silent; most shots will be. Decide now where the sound comes from:

- One shot per place or mood that makes sound: a text-to-video establishing shot, a frames shot, or
  an extend, each with `audio: true` and a model whose row has the audio variant. End its prompt
  with a line such as "Sound: wind, rain on glass, distant thunder."
- In the cut, silent shots borrow that sound (muffled for an interior), or sit over a bed looped
  from a quiet stretch of it. See [ffmpeg steps 5 to 7](references/ffmpeg.md).
- Or the user's own music under the whole cut, added after the join
  ([reel edit R4](../memory-reel/references/reel-edit.md)), if they have the right to use it.

## 5. Write the film

1. **Logline**: one sentence.
2. **Beats**: one beat per shot, in order, with a clear ending.
3. **Shot count**: fit the length with the durations the models list. Each crossfade overlaps two
   shots by its length, so the film is the sum of the shots minus the transitions.
4. **The look line**: one sentence (medium, lens, colour grade, grain, light) that opens every
   still prompt word for word. This is what makes separate stills match. For a street, shop or
   city shot, add "shopfronts plain and unlettered, no signs, logos or writing" unless the user
   wants signage.
5. **Character lines**: one fixed description per character (age, hair, clothes, colours), repeated
   in every still that shows them.
6. **The shot list**, one row per shot, in the format in [the shot list reference](references/shot-list.md):
   beat, still (new, or an edit of which anchor), mode, duration, audio, motion prompt, transition.

Pick each shot's mode:

| Shot | Mode |
|---|---|
| Most shots: a moment that moves | `image`: animate the checked still |
| A move from one composition to another (a turn, a reveal, a light sweeping across) | `frames`: two stills made as edits of one anchor; can carry audio with an audio-capable frames model |
| A wide establishing shot that should carry sound | `text`, with `audio: true` |
| A shot longer than one duration allows | `extend` the finished shot; the extend output replaces the original in the cut |
| Optional: a flashback or dream look | `apply_template` `kind: "style"` on a finished shot, made once that shot has its `media_url` |

Show the user the logline, the beats and the shot list in one message, then start the stills.
With a shell, save it as `shots.md` in the project folder and fill in ids as they arrive, so a
dropped session can resume.

## 6. One run, stills to shots

The film runs straight through: the stills, your own check of them, then the shots, without
stopping between. See "Credits and account status" in the cheat sheet.

- Say the plan in one line: how many stills, how many shots of each mode, which carry sound, and
  any extends or style passes, which follow their source shot.
- Stills are quick, video takes minutes, so make and check every still before animating any.
- If a call is refused for not enough credits, follow "Credits run out midway" at the end.

## 7. Make the stills

- **Anchors first**: one `generate_image` `mode: "text"` per character or place: look line, then
  character line, then the moment, with the film's `aspect_ratio`. When one character or object
  is in every shot and only the place changes, make that one anchor and make every place as an
  edit of it ("Same <subject>, now <new place>"). Text anchors per place are for places the
  character is not in.
- **Every other still is an edit of its anchor**: `mode: "edit"`, `image` the anchor's
  `generation_id`, `aspect_ratio` the same, prompt "Same <character>, same <clothes>, <the new
  moment>. Keep the same film look." Always edit from the anchor, never from a previous edit, so
  drift does not add up.
- **Frames pairs**: two edits of the same anchor, one for the first frame and one for the last.
- Keys: `<film>-<run>-k<nn>-<slug>`, such as `lighthouse-k7f2-k03-crank`, where `<run>` is four
  random characters chosen once for the whole film (see the cheat sheet); a retake is `...-t2`.
- `generate_image` usually answers with the `media_url`. Wait for it before using a still as input.
- **Check them together, yourself.** With ffmpeg, download them and build a contact sheet
  ([ffmpeg step 3](references/ffmpeg.md)) and look at it: the same face and clothes, the same
  palette, room in the frame for the planned motion. Without a shell, look at each link in shot
  order. Show the user the stills in shot order, then go straight on to step 8.
- **A still that breaks continuity** (a drifted face, the wrong clothes, garbled text) is not
  animated. Animate every still that passed, and in the same message name the one that failed,
  say why, and offer a retake from its anchor (a new key, `...-t2`). Make it when the user asks,
  then animate it.

## 8. Animate the shots

Call shapes (all values from `list_models`; the prompt describes motion, not the picture; see
[the prompt patterns](../generate/references/prompting.md)):

```
generate_video {"mode": "image", "image": {"generation_id": "<still>"}, "prompt": "<motion, camera>",
  "model": "<image-to-video model>", "duration": <a listed duration>, "client_request_id": "<film>-<run>-s02-lamp"}
generate_video {"mode": "frames", "start_image": {"generation_id": "<first>"}, "end_image": {"generation_id": "<last>"},
  "prompt": "<the path between them>. Sound: ...", "model": "<frames model with an audio row>",
  "duration": <a listed duration with audio>, "audio": true, "client_request_id": "<film>-<run>-s04-beam"}
generate_video {"mode": "text", "prompt": "<look line>. <establishing shot>. Sound: ...", "model": "<model with an audio row>",
  "duration": <from durations_with_audio>, "aspect_ratio": "<the film's>", "audio": true, "client_request_id": "<film>-<run>-s01-storm"}
```

- Image mode takes no `audio` and no `aspect_ratio`; sending them is refused.
- Start shots in batches of about five, then poll each with `get_generation` (`wait_seconds` up
  to 25) until its `media_url` arrives. Each shot takes a few minutes. If a call is rate-limited,
  wait the seconds it names and retry with the same key.
- **Extends wait for their source.** When the source shot has its `media_url`, call
  `generate_video` `mode: "extend"` with `video` its `generation_id`, a prompt for what happens
  next, and a model and duration from the extend row. A planned style pass follows the same way:
  `apply_template` `kind: "style"` with `video` the shot's `generation_id`, once it has its
  `media_url`.
- Keys: `<film>-<run>-s<nn>-<slug>`; a retake is `...-t2`. Never reuse a key for a retake.

## 9. Check every shot

- With ffmpeg: download each clip as soon as its link arrives (links last one hour), probe it and
  add its first and last frames to a sheet ([ffmpeg steps 2 and 3](references/ffmpeg.md)). Step 3
  also lists any cut hidden inside a clip.
- Look for a face or costume that drifted, warped hands, the action not happening, text that came
  out garbled or that names a real brand (shop signs, vehicles, packaging), a cut hidden inside
  the clip, and a camera move that fights the next shot.
- A shot that fails the brief: say which shot and why, and offer a retake (a new job with a new
  key); make it when the user asks. A failed shot shows its error, `retryable` and `refunded` in
  `get_generation`: when `retryable` is true, run it once more as a new job with a new key, and
  tell the user only if that one fails too.

## 10. Cut the film (with ffmpeg)

Follow [the ffmpeg reference](references/ffmpeg.md) in order:

1. Pick the output size and frame rate (step 4, with `R` set to the film's `aspect_ratio`).
2. Normalise each clip to its planned length, and give every silent shot a sound: borrowed or
   bed (steps 5 to 7). Use each extend output in place of its source. Music goes on after step 4
   of this list, with [reel edit R4](../memory-reel/references/reel-edit.md) (then
   `mv film-music.mp4 film.mp4`).
3. Render the title over the first shot and an end card (step 8), with the words the user gave,
   or the title you wrote and named in the plan.
4. Join with crossfades, or hard cuts (steps 9a or 9b), which also sets the loudness.
5. Check the length, the loudness, unplanned silence and a contact sheet of the cut (step 10). Fix
   and re-cut until it is clean.
6. Make the phone copy (step 11).
7. When the film is going on social media, offer a social cut with [the social finish](../_shared/social-finish.md):
   a vertical master (an `edit_video` reframe of the shots, or a crop), captions for any speech,
   -14 LUFS and the posting copies. Make it when the user asks.

Hand over: the paths of both files, the running time, and the shot list with every
`generation_id`. Offer changes: a new cut, title or transition is only a re-edit here; a new shot
is a new job with a new key, made when the user asks.

## 11. Without a shell: the edit list

Say plainly that the film is not joined here, then deliver, in order:

| # | Shot | generation_id | Link (valid one hour) | Use from/to | Transition into the next | Sound under it |
|---|---|---|---|---|---|---|

Add the title and end card text with when they appear. Tell the user to download the clips now,
and that `get_generation` or `list_generations` gives fresh links later. Any video editor can
assemble it from this list.

## When something goes wrong

- **Moderation refused a still or a shot**: say which input, and change the idea with the user.
  Never reword a prompt to get it past the check.
- **A character drifts**: re-edit from the anchor, not from the drifted still.
- **Credits run out midway** (`insufficient_credits`): stop and do not retry. Hand over what is
  made (ids and links), say once that the balance does not cover the rest, and list the stills and shots still to make. Offer a smaller film: fewer
  shots, fewer audio shots, the default models, or the user's own music instead of generated
  sound. Resume later from `shots.md` or `list_generations`.
- **A session dropped**: `list_generations` (`kind: "image"` and `"video"`) and match the prompts to
  the shot list.
- **"that generation has no finished file yet"**: the input is still being saved; wait for its
  `media_url`.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
