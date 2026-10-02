from data.models import Scenario, Suspect

from engine.constraints import (
    is_present,
    has_access,
    is_available,
    can_reach_crime_scene
)


def get_all_suspects(
    scenario: Scenario
) -> set[str]:

    return {
        suspect.id
        for suspect in scenario.suspects
    }


def get_access_set(
    scenario: Scenario
) -> set[str]:

    access_set = set()

    for suspect in scenario.suspects:

        if has_access(
            suspect,
            scenario
        ):
            access_set.add(
                suspect.id
            )

    return access_set


def get_presence_set(
    scenario: Scenario
) -> set[str]:

    presence_set = set()

    for suspect in scenario.suspects:

        if is_present(
            suspect,
            scenario
        ):
            presence_set.add(
                suspect.id
            )

    return presence_set


def get_availability_set(
    scenario: Scenario
) -> set[str]:

    availability_set = set()

    for suspect in scenario.suspects:

        if is_available(
            suspect,
            scenario
        ):
            availability_set.add(
                suspect.id
            )

    return availability_set


def get_reachability_set(
    scenario: Scenario
) -> set[str]:

    reachability_set = set()

    for suspect in scenario.suspects:

        if can_reach_crime_scene(
            suspect,
            scenario
        ):
            reachability_set.add(
                suspect.id
            )

    return reachability_set


def calculate_possible_set(
    scenario: Scenario
) -> set[str]:

    access_set = get_access_set(
        scenario
    )

    presence_set = get_presence_set(
        scenario
    )

    availability_set = get_availability_set(
        scenario
    )

    reachability_set = get_reachability_set(
        scenario
    )

    possible_set = (
        access_set
        & presence_set
        & availability_set
        & reachability_set
    )

    return possible_set


def get_suspects_from_ids(
    scenario: Scenario,
    suspect_ids: set[str]
) -> list[Suspect]:

    suspects = []

    for suspect in scenario.suspects:

        if suspect.id in suspect_ids:
            suspects.append(
                suspect
            )

    return suspects


def get_set_analysis(
    scenario: Scenario
) -> dict:

    all_suspects = get_all_suspects(
        scenario
    )

    access_set = get_access_set(
        scenario
    )

    presence_set = get_presence_set(
        scenario
    )

    availability_set = get_availability_set(
        scenario
    )

    reachability_set = get_reachability_set(
        scenario
    )

    possible_set = (
        access_set
        & presence_set
        & availability_set
        & reachability_set
    )

    return {
        "all": all_suspects,
        "access": access_set,
        "presence": presence_set,
        "availability": availability_set,
        "reachability": reachability_set,
        "possible": possible_set
    }