# Phase 7 — Dashboard and showcase website

| | |
|---|---|
| **Goal** | One public site that a judge understands in 60 seconds and can explore for 10 minutes. It is the pitch, the demo, and the place every social post links to. |
| **Owner** | Teammate (Aman writes content, failure analysis and limitations) |
| **When** | Round 1, days 2–13. Skeleton on mock data from day 2; real data from day 11–12. |
| **Depends on** | Phase 6 export schema (day 2); real export (day 11) |
| **Unblocks** | Demo video, social posts, submission |

---

## 1. Stack

| Concern | Choice |
|---|---|
| Build | Vite + React + TypeScript (strict) |
| Routing | React Router with hash routes, so every state has a shareable URL on static hosting (`#/explore/hydraulic-01423`) |
| Styling | Tailwind CSS, with colour tokens for light and dark mode |
| Time series | uPlot (handles thousands of points smoothly, synced cursors across charts) |
| Summary charts | Recharts (bars, confusion-matrix heat maps) |
| Data | Static JSON from `web/public/data/`; types generated from the JSON Schemas in Phase 6 |
| Live mode | Optional calls to the Phase 6 API, behind a feature check on `/health` |
| Hosting | Vercel or GitHub Pages; free |
| Tests | Vitest + React Testing Library for components; Playwright for a smoke test of each page on desktop and phone sizes |

## 2. Data contract — agree on day 2

- [ ] Teammate and Aman agree the export JSON shape (Phase 6, section 2) on day 2 and freeze it as `schema_version: 1`.
- [ ] `web/public/data-mock/` holds a hand-built mock export in the same shape: 5 cycles, fake results. The site reads mock data until the real export lands; a build flag switches the source.
- [ ] A schema change after day 2 needs both people to agree, a version bump, and an update to the mock.

## 3. Pages

| # | Route | Page | What it shows | Key interactions |
|---|---|---|---|---|
| 1 | `#/` | Home / pitch | One-line problem; 30-second demo GIF; three headline numbers (mean macro-F1, claim accuracy vs GPT-4o, datasets onboarded); "how it works" in four steps | Buttons to Explore, Results, Dataset |
| 2 | `#/explore/:cycleId?` | **Diagnosis explorer** (the hero) | Pick a test cycle; all sensors on synced time axes; diagnosis per component; rationale with every number highlighted | Hover a number → its sensor and time window light up on the chart; tick or cross icon per claim; reveal true label on click; filter cycles by component, label, correct / wrong, faithful / not |
| 3 | `#/whatif/:cycleId?` | What-if lab | A healthy cycle with sliders: reduce flow, raise temperature, add pressure ripple | Diagnosis and rationale update from the precomputed grid, or the live API if it's up |
| 4 | `#/results` | Results | Model vs baselines table; per-component F1 bars; confusion matrices; faithfulness comparison chart; ablations | Toggle backbone; filter by component |
| 5 | `#/failures` | Failure gallery | Cases where Sightglass was wrong or unfaithful, with written analysis | Browse by error type; open in explorer |
| 6 | `#/dataset` | Dataset | The TimeNet connector: sensors, rates, labels, split method, link to the PR, a load snippet | Copy-to-clipboard snippet |
| 7 | `#/method` | Method | Architecture diagram, rationale format and templates, training setup, compute used, faithfulness rules | Expandable details |
| 8 | `#/limitations` | Limitations and roadmap | Single lab rig, virtual-sensor caveat, test-split size; what rounds 2–3 add | Links to future dataset pages |
| 9 | `#/team` | Team and links | Names, GitHub, PR, model card, posts | — |

Later rounds add `#/bearing/...`, `#/wind/...` and `#/cross-machine` (see Phases 8–10).

## 4. The explorer in detail

This is the page that wins or loses the judge, so it gets the most care.

**Layout (desktop):** cycle picker on the left; sensor charts in the middle, grouped by source (pressure, power, flow, temperature, vibration, virtual); diagnosis cards and rationale on the right.
**Layout (phone):** picker becomes a dropdown at the top; diagnosis cards first, then the rationale, then charts stacked full width.

