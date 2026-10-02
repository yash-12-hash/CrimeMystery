from data.models import Scenario, Suspect

from graph.scene_graph import (
    get_reachability_analysis
)


# ============================================================
# TIME UTILITIES
# ============================================================

def time_to_minutes(time_string: str) -> int:
    """
    Convert HH:MM into minutes from midnight.
    """

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


# ============================================================
# PRESENCE
# ============================================================

def is_present(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    crime_location = (
        scenario.crime.location_id
    )

    crime_start = time_to_minutes(
        scenario.crime.start_time
    )

    crime_end = time_to_minutes(
        scenario.crime.end_time
    )

    for evidence in scenario.evidence:

        if evidence.suspect_id != suspect.id:
            continue

        if evidence.location_id != crime_location:
            continue

        if evidence.time is None:
            continue

        try:
            evidence_time = time_to_minutes(
                evidence.time
            )
        except ValueError:
            continue

        # Evidence occurs during the crime interval.
        if (
            crime_start
            <= evidence_time
            <= crime_end
        ):
            return True

    return False


# ============================================================
# ACCESS
# ============================================================

def has_access(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    crime_location = (
        scenario.crime.location_id
    )

    for evidence in scenario.evidence:

        if evidence.suspect_id != suspect.id:
            continue

        if evidence.location_id != crime_location:
            continue

        if (
            evidence.evidence_type
            == "Access Permission"
        ):
            return True

    return False


# ============================================================
# ALIBI
# ============================================================

def has_valid_alibi(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    crime_location = (
        scenario.crime.location_id
    )

    crime_start = time_to_minutes(
        scenario.crime.start_time
    )

    crime_end = time_to_minutes(
        scenario.crime.end_time
    )

    for evidence in scenario.evidence:

        if evidence.suspect_id != suspect.id:
            continue

        if evidence.location_id is None:
            continue

        if evidence.location_id == crime_location:
            continue

        if evidence.time is None:
            continue

        try:
            evidence_time = time_to_minutes(
                evidence.time
            )
        except ValueError:
            continue

        # An observation at another location during
        # the crime interval counts as an alibi.
        if (
            crime_start
            <= evidence_time
            <= crime_end
        ):
            return True

    return False


# ============================================================
# AVAILABILITY
# ============================================================

def is_available(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    return not has_valid_alibi(
        suspect,
        scenario
    )


# ============================================================
# REACHABILITY
# ============================================================

def can_reach_crime_scene(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    # --------------------------------------------------------
    # CASE 1:
    #
    # The suspect is already observed at the crime scene
    # during the crime interval.
    #
    # Therefore:
    #
    # d(Lc, Lc) = 0
    #
    # and the suspect is reachable.
    # --------------------------------------------------------

    if is_present(
        suspect,
        scenario
    ):
        return True

    # --------------------------------------------------------
    # CASE 2:
    #
    # Use the graph-theory reachability engine.
    #
    # IMPORTANT:
    #
    # get_reachability_analysis() is defined around the
    # suspect and scenario:
    #
    #     get_reachability_analysis(suspect, scenario)
    #
    # The previous implementation incorrectly called it as:
    #
    #     get_reachability_analysis(scenario, graph)
    #
    # That caused an exception which was silently converted
    # into False.
    # --------------------------------------------------------

    reachability = get_reachability_analysis(
        suspect,
        scenario
    )

    if not isinstance(
        reachability,
        dict
    ):
        return False

    return bool(
        reachability.get(
            "reachable",
            False
        )
    )


# ============================================================
# ALL CONSTRAINTS
# ============================================================

def satisfies_all_constraints(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

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

    return (
        present
        and
        access
        and
        available
        and
        reachable
    )


# ============================================================
# FIND POSSIBLE SUSPECTS
# ============================================================

def find_possible_suspects(
    scenario: Scenario
) -> list[Suspect]:

    possible_suspects = []

    for suspect in scenario.suspects:

        if satisfies_all_constraints(
            suspect,
            scenario
        ):

            possible_suspects.append(
                suspect
            )

    return possible_suspects


# ============================================================
# SOLUTION CLASSIFICATION
# ============================================================

def classify_solution(
    possible_suspects: list[Suspect]
) -> str:

    number_of_candidates = (
        len(possible_suspects)
    )

    if number_of_candidates == 0:

        return "NO SOLUTION"

    elif number_of_candidates == 1:

        return "UNIQUE SOLUTION"

    else:

        return "MULTIPLE SOLUTIONS"
