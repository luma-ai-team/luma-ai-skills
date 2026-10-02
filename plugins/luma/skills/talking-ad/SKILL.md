---
name: talking-ad
description: Use when the user wants a talking-head or UGC-style ad, a product explainer or a spokesperson clip for social media or a shop: a face, a voice recording and a product become one captioned vertical ad with product shots, music and sound.
title: Make a talking ad
needs_shell: true
---

# Make a talking ad

A person talks to camera about a product, the edit cuts to the product while they talk, captions
carry the words for people watching muted, and music sits under the voice. The talking part is
`lip_sync`: a photo of the presenter and the user's own voice recording become a clip of that face
saying it. The product shots are image-to-video clips. Read
[the tool cheat sheet](../_shared/luma-tools.md) first; the edit is in
[the ad edit](references/ad-edit.md) and [the social finish](../_shared/social-finish.md).

## The rules this ad lives by

- **Only a face the user owns or has that person's permission to use, and a voice they have the
  right to use.** A real person never says words they did not agree to. A generated presenter is
  never presented as a real customer.
- **Only true claims.** The script says what the product really is and does. No invented reviews,
  results, numbers, awards or before-and-after the user cannot back.
- **Luma does not make voices.** The voice is a recording the user makes or owns. Say so up front.

## 1. Check the finish before anything else

