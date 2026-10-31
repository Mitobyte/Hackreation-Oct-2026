# Kwik Trip-ify: agent skills for carving helper roles (P4 add-on)

Team: Paul Rinaldi. Project: P4 Employer Opportunity & Support Hub.

What ERI would need: a free ChatGPT account (or any agent that loads skill folders) and the one file `chatgpt-kit/ERI-Helper-Kit.md`; staff attach it to a Temporary Chat with "Improve the model" turned off, paste a public job posting, and review the draft. No install, no paid service, no client data.

## What it does

A job developer pastes a public job posting. The skill splits it into one to three small "helper" roles, the way Kwik Trip carved its Retail Helper role out of Guest Services work:

- a task list with a "done looks like" standard for each task
- executive-function demands of each role (nine dimensions, rated 0-3)
- support intensity of the role (light, moderate, intensive): it describes the role, never a person
- supports the employer agrees to provide
- variations: fewer or more tasks (Core, Standard, Plus) and schedules from 2 days x 2 hours up to the 15-hour Kwik Trip start
- screening flags (no duties, unclear or sub-minimum pay, adult content, contractor work) and questions for the employer

A second skill guides a job developer through a 31-question employer interview and drafts a role card and a 15-point readiness check. A third holds the privacy, ADA, fair-language and pay rules the other two load first.

It never asks for a disability or diagnosis, never scores or ranks candidates, and makes no hiring decision. Every output is a draft for ERI review.

## Live prototype

**https://eri-employer-finder.pages.dev/** (demo password `eri-demo`; all 60 employers are made-up sample data)

- **Employer Finder:** search Wisconsin employers screened for helper roles by company name (starts with), company age, county and city, plus brief status and lightest role. Copy any search as CSV. The live version would load a real list from a free database (Supabase) and link a Word brief per employer. The password screen is for show; real use goes behind Cloudflare Access.
- **ChatGPT to Word** (`/word/`): paste a ChatGPT answer and download a formatted .docx. It runs in the browser; nothing is uploaded. The same tool is `chatgpt-kit/ChatGPT-to-Word.html` for offline use.

A 67-second captioned demo video of the kit in free ChatGPT was shared with ERI separately (this folder keeps text files only).

## Folders

| Folder | What is in it |
| --- | --- |
| `skills/` | The three skills in Agent Skills format (`SKILL.md` + references + Python scripts). `render_roles.py` validates a draft against the rubric and writes Markdown and Word |
| `chatgpt-kit/` | The same skills as one file for free ChatGPT, plus `QUICKSTART.md` for staff |
| `example-briefs/` | Eight runs on real public postings (Best Buy, Walmart, a dental office, Waukesha County, Strattec, Connct, Johnson Health Tech), with an index |
| `employer-finder/` | Source of the live prototype: `index.html` (finder) and `word/` (Markdown-to-Word converter, no libraries) |
| `handoff/` | One-pagers for ERI, the full problem-discovery and Setworks reports, and an offer to rank Wisconsin employers (employers, not people) with an illustrative sample |

## Run it

```bash
cd challenges/p4-employer-hub/kwik-tripify/skills/helperize-job-posting
python3 scripts/fetch_posting.py examples/sample-posting.html -o /tmp/posting.txt
python3 scripts/render_roles.py examples/roles.json -o /tmp/helper_roles   # validates, then writes .md (and .docx if python-docx is installed)
```

The P4 web app in the parent folder is unchanged: `npm start` and `npm test` there work as before.

## Backlog IDs

P4-F1 (employer needs), P4-F3 (job task development), P4-F5 (accommodation and support ideas), P4-F6 (onboarding checklist), P4-US3, P4-US5 (a job developer facilitates employer conversations).

All data is synthetic or public: job postings are public; the one customized brief uses a made-up client ID (C-0001) with no personal details.
