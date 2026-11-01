#!/usr/bin/env python3
"""Render helperize JSON (see ../references/output-schema.md) into a Markdown brief
and, if python-docx is installed, a Word file staff can edit.

Usage:
  python3 render_roles.py roles.json [-o out_basename]
Writes out_basename.md (always) and out_basename.docx (when python-docx is available).
Also validates the JSON and exits non-zero with the problems it finds, so the agent
can fix them before a human sees the brief.
"""
import argparse, json, re, sys

LEVEL = {0: "none", 1: "low", 2: "medium", 3: "high"}
REQUIRED_ROLE = ["title", "summary", "task_ids", "hours_per_week", "schedule", "pay_note", "ef_profile",
                 "support_intensity", "supports", "frees_up", "why_this_bundle", "growth_path", "variations"]
# Words that describe people instead of tasks (privacy-guardrails: "Describing who a role suits").
PERSON_LABELS = re.compile(r"\b(autis\w*|asperger\w*|high[- ]functioning|low[- ]functioning|level [123]\b|"
                           r"diagnos\w*|disorder|disabled (worker|person|people)|special needs|retard\w*|"
                           r"for (people|workers|someone) with)\b", re.I)
STATUSES = {"ready", "needs_info", "on_hold"}
FLAG_TYPES = {"no_duties", "pay_below_minimum_or_unclear", "unpaid_or_commission_only", "contractor_not_employee",
              "eligibility_restriction", "adult_content", "remote_only", "temporary", "other"}
BLOCKING = {"no_duties", "pay_below_minimum_or_unclear", "unpaid_or_commission_only", "contractor_not_employee", "adult_content"}
STATUS_TEXT = {"needs_info": "Needs more information before roles can be carved.",
               "on_hold": "On hold: the roles below are drafts. Do not take them to the employer until the flags are resolved."}
CLIENT_ID = re.compile(r"^[A-Z]{1,4}-\d{2,6}$")
OFFER_TEXT = ("These roles can be customized for a specific person. Share a de-identified client profile "
              "(client ID, interests, tasks they want or do not want to do, days and hours they can work, "
              "transportation, and supports that help) and the brief will add a version built around them.")


def profile_of(tasks):
    prof = {}
    for t in tasks:
        for dim, v in (t.get("ef") or {}).items():
            prof[dim] = max(prof.get(dim, 0), v)
    return prof


def intensity(prof):
    twos = sum(1 for v in prof.values() if v == 2)
    return "intensive" if any(v == 3 for v in prof.values()) or twos >= 5 else "moderate" if twos >= 2 else "light"


def check_task_set(where, ids, tmap, errs):
    out = []
    for tid in ids:
        t = tmap.get(tid)
        if not t:
            errs.append(f"{where}: unknown task id {tid}")
            continue
        if t.get("keep_with_staff"):
            errs.append(f"{where}: task {tid} is keep-with-staff")
        for dim, v in (t.get("ef") or {}).items():
            if v == 3:
                errs.append(f"{where}: task {tid} rated 3 on {dim}; move it to the growth path")
        out.append(t)
    return out


def weekly(s):
    return s.get("days_per_week", 0) * s.get("hours_per_day", 0)


