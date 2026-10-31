# ERI helper-role skills

Three agent skills that help ERI staff create Kwik Trip-style helper roles with employers. They are written in the Agent Skills format (a folder per skill with a `SKILL.md`), so any agent that loads that format can use them, including one running a local Qwen model.

| Skill | What it does | Who uses it |
| --- | --- | --- |
| `employer-role-interview/` | Walks a job developer through an employer interview (31 questions in 9 blocks), then drafts a role card and a 15-item readiness check | ERI job developer, with an employer |
| `helperize-job-posting/` | Turns a job posting (URL, saved page, or text) into one to three carved helper roles, with tasks, executive-function demands, support intensity, and supports. Every role comes in variations: fewer or more tasks (Core, Standard, Plus) and schedules from 2 days x 2 hours up to the 15-hour standard. Given a de-identified client profile, it adds a version built for that person plus an employer-facing summary; without one, the brief opens by offering to customize. Outputs Markdown and Word | ERI staff, before or after meeting an employer |
| `privacy-guardrails/` | HIPAA, ADA, fair-language, and pay rules the other two skills load first | Loaded automatically by the other skills |

## Try it

```bash
cd helperize-job-posting
python3 scripts/fetch_posting.py examples/sample-posting.html -o posting.txt
# The agent follows SKILL.md steps 2-5 and writes roles.json, then:
python3 scripts/render_roles.py examples/roles.json -o helper_roles   # -> helper_roles.md and .docx
```

`examples/` holds a fictional grocery posting and the finished output. Scripts use the Python standard library; `python-docx` is optional and adds the Word file.

## Running with a local model

- Install a local model runner (for example Ollama) and a Qwen model that supports tool calling.
- Use an agent harness that loads Agent Skills folders and can run shell commands. Check your harness's docs for where skill folders go.
- Keep the model and the files on an ERI machine. Client data is not needed for helperize or the employer interview. Matching people to roles comes later and needs de-identified data (see `privacy-guardrails`).

## Customizing for a person

Add a de-identified profile to the request, for example: "Helperize this posting for C-0042: likes sorting, prefers little customer talk, no freezer work, Tue/Thu mornings up to 3 hours, paratransit." See `helperize-job-posting/references/client-profile.md`. Use an ERI client ID, never a name; the script rejects names, diagnosis wording, and a missing benefits-counselor check.

## Design choices

- **Roles, not people.** Fit is described as the role's support intensity (light, moderate, intensive) and its executive-function demands. The skills never label a role by diagnosis or guess where anyone sits on the autism spectrum. Doing so would be a stereotype, and it risks disability-based screening ([JAN](https://AskJAN.org/disabilities/Autism-Spectrum.cfm), [ASAN](https://autisticadvocacy.org/?p=8064)).
- **The validator enforces the rubric.** `render_roles.py` refuses output where a role's demand profile, support intensity, or task choices break the rules in `ef-demand-rubric.md`.
- **Humans decide.** Every output is labeled a draft for ERI review. Hours and pay changes go to a benefits counselor.

## Before real use

Have counsel confirm the items marked **counsel** in `privacy-guardrails/SKILL.md`: ERI's HIPAA status, 42 CFR Part 2, and Wisconsin record law. Sources for the Kwik Trip pattern are in `employer-role-interview/references/kwik-trip-pattern.md`.
