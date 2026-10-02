from dataclasses import dataclass, field

from data.models import Scenario, Suspect

from engine.constraints import (
    is_present,
    has_access,
    is_available,
    can_reach_crime_scene
)

from engine.set_filter import (
    get_all_suspects,
    get_access_set,
    get_presence_set,
    get_availability_set,
    get_reachability_set,
    calculate_possible_set
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class ReasoningStep:
    number: int
    title: str
    mathematical_expression: str
    explanation: str
    remaining_suspects: set[str] = field(default_factory=set)


@dataclass
class SuspectReason:
    suspect_id: str
    suspect_name: str
    status: str
    reasons: list[str] = field(default_factory=list)


@dataclass
class ReasoningReport:
    initial_set: set[str] = field(default_factory=set)

    access_set: set[str] = field(default_factory=set)
    presence_set: set[str] = field(default_factory=set)
    availability_set: set[str] = field(default_factory=set)
    reachability_set: set[str] = field(default_factory=set)

    possible_set: set[str] = field(default_factory=set)

    reasoning_steps: list[ReasoningStep] = field(
        default_factory=list
    )

    suspect_reasons: list[SuspectReason] = field(
        default_factory=list
    )

    final_status: str = ""

    final_explanation: str = ""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_set(values: set[str]) -> str:
    """
    Convert a Python set into a mathematically readable form.

    Example:
        {"S1", "S2", "S3"}
    becomes:
        {S1, S2, S3}
    """

    if not values:
        return "{}"

    sorted_values = sorted(values)

    return "{" + ", ".join(sorted_values) + "}"


def get_suspect_name(
    scenario: Scenario,
    suspect_id: str
) -> str:

    for suspect in scenario.suspects:
        if suspect.id == suspect_id:
            return suspect.name

    return "Unknown"


# ============================================================
# INDIVIDUAL SUSPECT ANALYSIS
# ============================================================

def explain_suspect(
    suspect: Suspect,
    scenario: Scenario
) -> SuspectReason:

    reasons = []

    present = is_present(
        suspect,
        scenario
    )

    access = has_access(
        suspect,
        scenario
    )

    available = is_available(
        suspect,
        scenario
    )

    reachable = can_reach_crime_scene(
        suspect,
        scenario
    )

    # --------------------------------------------------------
    # PRESENCE
    # --------------------------------------------------------

    if present:
        reasons.append(
            "Present at the crime location during "
            "the crime interval."
        )
    else:
        reasons.append(
            "Not present at the crime location during "
            "the crime interval."
        )

    # --------------------------------------------------------
    # ACCESS
    # --------------------------------------------------------

    if access:
        reasons.append(
            "Has authorized access to the crime location."
        )
    else:
        reasons.append(
            "Does not have authorized access to "
            "the crime location."
        )

    # --------------------------------------------------------
    # AVAILABILITY
    # --------------------------------------------------------

    if available:
        reasons.append(
            "No valid alibi places the suspect at "
            "another location during the crime."
        )
    else:
        reasons.append(
            "A valid alibi places the suspect at "
            "another location during the crime."
        )

    # --------------------------------------------------------
    # REACHABILITY
    # --------------------------------------------------------

    if reachable:
        reasons.append(
            "The suspect can reach the crime scene."
        )
    else:
        reasons.append(
            "The suspect cannot reach the crime scene "
            "under the current graph constraints."
        )

    satisfies_all = (
        present
        and access
        and available
        and reachable
    )

    if satisfies_all:
        status = "CANDIDATE"
    else:
        status = "ELIMINATED"

    return SuspectReason(
        suspect_id=suspect.id,
        suspect_name=suspect.name,
        status=status,
        reasons=reasons
    )


# ============================================================
# MAIN REASONING ENGINE
# ============================================================

def generate_reasoning_report(
    scenario: Scenario
) -> ReasoningReport:

    report = ReasoningReport()

    # --------------------------------------------------------
    # STEP 1 — INITIAL SET
    # --------------------------------------------------------

    report.initial_set = get_all_suspects(
        scenario
    )

    # --------------------------------------------------------
    # STEP 2 — INDIVIDUAL SETS
    # --------------------------------------------------------

    report.access_set = get_access_set(
        scenario
    )

    report.presence_set = get_presence_set(
        scenario
    )

    report.availability_set = get_availability_set(
        scenario
    )

    report.reachability_set = get_reachability_set(
        scenario
    )

    # --------------------------------------------------------
    # STEP 3 — ACCESS
    # --------------------------------------------------------

    remaining = (
        report.initial_set
        & report.access_set
    )

    report.reasoning_steps.append(
        ReasoningStep(
            number=1,
            title="Access Constraint",
            mathematical_expression=(
                "S₁ = S ∩ Access"
                "\n= "
                + format_set(report.initial_set)
                + " ∩ "
                + format_set(report.access_set)
                + "\n= "
                + format_set(remaining)
            ),
            explanation=(
                "Only suspects who have authorized "
                "access to the crime location remain."
            ),
            remaining_suspects=remaining.copy()
        )
    )

    # --------------------------------------------------------
    # STEP 4 — PRESENCE
    # --------------------------------------------------------

    remaining = (
        remaining
        & report.presence_set
    )

    report.reasoning_steps.append(
        ReasoningStep(
            number=2,
            title="Presence Constraint",
            mathematical_expression=(
                "S₂ = S₁ ∩ Presence"
                "\n= "
                + format_set(
                    report.access_set
                )
                + " ∩ "
                + format_set(
                    report.presence_set
                )
                + "\n= "
                + format_set(remaining)
            ),
            explanation=(
                "Only suspects confirmed to be at "
                "the crime location during the crime "
                "interval remain."
            ),
            remaining_suspects=remaining.copy()
        )
    )

    # --------------------------------------------------------
    # STEP 5 — AVAILABILITY
    # --------------------------------------------------------

    remaining = (
        remaining
        & report.availability_set
    )

    report.reasoning_steps.append(
        ReasoningStep(
            number=3,
            title="Availability Constraint",
            mathematical_expression=(
                "S₃ = S₂ ∩ Availability"
                "\n= "
                + format_set(
                    report.presence_set
                )
                + " ∩ "
                + format_set(
                    report.availability_set
                )
                + "\n= "
                + format_set(remaining)
            ),
            explanation=(
                "Suspects with a conflicting alibi "
                "during the crime interval are removed."
            ),
            remaining_suspects=remaining.copy()
        )
    )

    # --------------------------------------------------------
    # STEP 6 — REACHABILITY
    # --------------------------------------------------------

    remaining = (
        remaining
        & report.reachability_set
    )

    report.reasoning_steps.append(
        ReasoningStep(
            number=4,
            title="Reachability Constraint",
            mathematical_expression=(
                "S₄ = S₃ ∩ Reachability"
                "\n= "
                + format_set(
                    report.availability_set
                )
                + " ∩ "
                + format_set(
                    report.reachability_set
                )
                + "\n= "
                + format_set(remaining)
            ),
            explanation=(
                "Only suspects who can physically "
                "reach the crime scene remain."
            ),
            remaining_suspects=remaining.copy()
        )
    )

    # --------------------------------------------------------
    # FINAL SET
    # --------------------------------------------------------

    report.possible_set = calculate_possible_set(
        scenario
    )

    # --------------------------------------------------------
    # COMPLETE MATHEMATICAL EXPRESSION
    # --------------------------------------------------------

    final_expression = (
        "Possible = Access ∩ Presence ∩ "
        "Availability ∩ Reachability"
        "\n= "
        + format_set(report.access_set)
        + " ∩ "
        + format_set(report.presence_set)
        + " ∩ "
        + format_set(report.availability_set)
        + " ∩ "
        + format_set(report.reachability_set)
        + "\n= "
        + format_set(report.possible_set)
    )

    report.reasoning_steps.append(
        ReasoningStep(
            number=5,
            title="Final Set Intersection",
            mathematical_expression=final_expression,
            explanation=(
                "The final candidate set is obtained "
                "by intersecting all required "
                "constraint sets."
            ),
            remaining_suspects=report.possible_set.copy()
        )
    )

    # --------------------------------------------------------
    # SUSPECT-BY-SUSPECT EXPLANATIONS
    # --------------------------------------------------------

    for suspect in scenario.suspects:

        suspect_reason = explain_suspect(
            suspect,
            scenario
        )

        report.suspect_reasons.append(
            suspect_reason
        )

    # --------------------------------------------------------
    # FINAL CLASSIFICATION
    # --------------------------------------------------------

    candidate_count = len(
        report.possible_set
    )

    if candidate_count == 0:

        report.final_status = "NO SOLUTION"

        report.final_explanation = (
            "No suspect satisfies all required "
            "mathematical constraints."
        )

    elif candidate_count == 1:

        report.final_status = "UNIQUE SOLUTION"

        culprit_id = next(
            iter(report.possible_set)
        )

        culprit_name = get_suspect_name(
            scenario,
            culprit_id
        )

        report.final_explanation = (
            f"{culprit_id} ({culprit_name}) is the "
            "unique mathematically valid candidate."
        )

    else:

        report.final_status = "MULTIPLE SOLUTIONS"

        names = []

        for suspect_id in sorted(
            report.possible_set
        ):
            names.append(
                f"{suspect_id} "
                f"({get_suspect_name(scenario, suspect_id)})"
            )

        report.final_explanation = (
            "The current evidence does not uniquely "
            "determine one candidate. "
            "Valid candidates: "
            + ", ".join(names)
        )

    return report


# ============================================================
# PRINT REASONING REPORT
# ============================================================

def print_reasoning_report(
    report: ReasoningReport
):

    print("\n")
    print("=" * 70)
    print("STEP 11 — MATHEMATICAL REASONING ENGINE")
    print("=" * 70)

    print("\nINITIAL SUSPECT SET")
    print("-" * 70)

    print(
        "S =",
        format_set(report.initial_set)
    )

    print("\nCONSTRAINT SETS")
    print("-" * 70)

    print(
        "Access       =",
        format_set(report.access_set)
    )

    print(
        "Presence     =",
        format_set(report.presence_set)
    )

    print(
        "Availability =",
        format_set(report.availability_set)
    )

    print(
        "Reachability =",
        format_set(report.reachability_set)
    )

    print("\nREASONING TRACE")
    print("-" * 70)

    for step in report.reasoning_steps:

        print(
            f"\n{step.number}. "
            f"{step.title}"
        )

        print(
            "\nMathematical expression:"
        )

        print(step.mathematical_expression)

        print(
            "\nExplanation:"
        )

        print(step.explanation)

        print(
            "\nRemaining suspects:"
        )

        print(
            format_set(
                step.remaining_suspects
            )
        )

    print("\n")
    print("=" * 70)
    print("SUSPECT-BY-SUSPECT ANALYSIS")
    print("=" * 70)

    for reason in report.suspect_reasons:

        print(
            f"\n{reason.suspect_id} "
            f"-> {reason.suspect_name}"
        )

        print(
            f"Status: {reason.status}"
        )

        for explanation in reason.reasons:

            print(
                f"  - {explanation}"
            )

    print("\n")
    print("=" * 70)
    print("FINAL MATHEMATICAL RESULT")
    print("=" * 70)

    print(
        "\nPossible = "
        "Access ∩ Presence ∩ "
        "Availability ∩ Reachability"
    )

    print(
        "\nPossible =",
        format_set(report.possible_set)
    )

    print(
        "\nSTATUS:"
    )

    print(
        report.final_status
    )

    print(
        "\nEXPLANATION:"
    )

    print(
        report.final_explanation
    )