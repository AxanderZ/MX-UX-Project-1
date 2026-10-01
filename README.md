# Encyclopedia Redesign

A UX class project that rebuilds Wikipedia's core reading experience (the homepage, the search flow, and a full article followed through to a related article), fixing its most severe usability problems and its WAVE accessibility errors.

**Live site:** https://axanderz.github.io/MX-UX-Project-1/

## The task this redesign supports

> *"Find out how many championships the Golden State Warriors have won and who was Finals MVP in 2022, then learn how Stephen Curry's career began."*

Path: **Homepage** → **search** "golden state warriors" (autocomplete or results page) → **[Golden State Warriors](https://axanderz.github.io/MX-UX-Project-1/wiki/Golden_State_Warriors.html)** → related-article link → **[Stephen Curry](https://axanderz.github.io/MX-UX-Project-1/wiki/Stephen_Curry.html)**.

| Page | File |
|---|---|
| Homepage | `index.html` |
| Search results (live Wikipedia search) | `search.html` |
| Help and how-to guide | `help.html` |
| Article | `wiki/Golden_State_Warriors.html` (all 17,457 words of the original) |
| Related article | `wiki/Stephen_Curry.html` (all 29,420 words of the original) |
| Error page | `404.html` |

## Heuristic violations resolved

These are the three violations from my heuristic evaluation, in order of severity.

| Heuristic (severity) | Problem on Wikipedia | Change in the redesign |
|---|---|---|
| **#10 Help and documentation (3)** | Help is hidden inside the ☰ "Main menu" button, which has low contrast against the page. Once the menu is open, "Help" is in the same color as every other item, so it's hard to spot. | **A solid gold "Help" button sits in the header of every page** (`.help-btn`). It has an icon and a text label, and dark ink on gold measures 9.6:1. It is never folded into a menu, even on phones, where the other nav links are hidden. It opens a new **Help page** (`help.html`) with plain-language answers on finding an article, reading quickly, citations, display settings, keyboard and screen reader use, and suggesting a correction. It also includes a glossary of Wikipedia jargon and a "Find a help topic" filter. Help is also offered in context: **"How to read this page"** under every article title, **"More about searching"** on the search page, and Help, Accessibility and Report-a-problem links in every footer. |
| **#8 Aesthetic and minimalist design (3)** | Too many in-text links and citation marks compete for attention and pull readers away from their goal. Key facts are buried in 17,500 words. | **Links and citations are quiet by default.** In-text links use the text color with a thin gray underline, so they're still recognizable but don't shout. Citation numbers are small and gray. **A "Hide links and citations" button under each article title** removes them entirely for distraction-free reading. Press it again to bring them back, and the same choice appears under Display, Links and citations (Highlighted / Quiet / Hidden). Navigation links such as "History in brief", "Main article" and buttons are never quietened. Content is reorganized too: "At a glance" facts come first, "History in brief" gives two sentences per era, and every subsection is collapsed with its reading time. |
| **#2 Match between system and the real world (2)** | "Talk" (an editors' discussion page) and "View source" (wiki markup, easy to confuse with the article's sources) mean little to casual fans. "View history", "v · t · e" and an unexplained padlock add to the confusion. | Plain-language actions: **Discuss this article**, **See who edited it**, **Suggest a correction**, **Read on Wikipedia**. "View source" is removed. The padlock is explained in a sentence. Navboxes become "Related topics" with no "v · t · e". "References" is renamed **Sources**, and "External links" is renamed **Elsewhere on the web**. The help page's glossary maps every Wikipedia label to its new name. |

The redesign keeps what Wikipedia already does well:
- **H1:** a contents list that highlights the current section, plus a reading progress bar.
- **H3 and H7:** reversible display settings for text size, width, theme and links.
- **H4:** a conventional header.
- **H5:** search suggestions.
- **H6:** roster legends and table keys sit above the tables.
- **H9:** "Showing results for … / Search instead for …" spelling correction, plus a clear error with a retry button if search is unreachable.

## Accessibility issues resolved

Baseline WAVE report for the original article: **AIM score 3.7**, with 25 errors, 93 contrast errors and 1,147 alerts.

The two issues I tested by hand, and how each is fixed:

| Finding in my evaluation | Who it affects | Fix |
|---|---|---|
| **Contrast:** the "1946" link in the team navigation box at the bottom is blue on gold, which fails. | People with color blindness or low vision | Team-color backgrounds are stripped from navigation boxes, now "Related topics". Every text color pair measures at least 6.2:1 in both light and dark themes, including the gold Help button at 9.6:1. |
| **Alt text:** the photo of Joe Fulks in the History section has no alt attribute, and the image is a link. | Blind and low-vision readers using screen readers | The photo now has the alt text "Professional basketball player Joe Fulks". The file-page link around it is removed, so there's no empty link. All 23 images WAVE flagged get the same fix. |

All WAVE findings:

| WAVE finding on Wikipedia | Fix |
|---|---|
| 4 missing alt text, 19 linked images missing alt | Every image has alt text. Descriptions come from Wikimedia Commons (95 characters max), and icons get `alt=""`. File links around images are removed. |
| 1 missing form label | Every search field has a `<label>`. |
| 1 empty link | Icon-only links (Wikidata edit pencils) are removed. |
| 93 very low contrast (team-color table headers, tinted navboxes) | Inline colors are stripped, and every text color pair measures at least 6.2:1 in light and dark themes. |
| 13 layout tables, 1 possible table caption | Layout tables become CSS layouts. Data tables get a `<caption>`, `<thead>` and `scope`, and empty header cells are removed. |
| 1,099 redundant title texts, 20 accesskeys, 8 redundant links | `title` attributes and access keys are removed, and the duplicate "Home" link is gone. |
| 3 missing fieldsets | Display options are grouped with `<fieldset>`/`<legend>`. |
| Bold paragraphs used as headings | Converted to real headings, so screen-reader heading navigation works. |

Also included: a skip link, landmarks, a sticky table of contents, visible focus rings, 24px minimum target size for citation markers (WCAG 2.2), an accessible combobox for search suggestions, sortable tables with `aria-sort` and a live announcement, and support for reduced motion and dark mode.

**WAVE results on the live site** (September 24, 2026):

| Page | AIM score | Errors | Contrast errors | Alerts |
|---|---|---|---|---|
| Original Wikipedia article | 3.7 | 25 | 93 | 1,147 |
| [Golden State Warriors](https://wave.webaim.org/report#/https://axanderz.github.io/MX-UX-Project-1/wiki/Golden_State_Warriors.html) | **10** | 0 | 0 | 2 |
| [Stephen Curry](https://wave.webaim.org/report#/https://axanderz.github.io/MX-UX-Project-1/wiki/Stephen_Curry.html) | **10** | 0 | 0 | 3 |
| [Homepage](https://wave.webaim.org/report#/https://axanderz.github.io/MX-UX-Project-1/) | **10** | 0 | 0 | 0 |
| [Search results](https://wave.webaim.org/report#/https://axanderz.github.io/MX-UX-Project-1/search.html?q=golden+state+warirors) | **10** | 0 | 0 | 0 |

**Automated check** (`tools/check_pages.py`, axe-core 4.10 plus WAVE-style rules, light and dark themes): **0 errors, 0 contrast errors, 0 axe violations on every page.** The only alerts left are WAVE's "Link to PDF document" on citations whose original sources are PDFs: 2 on the Warriors page and 3 on the Curry page. Those source links are kept on purpose.

## How it's built

`tools/build.py` downloads the current articles from the Wikipedia API and turns them into the redesigned pages: cleanup, restructuring, accessibility fixes and image credits. It also snapshots today's featured content for the homepage. The generated HTML is committed, so the site is plain static files.

```bash
pip install -r tools/requirements.txt
```
```bash
python3 tools/build.py
```

To run the checks, serve the folder (`python3 -m http.server 8765`), then run `python3 tools/check_pages.py` (needs `pip install playwright` and Google Chrome).

## Credits and license

Article text and data come from Wikipedia and its contributors under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This project is shared under the same license. Images come from Wikimedia Commons and are credited on each page. The at-a-glance summaries and "History in brief" were written for this redesign. This is a student project, not affiliated with Wikipedia or the Wikimedia Foundation.