Components:

| Component | Job |
|---|---|
| `CyclePicker` | Searchable list from `index.json`, with badges for correct / wrong and the number of verified claims; "interesting cycles" preset list chosen by Aman |
| `SensorPanel` | One uPlot chart per source group; synced x-axis (seconds) and cursor; healthy-reference band drawn behind each series |
| `DiagnosisCard` | Per component: predicted label, severity colour plus an icon and text (never colour alone), true label hidden until revealed |
| `Rationale` | Renders the rationale text, wrapping each claim span in a `ClaimChip` |
| `ClaimChip` | Shows the stated number, a ✓ / ✗ icon, and on hover or tap: stated vs true value, % difference, verdict status; highlights the sensor series and shades the feature's time window |
| `CompareToggle` | Show the tokenized-LLM baseline's rationale for the same cycle, with its own ticks and crosses |

Behaviour:

- [ ] Hover (desktop) or tap (phone) a `ClaimChip`: the matching sensor chart scrolls into view, the series thickens, the window shades.
- [ ] URL updates on cycle change, so `#/explore/hydraulic-01423` can be shared.
- [ ] Keyboard: arrow keys move between cycles; Tab moves between claims; Enter reveals the true label.
- [ ] Loading a cycle file shows a skeleton, not a blank page.

## 5. Results page

- [ ] Main table generated from `results.json`; Sightglass row highlighted; best value per column in bold; ± seed std shown in small text.
- [ ] Faithfulness chart: grouped bars of claim accuracy, direction accuracy, hallucinated-sensor rate for Sightglass, tokenized LLM and GPT-4o, on the same 200 cycles; error bars from bootstrap CIs.
- [ ] Confusion matrices as heat maps, one per component, with counts in cells.
- [ ] Ablations as a table of deltas against the reference run.
- [ ] Every chart has a one-sentence caption that states what to take from it.

## 6. Design rules

- [ ] The explorer is one click from the home page.
- [ ] Every number on the site is loaded from the exported JSON; nothing is hard-coded. A CI check greps `web/src` for numeric literals inside JSX text and fails on any outside an allow-list.
- [ ] Works on a phone (judges open links from X and LinkedIn), loads in under 3 seconds on a mid-range phone over 4G, light and dark mode.
- [ ] Accessible: verified / unverified uses icons and text, not red and green alone; contrast ≥ 4.5:1; charts have text summaries for screen readers.
- [ ] Open Graph image and description per page, so shared links look good on X and LinkedIn; per-cycle links use a generic image plus the cycle id in the title.
- [ ] Lazy-load cycle files; code-split the results and what-if pages.

## 7. Build order

1. Data loader, types and mock data (day 2).
2. Explorer (days 3–7).
3. Results (days 7–9).
4. Home (day 9).
5. Dataset, method, limitations, team (days 10–11).
6. Failure gallery (day 12, once failures exist).
7. What-if lab (last and optional).
8. Real data switch-over, phone testing and deploy (days 11–13).

## Tests

- [ ] Vitest: `Rationale` highlights every span correctly; `ClaimChip` shows the right status; data loader rejects files with the wrong `schema_version`.
- [ ] Playwright: every route renders on 1280 × 800 and 390 × 844 viewports; the explorer's hover-to-highlight works; no console errors.
- [ ] Lighthouse on home and explorer: performance ≥ 85, accessibility ≥ 95.

## Exit criteria

- [ ] Site deployed at a public URL.
- [ ] Every page populated from real results.
- [ ] Tested on desktop and on at least one real phone.
- [ ] Shareable explorer URLs work when opened fresh.

## Risks in this phase

| Risk | What to do |
|---|---|
| Real data lands late | Mock data in the frozen schema means only the data source switches |
| Charts slow on phones | Display data is already downsampled; render only visible charts; reduce to 5 Hz on small screens |
| Scope creep | What-if lab is optional; cut it before cutting explorer polish |
