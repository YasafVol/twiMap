You picked a tiny project, I see. “Let’s index the longest novel in the English language and turn it into a knowledge engine.”

I like it.

I’ll break this into: **(1) Reality checks & constraints, (2) Data model & filters, (3) Ingestion & LLM “x-ray”, (4) Backend architecture, (5) UI/UX design, (6) Phased roadmap.**

---

## 1. Reality checks & constraints

**1.1. Copyright & permission**

The Wandering Inn is fully copyrighted, not public domain. The site & books are commercial, heavily monetized via ebooks, audio, Patreon, merch, etc.([The Wandering Inn][1])

So:

* Scraping the *full text* and running a *public* webapp on top of it is murky at best and likely not OK without explicit permission.
* Safe pattern:

  * For **personal use**: you can scrape locally, run analysis, keep everything private.
  * For a **public site**: store **metadata & structured summaries**, not raw text; ideally get author’s blessing.

I’d design assuming:

* Internally: full text allowed (for you).
* Publicly: you only expose summaries, stats, graph structures and short, non-substantial snippets.

**1.2. Scale**

We’re around 12–15M words so far.([The Wandering Inn][2])
That’s:

* Thousands of chapters & interludes.([Wandering Inn Wiki][3])
* A ridiculous number of entities (characters list alone is >1,200).([The Wandering Inn][4])

TL;DR: you’re building *a real product*, not a weekend hack.

---

