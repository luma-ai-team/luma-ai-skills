# Luma AI skills for Claude Code

Eight workflows for making pictures, clips and short films with your own Luma AI account, from
inside Claude Code.

This is for Luma AI, at [luma.ai](https://luma.ai). Luma Labs and Dream Machine are different
products, and this plugin does not connect to them.

The plugin does two things. It connects Claude Code to the Luma MCP at `https://luma.ai/api/mcp`,
and it adds one skill per workflow. Each skill fixes the order Claude works in: ask what you want,
quote the cost, wait for your yes, generate, show you the result.

## Install

```
/plugin marketplace add luma-ai-team/luma-ai-skills
/plugin install luma@luma-ai
```

Type both inside Claude Code, not in a terminal. The connection comes with the plugin, so there is
no server address to paste and no token to copy.

## What connecting does

Run `/mcp`, pick `luma-ai` and choose Authenticate. A browser opens, you sign in to your own Luma
account and approve the connection. You do this once.

Everything Claude generates spends credits from that account. Nothing is free over MCP. Each
workflow tells you how many generations it plans, quotes the cost with `estimate_cost` and waits for
your yes before it spends anything. Prices, lengths, shapes and models come from Luma's catalog when
the workflow runs, so this page names none of them.

Use photos you own or have the right to use. Luma's content policy applies, and the tools enforce
it.

## The eight workflows

Type a command, or describe what you want and Claude picks the workflow.

| Command | What it does |
|---|---|
| `/luma:generate` | Make anything with Luma. Picks the tool, mode and settings for your brief, quotes, runs it, and hands off to a more specific workflow when one fits. |
| `/luma:short-film` | Make a short film. Script, shot list, matching stills, one animated clip per shot, then one cut with titles and sound. |
| `/luma:photo-to-video` | Bring a photo to life. One photo in, the effects that fit it and a plain animation out, each quoted first. |
| `/luma:restyle` | Restyle a photo or video. Redraws a photo, or one of your Luma videos, in a look you choose, with several variants side by side. |
| `/luma:memory-reel` | Turn photos into a memory reel. Five to ten photos become a short recap with transitions and music. |
| `/luma:vertical-hook` | Make a vertical hook clip. A social clip that opens on the hook, with an optional loop from matching first and last frames. |
| `/luma:character-sheet` | Keep a character consistent. One character across angles, outfits and scenes, ready for the film and hook workflows. |
| `/luma:product-clip` | Make a product clip. A product photo cleaned up, then short motion treatments in vertical and square. |

`/luma:short-film` and `/luma:memory-reel` join clips with ffmpeg on your machine. Without ffmpeg,
or in a client with no shell, they give you the clips in order with a suggested edit instead of one
file.

## If Luma is not connected

Without the connection the workflows have no tools to call. Nothing is generated and nothing is
charged. Connect as described above. The same steps reconnect an expired sign-in.

## Contributing

The workflow text is written and tested in Luma's own source, then copied into
`plugins/luma/skills` by `scripts/sync-from-luma.mjs`. A change made to those files here is
overwritten on the next sync. Open an issue with what went wrong and the workflow it happened in.

## License

MIT. See [LICENSE](LICENSE).
