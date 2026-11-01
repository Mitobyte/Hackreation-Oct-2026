# Screening a posting

Run every check. Record each hit in `posting_flags` as `{"type": ..., "detail": ...}`. The validator makes a blocking flag set `status` to `needs_info` or `on_hold`.

| Check | Flag type | Blocking? | What to do |
| --- | --- | --- | --- |
| Fewer than three duty lines, or duties too vague to name a task | `no_duties` | Yes: `needs_info` | Carve nothing. Write questions asking for a duty list or a site visit. |
| Pay below the Wisconsin minimum wage ($7.25/hour, the federal rate), or pay that cannot be checked per hour (monthly stipend, "up to," no hours) | `pay_below_minimum_or_unclear` | Yes: `on_hold` | Work out the hourly rate if hours are known. Ask for an hourly rate. Helper roles must pay at least minimum wage and the coworker rate. |
| Unpaid, volunteer, or commission-only pay | `unpaid_or_commission_only` | Yes: `on_hold` | Competitive integrated employment needs at least minimum wage. |
| Independent contractor or 1099 work | `contractor_not_employee` | Yes: `on_hold` | Ask whether the role can be a W-2 employee position. |
| Adult or sexual content in the product or work (18+, intimate, gambling) | `adult_content` | Yes: `on_hold` | An ERI supervisor decides whether to pursue it, with the client's informed choice. |
| Eligibility rules a helper may not meet (enrolled student, degree, license) | `eligibility_restriction` | No | Ask whether the employer would create a separate aide role without that rule. |
| Fully remote work | `remote_only` | No | Supports change: a video check-in replaces the on-site coach; ask about equipment and internet. |
| Temporary or seasonal term | `temporary` | No | Note the end date; plan the next placement. |

([Competitive integrated employment](https://www.govinfo.gov/content/pkg/FR-2023-04-05/pdf/2023-07204.pdf); [Wisconsin minimum wage, unchanged at $7.25 since 2009](https://civicmedia.us/news/2026/05/21/is-wisconsins-minimum-wage-in-2026-the-same-as-it-was-in-2009))
