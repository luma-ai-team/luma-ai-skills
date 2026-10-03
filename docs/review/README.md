# Luma MCP review walkthrough

[Watch or download the recording](https://raw.githubusercontent.com/luma-ai-team/luma-ai-skills/main/docs/review/luma-mcp-review-20261003.mp4).

Recorded on 3 October 2026 UTC using a dedicated demo account and the standard MCP SDK client. The browser capture contains actual requests, results and playback. Idle intervals were shortened. Passwords, OAuth codes, tokens and signed media URLs are excluded.

## What was exercised

| Case | Observed result |
| --- | --- |
| Account | Connected through OAuth; 318 credits and accepted content policy. No generation. |
| Catalog | Current image and video models and supported settings returned by `list_models`. |
| Estimate | A square mug image cost 18 credits. Balance remained 318. |
| Image | One 1024 by 1024 mug image completed, was saved and displayed. Charged 18 credits. |
| Video | One fast, silent landscape video completed, was saved and played. Requested duration 5 seconds, 16:9. Charged 300 credits. |

Exactly one image and one video were generated, with no paid retries. The total charge was 318 credits. The initial recording client's media proxy was corrected to follow Luma's normal signed redirect; both existing results were then fetched in a session with generation disabled.

The three negative prompts are shown as decisions made by the operating Codex assistant: refuse another account's private media, refuse non-consensual intimate imagery, and decline an unsupported bank transfer. They are separately labeled observations. They are not MCP server refusals or moderation-classifier results, and no generation or payment call was made for them.

This is a direct MCP functionality demonstration. It does not establish ChatGPT's native prompt routing or player rendering. Reviewers should run the five positive and three negative prompts from the plugin manifest in their client. Automated approval and publisher attestations are separate from these checks.

Enter reviewer credentials exclusively through OpenAI's private review form. No account login is included in the recording or package.
