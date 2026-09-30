---
name: character-sheet
description: Use when the user needs the same character, person or mascot to look the same across several pictures, in other angles, outfits, expressions and scenes. Builds one reference picture and a set of edits of it, and saves their ids for films and social clips.
title: Keep a character consistent
needs_shell: false
---

# Keep a character consistent

One character in; a small named set of pictures out: a reference, then the angles, outfits,
expressions and scenes the user needs, each made as an edit of that one reference so the face and
the details hold. Every picture's `generation_id` goes into a sheet that the `short-film` and
`vertical-hook` workflows reuse. Read [the tool cheat sheet](../_shared/luma-tools.md) first.

## How consistency works here

- **One anchor.** The reference picture is the character's identity. Every other picture is a
  `generate_image` `mode: "edit"` of the anchor, never an edit of an edit (one exception: an
  approved outfit picture, below), so small drifts do not add up. The same rule runs the film's stills (step 7 of the `short-film` workflow).
- **One character line**: species or age, build, face, hair or fur, clothes, colours and one
  distinctive detail. Choose something worn or carried (round glasses, a red scarf) over a small
  facial marking (a scar, a patch, a freckle), which the model redraws in a different place in
  every view. Describe how the character looks, not what they do: a job word ("courier", "chef",
  "pilot") brings its props (a bicycle, a hat) into every picture, so put the job into the scene
  rows instead. Repeat the line word for word in every prompt.
- **One look line**, when the set is for a film or a series: medium, lens, colour grade, light.
  It opens every prompt, word for word.
- **One change per edit**: the angle, or the outfit, or the place. For a scene in a new outfit,
  make the outfit first, approve it, and use that picture as the anchor for its scenes. Never go
  deeper than that.
- **An edit takes one picture.** Two characters from two sheets cannot be merged into one scene.
  For a pair, make a pair anchor from text with both character lines, and edit that.

## 1. Ask first, in one message

- **Who**: an invented character (describe them), or a real person from a photo. A photo must be
  theirs or one they may use, and the person must have agreed. Luma's content policy applies to
  photos of real people and may refuse one; never promise it will pass.
- **What they need**: angles (front, three-quarter, profile, back, a close-up of the face),
  outfits, expressions, scenes. Default: the anchor plus five pictures.
- **What it is for**: a film (its shape), vertical clips, or both. The shape decides the
  `aspect_ratio` of every picture.
- **The look**: photographic, illustrated, 3D mascot, a film reference.
- **The photo, if any, and how it reaches Luma**: a direct https link to the image file, a file
  path when you have a shell, or one of their Luma pictures. Luma cannot read a file attached to
  the chat; if they attached one, say so and ask for a link or a path.

## 2. Read the catalog

`get_account` (balance, consent). `list_models` `{"feature": "text-to-image"}` and
`{"feature": "image-edit"}`.

- Choose the `aspect_ratio` for the shape from the `text-to-image` row, and pass the same value on
  every edit. When the `image-edit` row lists ratios too, pick one both rows list.
- `estimate_cost` does not check shapes: a value no row lists can fail only after the call starts,
  as a provider refusal that returns the credits. Use only listed values.
- A sheet for two shapes (a landscape film and vertical clips) needs the scenes made once per
  shape; the angles and outfits can stay in one.

## 3. Make the anchor

