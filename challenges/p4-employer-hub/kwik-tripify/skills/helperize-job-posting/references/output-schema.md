# Output schema (roles.json)

`scripts/render_roles.py` validates this shape. Ratings use the keys in `ef-demand-rubric.md`.

```json
{
  "status": "ready | needs_info | on_hold",
  "posting_flags": [{"type": "remote_only", "detail": "Fully remote; supports must work by video."}],
  "source": {"title": "", "employer": "", "url": "URL, or the file name for a saved or pasted posting", "location": "", "pay": "as posted, or \"not stated\"", "hours": "as posted, or \"not stated\""},
  "tasks": [
    {
      "id": "t1",
      "task": "Restock the coffee station",
      "from_posting": "quote of the duty line it came from",
      "inferred": false,
      "frequency": "every 2 hours",
      "standard": "cups, lids, and creamer full; counter wiped",
      "keep_with_staff": false,
      "ef": {"working_memory": 1, "sequencing": 1, "time_management": 2, "attention": 1,
             "organization": 1, "flexibility": 1, "social_communication": 1,
             "sensory_load": 1, "paperwork": 0}
    }
  ],
  "roles": [
    {
      "title": "Store Helper (mornings)",
      "summary": "Two or three sentences on what the role does and why it helps the business.",
      "task_ids": ["t1", "t3"],
      "hours_per_week": {"min": 10, "max": 15},
      "schedule": "weekday mornings, 8:30-11:30, fits bus route times",
      "pay_note": "same starting rate as other associates; at least minimum wage",
      "ef_profile": {"working_memory": 1, "sequencing": 1, "time_management": 2, "attention": 1,
                     "organization": 1, "flexibility": 1, "social_communication": 1,
                     "sensory_load": 1, "paperwork": 0},
      "support_intensity": "light | moderate | intensive",
      "supports": ["picture checklist at the coffee station", "phone timer for the every-2-hours round", "one named coworker for questions"],
      "frees_up": "cashiers during the morning rush",
      "why_this_bundle": "same area, same time of day, clear visual standards",
      "growth_path": "add register backup after 90 days, then stocking deliveries",
      "variations": [
        {"name": "Core", "task_ids": ["t1"],
         "schedules": [{"days_per_week": 2, "hours_per_day": 2, "days": "Tue, Thu mornings"}],
         "best_when": "prefers one task at a time and a short shift",
         "extra_supports": ["coach on site for every shift in week one"]},
        {"name": "Standard", "task_ids": ["t1", "t3"],
         "schedules": [{"days_per_week": 3, "hours_per_day": 3}, {"days_per_week": 3, "hours_per_day": 5}],
         "best_when": "ready for two tasks in a set routine"}
      ]
    }
  ],
  "customization": null,
  "questions_for_employer": ["Confirm the starting wage for associates."],
  "guardrail_notes": ["No client information used.", "Hours or pay changes go to an ERI benefits counselor."]
}
```

`customization` stays `null` unless the request includes a client profile (see `client-profile.md`). Filled, it looks like:

```json
"customization": {
  "client_id": "C-0042",
  "profile_summary": ["likes sorting and organizing", "prefers little customer conversation", "2 weekday mornings, up to 3 hours; paratransit"],
  "role": "Backroom Sort Helper",
  "task_ids": ["t2", "t6"],
  "not_doing_task_ids": ["t10"],
  "schedule": {"days_per_week": 2, "hours_per_day": 3, "days": "Tue, Thu", "times": "9:00-12:00"},
  "supports": ["department color codes", "one named person to ask"],
  "interests_matched": ["sorting", "organizing"],
  "employer_facing_summary": "A Backroom Sort Helper for two weekday mornings, 9:00-12:00, sorting boxes onto department carts and breaking down empties, with color-coded carts and one named coworker to ask.",
  "counselor_check": true
}
```

`render_roles.py` enforces all of these:

- Every role field shown above is present, and every `task_id` exists. A task may appear in more than one role.
- Ratings are 0-3, and every `ef_profile` value equals the highest rating among the role's tasks.
- `support_intensity` matches the rubric rule.
- No role holds a `keep_with_staff` task or a task rated 3.
- Each role lists at least 3 supports, and `hours_per_week.min` is at most `max`.
- Each role has at least 2 variations, one with fewer tasks than the full role, and at least one schedule of 6 hours a week or less. Variation tasks follow the same rules as role tasks.
- A filled `customization` uses an ID like `C-0042` (never a name), has `counselor_check: true`, and holds no keep-with-staff or 3-rated tasks.
- `status` is ready, needs_info, or on_hold; a blocking flag (see `screening.md`) cannot be ready; needs_info may have no roles; any status but ready needs a flag and questions.
- `guardrail_notes` is not empty.
- Roles, questions, and customization use no wording that labels people (diagnoses, autism, levels, functioning labels).
