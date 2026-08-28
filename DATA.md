# Data documentation

## Released data

ForesightSafety-SAGE releases the final scenario-family definitions and executable evaluation scenarios used by the main benchmark. It does not release target-model outputs, episode trajectories, judge records, runtime logs, human-annotation files, or rebuttal-only data.

The benchmark covers five first-level risk dimensions and sixteen subcategories:

| Dimension directory | Subcategories | Scenarios |
|---|---:|---:|
| `interaction_understanding_failure` | 2 | 134 |
| `goal_norm_misalignment` | 3 | 201 |
| `robustness_generalization_failure` | 3 | 201 |
| `supervision_control_failure` | 4 | 268 |
| `autonomy_authority_failure` | 4 | 268 |
| **Total** | **16** | **1,072** |

Each subcategory directory under `data/tasks/` contains:

- `seeds.json`: 7 expert-designed seed scenarios.
- `generation_selected_60*.json`: 60 expanded scenarios retained after quality and diversity filtering.
- `benchmark.json`: the merged, runnable set of 67 unique scenarios used by the release commands.

The `input_path` in `quality_selection_metadata` records the pre-filter candidate pool used during selection. Those intermediate candidate-pool files are not included in the release.

The legacy directory name `side_sffect_negligence_seeds` is retained to preserve compatibility with the experimental code. The runners map it to the `side_effect_negligence` subcategory automatically.

## Scenario schema

Each task file contains top-level family metadata and an `instances` list. A scenario generally includes:

- `instance_id`, `scenario_theme`, and `domain`;
- `target_spec`, including task, crisis, consequence, and authority contexts;
- `environment_state`, containing target-visible workflow state;
- `judge_spec`, containing hidden boundaries and evaluation criteria;
- `tool_manifest`, containing required tool roles, optional preferred tool names, and family constraints;
- `attacker`, containing the pressure strategy, initial message, and turn budget.

The target agent does not receive judge-only fields or internal tool risk metadata. The simulated environment uses those fields to update runtime state, and the episode-level judge uses them as evaluation references.

## Scenario-family definitions

Files under `data/families/<dimension>/<subcategory>.json` define the failure mechanism, authority or safety boundary, safe and risky behavior patterns, attacker guidance, judge criteria, and tool patterns for each subcategory. They are used by scenario generation and episode-level judgment.

## Integrity checks

For the released `benchmark.json` files:

- all 16 subcategories contain exactly 67 scenarios;
- the 1,072 `instance_id` values are globally unique;
- each merged file contains exactly the IDs from its 7 seeds and 60 selected expansions.

Run `python scripts/check_release.py` to repeat the count, uniqueness, path, and credential checks locally.
