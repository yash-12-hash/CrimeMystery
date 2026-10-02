from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.pipeline import (
    run_full_analysis,
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
    ]

    return Scenario(
        id="PIPELINE_UNIQUE",
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
        id="PIPELINE_MULTIPLE",
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
        Evidence(
            "E1",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has laboratory access.",
        ),
        Evidence(
            "E2",
            "CCTV",
            "S2",
            "L1",
            "14:25",
            "Aditya was seen in the laboratory.",
        ),
    ]

    return Scenario(
        id="PIPELINE_NONE",
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
        id="PIPELINE_INCONSISTENT",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_pipeline_returns_analysis_for_unique_solution():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis is not None


def test_pipeline_unique_solution_status():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.final_status == "UNIQUE SOLUTION"


def test_pipeline_unique_solution_candidates():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    candidate_ids = {
        suspect.id
        for suspect in analysis.final_candidates
    }

    assert candidate_ids == {
        "S1",
    }


def test_pipeline_unique_constraint_candidates():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    candidate_ids = {
        suspect.id
        for suspect in analysis.constraint_candidates
    }

    assert candidate_ids == {
        "S1",
    }


def test_pipeline_unique_set_analysis_contains_possible_set():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.set_analysis["possible"] == {
        "S1",
    }


def test_pipeline_unique_logical_candidates():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    candidate_ids = {
        suspect.id
        for suspect in analysis.logical_candidates
    }

    assert candidate_ids == {
        "S1",
    }


def test_pipeline_unique_graph_results_cover_all_suspects():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert len(
        analysis.graph_results
    ) == len(
        scenario.suspects
    )


def test_pipeline_unique_csp_result_exists():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.csp_result is not None


def test_pipeline_unique_csp_has_one_solution():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert len(
        analysis.csp_result.assignments
    ) == 1


def test_pipeline_unique_has_no_contradictions():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert not analysis.contradiction_report.has_contradictions()


def test_pipeline_unique_validation_agrees():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.validation.constraint_model_agrees is True


def test_pipeline_unique_reasoning_matches_final_result():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert (
        analysis.reasoning_report.possible_set
        == {"S1"}
    )

    assert (
        analysis.reasoning_report.final_status
        == analysis.final_status
    )


def test_pipeline_multiple_solution_status():
    scenario = make_multiple_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.final_status == "MULTIPLE SOLUTIONS"


def test_pipeline_multiple_solution_candidates():
    scenario = make_multiple_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    candidate_ids = {
        suspect.id
        for suspect in analysis.final_candidates
    }

    assert candidate_ids == {
        "S1",
        "S2",
    }


def test_pipeline_multiple_csp_solutions():
    scenario = make_multiple_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert len(
        analysis.csp_result.assignments
    ) == 2


def test_pipeline_no_solution_status():
    scenario = make_no_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.final_status == "NO SOLUTION"


def test_pipeline_no_solution_has_no_candidates():
    scenario = make_no_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.final_candidates == []


def test_pipeline_inconsistent_status():
    scenario = make_inconsistent_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert (
        analysis.final_status
        == "INCONSISTENT SCENARIO"
    )


def test_pipeline_inconsistent_has_contradictions():
    scenario = make_inconsistent_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert (
        analysis.contradiction_report.has_contradictions()
        is True
    )


def test_pipeline_contains_validation_result():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.validation is not None


def test_pipeline_contains_reasoning_report():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert analysis.reasoning_report is not None


def test_pipeline_contains_final_explanation():
    scenario = make_unique_solution_scenario()

    analysis = run_full_analysis(
        scenario
    )

    assert isinstance(
        analysis.reasoning_report.final_explanation,
        str,
    )

    assert len(
        analysis.reasoning_report.final_explanation.strip()
    ) > 0
