# Customizing for a client profile

Use this only when the request includes a specific person ("this is for C-0042; they can't do X"). Apply the `privacy-guardrails` skill first.

## What to use from the profile

Keep the client to an ERI ID (like `C-0042`). Use only functional facts the job needs:

| Field | Example |
| --- | --- |
| Interests | "likes sorting, organizing, being outdoors" |
| Tasks they want, can do, or do not want | "can face shelves and sort; does not want customer conversations" |
| Days and hours | "2 weekday mornings, up to 3 hours" |
| Transportation | "paratransit; needs pickup by 1:00" |
| Supports that help | "picture checklist; one named person to ask; headphones in the backroom" |
| Benefits note | "on SSI; hours need counselor review" (never amounts or account numbers) |

Leave out names, birthdates, addresses, diagnoses, medications, and record numbers. When the request includes them, drop them and note in `guardrail_notes` that they were removed. When a profile gives a diagnosis instead of needs, ask the job developer which tasks and supports it means for work.

## How to customize

1. Pick the role and variation whose tasks best match the person's interests and what they can and want to do.
2. Remove tasks the person cannot or does not want to do. List them in `not_doing_task_ids`.
3. Choose a schedule from the ladder in `variations.md` that fits their days, hours, and transport.
4. Add the supports from their profile that match the role's demands.
5. Write an employer-facing summary. It describes the tasks, schedule, and supports only. A disability or diagnosis reaches the employer only with the client's written consent.
6. Set `counselor_check: true`. The hours go to an ERI benefits counselor before they are offered.

Done when: every task in the customized version is one the person can do, the schedule fits their days and transport, and the employer-facing summary has no personal details.
