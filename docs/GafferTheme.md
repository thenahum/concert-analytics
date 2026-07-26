# Gaffer Theme

The Gaffer theme is the visual language for On the Setlist data journalism.

It exists to make charts feel like part of a documentary, not a dashboard. A
gaffer lights a scene without becoming the subject of the scene. Gaffer charts
should work the same way: guide attention, clarify evidence, and help readers
notice the thing the story needs them to see next.

## Contents

- [Purpose](#purpose)
- [Data Storytelling Philosophy](#data-storytelling-philosophy)
- [Colors](#colors)
- [Fonts](#fonts)
- [Using Codex For Visualizations](#using-codex-for-visualizations)
- [Checklist](#checklist)

## Purpose

Every chart, table, annotation, and paragraph should answer one question:

```text
What should the reader notice next?
```

The theme is intentionally understated. Visuals exist to illuminate the story,
not compete with it. Good Gaffer work should leave readers remembering the
insight more than the styling.

## Data Storytelling Philosophy

### Story First

Begin with a question, not a chart.

Useful starting questions sound like:

- Why do concerts evolve over a tour?
- Why do encore songs feel inevitable?
- Why does this artist never open with their biggest hit?

Only after the question is clear should we decide what visualization best
answers it.

### One Insight Per Graphic

Each visualization should communicate one primary idea. A chart can include
supporting context, but it should not ask readers to choose between competing
stories.

### Visual Hierarchy Is Editorial Hierarchy

Important observations get emphasis. Everything else supports quietly.

Use:

- color
- contrast
- annotation
- labels
- whitespace
- ordering

Never highlight something just because it looks attractive. Highlight it because
it matters.

### Restraint Is A Feature

Most dashboards contain too much information. Most stories contain too many
charts. Gaffer should make it easy to leave things out until they are useful.
Complexity should emerge gradually.

### Annotation Over Decoration

Annotations teach. Decoration distracts.

Prefer direct labels, callouts, highlighted observations, and plain source
captions. Avoid unnecessary gradients, decorative effects, chart junk, and
ornament that does not help the reader understand the evidence.

### Reproducibility Is Part Of Journalism

Published insights should be reproducible. Charts are code outputs. Data
transformations are documented. Queries are version controlled. Trust comes from
showing the path from source data to figure.

### Concerts Are Performances, Not Datasets

On the Setlist is not trying to prove that concerts can be quantified. It uses
data to reveal details of live performance that are hard to notice across dozens
or hundreds of shows. Statistics are the flashlight, not the destination. Every
metric should bring readers closer to the artistic decisions, rituals, and
evolution of a performance.

## Colors

Use `gaffer.COLORS` for the current palette.

The palette is meant to feel musical and editorial without becoming loud. Use
bright colors sparingly for emphasis, and let neutrals carry structure,
backgrounds, captions, and quiet context.

| Swatch | Name | Hex | Suggested Use |
| --- | --- | --- | --- |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#FB9E50;border:1px solid #777777;"></span> | `lightAmpOrange` | `#FB9E50` | Warm secondary highlight, period segment, accessible contrast against darker marks. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#F986BA;border:1px solid #777777;"></span> | `floodPink` | `#F986BA` | Occasional accent, contrast category, editorial callout. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#3C7DC4;border:1px solid #777777;"></span> | `setlistBlue` | `#3C7DC4` | Primary cool category, baseline series, link-like emphasis. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#D64848;border:1px solid #777777;"></span> | `spotRed` | `#D64848` | Alerting emphasis, negative comparison, rare but meaningful highlight. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#F25C05;border:1px solid #777777;"></span> | `ampOrange` | `#F25C05` | Strong warm highlight, use when the reader should notice one thing first. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#A7ECF5;border:1px solid #777777;"></span> | `lightBlue` | `#A7ECF5` | Soft comparison category, low-pressure fill, background-friendly segment. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#5D4E8C;border:1px solid #777777;"></span> | `encorePurple` | `#5D4E8C` | Encore, late-set, night, or special-context emphasis. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#33C27D;border:1px solid #777777;"></span> | `stageGreen` | `#33C27D` | Main positive highlight, current default for important bars. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#F6D357;border:1px solid #777777;"></span> | `clockYellow` | `#F6D357` | Time, sequence, duration, or careful emphasis. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#FAF3E0;border:1px solid #777777;"></span> | `spotlightCream` | `#FAF3E0` | Default plot and panel background. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#777777;border:1px solid #777777;"></span> | `gafferGrey` | `#777777` | Axis text, captions, subtle grid lines, quiet supporting marks. |
| <span style="display:inline-block;width:1.4em;height:1.4em;background:#1C1C1C;border:1px solid #777777;"></span> | `backstageBlack` | `#1C1C1C` | Strong text, high-emphasis labels, dark foreground details. |

Palette guidance:

- Start with `spotlightCream`, `gafferGrey`, and `backstageBlack`.
- Add one emphasis color for the primary insight.
- Add more colors only when categories truly need to be compared.
- Prefer direct labels over legends when space allows.
- Do not use color as decoration. Use it as editorial emphasis.

To preview the palette in Python:

```python
from setkit import gaffer

fig, ax = gaffer.preview_palette()
```

## Fonts

Use `gaffer.FONTS` for the current font roles.

| Role | Font | Current Use |
| --- | --- | --- |
| `axis` | `Courier New` | Axis text, captions, compact labels, technical texture. |
| `title` | `Helvetica` | Title or headline contexts when charts need a clean editorial voice. |

Font guidance:

- Keep typography restrained.
- Let chart titles and article prose carry the story outside the plot when
  possible.
- Use compact labels and captions inside charts.
- Avoid making charts feel like posters unless the story truly calls for it.

## Using Codex For Visualizations

When asking Codex to build or revise a Gaffer visualization, include the story
question first.

Helpful prompt shape:

```text
Question: What should the reader notice?
Audience: Curious music fans, not statisticians.
Dataframe: One row per song performance with columns ...
Primary comparison: Before Coachella vs Coachella vs After Coachella.
Required takeaway: Coachella sets leaned toward higher-popularity songs.
```

Good Codex visualization work should:

- identify the main insight before choosing the chart
- state what dataframe shape is expected
- use `setkit.transforms` before hand-rolled grouping when possible
- use `setkit.metrics` for reusable analytical calculations
- apply `gaffer.theme()` and `gaffer.source_caption()`
- save charts with `setkit.export`
- explain any live database, API, or notebook validation that was skipped

Avoid asking Codex for "a nice chart" without the editorial question. That tends
to optimize for appearance instead of evidence.

## Checklist

Before publishing or promoting a visualization, ask:

- Does the story answer a clear question?
- Does each visualization communicate one primary idea?
- Would the article become harder to understand if this chart were removed?
- Is visual hierarchy directing attention intentionally?
- Are annotations teaching rather than decorating?
- Can another engineer reproduce the figure?
- Would a curious music fan understand the point without knowing statistics?
- What is the one sentence readers should remember tomorrow?
