# Luma AI plugin for ChatGPT, Codex and Claude Code

Ten workflows for making pictures, clips, ads and short films with your own Luma AI account, from
inside a connected AI client: product clips and talking ads for a shop, hooks and every-feed copies
for social media, and the finish that makes them postable (captions, music under the voice, sound,
loudness).

This is for Luma AI, at [luma.ai](https://luma.ai). Luma Labs and Dream Machine are different
products, and this plugin does not connect to them.

The plugin does two things. It connects your client to the Luma MCP at `https://luma.ai/api/mcp`,
and it adds one skill per workflow. Each skill fixes the order Claude works in: ask only what is
missing, say the plan in one line, make it, check it, and show you the result.

## ChatGPT

The OpenAI package is prepared for directory submission. It is not yet an approved, published
ChatGPT plugin. Until publication, use the [ChatGPT connection guide](https://luma.ai/mcp?tab=chatgpt)
if your account supports custom MCP connections in Developer mode.

Package and review preparation are documented in [OpenAI submission](docs/openai-submission.md).

## Codex

Register this repository marketplace and install Luma in Codex:

```sh
codex plugin marketplace add luma-ai-team/luma-ai-skills
codex plugin add luma@luma-ai
```

After the marketplace is registered, the native install link is
`codex://plugins/install/luma?marketplace=luma-ai`. It depends on that marketplace already being
known to Codex. It is not a universal install link for an unconfigured client.
Installation requests Luma authentication: sign in to your own account and approve the connection.

## Claude Code

```
/plugin marketplace add luma-ai-team/luma-ai-skills
/plugin install luma@luma-ai
```

Type both inside Claude Code, not in a terminal. The connection comes with the plugin, so there is
no server address to paste and no token to copy.

## What connecting does

In Claude Code, run `/mcp`, pick `luma-ai` and choose Authenticate. Codex requests authentication
when you install the plugin. A browser opens so you can sign in to your own Luma account and
approve the connection. ChatGPT custom connections use the steps in the connection guide above.

Everything generated spends credits from that account, at the same prices as on luma.ai.
Your request authorizes the requested generation. Ask what something costs or what you have left,
and the assistant checks with Luma. If the balance runs short, it explains the problem. Your
client's tool permission settings still apply. Prices, lengths, shapes and models come from Luma's
catalog when the workflow runs.

Use photos, footage, faces and voices you own or have the right to use. Luma's content policy
applies, and the tools enforce it.

## The ten workflows

Describe what you want and the assistant picks the workflow. The commands below are Claude Code
shortcuts; other clients expose workflows through their skill or plugin controls.

| Claude Code command | What it does |
|---|---|
| `/luma:generate` | Make anything with Luma. Picks the tool, mode and settings for your brief, runs it, and hands off to a more specific workflow when one fits. |
| `/luma:short-film` | Make a short film. Script, shot list, matching stills, one animated clip per shot, then one cut with titles and sound. |
| `/luma:photo-to-video` | Bring a photo to life. One photo in, the effects that fit it and a plain animation out. |
| `/luma:restyle` | Restyle a photo or video. Redraws a photo, or one of your Luma videos, in a look you choose, with several variants side by side. |
| `/luma:memory-reel` | Turn photos into a memory reel. Five to ten photos become a short recap with transitions and music. |
| `/luma:vertical-hook` | Make a vertical hook clip. A social clip that opens on the hook, with an optional loop from matching first and last frames. |
| `/luma:character-sheet` | Keep a character consistent. One character across angles, outfits and scenes, ready for the film and hook workflows. |
| `/luma:product-clip` | Make a product clip. A product photo cleaned up, then short motion treatments in vertical and square, reframed, or restaged for a season or a scene. |
| `/luma:talking-ad` | Make a talking ad. A face, your own voice recording and your product become a captioned vertical ad with product shots and music. |
| `/luma:every-feed` | Fit a video to every feed. One video in, a copy for every feed out: the subject whole in each shape, sharpened, and checked before you post. |

`/luma:short-film`, `/luma:memory-reel` and `/luma:talking-ad` join clips with ffmpeg on your
machine, and every workflow can finish a clip for posting the same way: captions timed to the
speech, music that drops under the voice, a few sound effects, -14 LUFS, and a copy per platform.
Without ffmpeg, or in a client with no shell, they give you the clips in order with a suggested edit
instead of one file.

## If Luma is not connected

Without the connection the workflows have no tools to call. Nothing is generated and nothing is
charged. Connect as described above. The same steps reconnect an expired sign-in.

## Contributing

The workflow text is written and tested in Luma's own source, then copied into
`plugins/luma/skills` by `scripts/sync-from-luma.mjs`. A change made to those files here is
overwritten on the next sync. Open an issue with what went wrong and the workflow it happened in.

## License

MIT. See [LICENSE](LICENSE).