Check once for `ffmpeg -version`, `python3 -c "import PIL"` (the captions are rendered with
Pillow) and `command -v whisper mlx_whisper` (word times for the captions and the cuts; without
one, the script's own timing stands in, less exactly). Without a shell (claude.ai, the phone app), say now that you will make the talking clip
and the product shots and hand over an edit list with the captions as an `.srt` text to paste into
an editing app (CapCut, Instagram's editor), not one finished file.

## 2. Ask only for what is missing, in one message

- **The product**: what it is, the one thing it does better, the offer if any, and a product photo
  (a direct https link, a file path with a shell, or one of their Luma pictures). The accuracy rule
  of the `product-clip` workflow (`get_workflow` with that name) applies to every product shot.
- **The presenter**: a photo of themselves or of someone who agreed, or a generated presenter (a
  person who does not exist; the `character-sheet` workflow keeps one consistent across ads).
  Front-facing, the face clear and well lit, shoulders up, mouth closed or relaxed, eyes open,
  nothing in front of the mouth. A generated one is `generate_image` text with the portrait
  `aspect_ratio` and a prompt like "Photorealistic portrait of <who, matching the product's
  buyer>, looking straight into the camera, head and shoulders, centred with room above the head,
  soft window light, mouth closed in a relaxed smile, <plain clothes>, a softly lit <setting that
  suits the product> behind, natural skin texture, shot on a phone." Its `generation_id` is the
  `image` for `lip_sync`.
- **The voice**: their recording of the script, or one they have the right to use. When they have
  none yet, write the script (step 3) and ask them to record it: phone close to the mouth, a quiet
  room with soft furnishings, an even pace, half a second of silence before and after.
- **Where it runs**: vertical (Reels, TikTok, Shorts) unless the brief says otherwise.
- **Music**: a track they have the right to use, or none.

## 3. Write the script (when they have none)

One reader, one idea, one ask. At an even pace people say about two and a half words a second, so
a script is that many words per second of the ad you want. The voice's length must also fit
`source_limits` for `list_models` `{"feature": "avatar"}`.

| Part | Job | Example shape |
|---|---|---|
| Hook, the first sentence | The viewer's own problem, in their words, as a scene | "Your coffee is cold before you get to it." |
| Turn | What changes it | "This mug keeps it hot for hours." |
| Proof | One concrete, true detail | "Double wall steel, and it fits a car cup holder." |
| Ask | One verb, one place | "Tap the link and pick your colour." |

No greeting, no brand name first, no "in today's world". Mark in the script which lines cut to a
product shot and which word to stand out in the captions (`*word*`). Cut to the product on the
lines that name it or what it does (the turn and the proof); with a script of their own and no
proof line, the turn and the ask, so the ad ends on the product. Never on the hook: the first
two seconds show the face. Show the user the script and go on when they have recorded it.

## 4. Bring the photo, the voice and the product in

1. **Clean the voice** with [social finish F4](../_shared/social-finish.md) and trim the silence at
   both ends. Measure it: `ffprobe -v error -show_entries format=duration -of csv=p=0 voice.wav`.
   Longer than the avatar `source_limits`: split it at a sentence break into parts that fit, one
   lip-sync each, joined in the edit.
2. **Upload a compressed copy of the voice**: the avatar `source_limits` cap the file's size as
   well as its length, and a stereo WAV passes a few megabytes in well under a minute. `ffmpeg -loglevel error -y -i voice.wav -c:a aac -b:a 160k
   -movflags +faststart voice-upload.m4a`, then `upload_media` `start` with `content_type` from
   `file --mime-type -b voice-upload.m4a` (`audio/x-m4a` or `audio/mp4`, both taken) and `size`
   from `wc -c`, the PUT, and `confirm`. Upload the
   presenter photo the same way, and the product photo unless it is already a Luma picture.
   `audio_file` takes only an `upload_id`.
3. **The presenter in the ad's shape**: lip-sync keeps the photo's shape. When the photo is not
   vertical, make a vertical version with `generate_image` `mode: "edit"`, the portrait
   `aspect_ratio` from the `image-edit` row and "The same person, unchanged: same face, hair and
   clothes. Head and shoulders, centred, room above the head. <a plain, softly lit background that
   suits the product>." Compare the face with the photo; if it changed, use the original photo and
   crop in the edit instead.

## 5. Plan in one line, then run

Say the plan in one line: one lip-sync per voice part, how many product shots, and that the edit
puts it together. Then run it. See Credits in the cheat sheet: the request is the go-ahead. `<run>`
is four random characters chosen once for this conversation.

```
lip_sync {"image": {"upload_id": "<presenter>"}, "audio_file": {"upload_id": "<voice part 1>"},
  "client_request_id": "<product>-<run>-talk-1"}
generate_image {"mode": "edit", "image": {"upload_id": "<product photo>"},
  "prompt": "The same <product>, unchanged: same shape and colours<, and the same label and logo, when it has them>. <a setting that matches the line it illustrates>. The whole product in frame, centred.",
  "aspect_ratio": "<portrait value>", "client_request_id": "<product>-<run>-still-1"}
generate_video {"mode": "image", "image": {"generation_id": "<checked still>"}, "prompt": "<a slow push-in, the product in use, a hand picking it up>",
  "model": "<from list_models>", "duration": <a listed duration>, "client_request_id": "<product>-<run>-broll-1"}
```

- A photo or presenter that is one of their Luma pictures goes in as `{"generation_id": "..."}`
  instead of an `upload_id`, everywhere above.
- Two or three product shots are enough: one per line marked for a cutaway. Each needs only to
  cover its line, and the edit can start it from any second (the action may come late), so the
  shortest duration the image-to-video row lists is enough.
- Start the lip-sync and the stills together, then animate the stills that pass the accuracy
  check, then poll everything with `get_generation` until `poll_after_seconds` is null.

## 6. Check before the edit

- **The talking clip**: download it and check the mouth against the words. You cannot listen, so
  check it this way: frames at the word times from A2 of the ad edit (lips closed on an "m", "b" or
  "p", open on a long vowel) and at every pause (mouth closed), and the clip's pauses
  (`silencedetect`) against the voice's, within about a tenth of a second. The face stays the same
  person from first to last frame, with no flicker around the teeth or eyes and no frozen
  stretch. Eyes closed for longer than half a second in the first two seconds spoils the hook:
  retake (a new key) or start the ad after it. A clip that drifts is retaken with a new key (often
  a better-lit, more frontal photo fixes it); never hide a bad stretch under a cutaway or a
  caption. Tell the user to watch the result once with sound before posting.
- **The product shots**: the product unchanged as it moves (label, colour, shape).

## 7. Cut the ad (with ffmpeg)

Follow [the ad edit](references/ad-edit.md): it lays the talking clip down as the spine, cuts to the
product shots over it while the voice runs on, burns in the captions, adds the music under the
voice, a whoosh on the cutaways, the ask on screen at the end, -14 LUFS, and the posting copies and
checks from [the social finish](../_shared/social-finish.md).

Hand over: the ad's path and length, the silent copy and the cover, the script, and every
`generation_id`. A new cut, caption fix or music change is only a re-edit; a new take is a new job
with a new key, made when the user asks.

## 8. Without a shell: the edit list

List in order: the talking clip (`media_url`, `generation_id`), each product shot with the second
of the voice where it goes in and out, the captions as `.srt` text (times from the script at two and
a half words a second; tell the user to nudge them to the voice), the music note and the ask to put
on screen. Say the links expire in an hour and `list_generations` finds them later.

## When something goes wrong

- **The audio was refused** as a wrong type or unreadable length: save it again as WAV (F4 does),
  upload again, new key.
- **"This tool needs a clip between ..."** (`source_length_unsupported`): the voice is too long or
  too short for lip-sync; split or trim it.
- **Moderation refused the photo, the voice or a prompt**: final for that input. Tell the user; do
  not reword or swap in a look-alike face to get around it.
- **The face changed or the lips drift**: retake with a clearer, more frontal photo and a new key,
  once; if it fails again, say so and offer the generated-presenter route.
- **Not enough credits**: stop and do not retry. Hand over what is made, say once that the balance
  does not cover the rest, give the account link from the refusal, and offer fewer product shots.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
