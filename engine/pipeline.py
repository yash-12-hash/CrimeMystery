from dataclasses import dataclass

from data.models import Scenario

from engine.constraints import (
    find_possible_suspects,
    has_access,
    has_valid_alibi,
    is_available,
    is_present,
    can_reach_crime_scene,
    satisfies_all_constraints,
)

from engine.set_filter import get_set_analysis

from engine.logic import (
    build_rules,
    evaluate_suspect_logic,
    find_logically_possible_suspects,
)

from graph.scene_graph import get_reachability_analysis

from engine.csp_solver import (
    solve_crime_csp,
    get_csp_suspects,
    classify_csp_result,
)

from engine.contradictions import detect_contradictions

from engine.solution_validator import validate_solution

from engine.reasoning import generate_reasoning_report


@dataclass
class FullAnalysis:
    """
    Single source of truth for one complete scenario analysis.

    Every project layer is evaluated once and the resulting objects are
    passed to the UI and other consumers. This prevents the Streamlit UI
    from independently running slightly different versions of the same
    analysis.
    """

    scenario: Scenario

    constraint_rows: list[dict]
    constraint_candidates: list

    set_analysis: dict

    rules: list
    logic_evaluations: list
    logical_candidates: list

    graph_results: list[dict]

    csp_result: object
    csp_candidates: list
    csp_classification: str

    contradiction_report: object

    validation: object

    reasoning_report: object

    final_candidates: list
    final_status: str


def run_full_analysis(scenario: Scenario) -> FullAnalysis:
    """
    Run the complete mathematical crime-mystery pipeline once.

    Pipeline order:

        Constraint Analysis
              ↓
        Set Theory
              ↓
        Predicate Logic
              ↓
        Graph Reachability
              ↓
        CSP / Backtracking
              ↓
        Contradiction Detection
              ↓
        Solution Validation
              ↓
        Mathematical Reasoning
              ↓
        Final Classification

    The functions themselves remain in their original modules. This
    integration layer only coordinates them and preserves their existing
    APIs.
    """

    # --------------------------------------------------------
    # STEP 3 — CONSTRAINT ANALYSIS
    # --------------------------------------------------------

    constraint_rows = []

    for suspect in scenario.suspects:
        present = is_present(
            suspect,
            scenario,
        )

        access = has_access(
            suspect,
            scenario,
        )

        alibi = has_valid_alibi(
            suspect,
            scenario,
        )

        available = is_available(
            suspect,
            scenario,
        )

        reachable = can_reach_crime_scene(
            suspect,
            scenario,
        )

        possible = satisfies_all_constraints(
            suspect,
            scenario,
        )

        constraint_rows.append(
            {
                "ID": suspect.id,
                "Suspect": suspect.name,
                "Present": present,
                "Access": access,
                "Valid Alibi": alibi,
                "Available": available,
                "Reachable": reachable,
                "All Constraints": possible,
            }
        )

    constraint_candidates = find_possible_suspects(
        scenario
    )

    # --------------------------------------------------------
    # STEP 4 — SET THEORY
    # --------------------------------------------------------

    set_analysis = get_set_analysis(
        scenario
    )

    # --------------------------------------------------------
    # STEP 5 — PREDICATE LOGIC
    # --------------------------------------------------------

    rules = build_rules(
        scenario
    )

    logic_evaluations = []

    for suspect in scenario.suspects:
        logic_evaluations.append(
            evaluate_suspect_logic(
                suspect,
                scenario,
            )
        )

    logical_candidates = find_logically_possible_suspects(
        scenario
    )

    # --------------------------------------------------------
    # STEP 6 — GRAPH THEORY
    # --------------------------------------------------------

    graph_results = []

    for suspect in scenario.suspects:
        result = get_reachability_analysis(
            suspect,
            scenario,
        )

        graph_results.append(
            {
                "ID": suspect.id,
                "Suspect": suspect.name,
                "Result": result,
            }
        )

    # --------------------------------------------------------
    # STEP 7 — CSP / BACKTRACKING
    # --------------------------------------------------------

    csp_result = solve_crime_csp(
        scenario
    )

    csp_candidates = get_csp_suspects(
        scenario,
        csp_result,
    )

    csp_classification = classify_csp_result(
        csp_result
    )

    # --------------------------------------------------------
    # STEP 8 — CONTRADICTION DETECTION
    # --------------------------------------------------------

    contradiction_report = detect_contradictions(
        scenario
    )

    # --------------------------------------------------------
    # STEP 9 — SOLUTION VALIDATION
    # --------------------------------------------------------

    validation = validate_solution(
        scenario=scenario,
        csp_result=csp_result,
        contradiction_report=contradiction_report,
        constraint_candidates=constraint_candidates,
    )

    # --------------------------------------------------------
    # STEP 11 — MATHEMATICAL REASONING
    # --------------------------------------------------------

    reasoning_report = generate_reasoning_report(
        scenario
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    final_candidates = constraint_candidates

    if contradiction_report.has_contradictions():
        final_status = "INCONSISTENT SCENARIO"
    elif len(final_candidates) == 0:
        final_status = "NO SOLUTION"
    elif len(final_candidates) == 1:
        final_status = "UNIQUE SOLUTION"
    else:
        final_status = "MULTIPLE SOLUTIONS"

    return FullAnalysis(
        scenario=scenario,
        constraint_rows=constraint_rows,
        constraint_candidates=constraint_candidates,
        set_analysis=set_analysis,
        rules=rules,
        logic_evaluations=logic_evaluations,
        logical_candidates=logical_candidates,
        graph_results=graph_results,
        csp_result=csp_result,
        csp_candidates=csp_candidates,
        csp_classification=csp_classification,
        contradiction_report=contradiction_report,
        validation=validation,
        reasoning_report=reasoning_report,
        final_candidates=final_candidates,
        final_status=final_status,
    )
