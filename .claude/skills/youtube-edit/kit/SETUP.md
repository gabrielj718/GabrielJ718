# Setup: from zero to your first edit

About 30 minutes. You click through steps 1 to 6. Claude does the installing in step 7.

## 1. Get the Claude desktop app

Download it from Anthropic's site (claude.com/download) and install it. Sign in with Google or with an email and password. If it's your first time in Claude, go through the first-run setup it offers.

## 2. Pick a plan

You need a paid plan. The $20 plan is enough to set all of this up. Editing full videos uses a lot more. I run mine on the $200 Max plan.

## 3. Open Claude Code

Click **New**. On the left you'll see Claude (chat and Cowork) and Claude Code. Pick **Claude Code**.

## 4. Four settings before you start

- **Local**, so it works on your own computer, where your footage is.
- **Your folder.** Click the folder picker and create a new one, for example "Video Editing". Everything happens in there: your clips, the skill, the renders.
- **Permissions on Auto**, so it can run without asking you yes or no a thousand times.
- **The latest model** for the setup. Setup is the important part. You can switch to a cheaper model afterwards.

## 5. Let it use the browser

Bottom left: **Settings**, then **Claude Code**, and turn on the browser setting. The skill uses it to find screenshots, articles and posts to show on screen while you talk about them.

## 6. Connect your tools

**Customize**, then **Connectors**. Search, click the plus, and log in when the browser opens. You'll see a check mark when it's connected.

- **Tella**, if you record your screen with it. Claude can then open your recordings by name, no uploading.
- **Epidemic Sound**, if you use it for music and sound effects.

Both are optional. Without Tella, export your screen recordings as files. Without Epidemic Sound, the skill uses the free HyperFrames sound library.

## 7. Install the skill

Put the `WeAreNoCode-YouTube-Editor` folder inside your project folder. Then type:

> Install the youtube-edit skill from the WeAreNoCode-YouTube-Editor folder into this project's .claude/skills folder. Then check everything it needs, install what's missing, and run its tests.

Claude installs the rest itself: FFmpeg (the tool that joins and encodes video), HyperFrames (it draws the animations and renders the frames), auto-editor and Parakeet (they find where you speak and write down every word with its exact time), plus a few Python packages. If it can't find HyperFrames, search "HyperFrames" (it's on GitHub, and it's in the Connectors list too).

When the tests pass, open a **new** thread. Skills load at the start of a thread.

## 8. Your first edit

Start small: a 30 to 60 second hook. Drop the raw clip in and use the first prompt in `PROMPTS.md`. Expect 10 to 20 minutes for a hook. Then watch it and give it notes.

## How to record so it edits well

- Record in 4K if you can. Zooms stay sharp. 1080p goes soft past about 112%.
- Mess up a line? Pause and say it again. The skill keeps your last take of every line and cuts the rest.
- Keep the file flat: no zooms, captions or transitions baked in. The skill adds those.
- Talking-head clips and screen recordings can be separate files. Tell Claude which is which.

## Rather build your own from scratch?

That's what I did first. Use the setup prompt in `PROMPTS.md`, let Claude walk you through it, and when it works, ask it to save everything as a skill. Then open a new thread and test it.
