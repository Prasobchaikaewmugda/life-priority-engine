# Selected File Index for Phase10O Commit and Freeze

## Commit used for freeze

- Commit SHA: 65a739db7cf3e9e888ad98b7644b19de7915b497
- Commit subject: LPE Phase10O accepted daily-use and settings state

## Files committed in Phase10P commit-only gate

| File | SHA256 | Role |
|---|---:|---|
| app.py | 6e24bff7c30e7e5263182c3fe1e45f9a3da1e7bd1ae87430f8fb59122affffb8 | Accepted application state |
| acceptance/lpe_version_a_phase10n_end_of_day_tomorrow_runtime_authority_visual_cleanup_acceptance_v1.md | 7001812f76bb21fdea61b605ff745e1070cf879e78e6eb7321368f4ab0cf3f77 | Phase10N acceptance evidence |
| acceptance/lpe_version_a_phase10n_end_of_day_tomorrow_runtime_authority_visual_cleanup_acceptance_v1_SHA256SUMS.txt | fff9832ccd32b631dea52e3fa78f1ba36b0a56f9e64c5f8264dfef7ae1dc8124 | Phase10N acceptance SHA file |
| acceptance/lpe_version_a_phase10o_final_visual_acceptance_after_table_first_readability_guided_questions_acceptance_v2.md | 4d20fff7f351eea700bfaef49be97992432045c1833d3a32a46f672d8156ad80 | Phase10O final visual acceptance evidence |
| acceptance/lpe_version_a_phase10o_final_visual_acceptance_after_table_first_readability_guided_questions_acceptance_v2_SHA256SUMS.txt | 18352e03d971061e28d1ad71f4c3f16081bc06779f478c36f381ba4dfaab73f2 | Phase10O acceptance SHA file |

## Hold list

The following should not be staged or committed as part of this freeze unless a separate owner gate authorizes it:

- scripts/
- docs/
- prototypes/
- app_phase10n_runtime_authority_v2_Oa1mhp.py
- legacy runner files
- untracked acceptance files from older phases not selected for this freeze
