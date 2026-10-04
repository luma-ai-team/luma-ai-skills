---
name: generate
description: Use when the user wants Luma to make a picture or a video clip from an idea, a photo, or one of their own Luma videos, and no more specific Luma workflow fits. Picks the tool, mode, model and settings, makes it and shows the result.
title: Make anything with Luma
needs_shell: false
---

# Make anything with Luma

The base workflow. It turns a brief into one picture, one clip, or a few variations, and it sends
bigger jobs to the specialised workflows. Read [the tool cheat sheet](../_shared/luma-tools.md)
before the first Luma call; this file assumes it.

## Hand off when a specialised workflow fits

Check the brief against this table first. When one row fits, tell the user in one line which
workflow you are switching to and why, then load it: through the Luma connector, call
`get_workflow` with its name; when local skills are available, use the skill of the same name. If neither is
available, carry on here.

| The user wants | Workflow |
|---|---|
| A story told in several shots: a short film, a trailer, a scene with titles and sound | `short-film` |
| One photo brought to life, "make this photo move" | `photo-to-video` |
| A photo, or one of their Luma videos, redrawn in a look (anime, oil paint, noir) | `restyle` |
| Several photos from a trip or an event turned into one recap clip | `memory-reel` |
| A vertical clip for social media that grabs attention in the first second, a loop, a character doing a trend's movement, or their own video made vertical | `vertical-hook` |
| The same character kept consistent across several pictures or scenes | `character-sheet` |
| A product photo turned into clean shop or ad clips, or a product video changed for a season or a scene | `product-clip` |
| A talking-head, UGC or spokesperson ad: a face and a voice recording selling a product | `talking-ad` |
| One video they already have, in the other shapes for Reels, a feed, YouTube or a shop, or sharper | `every-feed` |

## Ask only for what is missing, in one message

Ask only for what the brief leaves out and you cannot choose yourself: what to make, when there is
no idea at all, and the photo or video to start from, when the brief mentions one you do not have.
Everything else, pick a sensible default, state it in the plan line, and go ahead.

- **What**: a picture, a clip, or both, and the idea in a sentence. The user's to give.
- **Starting point**: nothing, a photo (see "Getting the user's photo into Luma" in the cheat
  sheet), or one of their Luma pictures or videos. The user's to give.
- **Shape**: landscape, vertical or square. When the brief says where it goes, take the shape from
  that: a blog or website header or a video thumbnail is landscape (a wider value, or a squarer
  one for a banner, when the row offers both), a story or a Reel is vertical, a feed post or a
  profile picture is square. When it says nothing, use the model's default. Take the exact value
  from the model's row.
- **Length and sound** for a clip: from the brief, or the defaults below.
- **Look**: style, mood, lighting, any reference: from the brief, or what suits the idea.
- **How many**: what the brief asks for, otherwise one.

## Choose the call

| The brief | Call |
|---|---|
| A picture from words | `generate_image` `mode: "text"` |
| Change something in a picture (background, clothes, time of day, add or remove an object) | `generate_image` `mode: "edit"` with `image` and `prompt` |
| A picture in a ready-made look | `generate_image` `mode: "style"` with `image` and a `style` key |
| A clip from words | `generate_video` `mode: "text"` |
| Animate a picture | `generate_video` `mode: "image"` |
| A clip that moves from one picture to another | `generate_video` `mode: "frames"` |
| One of their clips, longer | `generate_video` `mode: "extend"` |
| A ready-made effect on one or more photos | `apply_template` `kind: "effect"` |
| One of their clips in a look | `apply_template` `kind: "style"` |
| Change something in a video (a new background, outfit, season or character) | `edit_video` `mode: "edit"` with `video` and `prompt` |
| A video in another shape (vertical for Reels, square for a feed) without cutting anything off | `edit_video` `mode: "reframe"` with `video` and `aspect_ratio` |
| A video sharper or smoother (higher resolution or frame rate) | `edit_video` `mode: "enhance"` with `video` |
| The person or character in a photo doing the movement of a video | `edit_video` `mode: "motion"` with `video` and `image` |
| The face in a photo speaking or singing an audio file | `lip_sync` with `image` and `audio_file` |

`edit_video` takes a video the user uploaded (`upload_media`, an `upload_id`) as well as one of
their Luma videos; nothing else does. Its result, like a lip-sync, is as long as the source (the
audio, for a lip-sync), which must fit the `source_limits` of its feature in `list_models`. Motion
and lip-sync put a real face to work: only a face the user owns or has that person's permission to
use, and a voice they have the right to use.

Two rules of thumb:

- **For control, go through a still.** Make the picture first (text or edit), check it against
  the brief, then animate it with image mode. A clip straight from text is quicker but harder to
  steer. Take the still route when a specific look must hold (a character, a product, a logo), and
  say so in the plan line. For scenery, animals and mood pieces, go straight to text.
