# Luma tools: the cheat sheet every workflow uses

Read this before the first Luma call in a conversation. Every workflow in this bundle links here
instead of repeating it. The tools themselves are the authority: when a tool's description or
answer says something different from this page, follow the tool.

Prices, durations, aspect ratios, resolutions and model names change with the catalog. Never quote
one from memory or from this page. Read them at run time from `list_models`, `list_templates` and
`estimate_cost`.

## The ten tools

| Tool | Use it to | Spends credits |
|---|---|---|
| `get_account` | Read the balance, the plan, and whether the content policy still needs accepting | No |
| `list_models` | See each feature's models, the settings each accepts, and the price per unit | No |
| `list_templates` | Search effects (photos into a short video) and styles (a look for a photo or video) | No |
| `list_generations` | Find the user's recent generations, including running and failed ones | No |
| `get_generation` | Read one generation's status, wait for it, get its `media_url` | No |
| `estimate_cost` | Price a call before running it, from the same arguments | No |
| `upload_media` | Bring an outside photo into Luma and get an `upload_id` | No |
| `generate_image` | Make or change a picture | Yes |
| `generate_video` | Make a clip from a prompt, a photo, two frames, or extend one of the user's videos | Yes |
| `apply_template` | Run an effect on photos, or restyle one of the user's videos | Yes |

## Modes, and the arguments each one takes

Each generation tool is one flat object with a mode (`mode`, or `kind` for `apply_template`). A
field the mode does not list is refused, and so is a missing required field. Every generation call
also takes `client_request_id` (required, see Idempotency below).

| Call | Required | Optional | Catalog feature in `list_models` |
|---|---|---|---|
| `generate_image` `mode: "text"` | `prompt` | `aspect_ratio` | `text-to-image` |
| `generate_image` `mode: "edit"` | `image`, `prompt` | `aspect_ratio` | `image-edit` |
| `generate_image` `mode: "style"` | `image`, `style` | none | not listed; `estimate_cost` prices it |
| `generate_video` `mode: "text"` | `prompt` | `model`, `duration`, `aspect_ratio`, `audio` | `text-to-video` |
| `generate_video` `mode: "image"` | `image` | `prompt`, `model`, `duration` | `image-to-video` |
| `generate_video` `mode: "frames"` | `start_image`, `end_image` | `prompt`, `model`, `duration`, `audio` | `frames` |
| `generate_video` `mode: "extend"` | `video` | `prompt`, `model`, `duration`, `audio` | `extend` |
| `apply_template` `kind: "effect"` | `key`, `images` (a list of photos) | none | `list_templates` kind `effect` |
| `apply_template` `kind: "style"` | `key`, `video` | `tier` (`"fast"` default, or `"max"`) | `list_templates` kind `style` |

Things the table implies that are easy to miss:

- **Image-to-video takes no `audio` and no `aspect_ratio`.** The clip comes out silent (the file has
  no audio track at all) and in the shape of the photo. To get a vertical or square clip from a
  photo, make the still in that shape first (`generate_image` text or edit with `aspect_ratio`),
  then animate the still. For sound, use text-to-video, frames or extend with `audio: true`, an
  effect that brings its own soundtrack, or add sound in the edit.
- **Frames and extend take no `aspect_ratio` either**; they follow their inputs.
- **Style is named twice.** `generate_image` style mode takes the style's key as `style`;
  `apply_template` takes it as `key`. Both keys come from `list_templates` kind `style`.
- **An effect takes exactly `input_count` photos**, as `list_templates` shows for that effect. Any
  other number is refused before anything is charged.
- **Extend returns the whole clip**, the original plus the new seconds, as one file. In an edit, use
  the extended clip in place of the original, never both. When the original was silent and the
  extension asked for audio, the first part of the new file stays silent.
- **Prompts have a length ceiling.** An over-long prompt is refused with the limit in the message.
  One focused paragraph per prompt is enough.

