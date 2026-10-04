# OpenAI submission

The portable package connects to Luma through OAuth and includes the ten existing workflows.
It is intended for the shared ChatGPT and Codex directory. Repository marketplace installation
is also available in Codex; it does not create a public ChatGPT listing.

## Build and validate

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/package_openai.py
```

The ZIP has `plugin.json` and `mcp.json` at its root. The builder includes only the manifests,
license, SVG assets and workflow Markdown. It rejects symlinks, unexpected skill files, hooks,
app manifests, static authorization headers and private review fields. It produces identical
bytes from identical inputs. CI uploads the ZIP as a build artifact.

The Luma icon is copied from Luma V2's `src/app/icon.svg`; it is the existing 64 by 64 favicon.
Workflow text is copied by `scripts/sync-from-luma.mjs` and remains canonical in Luma V2.

## Current review state

The manifest contains five positive and three negative review cases and a URL for the recorded
MCP walkthrough. Reviewer credentials, publisher verification and domain verification are managed
separately in the private submission portal. This repository does not establish an approved public
listing. Package validation proves package structure; it does not prove test execution or review
approval.

Before submitting for review:

1. Upload the ZIP at [OpenAI Plugins](https://platform.openai.com/plugins) using the correct
   publisher organization and resolve automated package and MCP findings.
2. Select a verified publisher identity and complete the dashboard's domain challenge.
3. Prepare a dedicated reviewer Luma account and sample data. Creating or sharing credentials
   requires the account owner's authorization. Enter credentials only in the private dashboard
   review form, never in Git, the ZIP, test output or a public issue.
4. Execute all eight cases with that account. Image and video generation spend real Luma
   credits; obtain authorization before those runs. Record actual outcomes and keep the
   test account usable for review.
5. Record an accessible walkthrough covering connection, successful generation and refusal.
   Put the actual video URL in `extensions.com.openai.review.demo_recording_url`.
6. Review the dashboard's policy attestations with the authorized publisher, then submit.
   Approval and publication are separate steps.
7. After approval and publication, use the actual directory listing and assigned plugin ID
   on Luma's connection page. Do not advertise a repository marketplace link as a universal
   install link before the client knows that marketplace.

Luma's `/support` requires sign-in, so this package uses the public repository's Issues page
for plugin support. Keep account information and private media out of public issues.

## Sources

- [Portable plugin package](https://developers.openai.com/plugins/build/plugins)
- [Submission and review requirements](https://developers.openai.com/plugins/deploy/submission)
- [Codex plugin installation](https://learn.chatgpt.com/docs/plugins)
- [Codex commands](https://learn.chatgpt.com/docs/reference/commands)

The manifest format and submission requirements were checked on 2026-10-03.

## Local security inspection

`skillspector scan plugins/luma --no-llm` completed on 2026-10-03 and reported two existing
workflow matches. Both were inspected independently:

- P5, `_shared/luma-tools.md:76`: "a clip you cut yourself" describes trimming a video to whole
  billed seconds with ffmpeg. It contains no self-harm instruction or moderation bypass.
- OH3, `generate/SKILL.md:65`: the `edit_video` reframe routing row describes a supported tool.
  It contains no instruction hierarchy override or unbounded generation loop.

These are false positives; the scanner still exits nonzero. No plugin installation was performed.
