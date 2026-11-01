# Challenge P4: Employer Opportunity & Support Hub

What ERI would need: a free ChatGPT account (or any agent that loads skill folders) and one file, `kwik-tripify/chatgpt-kit/ERI-Helper-Kit.md`; staff paste a public job posting and get draft helper roles to review. No install, no paid service, no client data. See [kwik-tripify/](kwik-tripify/README.md).

**PRD:** [wiki/prds/p4-employer-hub.md](../../wiki/prds/p4-employer-hub.md) ·
**ERI's own words:** [docs/eri-problem-statements.md](../../docs/eri-problem-statements.md#project-4-employer-opportunity--support-hub) ·
**Acceptance:** [spec/acceptance.md](spec/acceptance.md) (39 rows)

An employer picks their industry, types three to five jobs that keep coming up,
and opens a profile a candidate chose to share. The hub shows where the two line
up and, for every suggestion, names the line of the employer's own sentence and
the skill from the candidate's own profile that produced it. It ends with a draft
set of responsibilities, next steps, and questions for an employment specialist.

**It does not score, rank, or decide anything, and it has no field anywhere for
a disability or a diagnosis.** ERI wrote seven ethical requirements in §10; they
are the deliverable here, not the disclaimer. Three of them are enforced by
guards that run in the browser on every render and fail closed - a suggestion
that cannot cite both sides is dropped and the drop is shown.

Plain HTML, CSS and vanilla ES modules. No npm packages, no build step, no
framework, no network calls, no storage, no timers.

```bash
cd challenges/p4-employer-hub
npm test                     # node:test, nothing to install
npm run bdd                  # the tagged scenarios in features/
npm run test:a11y            # the accessibility and page-wiring checks
npm run ci                   # all three, same as tools/run_project_suite.sh
npm start                    # http://localhost:8000/web/
```

`bash tools/run_project_suite.sh challenges/p4-employer-hub` from the repo root
is green with no warnings: it reads the `ci` script's composition and wants a
unit, a bdd and an accessibility stage.

**`bdd` is not Cucumber and `test:a11y` is not Playwright.** This challenge is
specified as zero-dependency, so `features/employer_hub.feature` runs under a
sixty-line Gherkin-subset runner in `test/features.test.js` - an unmatched step
throws rather than skipping, and the runner asserts it executed every step of
every scenario, because a partial run must not read as a pass. `test:a11y` is
the source and page-wiring checks. Neither drives a real browser, and the
`human` rows in [spec/acceptance.md](spec/acceptance.md) say plainly what that
leaves uncovered. Retiring those rows with Playwright and axe is on the job list below.

First 10 minutes: run `npm test`, open `http://localhost:8000/web/` and press
**Fill in the retail example**, then read `web/match.js` - it is the whole
product, and `suggestMatches()` at the bottom is the part worth arguing with.

## Spec → tests (traceability)

Full row-by-row table in [spec/acceptance.md](spec/acceptance.md).
`test/conformance.test.js` parses that file and fails if it claims coverage the
suite does not have.

| ERI section | IDs | Where it is proved |
| --- | --- | --- |
| §4 core features | P4-F1 to P4-F7 | `test/match.test.js`, `test/plan.test.js`, `test/conformance.test.js` |
| §6 MVP steps | P4-M1 to P4-M6 | `test/match.test.js`, `test/plan.test.js`, `test/ui-smoke.test.js` |
| §8 accessibility | P4-A1 to P4-A7 | `test/source-rules.test.js` (A1, A2, A3 are human-judged) |
| §9 success criteria | P4-S1 to P4-S6 | `test/conformance.test.js`, `test/match.test.js`, `test/plan.test.js` |
| §10 privacy and ethics | P4-V1 to P4-V7 | `test/guards.test.js` (positive control + clean run for each) |
| §11 out of scope | P4-X1 to P4-X6 | `test/guards.test.js`, `test/source-rules.test.js`, `test/conformance.test.js` |

Scenario-level coverage lives in `features/employer_hub.feature`, tagged with
the same IDs; `test/features.test.js` fails if a tag is not a real row in the
spec.

| Disposition | Rows |
| --- | --- |
| `mvp` built and tested | 23 |
| `forbidden` and guarded | 10 |
| `stretch` not built | 3 (F4 disclosure, F5 accommodation, F6 onboarding) |
| `human` judged by a person | 3 (A1 screen reader, A2 plain language, A3 layout) |

## How the two hard rules were made testable

**No ranking.** `findRankingViolations()` in `web/guards.js` deep-walks the
output and reports any key that reads as a score, any numeric value outside a
declared allow-list of positional and count fields, and any string that reads
as a grade (`72%`, `8/10`, `4 out of 5`). Order is a second axis:
`isEmployerOrdered()` asserts suggestions come out in the employer's own need
order, and a test shuffles the candidate's skill list to prove the order does
not depend on anything about the person. `suggestMatches()` takes exactly one
candidate and throws on an array, so there is no entry point that could compare
two people.

**Traceable reasoning.** Every suggestion carries two citations: a verbatim span
of the employer's typed sentence, and the skill id the candidate shared. The
explanation is a fixed template over those two quotes, and `isTraceable()`
rejects any suggestion whose explanation does not literally contain both. That
is what makes ERI's §9 criterion - *"reflect actual employer needs, not
assumptions about disability"* - falsifiable rather than a claim: free-text
reasoning cannot be checked, two quotes can.

