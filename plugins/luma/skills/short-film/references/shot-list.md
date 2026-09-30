# The shot list, and a worked example

## Format

Keep the plan in one file (`shots.md` in the project folder when you have a shell; in the chat
otherwise). Fill in the ids as they arrive. It is the manifest a later session resumes from.

```markdown
# <Film title>

Logline: <one sentence>
Shape: <landscape | vertical | square>, aspect_ratio <from list_models>
Look line: <medium, lens, grade, grain, light; opens every still prompt word for word>
Characters:
- <Name>: <age, hair, clothes, colours; repeated in every still that shows them>

## Stills

| Key | Anchor or edit of | Prompt (after the look line) | generation_id |
|---|---|---|---|
| k01 | anchor | ... | |
| k02 | edit of k01 | Same <name>, same <clothes>, <new moment>. Keep the same film look. | |

## Shots

| # | Beat | Mode | Input | Model | Duration | Audio | Motion prompt | Transition in | Sound in the cut | generation_id |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ... | text | none | ... | ... | yes | ... | none | own | |
| 2 | ... | image | k01 | ... | ... | no | ... | fade | borrowed from 1, muffled | |

## Titles

Opening: "<title>" over shot 1. End card: "<line>" ("<second line>").
```

## Worked example: how the lighthouse film was built

Numbers are left out on purpose: prices, durations and models come from the catalog on the day.

Logline: a lighthouse keeper relights the lamp in a storm and guides a lost fishing boat home.

Look line: "Cinematic film still, 35mm anamorphic, moody teal and amber grade." Two characters,
the keeper (late sixties, grey beard, yellow oilskin coat over a navy sweater) and the fisherman
(twenties, dark curly hair, orange life vest), each described the same way in every still.

Stills: two anchors (`text`): the keeper in the lantern room, the boat in the storm. Four edits:
the keeper cranking the lit lamp (edit of the keeper anchor), the view over his shoulder with the
beam finding the boat (edit of the keeper anchor), the boat entering the harbour at dawn (edit of
the boat anchor), the keeper on the gallery at sunrise (edit of the keeper anchor). All six were
checked on one contact sheet before any video was made.

| # | Beat | How it was made | Where its sound came from |
|---|---|---|---|
| 1 | Storm, the lighthouse dark | `text`, audio on, a long duration, the film's aspect ratio | its own |
| 2 | The keeper lights the lamp | `image` from the lantern-room anchor | shot 1's storm, low-passed so it sounds like it is outside the glass |
| 3 | The boat fights the waves | `image` from the boat anchor | a mix of shots 1 and 4 |
| 4 | The beam finds the boat | `frames` from the crank still to the over-the-shoulder still, with the frames model whose row had the audio variant | its own |
| 5 | The boat reaches the harbour | `image` from the dawn still, then `extend` with audio; the extend output replaced the original | its own (the second part); a dawn bed under the silent first part |
| 6 | The keeper smiles at sunrise | `image` from the gallery still | the dawn bed, cut from shot 5's own sound and looped |
| 7 | A last pull-back | an effect template (`apply_template` effect) on a photo | the effect's own soundtrack, kept low |
| 8 | End card | a PNG rendered with PIL | the tail of shot 7's sound, faded out |

What the run taught, all reflected in the workflow:

- Image-to-video calls sent with `audio` were refused before anything was charged; they were
  resent without it under new keys.
- Asking for audio without naming a model was refused; naming a model whose row had the audio
  variant worked.
- One call was sent a second time with its original key and came back `duplicate: true` with
  nothing charged.
- The clips came in different sizes and frame rates, and several had no audio track, so every clip
  was normalised before the crossfades.
- The ffmpeg build had no `drawtext`, so both titles were PNG overlays.
