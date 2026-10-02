from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.reasoning import (
    generate_reasoning_report,
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
        # S1 satisfies every constraint.
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

        # S3 has no evidence.
    ]

    return Scenario(
        id="REASONING_UNIQUE",
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
        # S1 satisfies every constraint.
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

        # S2 also satisfies every constraint.
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

        # S3 has access but no presence.
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
        id="REASONING_MULTIPLE",
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
        id="REASONING_NONE",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_reasoning_report_contains_initial_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.initial_set == {
        "S1",
        "S2",
        "S3",
    }


def test_reasoning_report_contains_access_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.access_set == {
        "S1",
        "S2",
    }


def test_reasoning_report_contains_presence_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.presence_set == {
        "S1",
    }


def test_reasoning_report_contains_availability_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.availability_set == {
        "S1",
        "S2",
        "S3",
    }


def test_reasoning_report_contains_reachability_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.reachability_set == {
        "S1",
        "S2",
    }


def test_reasoning_report_contains_possible_set():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.possible_set == {
        "S1",
    }


def test_reasoning_report_classifies_unique_solution():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.final_status == "UNIQUE SOLUTION"


def test_reasoning_report_classifies_multiple_solutions():
    scenario = make_multiple_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.possible_set == {
        "S1",
        "S2",
    }

    assert report.final_status == "MULTIPLE SOLUTIONS"


def test_reasoning_report_classifies_no_solution():
    scenario = make_no_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert report.possible_set == set()

    assert report.final_status == "NO SOLUTION"


def test_reasoning_steps_are_generated():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert len(
        report.reasoning_steps
    ) == 5


def test_reasoning_steps_have_correct_numbers():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    numbers = [
        step.number
        for step in report.reasoning_steps
    ]

    assert numbers == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_reasoning_steps_have_required_fields():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    for step in report.reasoning_steps:
        assert isinstance(
            step.number,
            int,
        )

        assert isinstance(
            step.title,
            str,
        )

        assert isinstance(
            step.mathematical_expression,
            str,
        )

        assert isinstance(
            step.explanation,
            str,
        )

        assert isinstance(
            step.remaining_suspects,
            set,
        )


def test_reasoning_steps_show_progressive_filtering():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    remaining_sets = [
        step.remaining_suspects
        for step in report.reasoning_steps
    ]

    assert remaining_sets[0] == {
        "S1",
        "S2",
    }

    assert remaining_sets[1] == {
        "S1",
    }

    assert remaining_sets[2] == {
        "S1",
    }

    assert remaining_sets[3] == {
        "S1",
    }

    assert remaining_sets[4] == {
        "S1",
    }


def test_suspect_reasons_cover_all_suspects():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    suspect_ids = {
        reason.suspect_id
        for reason in report.suspect_reasons
    }

    assert suspect_ids == {
        "S1",
        "S2",
        "S3",
    }


def test_surviving_suspect_is_candidate():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    s1_reason = next(
        reason
        for reason in report.suspect_reasons
        if reason.suspect_id == "S1"
    )

    assert s1_reason.status == "CANDIDATE"

    assert len(
        s1_reason.reasons
    ) == 4


def test_eliminated_suspects_are_marked_eliminated():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    eliminated = {
        reason.suspect_id
        for reason in report.suspect_reasons
        if reason.status == "ELIMINATED"
    }

    assert eliminated == {
        "S2",
        "S3",
    }


def test_every_suspect_reason_has_explanation():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    for reason in report.suspect_reasons:
        assert isinstance(
            reason.suspect_name,
            str,
        )

        assert isinstance(
            reason.status,
            str,
        )

        assert isinstance(
            reason.reasons,
            list,
        )

        assert len(
            reason.reasons
        ) == 4


def test_final_explanation_is_generated():
    scenario = make_unique_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    assert isinstance(
        report.final_explanation,
        str,
    )

    assert len(
        report.final_explanation.strip()
    ) > 0


def test_multiple_solution_has_candidate_reasons():
    scenario = make_multiple_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    candidate_ids = {
        reason.suspect_id
        for reason in report.suspect_reasons
        if reason.status == "CANDIDATE"
    }

    assert candidate_ids == {
        "S1",
        "S2",
    }


def test_no_solution_has_no_candidate_reasons():
    scenario = make_no_solution_scenario()

    report = generate_reasoning_report(
        scenario
    )

    candidate_ids = {
        reason.suspect_id
        for reason in report.suspect_reasons
        if reason.status == "CANDIDATE"
    }

    assert candidate_ids == set()
