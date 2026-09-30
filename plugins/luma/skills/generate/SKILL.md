---
name: generate
description: Use when the user wants Luma to make a picture or a video clip from an idea, a photo, or one of their own Luma videos, and no more specific Luma workflow fits. Picks the tool, mode, model and settings, quotes the cost, runs it and shows the result.
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
`get_workflow` with its name; in Claude Code, use the skill of the same name. If neither is
available, carry on here.

| The user wants | Workflow |
|---|---|
| A story told in several shots: a short film, a trailer, a scene with titles and sound | `short-film` |
| One photo brought to life, "make this photo move" | `photo-to-video` |
| A photo, or one of their Luma videos, redrawn in a look (anime, oil paint, noir) | `restyle` |
| Several photos from a trip or an event turned into one recap clip | `memory-reel` |
| A vertical clip for social media that grabs attention in the first second, or a loop | `vertical-hook` |
| The same character kept consistent across several pictures or scenes | `character-sheet` |
| A product photo turned into clean shop or ad clips | `product-clip` |

## Ask first, in one message

Ask only what the brief leaves open, all in one message. When the brief already answers
everything, state your assumptions and go straight to the quote.

- **What**: a picture, a clip, or both, and the idea in a sentence.
- **Starting point**: nothing, a photo (see "Getting the user's photo into Luma" in the cheat
  sheet), or one of their Luma pictures or videos.
- **Shape**: landscape, vertical or square.
- **Length and sound** for a clip.
- **Look**: style, mood, lighting, any reference.
- **How many** variations, and whether quality or cost matters more.

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

Two rules of thumb:

- **For control, go through a still.** Make the picture first (text or edit), let the user approve
  it, then animate it with image mode. A clip straight from text is quicker but harder to steer.
- **Generated sound comes from text, frames and extend** with `audio: true` and a model whose
  `list_models` row has the audio variant; some effect templates also bring their own soundtrack.
  Image-to-video is always silent. For sound on an animated photo, add it in the edit, or make a
  `frames` clip with `audio: true` from the photo to an edit of it. An extend with audio adds sound
  only to its new seconds.

## Read the catalog

1. `get_account`. If `consent_required` is true, send the user to the consent link first.
2. For a model-backed call, `list_models` with that feature. Use the default model unless the user
   asked for the best quality (quote the other listed models too), needs sound (an audio row), or
   needs a duration or shape that only another model lists. Take `duration`, and `aspect_ratio`
   where the mode takes it, from that model's row; never guess them.
3. For a style or an effect, `list_templates` with the kind, and `category` or `query` from the
   brief. Show the user three to five matches with their `preview_url` and let them pick.
4. Write the prompt with [the prompt patterns](references/prompting.md).

## Plan and quote

1. Say the plan in one line: how many pictures and how many clips, and in which modes.
2. Run `estimate_cost` once per distinct call shape with exactly the arguments you will send.
   Multiply by the count, add up, and show the total, the balance and whether it is enough. For a
   still you will animate, quote the still, make it, then quote the animation with its
   `generation_id` (or with the user's photo) before running it.
3. Say that every variation and every retake is its own generation and its own charge.
4. Wait for the user's yes. A yes covers this plan only; a new step gets a new quote.

## Run

Send each generation with a fresh `client_request_id` built from the idea, a run tag chosen once
for this conversation (see the cheat sheet) and a number. Examples (values in angle brackets come
from the catalog or from earlier answers):

```
generate_image {"mode": "text", "prompt": "...", "aspect_ratio": "<from list_models>", "client_request_id": "fox-snow-0930a-still-1"}
generate_video {"mode": "image", "image": {"generation_id": "<the approved still>"}, "prompt": "...", "client_request_id": "fox-snow-0930a-clip-1"}
generate_video {"mode": "text", "prompt": "... Sound: ...", "model": "<a model with an audio row>",
  "duration": <one of its durations_with_audio>, "audio": true, "client_request_id": "fox-snow-0930a-clip-2"}
```

Start the jobs of the step (in batches of about five), then poll them. A picture used as the input of the next call must
have its `media_url` first; if `generate_image` answered with `poll_after_seconds`, wait for it with
`get_generation`.

## Check and show

- Poll each video with `get_generation` (`wait_seconds` up to 25) until `poll_after_seconds` is
  null. Do not narrate each poll.
- Show each result as its `media_url` with a short label. Links last one hour.
- When you can see the picture, check it against the brief before calling it done: the subject,
  the count of people or objects, any text, hands and faces, the shape. Say what is off.
- Offer the obvious next step: an edit, another variation, animate the still, extend the clip, a
  style. Each is a new job with a new key and its own quote.

## Finish

- **Without a shell**: list what was made, in order, with each `media_url` and `generation_id`,
  and tell the user the links expire in an hour and that `list_generations` finds everything later.
- **With a shell**: offer to download the files into a project folder (`curl -sSL -o <name>
  "<media_url>"`), named by what they are.
- If the user wants several clips joined into one file, that is the `short-film` workflow's finish;
  its [ffmpeg reference](../short-film/references/ffmpeg.md) has the commands.

## When something goes wrong

The cheat sheet's refusal table covers every message. The ones that come up most here:

- **Arguments refused** ("X is not used when mode is 'Y'"): fix from the cheat sheet's mode table.
  Nothing was charged. Use a new key.
- **Audio refused without a model**: pass the model the message names.
- **Moderation refusal**: it is final. Tell the user which input was refused, and do not reword the
  prompt to slip past it. They may choose a different idea.
- **Not enough credits**: stop, show the account link, offer a smaller plan.
- **A failed generation**: read `error.message`, `retryable` and `refunded` from `get_generation`;
  offer a retry only as a new job, quoted, with a new key.
- **No answer, a timeout**: retry the same call with the same key; you get the first result, not a
  second charge.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer jobs at once.