Both guards are tested with a **positive control first**: a planted score, a
planted rank, a tampered citation, a planted disclosure field. A guard only
ever shown passing has not been shown to work.

## The design call you should know about before you demo

**ERI's §6 step 3 asks for the employer to type the candidate's skills. This
build does not default to that.** An employer narrating a disabled person's
abilities is the framing their own §10 guards against, so the default loads a
profile from `fixtures/candidates.js` as if the person sent it - their own
words, their own chosen skills, a recorded permission to share. Manual entry is
one radio button away and is stamped as the employer's account rather than the
person's.

ERI's §12 names this handoff ("could connect directly with the Show Your Skills
portfolio"), so the skill vocabulary uses plain ids a sibling project could emit
(`organizing`, `counting-stock`, `routine-work`) with no translation layer.

Reasoning is recorded against **P4-M3** in [spec/acceptance.md](spec/acceptance.md).
If ERI wants their literal step 3, it is a one-line change in `web/index.html`.

## Your job (pick one; finish it with a test, then pick the next)

- [ ] **Onboarding planner (ERI §4, P4-F6).** A printable checklist for
      training, communication and workplace supports, built from the tasks the
      employer kept - not from anything about the person. The safest of the
      three optional features; start here.
- [ ] **Accommodation explorer (ERI §4, P4-F5).** ⚠️ See the warning below.
      Index JAN's own pages by **task**, never by person, and link out. No
      generated text.
- [ ] **Disclosure guidance (ERI §4, P4-F4).** ⚠️ See the warning below. Quote
      EEOC material verbatim with a citation and a link. No paraphrase.
- [ ] A print stylesheet so the plan can go into a meeting on paper.
- [ ] Load a profile from a JSON file a P1 team exports, to demo ERI's §12
      handoff live. The vocabulary ids already line up.
- [ ] More industries and recurring tasks in `fixtures/industries.js`, from
      real conversations ERI Business Services has had.
- [ ] Widen the skill vocabulary, and add a test that every keyword stem is
      whole-word safe (see the "counter" / "count" case in
      `test/match.test.js`).
- [ ] Browser-level accessibility testing with Playwright and axe, to retire the
      `human` rows.

### ⚠️ The warning on F4 and F5

**Disclosure guidance and the accommodation explorer are the two features that
can do real legal harm.** A hackathon prototype that invents an answer to "what
do I say when someone discloses?" or "what accommodation should I give?" is
giving employment-law advice with nobody qualified behind it, and ERI's §10
bullet 7 says to refer those questions out.

If you build either one: **quote or link JAN and EEOC material and nothing
else.** Never generate it, never paraphrase it into advice, always show the
publisher and a link. `test/guards.test.js` has an advice-prose guard
(`findAdviceProse`) that catches "you must", "it is illegal", "the law
requires" - keep it green. `test/conformance.test.js` currently asserts both
features are absent; when you build one, change that test deliberately rather
than deleting it.

And ERI's §10 bullet 6 is absolute: **never suggest an accommodation from a
disability label.** In this build that is unreachable, because there is no
disability label in the data model to key one off. Do not add one.

## Guardrails

- Synthetic data only. Every person in `fixtures/candidates.js` is invented.
- Guidance, not legal advice. Legal and accommodation questions go to JAN
  (1-800-526-7234, free), the EEOC, Wisconsin DVR, or the employer's counsel.
- No disability or diagnosis field, anywhere. Not hidden, not optional: absent.
- No scores, no ranking, no ordering by goodness, no comparing two people.
- No automated hiring or accommodation decisions. The tool suggests, drafts and
  hands over; people decide.
- Nothing is stored and nothing is sent. No account, no server, no cookie.
- No time limits: there is no `setTimeout` anywhere in the build, so there is
  no clock to impose one.
- The employer is the authority on their own business. The candidate is the
  authority on their own abilities. The tool is the authority on nothing.

## Layout

| Path | What |
| --- | --- |
| `web/index.html` | the page: three steps, results, plan, resources |
| `web/match.js` | the product - needs to skills, with citations |
| `web/plan.js` | the employer action plan and specialist questions |
| `web/guards.js` | ERI's §10 as assertions; no imports, runs in both browser and node |
| `web/app.js` | DOM wiring only; runs the guards fail-closed before rendering |
| `web/style.css` | one stylesheet, dark mode, 44px targets, no fixed widths |
| `fixtures/vocabulary.js` | skills, interests and preferences - the shared ids |
| `fixtures/industries.js` | 8 industries, 49 recurring tasks |
| `fixtures/candidates.js` | 5 fictional profiles with recorded consent, plus ERI's §7 demo |
| `fixtures/resources.js` | JAN, EEOC, DVR - links and phone numbers only |
| `fixtures/art.js` | inline SVG, with `<title>` and `<desc>`. No binary files |
| `spec/acceptance.md` | 39 rows, one per requirement ERI wrote |
| `features/employer_hub.feature` | 10 scenarios, each tagged with its acceptance IDs |
| `test/features.test.js` | the Gherkin-subset runner; an unmatched step fails |
| `test/dom-stub.js` | a small DOM so `web/app.js` can be executed under node |