[![Volume 1 - The Wandering Inn Wiki](https://tse3.mm.bing.net/th/id/OIP.ej6jNfaTLdz0Q_ILKaTWzgHaL2?cb=ucfimg2\&pid=Api\&ucfimg=1)](https://wiki.wanderinginn.com/Volume_1?utm_source=chatgpt.com)

---

## 2. Core content model & filters

You already have: **character, location, event, plot line, time**. Good. Let’s systematize & expand.

### 2.1. Canonical entities

Use the existing wiki as your spine; it already breaks things down into volumes, chapters, characters, locations, classes, races, timeline, etc.([Wandering Inn Wiki][5])

**Entities:**

* **Work structure**

  * `Volume`
  * `Chapter` (includes main / interlude, book vs side story, etc.)([Wandering Inn Wiki][3])
  * `Scene` (your own subdivision inside chapters for x-ray granularity)

* **World entities**

  * `Character`
  * `Location` (continent / city / building / region)
  * `Faction` (Reinharts, Antinium hives, Pallass, etc.)
  * `Race`
  * `Class` (system classes listed in tables)([Wandering Inn Wiki][6])

* **Narrative entities**

  * `Arc / Plotline` (based in part on fan arc overviews)([The Wandering Inn][7])
  * `Event` (battle, negotiation, death, voyage, etc.)
  * `Theme` (war, trauma, slice-of-life, politics, leveling, etc.)
  * `Tone` (light, grim, horror, bittersweet, etc.)

* **Meta entities**

  * `PublicationDate`
  * `WordCount` for chapter/volume (stats are already tracked by fans).([The Wandering Inn][2])

### 2.2. Filters / facets

So for the UI, you want these main filters:

1. **Character POV**

   * Primary POV character of chapter/scene.
   * Other POVs present (for multi-POV scenes).

2. **Location**

   * Continent / region / city / specific place (The Wandering Inn, Liscor, Pallass, Rhir, etc.).

3. **Time**

   * In-world timeline (e.g. “X days after Erin arrives”, “Year of…”) using the fan timeline as reference.([Wandering Inn Wiki][8])
   * Real-world publication date (for release order).

4. **Volume / chapter / arc**

   * Volume index, chapter number.
   * Named arcs or major storylines (Meeting of Tribes, Antinium Wars, etc.)([The Wandering Inn][7])

5. **Faction / race / class**

   * Which factions appear in the scene.
   * Dominant race(s) & classes (e.g. [Innkeeper], [Necromancer], [King], etc).([Wandering Inn Wiki][6])

6. **Event type**

   * Battle, political meeting, dungeon crawl, downtime/slice-of-life, training, travel, flashback.

7. **Tone / content warnings**

   * Lighthearted, tragic, horror, high-tension, aftermath/quiet.
   * CW: graphic violence, body horror, etc.

8. **Spoiler level**

   * Tag each entity with its **earliest spoil-chapter**; you can then filter based on “I’ve read up to chapter X”.

That’s your “x-ray parameter space”.

---

## 3. Ingestion & LLM “x-ray” pipeline

### 3.1. Source data

1. **Official web serial**

   * Start from the official table of contents.([The Wandering Inn][9])
   * For each chapter URL, fetch HTML, strip ads/navigation, extract main content.

2. **Fan / official wiki**

   * Chapter list, volume boundaries, characters, classes, timeline, etc.([Wandering Inn Wiki][3])
   * Use this as *seed ontology* and for cross-checking LLM output.

3. **Word count stats**

   * Optional, but nice for analytics & pacing.([The Wandering Inn][2])

### 3.2. Chunking strategy

Chapters are huge. Word counts regularly blow past 10–20k.([The Shield][10])

You want:

* **Scene-sized chunks**: 1–3k words per chunk.
* Scene boundaries:

  * Obvious separators (horizontal rules, scene breaks, “—” separators).
  * POV change markers.
  * Fallback: naive chunk split on length with slight overlap.

Each chunk gets a `scene_id` with `chapter_id` + index.

### 3.3. X-ray via LLM

For each **scene**, send to your model with a structured prompt:

> “Given this scene from *The Wandering Inn*, extract JSON with:
>
> * `summary_short` (2–3 sentences, no spoilers beyond this scene)
> * `summary_detailed`
> * `characters` (list with `name`, `role_in_scene`, `status_change`, `faction`, `race`, `class_if_mentioned`)
> * `locations` (hierarchy: continent > region > city > place)
> * `events` (semantically meaningful actions; label with `event_type`)
> * `arcs` (choose from this controlled vocabulary, multi-select)
> * `time_anchor` (relative or absolute timeline notes)
> * `tone` & `content_tags`
> * `quotes` (0–2 short, non-critical lines for flavor; optional)
> * `spoiler_scope` (earliest chapter this reveals information about)
> * `links_to_prior` (chapter/scene IDs referenced if evident)”

Use a **controlled vocabulary** for:

* `event_type`, `tone`, `arcs`, `content_tags`. That keeps the data consistent.

You can give the model:

* A **global schema**.
* A **lookup table** of known characters/locations/arcs from the wiki, so it prefers canonical names.

You will also want:

* A second LLM pass per chapter that:

  * Merges scene-level outputs into chapter-level summary + metadata.
  * Detects cross-scene events (e.g. “battle” spans multiple scenes).

### 3.4. Quality & cost control

* Start with **one volume** (e.g. Volume 1 Rewrite) as a pilot.
* Build tools for **spot-checking**:

  * A UI for side-by-side: scene text (private) vs extracted JSON.
  * Manual override / corrections.
* Cache raw LLM responses; re-run only when schema changes.

---

## 4. Backend architecture

Keep this simple and composable.

### 4.1. Storage

I'd do:

1. **Relational / document store (Postgres or similar)**

   * Tables/collections:

     * `volumes`, `chapters`, `scenes`
     * `characters`, `locations`, `factions`, `races`, `classes`, `arcs`, `events`
     * `scene_entities` (join table mapping scenes ↔ entities with roles)
     * `chapter_stats` (word count, reading time, etc.)

2. **Graph layer**

   * Use either:

     * A graph DB (Neo4j) *or*
     * Graph tables in Postgres (`nodes`, `edges`) tagged by entity type.
   * Edges like:

     * `APPEARS_IN` (character → scene)
     * `TAKES_PLACE_IN` (scene → location)
     * `MEMBER_OF` (character → faction, race, class)
     * `PART_OF` (scene/chapter → arc)
     * `CAUSES`, `CONFLICTS_WITH`, `ALLY_OF`, etc. (optional).

3. **Search index**

   * For text queries & faceting:

     * Use Meilisearch / OpenSearch / Typesense.
   * Index:

     * `scene.summary_short`, `chapter.title`, `character.name`, tags, etc.

4. **Vector index**

   * For semantic similarity (“find scenes similar to this one”).
   * Could be pgvector inside Postgres or an external vector DB.
   * Embed: scene summaries, character bios, event descriptions.

### 4.2. API surface

Strong candidate: **GraphQL** API + a small REST layer for heavy queries.

Key operations:

* `chapter(id)` → metadata, summaries, scenes.
* `searchScenes(filters...)`:

  * filters: character IDs, locations, arcs, date range, tone, tags, etc.
* `character(id)` → timeline of appearances, relationships.
* `arc(id)` → chapters & scenes in that arc.
* `timeline(range, filters)` → list of events in chronological order.
* `similarScenes(sceneId)` / `recommendations`.

---

## 5. UI / UX design

Now the fun part. How to let a poor human brain navigate 15M words.

### 5.1. Core user modes

Think of three main modes:

1. **I want to know “what happens when/where/with whom”**
   → Timeline & arc explorer.

2. **I care about specific characters / factions**
   → Character & faction dashboards.

3. **I want to review or re-read specific parts**
   → Chapter / scene x-ray with fast filters.

---

### 5.2. Home screen

**Layout idea:**

* Left: **search + quick filters**

  * Search bar with suggestions: “Erin Solstice”, “Meeting of Tribes”, “Pallass”.
  * Toggles: `Hide spoilers beyond chapter X`, tone filters.
* Center: **“Story map”**

  * Multi-lane timeline; each lane is a major arc.
  * Scrollable horizontally; each node = volume cluster; click to zoom into chapters.
* Right: **Highlights**

  * Top characters, arcs, locations by number of appearances.
  * “Densest” chapters (by word count or events).

---

### 5.3. Chapter / scene explorer

From the TOC you already know volumes & chapters.([The Wandering Inn][9])

**List view:**

* Table with:

  * Volume, chapter number, title, word count, publication date.
  * Icons for:

    * Number of POVs.
    * Count of named characters.
    * Event types (battle, politics, downtime).
    * Tone (color-coded bar).
* Filters:

  * Volume range.
  * Character appears / POV.
  * Location.
  * Arc.
  * Tone / event type.
  * Only chapters you’ve already read.

**Detail view (“x-ray”):**

* Top:

  * Chapter title, volume, date, word count, reading time.
  * Arc chips (Meeting of Tribes, etc.).
  * Big warning bar for spoiler level if user reading position < this chapter.

* Middle:

  * **Non-spoiler summary** (safe for people reading along).
  * Optional: “expand to full summary” button.

* Sections:

  * **Scenes** list:

    * For each: short summary, filters (characters, location, event types, tone).
  * **Characters**:

    * Grid of faces or avatars (you can tie into the fanart/booru ecosystem for extra spice).([Wandering Inn Wiki][11])
    * Tag chips: race, class, faction.
  * **Events & consequences**:

    * List of events + “what changes as a result” (deaths, level ups, alliances, revelations).

---

### 5.4. Character explorer

**Character page:**

* Header:

  * Name, aliases, race, class, faction.
  * Spoiler badge: “Safe up to Ch 4.20 only” etc.

* Sections:

  1. **Bio summary**
  2. **Appearance timeline**

     * Horizontal timeline: ticks per chapter; heat map for “importance” (screen time).
  3. **Key events**

     * Table: chapter → event → outcome.
  4. **Relationships graph**

     * Network: this character centered, edges to allies/enemies/mentors/etc.
  5. **Arcs participation**

     * Bar chart / list: how many scenes per arc.

User flows:

* “Show me all scenes where Erin and Ryoka interact in Liscor before Volume 3.”
  That’s a multi-facet search: chars, location, volume range.

---

### 5.5. Arc / plotline explorer

Use the arc overview as a starting taxonomy.([The Wandering Inn][7])

**Arc page:**

* Title, short description, main themes.
* Arc timeline: chapters where it’s active.
* Lanes for:

  * Key characters in this arc.
  * Major events.
* “Entry points”:

  * Which chapter you can start from if you only want this storyline.

Nice feature: **arc braiding view**

* Multiple arcs shown as colored ribbons on a single timeline.
* Shows where they overlap or go dormant.

---

### 5.6. Timeline explorer

You already have fan-maintained timeline tables; you can align your events against them.([Wandering Inn Wiki][8])

* Zoomable horizontal timeline (think: World Anvil / timeline apps, but with filters).
* Filters:

  * Specific characters.
  * Specific locations.
  * Event types (battles only, political events, etc.).
  * In-world era vs “modern” story time.
* Clicking on an event shows:

  * Short description.
  * Linked scenes/chapters.
  * Involved characters.

---

### 5.7. Spoiler management

Crucial if you want people to actually use this.

* User declares: “I’m at **Volume X, Chapter Y**.”
* Every entity has `spoiler_from_chapter_id`.
* UI rules:

  * Hide or blur anything with `spoiler_from > user_read_upto`.
  * Option for “peek through spoilers” per page (manual override).

The chapter timeline page already tries to list events chronologically, which you can use to anchor these earliest spoil points.([The Wandering Inn][12])

---

## 6. Phased roadmap

You’re not building Innworld in a day.

### Phase 0 – Permission & scope

* Decide: **private tool** vs **public site**.
* If public, strongly consider contacting the author / team with a sane proposal:

  * “Graph x-ray site, no full text, links back to the main site & Patreon.”
* Define which parts stay private (raw scraped text, full LLM outputs).

### Phase 1 – Metadata-only prototype

No scraping yet, just:

* Import:

  * TOC & chapter list.([The Wandering Inn][9])
  * Volumes, wiki character list, locations, class list, timeline skeleton.([Wandering Inn Wiki][5])
* Build:

  * DB schema with entities & relationships.
  * Basic GraphQL API.
  * Simple UI:

    * Characters index.
    * Volume/chapter list.
    * Timeline with only major milestones from the wiki.

This lets you validate **data model & UX** without touching the text.

### Phase 2 – LLM x-ray for one volume

* Implement:

  * Scraper for your local environment.
  * Chunking + LLM extraction pipeline.
  * Admin review UI to spot-check outputs.
* Run it on **Volume 1 Rewrite** first.

Iterate until:

* Entity extraction is stable.
* Filters behave as expected.
* UI feels good.

### Phase 3 – Scale up & optimization

* Ingest more volumes gradually.
* Add:

  * Semantic search.
  * Graph visualizations.
  * Spoiler state.

### Phase 4 – Fancy stuff

Once basics work:

* “Story pace” visualizations (word count per chapter, density of events, etc.).([The Wandering Inn][2])
* Mood maps (“where are the most tragic chapters?”).
* Recommendation mode:

  * “Show me 5 ‘quiet’ Erin chapters between Meeting of Tribes and X.”
* Hook into fanworks (art, fangames) via the wiki fanworks page & booru.([Wandering Inn Wiki][11])

---

If you want next, I can:

* Sketch a concrete **DB schema** (tables / fields) and/or
* Draft the **LLM extraction prompt & JSON schema** so you can start running chapters through “the model you mentioned” and see how noisy the output is.

You’re basically building the Innverse Knowledge Graph. Mildly insane, but in a good way.

[1]: https://wanderinginn.com/?utm_source=chatgpt.com "The Wandering Inn: Overview"
[2]: https://wanderinginn.neocities.org/statistics?utm_source=chatgpt.com "The Wandering Inn — Statistics and Word Count - Neocities"
[3]: https://wiki.wanderinginn.com/Chapter_List?utm_source=chatgpt.com "Chapter List"
[4]: https://thewanderinginn.fandom.com/wiki/Category%3ACharacters?utm_source=chatgpt.com "Category:Characters | The Wandering Inn Wiki | Fandom"
[5]: https://wiki.wanderinginn.com/The_Wandering_Inn_Wiki?utm_source=chatgpt.com "The Wandering Inn Wiki"
[6]: https://wiki.wanderinginn.com/List_of_Classes?utm_source=chatgpt.com "List of Classes"
[7]: https://thewanderinginn.fandom.com/wiki/Arc_Overview?utm_source=chatgpt.com "Arc Overview | The Wandering Inn Wiki - Fandom"
[8]: https://wiki.wanderinginn.com/Timeline?utm_source=chatgpt.com "Timeline"
[9]: https://wanderinginn.com/table-of-contents/?utm_source=chatgpt.com "Table of Contents"
[10]: https://theshieldrrhs.wordpress.com/2023/03/15/the-wandering-inn-a-tale-within-itself/?utm_source=chatgpt.com "The Wandering Inn: A Tale Within Itself - The Shield"
[11]: https://wiki.wanderinginn.com/Fanworks?utm_source=chatgpt.com "Fanworks - The Wandering Inn Wiki"
[12]: https://thewanderinginn.fandom.com/wiki/Chapter_Timeline?utm_source=chatgpt.com "Chapter Timeline | The Wandering Inn Wiki - Fandom"
