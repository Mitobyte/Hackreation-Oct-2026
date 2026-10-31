---
name: helperize-job-posting
description: Turns a job posting (URL, saved page, or pasted text) into one to three Kwik Trip-style helper roles, each with task and schedule variations, executive-function demands, and supports; customizes a role for a specific client when a profile is given. Use when someone says helperize, carve a role, or shares a job ad to adapt.
---

You **helperize** a job posting: carve one to three helper roles out of it, the way Kwik Trip carved its Retail Helper out of Guest Services. You describe tasks and supports, never people. Run commands from this skill's folder.

Check the request for a client profile (a client ID with interests, tasks they can or cannot do, hours, or supports). With one, run step 6 too. Without one, skip step 6; the rendered brief then opens by offering to customize for a person.

## Steps

0. **Load guardrails.** Load the `privacy-guardrails` skill now. It applies to every later step.
   Done when: it is loaded.

1. **Get the text.** Run `python3 scripts/fetch_posting.py <url-or-file> -o posting.txt`. If the site blocks it, ask the person to save the page or paste the text into a `.txt` file and pass that. Fields the posting lacks (pay, hours) become questions for the employer in step 5.
   Done when: `posting.txt` holds the posting's duty list.

1b. **Screen the posting.** Check it against [`screening.md`](references/screening.md) and record each problem in `posting_flags`. A blocking flag sets `status` to `needs_info` (cannot carve yet) or `on_hold` (draft roles, but resolve the flag before the employer sees them). Fewer than three duty lines means `needs_info`: write questions instead of inventing tasks.
   Done when: every screening check is done and `status` is set.

2. **Inventory tasks.** Turn every duty line into concrete verb-object tasks ("restock coffee station," not "maintain store"). Split a line wherever it names two actions ("sweep and mop" becomes two tasks). An "at all times" duty (for example, "follow food safety rules") becomes a task with a checklist standard. Mark a task the posting only implies with `"inferred": true`.
   For each task, record its frequency and a "done looks like" standard. Set `keep_with_staff: true` for:
   - work that needs a license or certification (clinical care, driving, food-handler-only tasks until certified);
   - cash or payments;
   - keys, opening, or closing;
   - running powered machines such as balers or slicers;
   - accepting or rejecting deliveries;
   - handling complaints;
   - any decision with legal or safety consequences.

   Split a task when only part of it is a decision. For example, "count the delivery" is a helper task, but "accept the delivery" stays with staff.
   Done when: every duty line maps to at least one task.

3. **Rate demands.** Rate every task 0-3 on every dimension in [`ef-demand-rubric.md`](references/ef-demand-rubric.md), using its anchors.
   Done when: every task has all nine ratings.

4. **Carve roles.** Bundle tasks into one to three helper roles. Each bundle is:
   - repeatable, with visible standards;
   - in one area of the site at one time of day;
   - work that frees busy staff;
   - free of keep-with-staff tasks and of any task rated 3.

   Tasks rated 3 go on a growth path. One task may appear in more than one role. Start every role at 10-15 hours a week in daytime, fitted to transit (the Kwik Trip start), even when the posting asks for more. The posting's hours and days become a question for the employer.
   Rate honestly. A role is light only if the rubric says so. If no role is light, add a guardrail note naming the task that, if moved out, would make one light.
   Done when: each role says which staff it frees up and why its tasks belong together.

5. **Profile and support.** For each role:
   - Set each EF dimension to the highest rating among its tasks.
   - Set support intensity by the rubric rule.
   - List at least three supports from the rubric that match its 2-rated dimensions.
   - Name the growth path: the tasks held back, in order.

   Turn every assumption into a question for the employer. This covers hours, pay, inferred tasks, standards, and posting requirements such as "lift 40 lbs" or "works under pressure"; ask whether each requirement is essential for the helper role.
   Done when: no role has an unstated assumption.

5b. **Variations.** Give each role at least two variations from [`variations.md`](references/variations.md): a Core version with fewer tasks (a one-task role can skip this), the Standard version, and a Plus version when an eligible growth task exists. Attach schedules from the ladder, including at least one at 6 hours a week or less (for example, 2 days x 2 hours) and the 15-hour standard.
   Done when: every role has its variations, each with a "best when" line written in task terms.

6. **Customize (only with a client profile).** Follow [`client-profile.md`](references/client-profile.md) and fill `customization` in the JSON.
   Done when: every customized task is one the person can do, the schedule fits their days and transport, and the employer-facing summary has no personal details.

7. **Write and render.** Write the JSON described in [`output-schema.md`](references/output-schema.md). Then run `python3 scripts/render_roles.py roles.json -o helper_roles`. The script checks the schema, the rubric rules, the variations, the customization, and wording that labels people. Fix every error and rerun.
   Done when: the script writes `helper_roles.md` with no errors.

The output is a draft for an ERI job developer, who takes it to the employer using the `employer-role-interview` skill.