## Media is an id, never a link

- A photo is `{"upload_id": "..."}` (from `upload_media`) or `{"generation_id": "..."}` (one of the
  user's own images). Pass exactly one of the two.
- A video is only `{"generation_id": "..."}` of one of the user's own finished video generations.
  Videos cannot be uploaded; say so up front when a workflow needs one.
- An input must be finished: `status` completed and a `media_url` present. A picture whose file is
  still being saved (`media_state: "transferring"`) is refused as not ready; wait with
  `get_generation` until it shows a `media_url`, then use it.
- Ids of another account's generations, deleted ones and made-up ones all read as "no generation
  with that id on this account".

### Getting the user's photo into Luma

Chat attachments do not reach Luma by themselves: the Luma tools run on Luma's servers and cannot
read a file attached to the conversation. Three ways in:

1. **`upload_media` `action: "from_url"` with `url`**: Luma downloads a public https link itself and
   answers with a ready `upload_id`. The link must be the file, not a page that shows it (a Drive or
   Dropbox preview page is refused; ask for the direct download link). Works in every client.
2. **`action: "start"` with `content_type` and `size` (bytes), then a PUT, then `action: "confirm"`
   with the `upload_id`**: for a file on the user's machine, when you have a shell. The `start`
   answer contains a ready `curl -X PUT` command and an expiry; replace `@FILE` in it with
   `@<path>`, run it, then confirm. Also the route
   for a file too large or too slow for `from_url` (the refusal says so).
3. **A Luma image the user already has**: find it with `list_generations` `kind: "image"` and pass
   its `generation_id`.

Without a shell, only 1 and 3 work. Say so plainly and ask for a direct link; do not pretend an
attachment was uploaded. Photos only; the tool names the accepted types, and iPhone HEIC photos are
among them.

## Reading the catalog

- `list_models` with `feature` (`text-to-image`, `image-edit`, `text-to-video`, `image-to-video`,
  `frames` or `extend`; omit it for all) returns `models` (each with `value`, `label`,
  `is_default`) and priced `rows`. Each row has `model`, `variant` (such as `"audio"`),
  `luma_credits` per `per` unit, and `capabilities`: `audio`, `durations`, `durations_with_audio`,
  `aspect_ratios`, `resolutions`, `frame_rates`.
- Pass only values the chosen model's row lists. Omit `model`, `duration` or `aspect_ratio` to get
  the feature's default.
- **Model values belong to one feature.** Each feature lists its own models, and frames, for one,
  can use different values from text-to-video. Never carry a model value from one feature to
  another.
- **Audio may need a named model.** Passing the model of a row with the audio variant always
  works: find a row for that feature with `variant: "audio"` and `capabilities.audio: true`, and
  pass that row's `model` together with `audio: true`. Leaving `model` out works only when the
  default model has an audio row, and is otherwise refused with the model to pass ("The default
  model ... has no audio option. Pass model ..."); pass the model it names. With audio on, the
  allowed durations are `durations_with_audio`, which can differ from `durations`.
- `list_templates` needs `kind` (`"effect"` or `"style"`), and takes `category` (exact, from the
  `categories` list in the answer), `query` (matches name or key) and `limit`. Each template has
  `key`, `name`, `category`, `credits` (effects: per generation; styles: the fast tier per unit of
  `per`), `credits_max` (styles: the max tier), `input_count` and a `preview_url` showing a sample.
  Show the user `preview_url` links before spending; they are free.

## Quote first, then ask

Nothing that spends credits runs before the user says yes to a quote.

1. Call `estimate_cost` with `tool` and exactly the arguments the generate call will take
   (`client_request_id` may be included; it is ignored). It answers `credits`, `rate`, `per`,
   `priced_seconds`, `balance`, `enough` and `shortfall`, and charges nothing.
2. It also refuses, for free, an unavailable model, template or style, a duration the model does
   not offer, a wrong number of effect photos, and an input that is not the user's, the wrong kind,
   or not finished. Fix the plan there. It does not check `aspect_ratio`, a source video's length
   or size, content moderation, or the content-policy consent: a clean quote is not a promise the
   call will run.
3. The quote needs every input to exist and be finished. Edit, image, frames, extend and effect
   prices do not depend on which picture or video, so quote a step whose input is not made yet with
   one that exists (the uploaded photo, or a finished item from `list_generations`); when none
   exists, quote that step as its own gate once its input is made. A video restyle is priced by its
   source's length: quote it with the real source.
4. Quote once per distinct call shape (tool, mode, model, duration, audio, template), multiply by
   how many of that shape the plan has, and add them up.
5. Tell the user, in one short message: how many generations of each kind you plan, the total in
   credits, the balance, and whether it is enough. Then ask for a yes. Mention that a retake of any
   step costs that step again.
6. When `enough` is false, show the shortfall and the account link from the quote, and offer a
   smaller plan. You cannot buy credits for the user.

Use only numbers `estimate_cost` or the catalog returned in this conversation. `get_account` tells
you the balance and whether `consent_required` is true; when it is, send the user to the consent
link before planning any spend.

## Idempotency: `client_request_id`

- Required on `generate_image`, `generate_video` and `apply_template`: a key you choose, 8 to 100
  characters. A readable shape helps resumes: project, a run tag, shot, take, such as
  `lighthouse-0930a-s03-t1`. Choose the run tag once per run (the date plus a letter, or four
  random characters): a key used in any earlier run hands back that run's generation.
- **A fresh key for every new job**, including a retake of the same prompt (`...-t2`).
- **The same key only to retry the same call** when its answer never arrived, the call timed out,
  or the error says to retry with it. The retry returns the first generation with
  `duplicate: true` and `credits_charged: 0` instead of charging again.
- **A new key after any refusal** (credits, consent, moderation, an argument you fixed) and after
  "This generation did not start" or "That client_request_id is already taken".
- Reusing a key for a different request does not make a new generation; it hands back the old one.
- **A first call that answers `duplicate: true` hit a key used before**: nothing new was made, and
  the result shown is the old one. Say so and send it again with a new key.

## Waiting for results

- `generate_image` usually answers with the finished `media_url` in the same call. If it answers
  with `poll_after_seconds` instead, poll as below.
- `generate_video` and `apply_template` answer at once with a `generation_id` and
  `poll_after_seconds`. A video takes minutes.
- Poll with `get_generation` `generation_id` and `wait_seconds` (up to 25): the call waits on the
  server and returns early when the result is ready. While `poll_after_seconds` is set, the result is
  not final; call again after that many seconds. When it is null, show the `media_url` or the error.
- Start the independent jobs of a step first, then poll them, rather than one at a time. Start
  them in batches of about five: every generation call spends a per-minute budget, and a burst is
  refused with "Too many requests".
- Do not narrate each poll to the user. Say what is running and roughly that videos take minutes.
- `media_url` and `thumbnail_url` are signed links valid for one hour. Show or download them
  promptly; for a fresh link later, call `get_generation` again.
- Lost track of an id (a new conversation, a dropped connection)? `list_generations` (`kind`,
  `limit`) lists the newest first with their status and links.
- Some clients show a player under the tool result. Still give the link in text.

## Refusals and failures

A refused call comes back as an error whose text is written for the user, with a machine code in
`_meta["ai.luma/error"].code`. A call refused before it reaches the provider charges nothing; a
provider refusal was charged and returned at once. What to do:

| What it says (code) | What to do |
|---|---|
| "Input validation error ... X is not used when mode is 'Y'" or "X is required when ..." | Fix the arguments from the table above; new key |
| Any other message naming a field that is wrong (`invalid_input`) | Fix that argument; new key |
| "Too many requests to Luma right now. Try again in N seconds." (`rate_limited`) | Wait that long, retry the same call with the same key. Start fewer jobs at once |
| "Not enough Luma credits (this needs N)" plus a link (`insufficient_credits`) | Stop. Show the link; offer a smaller plan. Do not retry |
| "The user has to accept Luma's content policy" plus a link (`consent_required`) | Send the user to the link; after they accept, retry with a new key |
| "Content moderation refused this prompt / this image / this request." (`moderation_blocked`) | Final. Tell the user plainly which input was refused. Do not reword the prompt to get around it; the user may choose a different idea |
| "Generation is paused on this account ..." (`moderation_locked`) | Stop and pass the message on as written |
| "We could not check this request right now" or "Generation is temporarily paused while Luma is being upgraded" (`temporarily_unavailable`) | Wait a few minutes, then try again with a new key |
| "That model, setting or template is not available right now." (`option_unavailable`) | Re-read `list_models` or `list_templates` and pick an available option |
| "The default model ... has no audio option. Pass model ..." (`option_unavailable`) | Pass the model it names |
| "This model supports ... Pick one of those" (`duration_unsupported`) | Use one of the listed durations |
| "no finished upload ..." / "no generation with that generation_id ..." (`unknown_media`) | Check the id; upload the photo first |
| "that upload is a ..., but this needs a ..." (`wrong_media_kind`) | A photo went where a video belongs, or the reverse |
| "that generation has no finished file yet" (`media_not_ready`) | Wait with `get_generation` until it has a `media_url` |
| "this effect takes N photos" (`wrong_input_count`) | Pass exactly that many |
| "Luma does not know that video's length" (`unknown_length`) | That video cannot be restyled; pick another |
| "The provider refused this request; your credits were returned." (`provider_refused`) | The same request fails again; change it with the user |
| "Something went wrong on Luma's side. Try again with client_request_id ..." | Retry the same call with that same key |
| "This generation did not start ..." | Retry later with a new key; any credits come back by themselves |
| "Something went wrong on Luma's side. Try again in a minute." (`internal`) | Wait, then retry; for a generation call, with the same key |
| "You already have 3 uploads in progress" (`upload_refused`) | Confirm or finish the pending uploads, then start the next |
| "Upload limit reached. Try again in an hour." / "Your retained uploads reached 2GB" (`upload_refused`) | Stop uploading; tell the user. Photos already uploaded stay usable |
| "Reconnect Luma" or an invalid token | Ask the user to reconnect the Luma connector |

A generation that started and then failed shows up in `get_generation` as `status: "failed"` with
`error.message`, `error.retryable` and `refunded`. A picture or clip that moderation refused after
it was made arrives this way too, not as an error, and is just as final:

- `refunded: true` means the credits are back. `refunded: false` while `poll_after_seconds` is set
  means the refund is still being recorded; poll again before telling the user anything about money.
- If `retryable` is true, offer to run it again. That is a new job: new key, and it is charged
  again, so say so.
- If a generation finished but has no file ("its file is no longer available"), treat it the same.

## Rights and content

Use only photos the user owns or has the right to use, and faces of people who agreed. Luma's
content policy applies to every prompt and every photo, and the tools enforce it. Never promise that
a prompt or a photo will pass, and never coach around a refusal.

## With a shell, or without

Joining clips, adding titles or music and exporting one file needs ffmpeg on the user's machine:
Claude Code, or Claude Desktop with a shell. Check once with `ffmpeg -version`.

- **With ffmpeg**: download each `media_url` as soon as it is ready (`curl -sSL -o <file>
  "<media_url>"`, quoting the link), keep the files and a short manifest of ids in one project
  folder, and assemble locally.
- **Without it** (claude.ai, the phone app): say so before starting, and finish with an ordered list:
  position, what the clip is, its `generation_id`, its `media_url` (valid one hour), where to trim,
  the transition, and the sound to put under it. Never skip the assembly step silently.