def validate(d):
    errs = []
    tmap = {t.get("id"): t for t in d.get("tasks", [])}
    status = d.get("status", "ready")
    flags = d.get("posting_flags") or []
    if status not in STATUSES:
        errs.append("status must be ready, needs_info, or on_hold")
    for f in flags:
        if f.get("type") not in FLAG_TYPES or not f.get("detail"):
            errs.append(f"posting_flags: each flag needs a type from {sorted(FLAG_TYPES)} and a detail")
    if status == "ready" and any(f.get("type") in BLOCKING for f in flags):
        errs.append("a blocking flag (" + ", ".join(sorted(BLOCKING)) + ") needs status needs_info or on_hold")
    if status != "ready" and not flags:
        errs.append(f"status {status} needs at least one posting flag explaining why")
    if status != "ready" and not d.get("questions_for_employer"):
        errs.append(f"status {status} needs questions_for_employer that would resolve it")
    if not d.get("roles") and status != "needs_info":
        errs.append("no roles (use status needs_info when the posting cannot be carved yet)")
    for i, r in enumerate(d.get("roles", [])):
        where = f"role {i+1}"
        for k in REQUIRED_ROLE:
            if k not in r or r[k] in ("", [], None):
                errs.append(f"{where}: missing {k}")
        if r.get("support_intensity") not in ("light", "moderate", "intensive"):
            errs.append(f"{where}: support_intensity must be light, moderate or intensive")
        h = r.get("hours_per_week", {})
        if isinstance(h, dict) and h.get("min", 0) > h.get("max", 0):
            errs.append(f"{where}: hours min > max")
        # Rubric rules (ef-demand-rubric.md): profile = max over tasks; intensity from profile.
        rtasks = check_task_set(where, r.get("task_ids", []), tmap, errs)
        prof = profile_of(rtasks)
        for dim, v in prof.items():
            if r.get("ef_profile", {}).get(dim) != v:
                errs.append(f"{where}: ef_profile.{dim} should be {v} (highest among its tasks)")
        if rtasks and r.get("support_intensity") != intensity(prof):
            errs.append(f"{where}: support_intensity should be {intensity(prof)} by the rubric rule")
        if len(r.get("supports", [])) < 3:
            errs.append(f"{where}: list at least 3 supports")
        # Variations (variations.md): at least 2; one with fewer tasks (unless the role has one task); a starter schedule of 6 hours or less.
        vs = r.get("variations") or []
        if len(vs) < 2:
            errs.append(f"{where}: give at least 2 variations")
        if vs and len(r.get("task_ids", [])) > 1 and not any(len(v.get("task_ids", [])) < len(r.get("task_ids", [])) for v in vs):
            errs.append(f"{where}: one variation must use fewer tasks than the full role")
        scheds = [s for v in vs for s in v.get("schedules", [])]
        if vs and not any(weekly(s) <= 6 for s in scheds):
            errs.append(f"{where}: include a starter schedule of 6 hours a week or less (e.g. 2 days x 2 hours)")
        for j, v in enumerate(vs):
            vw = f"{where} variation {j+1}"
            for k in ("name", "task_ids", "schedules", "best_when"):
                if not v.get(k):
                    errs.append(f"{vw}: missing {k}")
            check_task_set(vw, v.get("task_ids", []), tmap, errs)
            for s in v.get("schedules", []):
                if not (1 <= s.get("days_per_week", 0) <= 6 and 0 < s.get("hours_per_day", 0) <= 8):
                    errs.append(f"{vw}: schedule needs days_per_week 1-6 and hours_per_day up to 8")
    c = d.get("customization")
    if c:
        if not CLIENT_ID.match(str(c.get("client_id", ""))):
            errs.append('customization.client_id must be an ERI ID like "C-0001", never a name')
        for k in ("profile_summary", "role", "task_ids", "schedule", "supports", "employer_facing_summary"):
            if not c.get(k):
                errs.append(f"customization: missing {k}")
        check_task_set("customization", c.get("task_ids", []), tmap, errs)
        for tid in c.get("not_doing_task_ids", []):
            if tid in c.get("task_ids", []):
                errs.append(f"customization: {tid} is in both task_ids and not_doing_task_ids")
        if c.get("counselor_check") is not True:
            errs.append("customization.counselor_check must be true: the hours go to a benefits counselor")
        if weekly(c.get("schedule", {})) <= 0:
            errs.append("customization.schedule needs days_per_week and hours_per_day")
    if not d.get("guardrail_notes"):
        errs.append("guardrail_notes is empty; note at least what data was used")
    text = json.dumps({k: d.get(k) for k in ("roles", "questions_for_employer", "customization")})
    for m in sorted(set(x.group(0) for x in PERSON_LABELS.finditer(text))):
        errs.append(f'wording "{m}" describes people; describe task demands and supports instead')
    for t in d.get("tasks", []):
        for dim, v in (t.get("ef") or {}).items():
            if v not in LEVEL:
                errs.append(f"task {t.get('id')}: ef.{dim} must be 0-3")
    return errs


def sched_text(s):
    w = weekly(s)
    days = f" ({s['days']})" if s.get("days") else ""
    return f"{s['days_per_week']} days x {s['hours_per_day']:g} h = {w:g} h/week{days}"


