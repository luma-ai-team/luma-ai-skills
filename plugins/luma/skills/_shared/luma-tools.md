# Luma tools: the cheat sheet every workflow uses

Read this before the first Luma call in a conversation. Every workflow in this bundle links here
instead of repeating it. The tools themselves are the authority: when a tool's description or
answer says something different from this page, follow the tool.

Durations, aspect ratios, model names and prices change with the catalog. Never take one from
memory or from this page. Read them at run time from `list_models` and `list_templates`.

## The tools

| Tool | Use it to | Spends credits |
|---|---|---|
| `get_account` | Read the balance, the plan, and whether the content policy still needs accepting | No |
| `list_models` | See each feature's models, the settings each accepts, and the price per unit | No |
| `list_templates` | Search effects (photos into a short video) and styles (a look for a photo or video) | No |
| `list_generations` | Find the user's recent generations, including running and failed ones | No |
| `get_generation` | Read one generation's status, wait for it, get its `media_url` | No |
| `estimate_cost` | Say what a call would cost, when the user asks | No |
| `upload_media` | Bring an outside photo, video or audio file into Luma and get an `upload_id` | No |
| `generate_image` | Make or change a picture | Yes |
| `generate_video` | Make a clip from a prompt, a photo, two frames, or extend one of the user's videos | Yes |
| `apply_template` | Run an effect on photos, or restyle one of the user's videos | Yes |
| `edit_video` | Change a video: edit it from a prompt, reframe it, enhance it, or move a photo's character with its motion | Yes |
| `lip_sync` | Make the face in a photo speak or sing an audio file | Yes |

## Modes, and the arguments each one takes

Each generation tool is one flat object with a mode (`mode`, or `kind` for `apply_template`;
`lip_sync` has none). A field the mode does not list is refused, and so is a missing required field.
Every generation call also takes `client_request_id` (required, see Idempotency below).

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
| `edit_video` `mode: "edit"` | `video`, `prompt` | `model` | `edit` |
| `edit_video` `mode: "reframe"` | `video`, `aspect_ratio` | none | `reframe` |
| `edit_video` `mode: "enhance"` | `video` | `resolution`, `frame_rate` | `upscale` |
| `edit_video` `mode: "motion"` | `video` (the movement), `image` (the character) | `model`, `audio` | `motion-control` |
| `lip_sync` | `image` (the face), `audio_file` | none | `avatar` |

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
- **`edit_video` and `lip_sync` take no `duration`.** The result runs about as long as the source
  video (for `lip_sync`, the audio), give or take a fraction of a second and a different frame
  rate, and the price follows the source's length. The source must be within the
  `source_limits` `list_models` shows for its feature; a longer or shorter one is refused before
  anything is charged.
- **Enhance with no `resolution` and `frame_rate`** runs at the catalog's default quality. Every
  `upscale` row lists the same `resolutions` and `frame_rates`; the pairs that can actually be
  ordered are the rows' `variant` values, written `<resolution>-<frame_rate>` (`4k-30`), and the
  row whose `variant` is null is the default. Pass a pair only when its `variant` exists. The result
  can come back at another frame rate and codec than the source.
- **An uploaded file is priced on its measured length**, rounded up to the price's unit (`per`). A
  clip you cut yourself before uploading should end on a whole unit (`-t 5`, not 5.04 seconds).
- **Motion transfer and lip sync take no prompt.** The photo decides who moves or speaks, the video
  or the audio decides how.
- **Prompts have a length ceiling.** An over-long prompt is refused with the limit in the message.
  One focused paragraph per prompt is enough.
- **Sizes differ by mode.** Pictures and clips come out close to the shape asked for, but at
  slightly different pixel sizes per mode and model: an edit of a picture, or two clips animated
  from one still by different modes, do not match it exactly. Joining them needs the normalising
  in [the ffmpeg reference](../short-film/references/ffmpeg.md) (steps 3 and 4).

## Media is an id, never a link

