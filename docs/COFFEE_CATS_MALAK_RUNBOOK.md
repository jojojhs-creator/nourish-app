# Coffee, Cats & Malak — Episode Runbook

Precise, repeatable procedure for producing one episode and handing it off to the
auto-posting pipeline. Wrapped as the `/coffee-cats-malak-daily` skill but can be
run manually step by step.

---

## Character Reference Element IDs

Embed these in every clip prompt using `<<<element_id>>>` syntax.
Only include characters who appear in the scenario.

| Character | Element ID | Notes |
|---|---|---|
| Malak | `1a65de6a-8d89-45e6-853f-383fb1e0ed6e` | Brunette, dark wavy hair, brown eyes, olive skin |
| Mocha | `f35a2c1b-9058-46d9-ac48-a44628d95785` | Golden Scottish Fold, folded ears, yellow-green eyes |
| Sky | `5df3dade-6a3a-4622-898c-a26e164f56f6` | White fluffy kitten, blue eyes |
| Olive | `74a58910-181f-4819-a00f-73f076bf5d69` | Classic tabby, striped, sleepy expression |

---

## Step 0 — Credit Check (mandatory before every run)

```
1. Call balance → log current credits
2. Call generate_video(get_cost: true, model: "seedance_2_0", duration: 15) → log cost
3. Call generate_image(get_cost: true, model: "nano_banana_pro") → log cost
4. Confirm total cost fits within balance before proceeding
```

Expected: ~22.5 credits for clip + ~2 credits for thumbnail = ~24.5 credits per episode.

---

## Step 1 — Pick the Scenario

Read `docs/CoffeeCatsMalak_Content_Calendar.md`.
Find the next row where Status = "Not started".
Note: Day number, Title, Characters, Setup, Payoff.

---

## Step 2 — Generate the SETUP Keyframe FIRST (it is also the thumbnail)

**CRITICAL ORDER: the keyframe image is generated BEFORE the video.** The image model
(nano_banana_pro) reliably produces the locked cartoon style; the video model drifts
photorealistic when run from text alone. The keyframe is passed to the video model as
its starting frame, forcing the whole clip into the correct style. The same image is
reused as the episode thumbnail. **ONE image per episode — never generate extra
thumbnails or extra frames.**

**The keyframe depicts the SETUP moment (beat 1), NOT the payoff.** The video plays
forward from this frame — if it shows the punchline, the story is already over at
second zero and the clip has nowhere to go (this ruined an early Episode 2 cut).
Make the setup frame charming enough to work as a thumbnail: mischief should be
*visibly imminent* (e.g. kitten ears peeking over the desk edge behind an unaware
Malak), with expressive faces.

Use `generate_image` with:

```
model: "nano_banana_pro"
params:
  aspect_ratio: "9:16"
  medias:
    - value: "7c8a4bde-3c17-4257-80f3-b8864f5a1ea9"   # canonical Malak portrait
      role: "image"
  prompt: <the scenario's SETUP moment with imminent mischief + element IDs +
           the Malak-match sentence + the mandatory style block below>
```

**Malak consistency rule**: job `7c8a4bde-3c17-4257-80f3-b8864f5a1ea9` (the approved
group portrait, also the channel profile picture) is the canonical Malak design.
Pass it as a reference image on EVERY keyframe where Malak appears, and include this
sentence in the prompt:
> `Malak must look exactly like the woman in the reference image: same face, same
> long dark wavy hair, same brown eyes, same soft rounded cartoon features and
> proportions.`

Save the job ID as `keyframe_job_id` and the image URL as `thumbnail_url`.

---

## Step 3 — Generate the 15s Clip FROM the Keyframe

Use `generate_video` with these exact params:

```
model: "seedance_2_0"
params:
  mode: "fast"
  resolution: "480p"
  aspect_ratio: "9:16"
  duration: 15
  genre: "comedy"                # Seedance's built-in comedic pacing
  medias:
    - value: <keyframe_job_id>   # setup frame — forces the cartoon style
      role: "start_image"
  prompt: <see prompt guidelines below>
  # DO NOT include generate_audio — omit it entirely
```

**Write the video prompt as a second-by-second script.** This is what produces real
story flow instead of a frozen scene. Required shape (proven on Episode 2 final cut):

> `Continuous single shot, exact same cartoon animation style and characters as the
> starting frame from first second to last.
> Seconds 0–3: <calm setup — what each character is doing>.
> Seconds 3–7: <the cat strikes — first escalating action, physical and specific>.
> Seconds 7–11: <counter-move and second escalation — Malak reacts, cat doubles down>.
> Seconds 11–15: <payoff — Malak's big exaggerated reaction + cat's smug final pose>.
> Lively squash-and-stretch character animation, exaggerated comedic timing,
> expressive cartoon faces, natural continuous motion with no frozen poses,
> no style change, no photorealism.`

Character element IDs are NOT needed in the video prompt — the start frame already
carries the characters. Every beat must contain motion; never leave a character
static ("like a toy") for more than a beat.

### Video prompt guidelines

- Use the second-by-second script shape above, filling the beats from the calendar
  row's Setup and Payoff columns.
