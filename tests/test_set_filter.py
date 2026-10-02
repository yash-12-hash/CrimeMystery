from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.set_filter import (
    get_all_suspects,
    get_access_set,
    get_presence_set,
    get_availability_set,
    get_reachability_set,
    calculate_possible_set,
    get_suspects_from_ids,
    get_set_analysis,
)


def make_scenario():
    suspects = [
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
        Suspect("S3", "Rohan"),
        Suspect("S4", "Sameer"),
    ]

    locations = [
        Location("L1", "Computer Laboratory"),
        Location("L2", "Library"),
        Location("L3", "College Gate"),
    ]

    connections = [
        Connection("P1", "L2", "L1", 2),
        Connection("P2", "L3", "L2", 3),
    ]

    crime = Crime(
        crime_type="Laptop Theft",
        location_id="L1",
        start_time="14:25",
        end_time="14:35",
    )

    evidence = [
        # S1 satisfies all four constraints.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:30",
            "Rahul was seen in the lab.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has lab access.",
        ),

        # S2 has access and presence,
        # but a valid alibi makes S2 unavailable.
        Evidence(
            "E3",
            "CCTV",
            "S2",
            "L1",
            "14:30",
            "Aditya was seen in the lab.",
        ),
        Evidence(
            "E4",
            "Access Permission",
            "S2",
            "L1",
            None,
            "Aditya has lab access.",
        ),
        Evidence(
            "E5",
            "CCTV",
            "S2",
            "L2",
            "14:30",
            "Aditya was also recorded in the library.",
        ),

        # S3 has access but no presence at the crime scene
        # during the crime.
        # The location evidence before the crime allows
        # reachability to be true.
        Evidence(
            "E6",
            "Access Permission",
            "S3",
            "L1",
            None,
            "Rohan has lab access.",
        ),
        Evidence(
            "E7",
            "CCTV",
            "S3",
            "L2",
            "14:20",
            "Rohan was in the library.",
        ),

        # S4 has neither access nor presence,
        # but has no alibi.
        Evidence(
            "E8",
            "CCTV",
            "S4",
            "L3",
            "14:20",
            "Sameer was near the gate.",
        ),
    ]

    constraints = [
        Constraint(
            "C1",
            "Suspect must be present at the crime location.",
        ),
        Constraint(
            "C2",
            "Suspect must have access to the crime location.",
        ),
        Constraint(
            "C3",
            "Suspect must not have a valid alibi.",
        ),
        Constraint(
            "C4",
            "Suspect must be reachable to the crime scene.",
        ),
    ]

    return Scenario(
        id="SET_TEST",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_get_all_suspects_returns_all_suspect_ids():
    scenario = make_scenario()

    result = get_all_suspects(scenario)

    assert result == {
        "S1",
        "S2",
        "S3",
        "S4",
    }


def test_individual_sets_are_calculated_correctly():
    scenario = make_scenario()

    access = get_access_set(scenario)
    presence = get_presence_set(scenario)
    availability = get_availability_set(scenario)
    reachability = get_reachability_set(scenario)

    assert access == {
        "S1",
        "S2",
        "S3",
    }

    assert presence == {
        "S1",
        "S2",
    }

    assert availability == {
        "S1",
        "S3",
        "S4",
    }

    assert reachability == {
        "S1",
        "S2",
        "S3",
        "S4",
    }


def test_possible_set_is_intersection_of_all_constraint_sets():
    scenario = make_scenario()

    access = get_access_set(scenario)
    presence = get_presence_set(scenario)
    availability = get_availability_set(scenario)
    reachability = get_reachability_set(scenario)

    possible = calculate_possible_set(scenario)

    expected = (
        access
        & presence
        & availability
        & reachability
    )

    assert possible == expected

    assert possible == {
        "S1",
    }


def test_get_suspects_from_ids_returns_correct_objects():
    scenario = make_scenario()

    suspects = get_suspects_from_ids(
        scenario,
        {
            "S1",
            "S3",
        },
    )

    assert {
        suspect.id
        for suspect in suspects
    } == {
        "S1",
        "S3",
    }

    assert {
        suspect.name
        for suspect in suspects
    } == {
        "Rahul",
        "Rohan",
    }


def test_get_set_analysis_contains_all_required_sets():
    scenario = make_scenario()

    analysis = get_set_analysis(scenario)

    assert set(analysis.keys()) == {
        "all",
        "access",
        "presence",
        "availability",
        "reachability",
        "possible",
    }

    assert analysis["all"] == {
        "S1",
        "S2",
        "S3",
        "S4",
    }

    assert analysis["access"] == {
        "S1",
        "S2",
        "S3",
    }

    assert analysis["presence"] == {
        "S1",
        "S2",
    }

    assert analysis["availability"] == {
        "S1",
        "S3",
        "S4",
    }

    assert analysis["reachability"] == {
        "S1",
        "S2",
        "S3",
        "S4",
    }

    assert analysis["possible"] == {
        "S1",
    }


def test_possible_set_cannot_contain_suspect_outside_all_suspects():
    scenario = make_scenario()

    possible = calculate_possible_set(scenario)

    assert possible <= get_all_suspects(scenario)