- A photo is `{"upload_id": "..."}` (from `upload_media`) or `{"generation_id": "..."}` (one of the
  user's own images). Pass exactly one of the two.
- A video is `{"generation_id": "..."}` of one of the user's own finished video generations. Only
  `edit_video` also takes an uploaded video, as `{"upload_id": "..."}`; `generate_video` extend and
  `apply_template` style take a generation only.
- An audio file (for `lip_sync`) is `{"upload_id": "..."}` of an mp3, wav or m4a from `upload_media`.
- An input must be finished: `status` completed and a `media_url` present. A picture whose file is
  still being saved (`media_state: "transferring"`) is refused as not ready; wait with
  `get_generation` until it shows a `media_url`, then use it.
- Ids of another account's generations, deleted ones and made-up ones all read as "no generation
  with that id on this account".

### Getting the user's photo, video or audio into Luma

Chat attachments do not reach Luma by themselves: the Luma tools run on Luma's servers and cannot
read a file attached to the conversation. Three ways in:

1. **`upload_media` `action: "from_url"` with `url`**: Luma downloads a public https link itself and
   answers with a ready `upload_id`. The link must be the file, not a page that shows it (a Drive or
   Dropbox preview page is refused; ask for the direct download link). Works in every client.
2. **`action: "start"` with `content_type` and `size` (bytes), then a PUT, then `action: "confirm"`
   with the `upload_id`**: for a file on the user's machine, when you have a shell. The `start`
   answer contains a ready `curl -X PUT` command and an expiry; replace `@FILE` in it with
   `@<path>`, run it, then confirm. The link in it is a private upload address: run it, never show
   it to the user. `content_type` is the file's type as `file --mime-type -b <path>` prints it. Also the route
   for a file too large or too slow for `from_url` (the refusal says so).
3. **A Luma image the user already has**: find it with `list_generations` `kind: "image"` and pass
   its `generation_id`.

Without a shell, only 1 and 3 work. Say so plainly and ask for a direct link; do not pretend an
attachment was uploaded. The tool names the accepted types: photos (iPhone HEIC among them), MP4 and
MOV videos, and MP3, WAV and M4A audio. An uploaded video or audio file is measured by Luma itself
when it is used; one it cannot read the length of is refused, and saving it again as a standard file
fixes that.

## Reading the catalog

- `list_models` with `feature` (`text-to-image`, `image-edit`, `text-to-video`, `image-to-video`,
  `frames`, `extend`, `edit`, `reframe`, `upscale`, `motion-control` or `avatar`; omit it for all) returns `features`, a list with one entry per feature,
  each with `models` (each with `value`, `label`, `is_default`) and priced `rows`.
- Each row is one priced way to call the feature: `model`, `variant` (null for the plain row,
  `"audio"` for the row priced with sound), `luma_credits` per `per` unit, and `capabilities` for
  that row: `audio` (true only on a row priced with sound), `durations` (on the audio row, the
  durations allowed with audio on), `durations_with_audio` (the same list on the audio row, null on
  a plain row) and `aspect_ratios` (null for `image-to-video`, `frames` and `extend`, whose modes
  take no `aspect_ratio`: the clip takes the shape of its input). `resolutions` and `frame_rates`
  are listed for `upscale` only, the values `edit_video` `mode: "enhance"` takes, and
  `source_limits` for the features priced on their source: its length in seconds and size in MB.
- Pictures from text and edits have a single model: `models` is empty, the row's `model` is null,
  and the call takes no `model` field. Take `aspect_ratios` from that row.
- Pass only values the chosen model's row lists. Omit `model`, `duration` or `aspect_ratio` to get
  the feature's default.
- **Model values belong to one feature.** Each feature lists its own models, and frames, for one,
  can use different values from text-to-video. Never carry a model value from one feature to
  another.
- **Audio may need a named model.** Passing the model of a row with the audio variant always
  works: find a row for that feature with `variant: "audio"` and `capabilities.audio: true`, and
  pass that row's `model` together with `audio: true` and a duration from that row. Leaving
  `model` out works only when the default model has an audio row, and is otherwise refused with the
  model to pass ("The default model ... has no audio option. Pass model ..."); pass the model it
  names. The plain rows are silent: a clip from text, frames or extend made without `audio: true`
  has no sound, and the audio row's durations can differ from the plain row's.
- `list_templates` needs `kind` (`"effect"` or `"style"`), and takes `category` (exact, from the
  `categories` list in the answer), `query` (matches only a template's name or key, never what it
  shows, so a subject word such as "dog" often finds nothing) and `limit`. Each template has
  `key`, `name`, `category`, `credits` (effects: per generation; styles: the video restyle price,
  fast tier, per unit of `per` of the source video), `credits_max` (styles: the video restyle price
  at the max tier), `input_count` and a `preview_url` showing a sample. A style's `credits` never
  price a photo in that style: `estimate_cost` does.
  When the user is choosing a look, show them the `preview_url` samples; they are free.

## Credits: the request is the go-ahead

Every generation is paid with the user's own Luma credits, at the same prices as on luma.ai. The
user asking for something is their go-ahead to make it.

- **Make it straight away.** Call the generation tool as soon as you know what to make. Do not
  stop to ask whether to spend the credits, and do not open with the price.
- **Make what was asked for, no more.** Add no variations, extra shots or retakes the user did not
  ask for. When they ask for another take or a change, make that the same way.
- **Show the result, not the bill.** After a generation, show what was made. Leave its cost and
  the balance out of what you say.

Credits come up in two cases only:

1. **A call is refused for not enough credits** (`insufficient_credits`). Stop, say once that the
   balance does not cover it, and give the account link from the refusal. Offer a smaller version
   (fewer shots, a shorter or silent clip). Do not retry the same call; you cannot buy credits for
   the user.
2. **The user asks** what something costs or what they have left. `estimate_cost` takes one flat
   object, `tool` plus the generate call's own fields at the top level, such as
   `{"tool": "generate_video", "mode": "image", "image": {"generation_id": "..."}, "model":
   "<model from list_models>", "duration": <a listed duration>}`, and answers `credits`, `rate`,
   `per`, `priced_seconds`, `balance`, `enough` and `shortfall` without charging anything. For a
   plan of several calls, price each distinct call shape once and multiply. `get_account` gives
   the balance. Use only numbers these tools returned in this conversation.

Every generation answer also carries `credits_charged` and `balance_after` as data. When the user
asks what a run spent, add up `credits_charged`: jobs started together can answer with the same
`balance_after`, and another session on the account moves the balance too, so never subtract
balances.

A generation refused because the content policy is not accepted yet (`consent_required`) comes
with the consent link: send the user there, and after they accept, run it again with a new key.

## Idempotency: `client_request_id`

- Required on `generate_image`, `generate_video`, `apply_template`, `edit_video` and `lip_sync`: a
  key you choose, 8 to 100 characters. A readable shape helps resumes: project, a run tag, shot, take, such as
  `lighthouse-k7f2-s03-t1`. The run tag is four random characters you choose once per run (`k7f2`
  is only an example; never a date or a word someone else would also pick): a key used in any
  earlier run hands back that run's generation.
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
- `generate_video`, `apply_template`, `edit_video` and `lip_sync` answer at once with a
  `generation_id` and `poll_after_seconds`. A video takes a few minutes, a long or high-quality one longer.
- Poll with `get_generation` `generation_id` and `wait_seconds` (up to 25): the call waits on the
  server and returns early when the result is ready. While `poll_after_seconds` is set, the result is
  not final; call again after that many seconds. When it is null, show the `media_url` or the error.
- **`completed` is not the end.** A finished video first reads `status: "completed"` with
  `media_state: "transferring"` and no `media_url`, while its file is being saved, and
  `poll_after_seconds` is still set. Keep polling until the `media_url` arrives.
- Start the independent jobs of a step first, then poll them, rather than one at a time. Start
  them in batches of about five: every generation call spends a per-minute budget, and a burst is
  refused with "Too many requests".
- Do not narrate each poll to the user. Say what is running and roughly that videos take minutes.
- `media_url` and `thumbnail_url` are signed links valid for one hour. Show or download them
  promptly; for a fresh link later, call `get_generation` again. `thumbnail_url` is often null for a
  video: do not promise a thumbnail. With a shell, take a frame with ffmpeg if a still is needed.
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
| "Not enough Luma credits (this needs N)" plus a link (`insufficient_credits`) | Stop. Say once that the balance does not cover it, give the link, offer a smaller version. Do not retry |
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
| "Luma does not know that video's length" (`unknown_length`) | That video cannot be used here; pick another |
| "Luma could not read how long that video / audio file is" (`unknown_length`) | Save it again as a standard MP4 or MOV video, or MP3, WAV or M4A audio, and upload it again |
| "This tool needs a clip between ..." (`source_length_unsupported`) | Trim the source to fit, or pick another |
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
- If `retryable` is true, run it once more as a new job with a new key, and tell the user only if
  that one fails too.
- If a generation finished but has no file ("its file is no longer available"), treat it the same.

## Rights and content

Use only photos, videos and audio the user owns or has the right to use, and faces and voices of
people who agreed. `edit_video` and `lip_sync` can make a real person appear to do or say something:
never use them on someone who did not agree to it. Luma's
content policy applies to every prompt and every photo, and the tools enforce it. Never promise that
a prompt or a photo will pass, and never coach around a refusal.

## With a shell, or without

Joining clips, adding titles or music and exporting one file needs ffmpeg on the user's machine
and a client with shell access. Check once with `ffmpeg -version`.

- **With ffmpeg**: download each `media_url` as soon as it is ready (`curl -sSL -o <file>
  "<media_url>"`, quoting the link), keep the files and a short manifest of ids in one project
  folder, and assemble locally. Links have no file extension: save stills as `.jpg` (they are
  JPEG) and clips as `.mp4`. For anything that will be posted or sold with, finish it with
  [the social finish](social-finish.md): the frame per platform, captions timed to the speech,
  music that drops under the voice, sound effects, one loudness and a check of every file.
- **Without it**: say so before starting, and finish with an ordered list:
  position, what the clip is, its `generation_id`, its `media_url` (valid one hour), where to trim,
  the transition, and the sound to put under it. Never skip the assembly step silently.
