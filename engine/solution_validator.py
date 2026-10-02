from dataclasses import dataclass, field

from data.models import (
    Scenario,
    Suspect
)

from engine.csp_solver import (
    CSPSolution,
    get_csp_suspects
)

from engine.contradictions import (
    ContradictionReport
)


# ============================================================
# SOLUTION STATUS
# ============================================================

UNIQUE_SOLUTION = "UNIQUE SOLUTION"

MULTIPLE_SOLUTIONS = "MULTIPLE SOLUTIONS"

NO_SOLUTION = "NO SOLUTION"

INCONSISTENT_SCENARIO = "INCONSISTENT SCENARIO"


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class SolutionValidationResult:

    status: str

    candidates: list[Suspect] = field(
        default_factory=list
    )

    candidate_count: int = 0

    contradiction_count: int = 0

    csp_solution_count: int = 0

    constraint_model_agrees: bool = False

    explanation: str = ""

    warnings: list[str] = field(
        default_factory=list
    )


# ============================================================
# VALIDATE SOLUTION COUNT
# ============================================================

def classify_solution_count(
    solution_count: int,
    has_contradictions: bool
) -> str:

    # --------------------------------------------------------
    # Contradictions take priority.
    # --------------------------------------------------------

    if has_contradictions:

        return INCONSISTENT_SCENARIO

    # --------------------------------------------------------
    # Exactly one solution
    # --------------------------------------------------------

    if solution_count == 1:

        return UNIQUE_SOLUTION

    # --------------------------------------------------------
    # More than one solution
    # --------------------------------------------------------

    if solution_count > 1:

        return MULTIPLE_SOLUTIONS

    # --------------------------------------------------------
    # No solutions
    # --------------------------------------------------------

    return NO_SOLUTION


# ============================================================
# BUILD EXPLANATION
# ============================================================

def build_solution_explanation(
    status: str,
    candidates: list[Suspect],
    contradiction_report: ContradictionReport
) -> str:

    candidate_count = len(
        candidates
    )

    contradiction_count = (
        contradiction_report.count()
    )

    # --------------------------------------------------------
    # Inconsistent
    # --------------------------------------------------------

    if status == INCONSISTENT_SCENARIO:

        return (
            "The evidence or scenario contains "
            f"{contradiction_count} contradiction(s). "
            "The mathematical model is therefore "
            "internally inconsistent. A culprit "
            "should not be announced until the "
            "conflicting information is resolved."
        )

    # --------------------------------------------------------
    # Unique
    # --------------------------------------------------------

    if status == UNIQUE_SOLUTION:

        suspect = candidates[0]

        return (
            "Exactly one suspect satisfies "
            "all required constraints. "
            f"The remaining candidate is "
            f"{suspect.name}."
        )

    # --------------------------------------------------------
    # Multiple
    # --------------------------------------------------------

    if status == MULTIPLE_SOLUTIONS:

        names = ", ".join(
            suspect.name
            for suspect in candidates
        )

        return (
            f"{candidate_count} suspects satisfy "
            "the current constraints: "
            f"{names}. The available evidence "
            "does not uniquely determine one "
            "candidate."
        )

    # --------------------------------------------------------
    # No solution
    # --------------------------------------------------------

    return (
        "No suspect satisfies all required "
        "constraints. No valid assignment "
        "exists under the current mathematical "
        "model."
    )


# ============================================================
# VALIDATE COMPLETE SOLVER RESULT
# ============================================================

def validate_solution(
    scenario: Scenario,
    csp_result: CSPSolution,
    contradiction_report: ContradictionReport,
    constraint_candidates: list[Suspect]
) -> SolutionValidationResult:

    # --------------------------------------------------------
    # CSP candidates
    # --------------------------------------------------------

    csp_candidates = get_csp_suspects(
        scenario,
        csp_result
    )

    # --------------------------------------------------------
    # Compare CSP and constraint engine
    # --------------------------------------------------------

    csp_ids = {
        suspect.id
        for suspect in csp_candidates
    }

    constraint_ids = {
        suspect.id
        for suspect in constraint_candidates
    }

    models_agree = (
        csp_ids == constraint_ids
    )

    # --------------------------------------------------------
    # Classify
    # --------------------------------------------------------

    status = classify_solution_count(

        solution_count=len(
            csp_candidates
        ),

        has_contradictions=(
            contradiction_report
            .has_contradictions()
        )
    )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = build_solution_explanation(

        status,

        csp_candidates,

        contradiction_report
    )

    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    warnings = []

    if not models_agree:

        warnings.append(
            "The CSP result and basic "
            "constraint engine disagree."
        )

    if (
        status == INCONSISTENT_SCENARIO
        and len(csp_candidates) > 0
    ):

        warnings.append(
            "A mathematical candidate exists, "
            "but contradictory evidence was "
            "detected. The candidate should "
            "not be treated as validated."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return SolutionValidationResult(

        status=status,

        candidates=csp_candidates,

        candidate_count=len(
            csp_candidates
        ),

        contradiction_count=(
            contradiction_report.count()
        ),

        csp_solution_count=len(
            csp_result.assignments
        ),

        constraint_model_agrees=(
            models_agree
        ),

        explanation=explanation,

        warnings=warnings
    )


# ============================================================
# PRINT VALIDATION RESULT
# ============================================================

def print_solution_validation(
    result: SolutionValidationResult
):

    print("\n")
    print("=" * 65)
    print("STEP 9 — SOLUTION VALIDATION")
    print("=" * 65)

    print(
        "\nCSP solutions:",
        result.csp_solution_count
    )

    print(
        "Candidate count:",
        result.candidate_count
    )

    print(
        "Contradictions:",
        result.contradiction_count
    )

    print(
        "Constraint model agrees:",
        result.constraint_model_agrees
    )

    print(
        "\nFINAL STATUS:"
    )

    print(
        result.status
    )

    print(
        "\nEXPLANATION:"
    )

    print(
        result.explanation
    )

    if result.candidates:

        print(
            "\nVALID CANDIDATES:"
        )

        for suspect in result.candidates:

            print(
                f"  {suspect.id} -> "
                f"{suspect.name}"
            )

    if result.warnings:

        print(
            "\nWARNINGS:"
        )

        for warning in result.warnings:

            print(
                f"  ⚠ {warning}"
            )