from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.constraints import (
    find_possible_suspects,
)

from engine.csp_solver import (
    solve_crime_csp,
)

from engine.contradictions import (
    detect_contradictions,
)

from engine.solution_validator import (
    validate_solution,
)


def make_base_scenario():
    suspects = [
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
        Suspect("S3", "Rohan"),
    ]

    locations = [
        Location(
            "L1",
            "Computer Laboratory",
        ),
        Location(
            "L2",
            "Library",
        ),
    ]

    connections = [
        Connection(
            "P1",
            "L1",
            "L2",
            2,
        ),
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

    return (
        suspects,
        locations,
        connections,
        crime,
        constraints,
    )


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
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:25",
            "Rahul was seen in the laboratory.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),

        # S2 is eliminated because there is
        # no presence at the crime scene.
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
        id="VALIDATION_UNIQUE",
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
            "Rahul was seen in the laboratory.",
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
            "Aditya was seen in the laboratory.",
        ),
        Evidence(
            "E4",
            "Access Permission",
            "S2",
            "L1",
            None,
            "Aditya has laboratory access.",
        ),

        # S3 is eliminated.
        Evidence(
            "E5",
            "Access Permission",
            "S3",
            "L1",
            None,
            "Rohan has laboratory access.",
        ),
    ]

    return Scenario(
        id="VALIDATION_MULTIPLE",
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

        # S2 has presence but no access.
        Evidence(
            "E2",
            "CCTV",
            "S2",
            "L1",
            "14:25",
            "Aditya was seen in the laboratory.",
        ),

        # S3 has no evidence.
    ]

    return Scenario(
        id="VALIDATION_NONE",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def make_inconsistent_scenario():
    (
        suspects,
        locations,
        connections,
        crime,
        constraints,
    ) = make_base_scenario()

    evidence = [
        # Valid evidence.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:25",
            "Rahul was seen in the laboratory.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),

        # Duplicate evidence ID creates a contradiction.
        Evidence(
            "E1",
            "CCTV",
            "S2",
            "L2",
            "14:20",
            "Duplicate evidence ID.",
        ),
    ]

    return Scenario(
        id="VALIDATION_INCONSISTENT",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def run_validation(scenario):
    """
    Run the prerequisite analysis stages required by validate_solution()
    and then validate the combined results.
    """

    constraint_candidates = find_possible_suspects(
        scenario
    )

    csp_result = solve_crime_csp(
        scenario
    )

    contradiction_report = detect_contradictions(
        scenario
    )

    return validate_solution(
        scenario,
        csp_result,
        contradiction_report,
        constraint_candidates,
    )


def test_unique_solution_is_validated():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert result.status == "UNIQUE SOLUTION"
    assert result.candidate_count == 1


def test_unique_solution_contains_correct_candidate():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    candidate_ids = {
        suspect.id
        for suspect in result.candidates
    }

    assert candidate_ids == {
        "S1",
    }


def test_unique_solution_has_no_contradictions():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert result.contradiction_count == 0


def test_unique_solution_has_one_csp_solution():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert result.csp_solution_count == 1


def test_unique_solution_models_agree():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert result.constraint_model_agrees is True


def test_multiple_solution_is_validated():
    scenario = make_multiple_solution_scenario()

    result = run_validation(scenario)

    assert result.status == "MULTIPLE SOLUTIONS"
    assert result.candidate_count == 2


def test_multiple_solution_contains_correct_candidates():
    scenario = make_multiple_solution_scenario()

    result = run_validation(scenario)

    candidate_ids = {
        suspect.id
        for suspect in result.candidates
    }

    assert candidate_ids == {
        "S1",
        "S2",
    }


def test_multiple_solution_has_two_csp_solutions():
    scenario = make_multiple_solution_scenario()

    result = run_validation(scenario)

    assert result.csp_solution_count == 2


def test_no_solution_is_validated():
    scenario = make_no_solution_scenario()

    result = run_validation(scenario)

    assert result.status == "NO SOLUTION"
    assert result.candidate_count == 0


def test_no_solution_has_no_candidates():
    scenario = make_no_solution_scenario()

    result = run_validation(scenario)

    assert result.candidates == []


def test_inconsistent_scenario_is_detected():
    scenario = make_inconsistent_scenario()

    result = run_validation(scenario)

    assert result.status == "INCONSISTENT SCENARIO"


def test_inconsistent_scenario_has_contradictions():
    scenario = make_inconsistent_scenario()

    result = run_validation(scenario)

    assert result.contradiction_count > 0


def test_validation_contains_explanation():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert isinstance(
        result.explanation,
        str,
    )

    assert len(
        result.explanation.strip()
    ) > 0


def test_validation_contains_warnings_list():
    scenario = make_unique_solution_scenario()

    result = run_validation(scenario)

    assert isinstance(
        result.warnings,
        list,
    )
