# Prompt patterns per mode

Write prompts as plain descriptive sentences, one focused paragraph each. Concrete nouns, one main
action, the camera, the light. These shapes are the ones that held up in real runs; adapt the
content, keep the order.

## Picture from words (`generate_image` text)

```
<Medium and look: film still, product photo, watercolour ...>, <lens or framing>, <colour grade>.
<Where and when>. <The subject, with the details that must stay fixed: age, hair, clothes, colours>.
<What the subject is doing>. <Light: where it comes from, warm or cold>. <Finish: photorealistic,
shallow depth of field, film grain ...>.
```

Example: "Cinematic film still, 35mm anamorphic, teal and amber grade. The lantern room of an old
stone lighthouse at night in a storm. A weathered keeper in his late sixties, grey beard, yellow
oilskin coat over a navy sweater, holds a lit match to the lamp wick. Rain streaks the glass. Warm
match light on his face, the room in cold blue shadow. Photorealistic, shallow depth of field, film
grain."

- Put the look first and keep it word for word across every picture of a set; that sentence is
  what makes separate pictures match.
- Text inside a picture (signs, labels) often comes out wrong. Ask for it only when needed, and
  check it.

## Change a picture (`generate_image` edit)

```
Same <subject>, same <identifying details>, <the one thing that changes>. Keep the same <composition /
lighting style / look>.
```

Example: "Same keeper, same grey beard and yellow oilskin coat, now outside on the iron gallery at
sunrise holding a steaming tin mug. Same film look, warm light."

- Name what stays before what changes. Change one thing per edit; chain edits for more.
- Edit from the best approved picture of the subject every time, not from the last edit, so small
  drifts do not add up.

## Animate a picture (`generate_video` image)

Describe the motion, not the picture: the picture already fixes who and where.

```
<What moves and how>. <What the subject does, in order>. <Camera move and pace>.
```

Example: "The keeper brings the match to the wick; the flame catches and grows, warm light blooming
across his face. He shakes out the match and watches the flame steady. Slow push-in on his face."

- One action per clip. Two or three beats in sequence are fine; a whole scene is not.
- Camera words that work: slow push-in, pull back to reveal, tracking shot, handheld, aerial,
  orbit, static.
- No sound line: this mode is silent.

## A clip from words (`generate_video` text)

Picture pattern plus motion plus, when `audio` is on, a sound line:

```
<Shot type and look>. <Place and subject>. <What happens>. <Camera move>. Sound: <three or four
concrete sounds>.
```

Example: "Aerial establishing shot at night, 35mm anamorphic. A lone stone lighthouse on a black
cliff in a violent storm; waves explode on the rocks, lightning shows the tower. Slow drone push-in
toward the lantern room. Sound: howling wind, heavy rain, crashing waves, a deep roll of thunder."

## Between two pictures (`generate_video` frames)

The first and last frames are fixed; describe the path between them.

```
<The action that turns the first frame into the last>. <How the camera travels>. Sound: <...>
```

Make the two frames as edits of one picture so the subject and the look match; the more the two
frames differ, the more the model has to invent.

## Longer (`generate_video` extend)

Say what happens next, continuing the action already in the clip, plus a sound line when `audio`
is on. The answer is the whole clip, the original plus the new seconds.

## Styles and effects

`generate_image` style mode and `apply_template` take no prompt: the template is the prompt. Choose
it from `list_templates` by its `preview_url`.