- **Generated sound comes from text, frames and extend** with `audio: true` and a model whose
  `list_models` row has the audio variant; some effect templates also bring their own soundtrack.
  Image-to-video is always silent. For sound on an animated photo, add it in the edit, or make a
  `frames` clip with `audio: true` from the photo to an edit of it. An extend with audio adds sound
  only to its new seconds.

## Read the catalog

1. `get_account`. If `consent_required` is true, send the user to the consent link, and carry on
   once they have accepted.
2. For a model-backed call, `list_models` with that feature. Use the default model unless the user
   asked for the best quality (then the listed model whose rows price highest, usually the top
   tier), needs sound (an audio row), or needs a duration or shape that only another model lists.
   Take `duration`, and `aspect_ratio` where the mode takes it, from that model's row; never guess
   them. Pictures from text have one model and no `model` field: take `aspect_ratios` from its row.
3. For a style or an effect, `list_templates` with the kind, and `category` or `query` from the
   brief. When the brief names the look or the effect, take the match. When it does not, show the
   user three to five matches with their `preview_url` and let them pick the one they like: a
   choice of look only they can make.
4. Write the prompt with [the prompt patterns](references/prompting.md).

## Plan in one line

1. Say the plan in one line: how many pictures and how many clips, in which modes, and for each
   clip whether it has sound. A clip from text, frames or extend made without `audio: true` is
   silent, as image clips always are. Take sound from the brief. When the brief does not mention
   it, make the clip silent and add in one line that a version with sound can be made.
2. Run it straight after the plan line. See "Credits and account status" in the cheat sheet. For a still you will animate, make the still, check it, then animate it with its
   `generation_id` (or with the user's photo).

## Run

Send each generation with a fresh `client_request_id` built from the idea, a run tag chosen once
for this conversation and a number. `k7f2` below stands for four random characters you choose once
for this conversation (see the cheat sheet). Examples (values in angle brackets come from the
catalog or from earlier answers):

```
generate_image {"mode": "text", "prompt": "...", "aspect_ratio": "<from list_models>", "client_request_id": "fox-snow-k7f2-still-1"}
generate_video {"mode": "image", "image": {"generation_id": "<the checked still>"}, "prompt": "...", "client_request_id": "fox-snow-k7f2-clip-1"}
generate_video {"mode": "text", "prompt": "... Sound: ...", "model": "<a model with an audio row>",
  "duration": <one of its durations_with_audio>, "audio": true, "client_request_id": "fox-snow-k7f2-clip-2"}
```

Start the jobs of the step (in batches of about five), then poll them. A picture used as the input of the next call must
have its `media_url` first; if `generate_image` answered with `poll_after_seconds`, wait for it with
`get_generation`.

## Check and show

- Poll each video with `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is
  null. Do not narrate each poll.
- Show each result as its `media_url` with a short label. Links last one hour.
- When you can see the picture, check it against the brief before calling it done: the subject,
  the count of people or objects, any text, hands and faces, the shape. Say what is off, and
  offer a retake when it misses the brief.
- Offer the obvious next step: an edit, another variation, animate the still, extend the clip, a
  style. Each is a new job with a new key; make it when the user asks.

## Finish

- **Without a shell**: list what was made, in order, with each `media_url` and `generation_id`,
  and tell the user the links expire in an hour and that `list_generations` finds everything later.
- **With a shell**: offer to download the files into a project folder (`curl -sSL -o <name>
  "<media_url>"`, a still as `.jpg`), named by what they are. For a clip that will play on a web
  page, offer the muted web copy in [ffmpeg step 11](../short-film/references/ffmpeg.md). For a
  picture meant as a full-width header, tell the user its pixel size (read it from the file) so
  they can judge whether it is wide enough.
- If the user wants several clips joined into one file, that is the `short-film` workflow's finish;
  its [ffmpeg reference](../short-film/references/ffmpeg.md) has the commands.
- For a clip that will be posted or used in a shop, offer [the social finish](../_shared/social-finish.md):
  captions, music under the voice, the frame and loudness each platform wants.

## When something goes wrong

The cheat sheet's refusal table covers every message. The ones that come up most here:

- **Arguments refused** ("X is not used when mode is 'Y'"): fix from the cheat sheet's mode table.
  Nothing was charged. Use a new key.
- **Audio refused without a model**: pass the model the message names.
- **Moderation refusal**: it is final. Tell the user which input was refused, and do not reword the
  prompt to slip past it. They may choose a different idea.
- **Not enough credits**: stop and do not retry. Hand over what is made (ids and links), say once
  that the balance does not cover the rest, say what is
  left to make, and offer a smaller version.
- **A failed generation**: read `error.message`, `retryable` and `refunded` from `get_generation`.
  When `retryable` is true, run it once more as a new job with a new key, and tell the user only if
  that one fails too. Otherwise show the error.
- **No answer, a timeout**: retry the same call with the same key; you get the first result, not a
  second charge.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer jobs at once.
