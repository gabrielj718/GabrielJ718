# Style guide

This is my look, the one the skill is set to. Fill in the "Yours" column, then tell Claude: "Here's my style guide. Update the youtube-edit skill to match it." Leave a row empty and it keeps mine.

Where it lives: the colours and font are at the top of `youtube-edit/scripts/compose.py` (the `:root` colour tokens and the font files). Every rule below is written into `youtube-edit/SKILL.md`. You don't need to open either; Claude does it.

## Colours

| Role | Mine | Yours |
|---|---|---|
| Highlight (key words, ticks, bars) | Cyan `#0AF0F0` | |
| Deep anchor (gradient end, a word-highlight block with white text) | Blue `#0005EE` | |
| Punchline (the payoff word, the last step of a diagram) | Magenta `#CD00EE` | |
| Money and stakes (dollar figures, warnings) | Amber `#FFB904` | |
| Text | White `#FFFFFF` | |

Two rules I learned the hard way: highlighted words are never dark blue (it disappears on dark footage), and only one gradient per frame.

## Font

| | Mine | Yours |
|---|---|---|
| Font | DM Sans, weights 400, 500 and 700 (in `youtube-edit/assets/fonts`) | |
| Headlines | 700, with a thin stroke in the same colour to make it heavier | |
| Big numbers | Every digit written out (`$207,000,000`, never `$207M`), white, counting up | |

## Cards and text on screen

| | Mine | Yours |
|---|---|---|
| Card style | Frosted glass: light glass on dark scenes, dark glass on a bright room | |
| Default for words | One line at the bottom, key words in the highlight colour | |
| Lists | Never a list panel. Each item becomes its own thing: pills next to my head, a diagram, one animation per number | |
| My face | Not the default background. 40% or more of a talking section is full-screen animation | |
| A person or job I mention | 3 seconds of B-roll of that person doing it | |
| An app I name | A clean, designed window of it, not a screenshot | |
| A website or post I name | The real page, in a browser window, scrolling | |

## Motion

| | Mine | Yours |
|---|---|---|
| Things coming in | 0.4 s, soft ease out. No bounces, no flips | |
| Things leaving | 0.35 s | |
| Timing | Every animation lands on the word it belongs to, a beat before I say it | |
| Variety | Never the same type of animation twice in a row | |
| Busy check | About 7 animations and 7 camera moves per 90 seconds | |

## Camera

| | Mine | Yours |
|---|---|---|
| Zoom anchor | The top of the frame, so my head never gets cropped | |
| Punch-in on a key word | 118 to 125%, a third of a second | |
| Slow creep across a thought | 110 to 112% over 5 to 10 seconds | |
| At every cut | Back to 100% | |

## Sound

| | Mine | Yours |
|---|---|---|
| Default | Silence. A sound has to earn its place | |
| Allowed | A pop when a logo lands, a light click when a cursor clicks, typing only when someone types, a cha-ching at very low volume for money | |
| Never | A whoosh under text | |
| Music | Something tense under the hook, then lo-fi, very low, ducked under my voice | |

## Cuts

| | Mine | Yours |
|---|---|---|
| Retakes | Keep the last take of every line | |
| Pauses | Nothing longer than about 0.4 s after a sentence | |
| Live demos | Show the result, not the waiting | |
| Flash cuts | Never | |