- Check the calendar row's **Energy** column — it sets the pacing:
  - **Chaotic** episodes: beats escalate hard — the cat strikes repeatedly and
    increasingly (multiple jumps, repeated pawing, knocking things one after another,
    zoomies). Never a single action. The payoff beat is Malak's BIG exaggerated
    reaction: bolts upright, messy hair over her face, wide cartoon eyes, dramatic
    slump, silent scream at the camera.
  - **Cozy** episodes: same timed structure but slow and warm — gentle movements,
    purring cuddles, soft smiles — ending with one small comedic surprise.
- Write ACTION VERBS: pounces, springs, bolts, knocks, scrambles, launches,
  freezes, whips around. Avoid static verbs like "sits" or "looks".
- Describe exaggerated reactions physically: "hair sticking up in all directions",
  "eyes comically wide", "deadpan slow blink", "dramatic collapse onto the couch".
- Never include dialogue, subtitles, or on-screen text.
- Keep it visual — expressions, body language, cat behavior carry the comedy.

**Proven example (Episode 2 final cut — The Laptop Situation):**
> `Continuous single shot, exact same cartoon animation style and characters as the
> starting frame from first second to last. Seconds 0-3: Malak types calmly on her
> laptop, small content smile, while Sky the white kitten's ears and eyes rise slowly
> over the far edge of the desk behind the screen — unnoticed. Seconds 3-7: Sky
> springs up onto the desk in one bouncy leap, trots across it and pounces onto the
> keyboard, batting the keys rapidly with both front paws; gibberish fills the screen;
> Malak jerks her hands back, startled. Seconds 7-11: Malak scoops Sky up with both
> hands and lifts her away — Sky twists free in mid-air with a playful wiggle, drops
> right back onto the keyboard, rolls onto her back and happily kicks the keys with
> her hind legs. Seconds 11-15: Malak flops back against her chair, covers her face
> with both hands as her hair flops loose over her forehead, then slowly peeks at the
> camera between two fingers with one wide exasperated eye, while Sky lies sprawled
> across the keyboard, utterly pleased with herself. Lively squash-and-stretch
> character animation, exaggerated comedic timing, expressive cartoon faces, natural
> continuous motion with no frozen poses, no style change, no photorealism.`

### After generation

Call `job_display` with the job ID to confirm completion and get the CloudFront URL.
Save the URL as `clip_url`.

---

## Keyframe/Thumbnail prompt guidelines (for Step 2)

- Show the SETUP moment with mischief visibly imminent — NOT the payoff (the video
  plays forward from this frame; a payoff frame leaves the story nowhere to go)
- Include `<<<MALAK_ID>>>` if Malak is visible
- Include relevant cat element IDs
- **MANDATORY style block** — end every image prompt with this exact sentence (it is
  the channel's locked visual identity; shorter phrasings like "Pixar/CGI animated
  style" drift photorealistic):
  > `Fully stylized Pixar/Disney 3D cartoon animation with cartoon proportions, big
  > expressive animated eyes, soft rounded features, NOT photorealistic, no
  > live-action look — animated movie style. Bright vibrant colors, expressive faces,
  > warm cozy lighting.`
- No text, no overlays

The keyframe image URL doubles as `thumbnail_url` — ONE image per episode, no
separate thumbnail generation.

---

## Step 4 — Write Platform Metadata

### YouTube title
Short, punchy, emoji-friendly. Max 70 chars. Examples:
- "My cat judged my entire work day 😐"
- "Tried to have coffee. The cats had other plans ☕"
- "She knocked it over and walked away like nothing happened"

### YouTube description
2–3 sentences. Warm, relatable tone. End with channel tagline.
"One girl, three cats, zero peace and quiet. New episode every day ☕😹"

### YouTube tags
`cats,funny cats,cat videos,animated cats,coffee cats malak,cat shorts,
cat animation,cute cats,cozy,daily cats,shorts`

### TikTok caption
Hook + 5–8 hashtags. Max 150 chars. Examples:
- "The audacity 😭 #catsoftiktok #catlife #funnycats #shorts #animation #fyp #viral"
- "Every. Single. Morning. ☕ #coffeecatsmalak #cats #catlover #funnyanimals #fyp"

---

## Step 5 — Trigger Posting

Use `mcp__github__actions_run_trigger`:

```
method: run_workflow
owner: jojojhs-creator
repo: nourish-app
workflow_id: storyowl-autopost.yml
ref: main
inputs:
  video_url: <clip_url>
  thumbnail_url: <thumbnail_url>
  youtube_title: <title>
  youtube_description: <description>
  youtube_tags: <tags>
  tiktok_caption: <caption>
```

No Cloudinary upload needed — pass the Higgsfield CloudFront URL directly.

---

## Step 6 — Mark Done

In `docs/CoffeeCatsMalak_Content_Calendar.md`, update the episode row:
- Status: `Done`
- Add the Higgsfield clip URL in the Notes column

---

## Troubleshooting

- **Out of credits**: check balance, do not proceed, notify user
- **Generation fails**: retry once; if it fails again, skip to next scenario and note the failure
- **Workflow dispatch fails**: check GitHub MCP connection; retry up to 3 times
- **TikTok DRAFT mode**: caption cannot be set via API — it appears in the Actions job
  summary for manual copy/paste in the TikTok app
