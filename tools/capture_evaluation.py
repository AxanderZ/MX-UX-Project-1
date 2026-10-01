#!/usr/bin/env python3
"""
Capture the annotated screenshots used in the heuristic evaluation write-up.

  pip install playwright   (uses your installed Google Chrome)
  python3 tools/capture_evaluation.py            # all shots
  python3 tools/capture_evaluation.py h1 a2      # only some

Each shot loads a real page (Wikipedia, WAVE, or the live redesign), draws numbered
markers on the elements being discussed, adds a legend card and a verdict banner,
and saves a PNG to docs/evaluation/.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "docs" / "evaluation"
OUT.mkdir(parents=True, exist_ok=True)
WP = "https://en.wikipedia.org/wiki/"
SITE = "https://axanderz.github.io/my-awesome-site/"

# Draws markers in viewport (fixed) coordinates, so it works at any scroll position.
ANNOTATE = r"""
({targets, banner, tone, legend}) => {
  document.querySelectorAll('.ux-annot').forEach(e => e.remove());
  const color = tone === 'violation' ? '#b3001b' : tone === 'info' ? '#1b4fb4' : '#0a6b2e';
  const font = '-apple-system, "Helvetica Neue", Arial, sans-serif';
  const mk = (css, txt) => { const d = document.createElement('div'); d.className = 'ux-annot';
    Object.assign(d.style, {position:'fixed', zIndex:2147483000, pointerEvents:'none', fontFamily:font, boxSizing:'border-box'}, css);
    if (txt !== undefined) d.textContent = txt; document.body.appendChild(d); return d; };
  const missing = [];
  targets.forEach((t, i) => {
    let els = [];
    if (t.selector) els = [...document.querySelectorAll(t.selector)].filter(e => { const r = e.getBoundingClientRect(); return r.width && r.height && r.bottom > 0 && r.top < innerHeight; });
    if (t.text) { const it = document.evaluate(`//*[not(self::script)][normalize-space(text())="${t.text}"]`, document, null, 7, null);
      for (let k = 0; k < it.snapshotLength; k++) { const e = it.snapshotItem(k); const r = e.getBoundingClientRect(); if (r.width && r.bottom > 0 && r.top < innerHeight) els.push(e); } }
    els = els.slice(0, t.max || 1);
    if (!els.length) missing.push(t.label.slice(0, 40));
    els.forEach((el, j) => {
      const r = el.getBoundingClientRect(); const pad = t.pad ?? 4;
      if (!t.nobox) mk({left:(r.left-pad)+'px', top:(r.top-pad)+'px', width:(r.width+pad*2)+'px', height:(r.height+pad*2)+'px',
          border:`3px solid ${color}`, borderRadius:'6px', boxShadow:'0 0 0 2px #fff'});
      if (j === 0) mk({left:(r.left-pad-13)+'px', top:(r.top-pad-13)+'px', width:'26px', height:'26px', borderRadius:'50%', background:color,
          color:'#fff', font:`700 14px/22px ${font}`, textAlign:'center', border:'2px solid #fff', boxShadow:'0 1px 4px rgba(0,0,0,.45)'}, String(i+1));
    });
  });
  const L = legend || {};
  const card = mk({left:(L.x ?? 1148)+'px', top:(L.y ?? 170)+'px', width:(L.w ?? 240)+'px', background:'#fff', color:'#111',
     border:`3px solid ${color}`, borderRadius:'10px', padding:'10px 12px', boxShadow:'0 6px 18px rgba(0,0,0,.28)', font:`14px/1.4 ${font}`});
  targets.forEach((t, i) => { const row = document.createElement('div'); Object.assign(row.style, {display:'flex', gap:'8px', margin: i ? '8px 0 0' : '0'});
    const n = document.createElement('span'); n.textContent = i+1;
    Object.assign(n.style, {flex:'0 0 22px', height:'22px', borderRadius:'50%', background:color, color:'#fff', font:`700 13px/22px ${font}`, textAlign:'center'});
    const s = document.createElement('span'); s.textContent = t.label; row.append(n, s); card.appendChild(row); });
  mk({left:'0', right:'0', bottom:'0', background:color, color:'#fff', font:`600 17px/1.35 ${font}`, padding:'11px 18px', boxShadow:'0 -2px 10px rgba(0,0,0,.3)'}, banner);
  return missing;
}
"""


def annotate(page, targets, banner, tone, legend=None):
    missing = page.evaluate(ANNOTATE, {"targets": targets, "banner": banner, "tone": tone, "legend": legend})
    if missing:
        print("   ! no match for:", missing)
    page.wait_for_timeout(250)


def scroll_to(page, js_el, offset=90):
    page.evaluate(f"(() => {{ const e = {js_el}; window.scrollTo({{top: e.getBoundingClientRect().top + scrollY - {offset}, behavior: 'instant'}}); }})()")
    page.wait_for_timeout(900)


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"))
    print("saved", name)


def open_page(browser, url, w=1400, h=860):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, locale="en-US",
                              color_scheme="light", reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(url, wait_until="networkidle")
    # Hide Wikipedia's fundraising banner, which appears randomly and covers content.
    page.add_style_tag(content="#centralNotice { display: none !important; }")
    page.wait_for_timeout(900)
    return page


SHOTS = {}
def register(name):
    def deco(fn):
        SHOTS[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- heuristics
@register("h1")
def h1(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    scroll_to(pg, "document.getElementById('Rivalries')", 20)
    pg.mouse.wheel(0, 300); pg.wait_for_timeout(1200)
    annotate(pg, [
        {"selector": ".vector-toc-level-1-active > a", "label": "The Contents list highlights the section you are reading (Rivalries) and updates as you scroll."},
        {"selector": "#vector-toc-pinned-container .vector-toc", "pad": 0, "label": "The list stays pinned on screen 20,000+ pixels down the page, so you always know where you are."},
    ], "H1 Visibility of system status: UPHOLDS. Readers can always see their position in a very long article.", "uphold")
    shot(pg, "h1-visibility-of-system-status")


@register("h2")
def h2(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    annotate(pg, [
        {"selector": "#ca-talk", "label": "“Talk” is the editors' discussion page. Casual readers have no reason to guess that."},
        {"selector": "#ca-viewsource", "label": "“View source” shows wiki markup, not the article's sources, which is easy to confuse with References."},
        {"selector": "#ca-history", "label": "“View history” is the edit log, not the team's History section."},
        {"selector": ".mw-indicators", "label": "An unlabeled padlock. It means the page is semi-protected from editing."},
        {"selector": "#mw-content-text p sup.reference", "max": 3, "label": "Two bracket systems, [a] notes and [1] citations, sit side by side in the prose."},
    ], "H2 Match between system and real world: VIOLATION (severity 2). Wiki-insider words and symbols instead of everyday language.", "violation",
        {"x": 1148, "y": 180, "w": 240})
    shot(pg, "h2-match-system-real-world")


@register("h3")
def h3(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    annotate(pg, [
        {"selector": "#vector-toc-pinned-container .vector-pinnable-header-unpin-button", "label": "“hide” moves the Contents panel out of the way. It can be pinned back from the icon beside the title."},
        {"selector": "#vector-appearance-pinned-container .vector-pinnable-header-unpin-button", "label": "“hide” collapses the Appearance panel, which can be restored the same way."},
        {"selector": "#vector-page-tools-dropdown", "label": "The Tools menu can also be pinned or unpinned."},
    ], "H3 User control and freedom: UPHOLDS. Every panel has a visible, reversible way to dismiss it.", "uphold",
        {"x": 290, "y": 590, "w": 520})
    shot(pg, "h3-user-control-freedom")


@register("h4")
def h4(b):
    pg = open_page(b, WP + "Main_Page")
    annotate(pg, [
        {"selector": ".mw-logo", "label": "Logo at top left returns to the homepage, a web convention."},
        {"selector": "#p-search", "label": "Search box at the top with a magnifier icon, in the same place on every page."},
        {"selector": ".vector-user-links", "label": "Account links at top right."},
        {"selector": "#left-navigation", "label": "The same tabs and layout as every article page, so skills carry over."},
    ], "H4 Consistency and standards: UPHOLDS. The homepage and all 7 million articles share one familiar layout.", "uphold",
        {"x": 1148, "y": 190, "w": 240})
    shot(pg, "h4-consistency-standards")


@register("h5")
def h5(b):
    pg = open_page(b, WP + "Main_Page")
    pg.click("#p-search input[type=search], #searchInput")
    pg.keyboard.type("golden state warr", delay=70)
    pg.wait_for_timeout(2500)
    annotate(pg, [
        {"selector": ".cdx-menu__listbox", "label": "Title suggestions appear while typing, so users pick the right article instead of mistyping a search."},
        {"selector": ".cdx-typeahead-search__search-footer, .cdx-menu__footer", "label": "A full-text search fallback is always offered."},
    ], "H5 Error prevention: UPHOLDS. Autocomplete stops failed searches before they happen (task step: search).", "uphold",
        {"x": 1100, "y": 170, "w": 280})
    shot(pg, "h5-error-prevention")


@register("h6")
def h6(b):
    pg = open_page(b, WP + "Golden_State_Warriors", h=1000)
    scroll_to(pg, "document.getElementById('Current_roster')", 10)
    annotate(pg, [
        {"text": "Pos.", "label": "“Pos.” and “DOB” are unexplained on screen (the meaning is only in a hover tooltip)."},
        {"text": "(TW)", "max": 3, "label": "“(TW)” tags on players. What TW means is not stated here."},
        {"selector": "img[alt='Injured'], img[alt*='njur']", "max": 2, "label": "A tiny red cross marks injured players, also unexplained here."},
        {"text": "Legend", "label": "The key sits in a separate column below the coaching staff, so readers must remember codes or scroll back and forth."},
    ], "H6 Recognition rather than recall: VIOLATION (severity 2). Readers must decode abbreviations explained elsewhere.", "violation",
        {"x": 1148, "y": 430, "w": 240})
    shot(pg, "h6-recognition-rather-than-recall")


@register("h7")
def h7(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    # The Stephen Curry link is in the first screen, so the search box stays visible too.
    pg.locator("#mw-content-text a", has_text="Stephen Curry").first.hover()
    pg.wait_for_timeout(2600)
    annotate(pg, [
        {"selector": ".mwe-popups", "label": "Shortcut 1: hovering a link (here the related article, Stephen Curry) previews it without leaving the page. Beginners can ignore it."},
        {"selector": "#p-search input[type=search], #searchInput", "label": "Shortcut 2: an access key jumps straight to search (Alt+Shift+F, or Ctrl+Option+F on a Mac). It appears only in the tooltip, so it adds no clutter."},
        {"selector": "#vector-appearance-pinned-container", "pad": 2, "label": "Minor clutter: the Appearance settings panel is open by default on wide screens, even for readers who never change it."},
    ], "H7 Flexibility and efficiency of use: UPHOLDS. Shortcuts for experienced readers that beginners never have to see.", "uphold",
        {"x": 20, "y": 425, "w": 250})
    shot(pg, "h7-flexibility-efficiency")


@register("h8")
def h8(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    stats = pg.evaluate("""() => { const c = document.querySelector('#mw-content-text');
        return {words: c.innerText.split(/\\s+/).length, h: document.documentElement.scrollHeight, links: c.querySelectorAll('a[href]').length,
                refs: document.querySelectorAll('sup.reference').length, tables: c.querySelectorAll('table').length}; }""")
    print("   stats:", stats)
    scroll_to(pg, "document.querySelector('[id^=\"2014\\u20132019\"]')", 70)
    pg.add_style_tag(content="#mw-content-text p a{background:#ffe45c !important;outline:1px solid #d9b300} #mw-content-text sup.reference, #mw-content-text p sup.reference a{background:#ffb3bd !important;outline-color:#e0788a}")
    annotate(pg, [
        {"selector": "[id^='2014–2019']", "label": "One history subsection. Every yellow mark is a link and every pink mark is a citation, so key facts compete for attention."},
        {"selector": "#vector-toc-pinned-container .vector-toc-level-1-active > a", "label":
            f"Whole article: {stats['words']:,} words, {stats['h']:,} px tall (about {stats['h'] // 860} screens), {stats['links']:,} links, {stats['refs']} citations, {stats['tables']} tables."},
    ], "H8 Aesthetic and minimalist design: VIOLATION (severity 3). Key facts are buried in a very long wall of links.", "violation",
        {"x": 1148, "y": 120, "w": 245})
    shot(pg, "h8-aesthetic-minimalist-design")


@register("h9")
def h9(b):
    pg = open_page(b, "https://en.wikipedia.org/w/index.php?search=golden+state+warirors&title=Special%3ASearch&ns0=1&fulltext=1")
    annotate(pg, [
        {"selector": ".searchdidyoumean", "label": "The misspelling is corrected in plain language, with a link to search for the original words instead."},
        {"selector": ".mw-search-result-heading a", "label": "The right article is one click away."},
    ], "H9 Recognize, diagnose, recover from errors: UPHOLDS. A misspelled search is fixed automatically (task step: search results).", "uphold",
        {"x": 1100, "y": 180, "w": 270})
    shot(pg, "h9-error-recovery")


@register("h10")
def h10(b):
    pg = open_page(b, WP + "Stephen_Curry")
    pg.click("#vector-main-menu-dropdown-checkbox")
    pg.wait_for_timeout(800)
    annotate(pg, [
        {"selector": "#n-help", "label": "“Help” opens a searchable, task-based help portal."},
        {"selector": "#n-contactpage", "label": "“Contact us” is always one menu away."},
        {"selector": "#vector-main-menu-dropdown", "pad": 2, "label": "Caveat: both live behind an unlabeled ☰ icon, so first-time readers may not find them."},
    ], "H10 Help and documentation: UPHOLDS (minor caveat). Task-focused help is available from every page, here the related article.", "uphold",
        {"x": 1100, "y": 190, "w": 280})
    shot(pg, "h10-help-documentation")


# ---------------------------------------------------------------- accessibility quick-check
@register("a1")
def a1(b):
    pg = open_page(b, "https://wave.webaim.org/report#/" + WP + "Golden_State_Warriors", h=900)
    pg.wait_for_timeout(12000)
    print("   WAVE:", pg.evaluate("document.body.innerText.match(/AIM Score:[^\\n]*/)?.[0]"))
    annotate(pg, [
        {"selector": "#numbers, .summary, #summary", "pad": 2, "label": "WAVE summary for the original article: errors, contrast errors and alerts, with the AIM score."},
    ], "Accessibility: WAVE automated check of the original article.", "info", {"x": 1100, "y": 120, "w": 280})
    shot(pg, "a1-wave-original")


@register("a2")
def a2(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    pg.evaluate("""() => { const t = document.querySelector('.navbox .mw-collapsible-toggle, .navbox .mw-collapsible-text');
        if (t) t.click(); }""")
    pg.wait_for_timeout(800)
    scroll_to(pg, "[...document.querySelectorAll('.navbox th')].find(th => th.textContent.trim() === 'Franchise')", 260)
    annotate(pg, [
        {"text": "1946", "label": "FAIL 3.10:1. Link “1946”, blue #3366CC on gold #FDB927 (needs 4.5:1)."},
        {"text": "Franchise", "label": "PASS 12.15:1. Label “Franchise”, black #000000 on gold #FDB927."},
        {"selector": ".navbox .navbar", "label": "Also FAIL 1.78:1: the “v · t · e” links, blue #3366CC on navy #1D428A."},
    ], "Manual contrast check on 2 text elements (WCAG 2.2 AA minimum 4.5:1 for normal text).", "info", {"x": 1100, "y": 150, "w": 280})
    shot(pg, "a2-contrast-check")


@register("a3")
def a3(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    annotate(pg, [
        {"selector": ".infobox img[alt='Golden State Warriors logo']", "label": "PASS. Team logo: alt=“Golden State Warriors logo”, which describes the image."},
    ], "Manual alt text check, image 1 of 2: infobox logo.", "uphold", {"x": 560, "y": 520, "w": 280})
    shot(pg, "a3-alt-text-logo")
    scroll_to(pg, "document.querySelector('img[src*=\"Joe_Fulks\"]')", 200)
    annotate(pg, [
        {"selector": "img[src*='Joe_Fulks']", "label": "FAIL. Photo of Joe Fulks: no alt attribute at all, and the image is a link, so screen readers announce only the file link."},
    ], "Manual alt text check, image 2 of 2: history photo (WAVE: “linked image missing alternative text”).", "violation", {"x": 560, "y": 420, "w": 300})
    shot(pg, "a3-alt-text-fulks")


@register("a4")
def a4(b):
    pg = open_page(b, WP + "Golden_State_Warriors")
    counts = pg.evaluate("""() => { const all = [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]')]
        .filter(e => e.getClientRects().length && e.tabIndex >= 0);
      const t = [...document.querySelectorAll('#mw-content-text a')].find(a => a.textContent.trim() === 'Stephen Curry');
      const start = document.getElementById('bodyContent');
      const afterSkip = all.filter(e => start.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING || start.contains(e));
      return {total: all.length, curry: all.indexOf(t) + 1, curryAfterSkip: afterSkip.indexOf(t) + 1}; }""")
    print("   tab stops:", counts)
    pg.keyboard.press("Tab")
    pg.evaluate("[...document.querySelectorAll('#mw-content-text a')].find(a => a.textContent.trim() === 'Stephen Curry').focus()")
    scroll_to(pg, "document.activeElement", 300)
    annotate(pg, [
        {"selector": ":focus", "pad": 10, "nobox": True, "label": f"Keyboard focus is clearly visible (2px blue outline). Reaching this link took {counts['curry']} Tab presses, or {counts['curryAfterSkip']} after using the skip link."},
    ], f"Manual keyboard check: every control is reachable and focus is visible, but the page has {counts['total']:,} tab stops.", "info",
        {"x": 1100, "y": 200, "w": 280})
    shot(pg, "a4-keyboard-focus")


# ---------------------------------------------------------------- redesign (after)
@register("r1")
def r1(b):
    pg = open_page(b, SITE + "wiki/Golden_State_Warriors.html")
    annotate(pg, [
        {"selector": ".page-actions", "label": "H2 fix: plain-language actions replace Talk / View source / View history."},
        {"selector": ".protect-note", "label": "H2 fix: page protection explained in a sentence instead of a padlock."},
        {"selector": ".stats", "label": "H8 fix: the answers most readers want come first, in “At a glance”."},
    ], "Redesign: article header and At a glance (fixes H2 and H8).", "uphold", {"x": 1130, "y": 120, "w": 255})
    shot(pg, "r1-redesign-header")


@register("r2")
def r2(b):
    pg = open_page(b, SITE + "wiki/Golden_State_Warriors.html")
    scroll_to(pg, "document.getElementById('History')", 80)
    annotate(pg, [
        {"selector": ".brief", "pad": 2, "label": "H8 fix: “History in brief” gives two sentences per era, each linked to the full original text."},
        {"selector": ".toc a[aria-current]", "label": "H1 kept: the contents list still highlights the current section."},
    ], "Redesign: summaries first, full detail on demand (fixes H8).", "uphold", {"x": 1130, "y": 140, "w": 255})
    shot(pg, "r2-redesign-history")


@register("r3")
def r3(b):
    pg = open_page(b, SITE + "wiki/Golden_State_Warriors.html")
    pg.evaluate("document.getElementById('Current_roster').closest('details').open = true")
    scroll_to(pg, "document.getElementById('Current_roster')", 80)
    annotate(pg, [
        {"selector": ".roster .legend", "label": "H6 fix: the legend sits above the table it explains."},
        {"selector": ".roster .badge", "max": 3, "label": "H6 fix: statuses are written out as text labels next to each name."},
        {"selector": "#roster-table thead", "label": "H6 fix: column names spelled out (Jersey number, Position, Born)."},
    ], "Redesign: roster that needs no memorizing (fixes H6).", "uphold", {"x": 1196, "y": 420, "w": 196})
    shot(pg, "r3-redesign-roster")


@register("r4")
def r4(b):
    pg = open_page(b, "https://wave.webaim.org/report#/" + SITE + "wiki/Golden_State_Warriors.html", h=900)
    pg.wait_for_timeout(12000)
    print("   WAVE:", pg.evaluate("document.body.innerText.match(/AIM Score:[^\\n]*/)?.[0]"))
    annotate(pg, [
        {"selector": "#numbers, .summary, #summary", "pad": 2, "label": "Redesigned article: 0 errors, 0 contrast errors, AIM score 10."},
    ], "Accessibility after the redesign: WAVE report of the rebuilt article.", "uphold", {"x": 1100, "y": 120, "w": 280})
    shot(pg, "r4-wave-redesign")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(SHOTS)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for name in wanted:
            print(name)
            SHOTS[name](browser)
        browser.close()
