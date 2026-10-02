---
version: 1
slug: "readme-md"
primary_target: "README.md"
related_targets: []
---

# Surface: GitHub profile README

Scope: `README.md` and its `assets/` SVGs. Mode: Persuade. Visitor arrives from a repo, a post or LinkedIn; success is a click into a product, kushalbanda.com, Medium or email.

World: inherited from kushalbanda.com (`kushalBanda/sites`, `docs/portfolio/DESIGN.md`). GitHub strips CSS and scripts, so every designed surface is a committed SVG; text between them is GitHub's own Markdown.

## Direction contract

THESIS: The products open the page, as the site's hover-preview cards laid flat, before any words about the person. Refuses the category default: emoji bullets, a badge wall and third-party stats cards.

OWN-WORLD: Three fields in order, grey #737677 name band, GitHub's page as the white body, ink #1C1D20 footer. General Sans 400 at -0.03em for anything large, embedded in each SVG. Product cards carry each product's own colours (OpusBar cream #F5F1E4, Graphy blue #5A8BE6, OpenTicker ink #0F1115); blue #455CE9 only on the footer's round "Get in touch". Circles and pills, 4px image corners, soft shadow only on screenshots.

STORY: Visitor sees three working products, learns Kushal builds tools for people who work with AI agents, sees he writes weekly, and taps a product, the site, or email.

FIRST VIEWPORT: Full-width grey band (about 4:1): "Kushal Banda" at display size sliding left, running off both edges; ink half-pill flush left "Based in Hyderabad, India" with the turning globe; role "AI Engineer, building tools for agents" upper right. Directly under it a filmstrip of three equal linked cards, each about a third of the width: cream OpusBar with the pixel cat running at 4x, blue Graphy with its screenshot, ink OpenTicker "Coming soon"; name and kind set inside each card's foot. Primary action is each card; the site link sits in the line right after.

FORM: Preview Filmstrip, position 5 of 7 on the ranked list; seed key 079c6fc7. Signature interaction: the name slides and the cat runs, both SVG-native CSS animation, both stopped under prefers-reduced-motion. Footer ink panel with the white page curving into it, light and dark variants via <picture>.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Decisions

- Cut: joke card, view counter, readme-stats/streak cards, shields badge wall (stack becomes one plain line). Kept as text links: Codeforces, LeetCode, CodeChef.
- Writing: latest five Medium posts between `<!-- medium:start -->` / `<!-- medium:end -->`, refreshed daily by `.github/workflows/medium.yml`.
