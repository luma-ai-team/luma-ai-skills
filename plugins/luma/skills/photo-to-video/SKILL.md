---
name: photo-to-video
description: Use when the user has one photo and wants it to move, such as "bring this photo to life", "animate my picture" or "turn this photo into a video". Offers the Luma effects that fit it plus a plain animation, quotes each, runs the ones they pick and shows the results.
title: Bring a photo to life
needs_shell: false
---

# Bring a photo to life

One photo in; a few short clips out, side by side: two or three ready-made effects that suit the
photo, and one plain animation that keeps the photo's framing and adds gentle motion. Every option
is quoted before it runs. Read [the tool cheat sheet](../_shared/luma-tools.md) first.

## 1. Ask first, in one message

- **The photo, and how it reaches Luma.** Luma cannot read a file attached to the chat. Ask for one
  of: a direct https link to the image file (works in every client), the path of a file on this
  computer (only when you have a shell), or one of their Luma pictures. If they attached a photo,
  say plainly that you cannot pass it to Luma from the chat, and ask for a link or a path.
- **The feel** they want: playful, cinematic, a dance, a greeting, something magical.
- **How many options**: default two effects and one plain animation.
- **Rights**: the photo is theirs, or they have the right to use it, and anyone in it agreed.

Sound: say up front that an effect may come with its own soundtrack and the plain animation is
silent.

## 2. Bring the photo in

- **A link**: `upload_media` `{"action": "from_url", "url": "<direct link>"}`. The answer has the
  `upload_id`. A link to a page that shows the photo (a Drive or Dropbox preview) is refused; ask
  for the direct download link.
- **A file here, with a shell**: `upload_media` `{"action": "start", "content_type": "<its MIME
  type, from file --mime-type -b <file>>", "size": <bytes, from wc -c < <file>>}`. Run the
  `curl -X PUT` command from the answer with the file, then
  `{"action": "confirm", "upload_id": "<id>"}`.
- **A Luma picture**: `list_generations` `{"kind": "image"}`, let the user pick, use its
  `generation_id`.

Look at the photo if you can see it: who or what is in it (one person, a couple, a group, a pet, a
product, a place), how it is framed, which way it is oriented. If you cannot see it, ask the user
what is in it in one line.

## 3. Pick the effects

1. `list_templates` `{"kind": "effect", "limit": 5}` to read the full `categories` list.
2. Search where the subject fits: `category` (exact name from that list) and, when useful, `query`.
   `query` matches only an effect's name or key, not its subject, so a word like "cat" or "dog"
   often returns nothing; use it for a word likely in a name, such as dance, wizard or bounce. For
   an animal, open the pet category and also try `query: "pet"`. Read a page of results.
3. Keep effects whose `input_count` is 1. An effect that takes two photos needs a second photo;
   offer one only when the user has it.
4. Choose two or three that match the subject and the feel. An effect built around a full body
   needs a photo that shows one; a close-up face suits a close-up effect.
5. Show each with its name, its `credits`, one line on why it fits this photo, and its
   `preview_url`, so the user sees the price and a sample before anything is spent. With a shell,
   download the previews and look at them on one contact sheet
   ([ffmpeg step 3](../short-film/references/ffmpeg.md)) before recommending any.

An effect sets its own shape and framing (some add black bars), so an effect clip can differ from
the photo's shape; its `preview_url` shows what to expect. Only the plain animation keeps the
photo's shape.

## 4. Write the plain animation

`generate_video` `mode: "image"` with the photo as `image` and a prompt of gentle motion that suits
it: hair and clothes stirring, a blink and a small smile, clouds and water moving, a slow push-in.
Describe motion only; the photo already fixes who and where. Take `model` and `duration` from the
`image-to-video` row of `list_models` (the default model unless the user wants the best quality).
The clip keeps the photo's shape and has no sound.

## 5. Quote and confirm

- `get_account` (balance, consent).
- `estimate_cost` for each chosen effect:
  `{"tool": "apply_template", "kind": "effect", "key": "<key>", "images": [<the photo>]}`.
- `estimate_cost` for the plain animation with exactly its generate arguments.
- Show one short list: each option and its price, the total, the number of generations and the
  balance. Let the user drop options, then ask for a yes.
- A clean quote does not promise an effect will run. Start one effect first and confirm it
  completes before starting the rest.

## 6. Run

```
apply_template {"kind": "effect", "key": "<key>", "images": [{"upload_id": "<id>"}], "client_request_id": "<photo>-<run>-fx-<key>"}
generate_video {"mode": "image", "image": {"upload_id": "<id>"}, "prompt": "<motion>", "model": "<from list_models>",
  "duration": <a listed duration>, "client_request_id": "<photo>-<run>-animate-1"}
```

`<run>` is four random characters chosen once for this conversation (see the cheat sheet), such
as `k7f2`. A retake of an option gets a new key, `...-t2`.

Start them in batches of about five, then poll each with `get_generation` (`wait_seconds` up to 25) until
`poll_after_seconds` is null. Do not narrate the polling.

## 7. Show the results

- List the clips in the order you offered them, each with its name and `media_url`, so the user
  can compare. Links last one hour.
- Ask which they like, and offer next steps, each a new job with its own quote and key: another
  effect, the plain animation again with different motion, an extend of a clip (new seconds; any
  generated sound covers only those seconds), or a restyle (the `restyle` workflow).
- **With a shell**: offer to download the clips into one folder. To join the favourites into a
  single preview, use a new folder holding only them, as `s01.mp4`, `s02.mp4` in the order
  offered, and follow [the ffmpeg reference](../short-film/references/ffmpeg.md): step 4 with `R`
  set to the plain animation's width and height (from `ffprobe` on it), or without one the photo's
  upright size (step 2); step 6 as `norm sNN.mp4 cNN.mp4 <the clip's own
  seconds, from ffprobe>` for each clip, with no other arguments; step 9b with only
  `c01.mp4 c02.mp4 ...` in `cuts.txt` (no titles, end card or sound bed).
- The effect clips may carry sound and the plain animation has none, so a joined preview goes
  silent during the animation. Say so, and offer a sound bed (ffmpeg step 5) or to keep the clips
  as separate files.
- **Without a shell**: give each `generation_id` with its link, and say that `list_generations`
  finds them later with fresh links.

## When something goes wrong

- **The link is refused**: pass the message on. A web page instead of the file needs the direct
  link; a file too big for `from_url` needs a shell and `action: "start"`.
- **"this effect takes N photos"**: pick a one-photo effect, or ask for the other photos.
- **Moderation refused the image**: it is final for this photo. Tell the user; do not crop, edit or
  reword to get it through.
- **An effect or animation failed**: show `error.message` and whether it was `refunded`; a retry is
  a new job, quoted, with a new key.
- **An effect that fails on its first poll with "The generator failed on this one"** will most
  likely fail again, whatever `retryable` says. Do not retry the same effect; offer a different
  one, once. If two different effects fail this way in a row, stop, tell the user which worked and
  which did not, and deliver what you have.
- **"Too many requests"**: wait the seconds it names, retry the same call with the same key, and
  start fewer jobs at once.
- **Not enough credits**: stop, show the account link from the refusal, offer fewer variants.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
