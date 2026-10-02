from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.csp_solver import (
    solve_crime_csp,
    get_csp_suspects,
    classify_csp_result,
)


def make_base_scenario():
    suspects = [
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
        Suspect("S3", "Rohan"),
    ]

    locations = [
        Location("L1", "Computer Laboratory"),
        Location("L2", "Library"),
    ]

    connections = [
        Connection("P1", "L1", "L2", 2),
    ]

    crime = Crime(
        crime_type="Laptop Theft",
        location_id="L1",
        start_time="14:25",
        end_time="14:35",
    )

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

    return suspects, locations, connections, crime, constraints


def make_unique_solution_scenario():
    (
        suspects,
        locations,
        connections,
        crime,
        constraints,
    ) = make_base_scenario()

    evidence = [
        # S1 satisfies all constraints.
        #
        # Presence:
        # Evidence is at the crime location (L1)
        # exactly when the crime starts (14:25).
        #
        # Reachability:
        # S1 is already at the crime location,
        # so travel time is 0.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:25",
            "Rahul was seen in the laboratory when the crime started.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),

        # S2 has access but is not present at the crime scene.
        Evidence(
            "E3",
            "Access Permission",
            "S2",
            "L1",
            None,
            "Aditya has laboratory access.",
        ),
        Evidence(
            "E4",
            "CCTV",
            "S2",
            "L2",
            "14:20",
            "Aditya was seen in the library.",
        ),

        # S3 has no useful evidence.
    ]

    return Scenario(
        id="CSP_UNIQUE",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def make_multiple_solution_scenario():
    (
        suspects,
        locations,
        connections,
        crime,
        constraints,
    ) = make_base_scenario()

    evidence = [
        # S1 satisfies all constraints.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:25",
            "Rahul was seen in the laboratory when the crime started.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),

        # S2 also satisfies all constraints.
        Evidence(
            "E3",
            "CCTV",
            "S2",
            "L1",
            "14:25",
            "Aditya was seen in the laboratory when the crime started.",
        ),
        Evidence(
            "E4",
            "Access Permission",
            "S2",
            "L1",
            None,
            "Aditya has laboratory access.",
        ),

        # S3 is eliminated because there is no presence
        # evidence at the crime location.
        Evidence(
            "E5",
            "Access Permission",
            "S3",
            "L1",
            None,
            "Rohan has laboratory access.",
        ),
        Evidence(
            "E6",
            "CCTV",
            "S3",
            "L2",
            "14:20",
            "Rohan was seen in the library.",
        ),
    ]

    return Scenario(
        id="CSP_MULTIPLE",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def make_no_solution_scenario():
    (
        suspects,
        locations,
        connections,
        crime,
        constraints,
    ) = make_base_scenario()

    evidence = [
        # S1 has access but no presence.
        Evidence(
            "E1",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),

        # S2 is present but has no access.
        Evidence(
            "E2",
            "CCTV",
            "S2",
            "L1",
            "14:25",
            "Aditya was seen in the laboratory.",
        ),

        # S3 has no useful evidence.
    ]

    return Scenario(
        id="CSP_NONE",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_csp_finds_unique_solution():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    assert len(result.assignments) == 1

    assert result.assignments[0].culprit_id == "S1"


def test_csp_classifies_unique_solution():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    classification = classify_csp_result(result)

    assert classification == "UNIQUE SOLUTION"


def test_csp_finds_multiple_solutions():
    scenario = make_multiple_solution_scenario()

    result = solve_crime_csp(scenario)

    culprit_ids = {
        assignment.culprit_id
        for assignment in result.assignments
    }

    assert culprit_ids == {
        "S1",
        "S2",
    }


def test_csp_classifies_multiple_solutions():
    scenario = make_multiple_solution_scenario()

    result = solve_crime_csp(scenario)

    classification = classify_csp_result(result)

    assert classification == "MULTIPLE SOLUTIONS"


def test_csp_finds_no_solution():
    scenario = make_no_solution_scenario()

    result = solve_crime_csp(scenario)

    assert result.assignments == []


def test_csp_classifies_no_solution():
    scenario = make_no_solution_scenario()

    result = solve_crime_csp(scenario)

    classification = classify_csp_result(result)

    assert classification == "NO SOLUTION"


def test_csp_tracks_nodes_explored():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    assert result.nodes_explored > 0


def test_csp_rejects_invalid_assignments():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    assert result.rejected_assignments > 0


def test_csp_generates_search_trace():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    assert len(result.search_trace) > 0


def test_search_trace_contains_suspect_ids():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    trace_text = " ".join(
        str(entry)
        for entry in result.search_trace
    )

    assert "S1" in trace_text
    assert "S2" in trace_text
    assert "S3" in trace_text


def test_get_csp_suspects_returns_suspect_objects():
    scenario = make_unique_solution_scenario()

    result = solve_crime_csp(scenario)

    suspects = get_csp_suspects(
        scenario,
        result,
    )

    assert len(suspects) == 1
    assert isinstance(suspects[0], Suspect)
    assert suspects[0].id == "S1"
    assert suspects[0].name == "Rahul"


def test_multiple_csp_suspects_are_returned():
    scenario = make_multiple_solution_scenario()

    result = solve_crime_csp(scenario)

    suspects = get_csp_suspects(
        scenario,
        result,
    )

    suspect_ids = {
        suspect.id
        for suspect in suspects
    }

    assert suspect_ids == {
        "S1",
        "S2",
    }


def test_no_csp_suspects_are_returned_for_no_solution():
    scenario = make_no_solution_scenario()

    result = solve_crime_csp(scenario)

    suspects = get_csp_suspects(
        scenario,
        result,
    )

    assert suspects == []