def to_markdown(d):
    src = d.get("source", {})
    task = {t["id"]: t for t in d.get("tasks", [])}
    names = lambda ids: "; ".join(task[i]["task"] for i in ids)
    emp = f" at {src['employer']}" if src.get("employer") else ""
    out = [f"# Helper roles from: {src.get('title', '(posting)')}{emp}", ""]
    if src.get("url"):
        out.append(f"Source posting: {src['url']}")
    out.append(f"Original pay/hours: {src.get('pay','not stated')} / {src.get('hours','not stated')}")
    out.append("")
    out.append("> Draft for a job developer and the employer to review. It describes tasks and supports, "
               "not people. It is not a hiring decision.")
    out.append("")
    status = d.get("status", "ready")
    if status != "ready":
        out += [f"> **Status: {status.replace('_', ' ')}.** {STATUS_TEXT[status]}", ""]
    if d.get("posting_flags"):
        out += ["## Screening flags", "", "| Flag | Detail |", "| --- | --- |"]
        out += [f"| {f['type'].replace('_', ' ')} | {f['detail']} |" for f in d["posting_flags"]]
        out.append("")
    c = d.get("customization")
    if not c and d.get("roles"):
        out += [f"> **Customize for a person:** {OFFER_TEXT}", ""]
    elif c:
        s = c["schedule"]
        out += [f"## Customized version for client {c['client_id']} (ERI internal)", "",
                f"Built from role: **{c['role']}**.", "",
                "**Profile used (functional, de-identified):**", ""]
        out += [f"- {p}" for p in c["profile_summary"]]
        out += ["", f"- **Schedule:** {sched_text(s)}" + (f"; {s['times']}" if s.get("times") else ""),
                f"- **Tasks:** {names(c['task_ids'])}"]
        if c.get("not_doing_task_ids"):
            out.append(f"- **Left out for this person:** {names(c['not_doing_task_ids'])}")
        if c.get("interests_matched"):
            out.append(f"- **Interests this uses:** {'; '.join(c['interests_matched'])}")
        out += ["- **Supports:**"] + [f"    - {x}" for x in c["supports"]]
        out += ["- **Before sharing:** an ERI benefits counselor reviews these hours and pay. "
                "Share only the employer-facing text below; disability details need the client's written consent.", "",
                "**Employer-facing version (no personal details):**", "", c["employer_facing_summary"], ""]
    for n, r in enumerate(d.get("roles", []), 1):
        h = r["hours_per_week"]
        out += [f"## Role {n}: {r['title']}", "", r["summary"], "",
                f"- **Hours:** {h.get('min')}-{h.get('max')} per week; {r['schedule']}",
                f"- **Pay:** {r['pay_note']}",
                f"- **Support intensity (of the role):** {r['support_intensity']}",
                f"- **Frees up:** {r['frees_up']}",
                f"- **Growth path:** {r['growth_path']}", "",
                "| Task | Standard (what done looks like) | Frequency |", "| --- | --- | --- |"]
        for tid in r["task_ids"]:
            t = task[tid]
            out.append(f"| {t['task']} | {t.get('standard','')} | {t.get('frequency','')} |")
        out += ["", "**Executive-function demands (role level)**", "",
                "| Dimension | Demand |", "| --- | --- |"]
        for dim, v in r["ef_profile"].items():
            out.append(f"| {dim.replace('_',' ')} | {LEVEL.get(v, v)} |")
        out += ["", "**Supports the employer agrees to provide**", ""]
        out += [f"- {s}" for s in r["supports"]]
        out += ["", f"_Why these tasks belong together:_ {r['why_this_bundle']}", "",
                "**Variations of this role (tasks and schedules can be mixed)**", ""]
        base = None
        for v in r["variations"]:
            vi = intensity(profile_of([task[i] for i in v["task_ids"]]))
            sch = " or ".join(f"{s['hours_per_day']:g} h/day x {s['days_per_week']} days = {weekly(s):g} h/week total"
                              + (f" ({s['days']})" if s.get("days") else "") for s in v["schedules"])
            ids = v["task_ids"]
            if base and set(base["task_ids"]) < set(ids):
                added = [i for i in ids if i not in base["task_ids"]]
                head = f"**{v['name']}** = {base['name']} + {names(added)}"
            else:
                head = f"**{v['name']}:** {names(ids)}"
            base = v
            extra = f" Extra supports: {'; '.join(v['extra_supports'])}." if v.get("extra_supports") else ""
            out.append(f"- {head} — {sch}. Support intensity: {vi}. Good fit: {v['best_when'].rstrip('.')}.{extra}")
        out += ["", "_Schedules above 15 hours a week, and any schedule a specific client takes, go to an ERI benefits counselor first._", ""]
    if d.get("questions_for_employer"):
        out += ["## Questions to confirm with the employer", ""]
        out += [f"- [ ] {q}" for q in d["questions_for_employer"]]
        out.append("")
    if d.get("guardrail_notes"):
        out += ["## Guardrail notes", ""] + [f"- {g}" for g in d["guardrail_notes"]]
    return "\n".join(out).rstrip() + "\n"


def to_docx(md_text, path):
    try:
        import docx  # python-docx
    except ImportError:
        return False
    doc = docx.Document()
    table = None
    for line in md_text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if set("".join(cells)) <= set("- "):
                continue
            if table is None:
                table = doc.add_table(rows=0, cols=len(cells))
                table.style = "Table Grid"
            row = table.add_row().cells
            for c, txt in zip(row, cells):
                c.text = txt.replace("**", "")
            continue
        table = None
        if line.startswith("# "):
            doc.add_heading(line[2:], 0)
        elif line.startswith("## "):
            doc.add_heading(line[3:], 1)
        elif line.startswith("- [ ] "):
            doc.add_paragraph("☐ " + line[6:])
        elif line.startswith("    - "):
            doc.add_paragraph(line[6:].replace("**", ""), style="List Bullet 2")
        elif line.startswith("- "):
            doc.add_paragraph(line[2:].replace("**", ""), style="List Bullet")
        elif line.strip():
            doc.add_paragraph(line.lstrip("> ").replace("**", "").replace("_", ""))
    doc.save(path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_file")
    ap.add_argument("-o", "--out", default="helper_roles")
    a = ap.parse_args()
    d = json.load(open(a.json_file, encoding="utf-8"))
    errs = validate(d)
    if errs:
        sys.exit("Fix these before rendering:\n- " + "\n- ".join(errs))
    md = to_markdown(d)
    open(a.out + ".md", "w", encoding="utf-8").write(md)
    made = to_docx(md, a.out + ".docx")
    print(f"wrote {a.out}.md" + (f" and {a.out}.docx" if made else " (install python-docx for .docx)"))


if __name__ == "__main__":
    main()
