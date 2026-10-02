from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.logic import (
    build_rules,
    evaluate_suspect_logic,
    find_logically_possible_suspects,
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
        # S1 satisfies all four predicates.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:30",
            "Rahul was seen in the computer laboratory.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has access to the computer laboratory.",
        ),

        # S2 is present and has access,
        # but has a valid alibi.
        Evidence(
            "E3",
            "CCTV",
            "S2",
            "L1",
            "14:30",
            "Aditya was seen in the computer laboratory.",
        ),
        Evidence(
            "E4",
            "Access Permission",
            "S2",
            "L1",
            None,
            "Aditya has access to the computer laboratory.",
        ),
        Evidence(
            "E5",
            "CCTV",
            "S2",
            "L2",
            "14:30",
            "Aditya was also seen in the library.",
        ),

        # S3 has access and can reach the scene,
        # but there is no evidence that S3 was present
        # at the crime location during the crime.
        Evidence(
            "E6",
            "Access Permission",
            "S3",
            "L1",
            None,
            "Rohan has access to the computer laboratory.",
        ),
        Evidence(
            "E7",
            "CCTV",
            "S3",
            "L2",
            "14:20",
            "Rohan was seen in the library.",
        ),

        # S4 has no access and no presence at the crime scene.
        Evidence(
            "E8",
            "CCTV",
            "S4",
            "L3",
            "14:20",
            "Sameer was seen near the college gate.",
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
        id="LOGIC_TEST",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_build_rules_creates_four_rules():
    scenario = make_scenario()

    rules = build_rules(scenario)

    assert len(rules) == 4


def test_build_rules_contains_expected_predicates():
    scenario = make_scenario()

    rules = build_rules(scenario)

    rule_names = {
        rule.name
        for rule in rules
    }

    assert rule_names == {
        "Guilty implies presence",
        "Guilty implies access",
        "Guilty implies availability",
        "Guilty implies reachability",
    }


def test_rules_have_guilty_as_antecedent():
    scenario = make_scenario()

    rules = build_rules(scenario)

    for rule in rules:
        assert rule.antecedent.name == "Guilty"


def test_fully_valid_suspect_satisfies_all_logic():
    scenario = make_scenario()

    suspect = scenario.suspects[0]

    result = evaluate_suspect_logic(
        suspect,
        scenario,
    )

    assert result.satisfied is True
    assert result.failed_predicates == []


def test_valid_suspect_has_all_required_facts():
    scenario = make_scenario()

    suspect = scenario.suspects[0]

    result = evaluate_suspect_logic(
        suspect,
        scenario,
    )

    fact_names = {
        fact.name
        for fact in result.facts
    }

    assert "Present" in fact_names
    assert "Access" in fact_names
    assert "Available" in fact_names
    assert "Reachable" in fact_names


def test_suspect_with_alibi_fails_available_predicate():
    scenario = make_scenario()

    suspect = scenario.suspects[1]

    result = evaluate_suspect_logic(
        suspect,
        scenario,
    )

    assert result.satisfied is False

    failed_names = {
        predicate.name
        for predicate in result.failed_predicates
    }

    assert "Available" in failed_names


def test_suspect_without_presence_fails_present_predicate():
    scenario = make_scenario()

    suspect = scenario.suspects[2]

    result = evaluate_suspect_logic(
        suspect,
        scenario,
    )

    assert result.satisfied is False

    failed_names = {
        predicate.name
        for predicate in result.failed_predicates
    }

    assert "Present" in failed_names


def test_suspect_can_fail_multiple_predicates():
    scenario = make_scenario()

    suspect = scenario.suspects[3]

    result = evaluate_suspect_logic(
        suspect,
        scenario,
    )

    assert result.satisfied is False

    failed_names = {
        predicate.name
        for predicate in result.failed_predicates
    }

    assert "Present" in failed_names
    assert "Access" in failed_names


def test_logical_solver_returns_only_valid_suspect():
    scenario = make_scenario()

    result = find_logically_possible_suspects(
        scenario
    )

    result_ids = {
        suspect.id
        for suspect in result
    }

    assert result_ids == {
        "S1",
    }


def test_logical_solver_returns_suspect_objects():
    scenario = make_scenario()

    result = find_logically_possible_suspects(
        scenario
    )

    assert all(
        isinstance(suspect, Suspect)
        for suspect in result
    )

    assert len(result) == 1
    assert result[0].id == "S1"
    assert result[0].name == "Rahul"