From a photo, bring it in first (`upload_media` `from_url`, or `start` then PUT then `confirm` with
a shell, or a Luma picture's `generation_id`); the quote needs it. Then quote the anchor on its own
(gate 1): `estimate_cost` for one call with exactly its arguments, times the candidates. Show the
total and the balance, and wait for a yes.

- **Invented**: `generate_image` `mode: "text"`: look line, character line, then "Full body, front
  view, standing, neutral expression, plain light grey background, even soft light." A plain
  background makes every later edit cleaner. Offer two or three candidates (each a generation) and
  let the user pick one.
- **From a photo**: make the anchor as an edit of it: "Same person, same
  face, hair and clothes, unchanged. Full body, front view, plain light grey background, even soft
  light." Compare the face with the photo before going on. A sharp, front-facing photo already in
  the right shape can be the anchor as it is, at no cost: then every edit and the sheet use its
  `upload_id` instead of a `generation_id`.
- Show the candidates, get the user's pick, and write down its `generation_id`. From now on that id
  is the character.
- Before you lock it, check the pick against the character line: every item in the line is visible
  (the distinctive detail, the colours, the clothes), there are no props the line did not ask for,
  and the view is what you asked for (a "front view" has the nose and both eyes centred). A
  candidate that misses one is a retake of the anchor, not something the edits will fix.

## 4. Plan the set and quote (gate 2)

Write the set as rows: label, kind, edit of (the anchor, or an approved outfit), prompt. Patterns,
after the look line:

| Kind | Prompt |
|---|---|
| Angle | "Same <character line>. The same person seen <in three-quarter view, turned about 45 degrees to the viewer's right or left / in full side profile, facing the viewer's left or right / from directly behind>, the same pose, plain background and light." |
| Close-up | "Same <character line>. Close-up of the face, <neutral / laughing / worried>, the same light." |
| Outfit | "Same person, same face and hair or fur, now wearing <outfit and colours>, and nothing else new. <If the outfit is only accessories, say what is under them: 'no other clothing, bare fur'.> The same pose, plain background." |
| Scene | "Same <character line>, <doing what> in <place, time of day, light>. Keep the same face, hair and clothes." |

- Scenes are made in the shape of the workflow that will animate them (a scene still is the first
  frame of its clip).
- If the user asks for a front view, check the anchor first. If it is not square-on, make "front"
  its own row; do not list the anchor as the front.
- Drift shows in what is visible: small facial markings and the size and shape of accessories
  change between views, so check those in every picture that shows them. A view from behind hides
  the face and is usually safe.
- `estimate_cost` for one edit with the anchor's `generation_id` as `image` and the sheet's
  `aspect_ratio`, times the rows. Show the count, the total and the balance, say that a retake costs
  one more picture, and wait for a yes.

## 5. Make the set

Keys: `<name>-sheet-<run>-<nn>-<label>`, such as `mira-sheet-k7f2-03-profile`, where `<run>` is
four random characters you choose once for this sheet, such as `k7f2` (see the cheat sheet); the
anchor candidates `mira-sheet-k7f2-anchor-1`, `-2`; a retake is `...-t2`.

```
generate_image {"mode": "text", "prompt": "<look line>. <character line>. Full body, front view, ...",
  "aspect_ratio": "<from list_models>", "client_request_id": "mira-sheet-k7f2-anchor-1"}
generate_image {"mode": "edit", "image": {"generation_id": "<anchor>"}, "prompt": "<look line>. Same <character line>. The same person seen in profile, ...",
  "aspect_ratio": "<the same value>", "client_request_id": "mira-sheet-k7f2-03-profile"}
```

- `generate_image` usually answers with the `media_url`; if it answers with `poll_after_seconds`,
  wait with `get_generation`. Start several rows, then collect them; if "Too many requests", wait
  the seconds it names and retry that call with the same key.
- **Check every picture against the anchor**: face shape, eye colour, hair, the distinctive detail,
  the clothes (unless the row changes them), the proportions, hands. With a shell, download them
  and look at one contact sheet ([ffmpeg step 3](../short-film/references/ffmpeg.md)).
- A drifted picture: retake it from the anchor with the character line first and the drifting
  detail named ("the same round glasses"). A new key, and it costs one more picture, so ask. After
  two drifted retakes, show the user the best one and let them decide.

## 6. Deliver the sheet

The sheet is the deliverable, because `generation_id`s last and `media_url`s expire in an hour.
With a shell, save it as `character-<name>.md` in the project folder and download the pictures
beside it. Without one, give it in the chat and ask the user to keep it.

```markdown
# Character: <name>

Character line: <word for word>
Look line: <word for word, or none>
Shape: aspect_ratio <value used>

| Label | Kind | Edit of | generation_id | Notes |
|---|---|---|---|---|
| anchor | anchor | none | <id> | the identity; edit from this (an upload_id if it is the photo itself) |
| 03-profile | angle | anchor | <id> | |
| 05-winter | outfit | anchor | <id> | anchor for winter scenes |
| 06-harbour-dawn | scene | 05-winter | <id> | vertical |
```

How the other workflows use it:

- **`short-film`**: the anchor is that character's anchor (its step 7), and the character line is
  its character line. New stills for the film are edits of this anchor in the film's shape; scene
  stills already in that shape go straight to image-to-video.
- **`vertical-hook`**: a scene still in the portrait shape is route A's first frame.
- **`photo-to-video`** and **`restyle`**: any picture on the sheet, by its `generation_id`.

In a later conversation, `get_generation` with each id on the sheet gives a fresh link.

## When something goes wrong

- **Moderation refused the photo or a prompt**: final for that input. Tell the user; they may
  choose an invented character instead. Do not edit or reword to get around it.
- **The face keeps drifting**: re-edit from the anchor, never from the drifted picture. If an angle
  still fails, drop it and say so.
- **A shape was refused by the provider**: the credits came back; choose a value the
  `list_models` rows list, with a new key.
- **Credits run out midway**: stop. Hand over the sheet so far and the quote for the rest.
- **A picture failed**: show `error.message` and `refunded`; a retry is a new job, quoted, new key.
- Everything else: the refusal table in [the cheat sheet](../_shared/luma-tools.md).
