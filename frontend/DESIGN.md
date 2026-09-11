# Design System: BioAgent-Lite

## 1. Visual Theme & Atmosphere
A precision-lab interface with gallery restraint — dense as a cockpit (6) but airy as a specimen archive. Confident asymmetry (8), fluid spring motion (6). Mood is **night-lab fluorescent**: deep void with sage bioluminescence, like a sequencer room at 2am. Every pixel calibrated, nothing decorative without function. Expensive instrument, not dashboard.

Dial: Creativity 9 | Density 6 | Variance 8 | Motion 6

## 2. Color Palette & Roles
- **Lab Void** (#070A0A) — Canvas background, deep green-black
- **Surface** (#111815) — Primary card fill, zinc-900 green-tinted
- **Surface Elevated** (#17201D) — Secondary surface, subtle lift
- **Surface Wash** (#1A2622) — Tertiary, for heatmap cells / code blocks
- **Charcoal Ink** (#F2F4F3) — Primary text, warm off-white
- **Muted Sage** (#8A9A93) — Secondary text, metadata, axis labels
- **Whisper Border** (rgba(45,90,75,0.18)) — 1px structural lines, card borders
- **Sage Signal** (#14BE8A) — **Single accent**, success/PASS/active, saturated <68%
- **Amber Caution** (#E8A42A) — Warning, correction loop only — not accent
- **Coral Down** (#E85D5B) — Down-regulated, FAIL only
- **Diffused Sage Glow** (rgba(20,190,138,0.08)) — Accent wash, not neon
- **Shadow** (rgba(0,0,0,0.4) 0 20px 40px -16px) — Deep lab shadow

Banned: Pure black #000000, AI purple/neon gradients, oversaturated >80%, warm/cool gray mix

## 3. Typography Rules
- **Display:** `Satoshi`, `Cabinet Grotesk`, fallback sans — Track-tight (-0.03em), compressed leading 0.95, weight 700-900, fluid clamp(2.2rem, 5vw, 4.2rem)
- **Body:** `Geist`, `Satoshi` weight 400 — 1.65 leading, 65ch max, Muted Sage #8A9A93
- **Mono:** `JetBrains Mono`, `Geist Mono` — For genes, log2FC, padj, timestamps, run IDs. 0.78rem, tabular-nums
- **Numbers:** Always mono when dense. log2FC ±0.00, padj 0.00e+00
- Banned: Inter, Times/Georgia, generic serif in dashboard

## 4. Component Stylings
* **Buttons:** Flat, 12px radius, accent fill Sage Signal with Void text for primary. Ghost with Whisper Border for secondary. Active: scale(0.97) + -1px y. No outer glow. Min 44px height.
* **Cards:** 24px radius (1.5rem), Surface fill, Whisper Border 1px, diffused shadow, padding 1.5–2rem. Used only when elevation conveys hierarchy. High-density replaces with border-top dividers.
* **Inputs/Select:** Label above (mono 0.7rem uppercase tracking 0.08em), input Surface Elevated + Whisper Border, focus ring Sage Signal 1px, 12px radius. Error below in Coral.
* **Badges:** Mono 10px uppercase, 999px pill, dotted border, accent wash for PASS, amber for WARNING, coral wash for FAIL.
* **Loaders:** Skeletal shimmer matching exact card dimensions, shifting sage reflection — never circular spinner.
* **Empty States:** Composed centrifuge/plate illustration + guidance, not "No data"

## 5. Layout Principles
- **Grid-first:** CSS Grid, never calc() hacks. Max-width 1440px centered, padding 1rem/2rem/3rem
- **Hero:** Asymmetric split — Left 58% headline + inline lab micro-images at type-height (rounded, 1.1em), Right 42% live helix/sequence viz. Stacks single column <1024px. Centered hero BANNED.
- **Bento:** Row 1: Run Console (2fr) + Resource/Model (1fr) | Row 2: Trace (1.4fr) + Volcano (1fr) | Row 3: Pathway Bento (3-col asymmetric 1.8fr 1fr 1fr)
- **No 3-equal-cards:** All grids asymmetric or bento
- **No overlapping:** Every element its own grid cell, clean separation
- **Full-height:** min-h-[100dvh] never h-screen

## 6. Motion & Interaction
- **Spring:** stiffness 100, damping 20, weighty premium feel. No linear easing
- **Perpetual:** Pulse on live dots, shimmer on loading strips, float on helix strands, typewriter on gene symbols, breathing on VRAM bar
- **Staggered:** Lists mount via calc(var(--i)*80ms) cascade, never instant
- **Hardware:** transform + opacity only. Grain on fixed pseudo-element only

## 7. Anti-Patterns (Banned)
No emojis, no Inter, no pure black, no neon glows, no oversaturated, no gradient text headers, no custom cursors, no overlapping, no 3-col equal grids, no centered hero, no filler "Scroll to explore", no generic names, no fake metrics, no LABEL // YEAR, no AI clichés Elevate/Seamless/Unleash
