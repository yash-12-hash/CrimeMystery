
from data.models import (
    Connection,
    Constraint,
    Crime,
    Evidence,
    Location,
    Scenario,
    Suspect,
)
from engine.constraints import (
    classify_solution,
    find_possible_suspects,
    has_access,
    has_valid_alibi,
    is_available,
    is_present,
    can_reach_crime_scene,
    satisfies_all_constraints,
    time_to_minutes,
)


def make_scenario(
    evidence,
    connections=None,
):
    suspects = [
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
        Suspect("S3", "Rohan"),
    ]

    locations = [
        Location("L1", "Computer Laboratory"),
        Location("L2", "Library"),
        Location("L3", "College Gate"),
    ]

    return Scenario(
        id="TEST-01",
        crime=Crime(
            crime_type="Laptop Theft",
            location_id="L1",
            start_time="14:25",
            end_time="14:35",
        ),
        suspects=suspects,
        locations=locations,
        connections=connections or [
            Connection("P1", "L2", "L1", 2),
            Connection("P2", "L3", "L2", 3),
        ],
        evidence=evidence,
        constraints=[
            Constraint("C1", "Present at crime location"),
            Constraint("C2", "Has access"),
            Constraint("C3", "No valid alibi"),
            Constraint("C4", "Reachable"),
        ],
    )


def evidence_item(
    evidence_id,
    evidence_type,
    suspect_id,
    location_id,
    time,
    statement="test evidence",
):
    return Evidence(
        id=evidence_id,
        evidence_type=evidence_type,
        suspect_id=suspect_id,
        location_id=location_id,
        time=time,
        statement=statement,
    )


def test_time_to_minutes():
    assert time_to_minutes("00:00") == 0
    assert time_to_minutes("14:25") == 865
    assert time_to_minutes("23:59") == 1439


def test_is_present_requires_evidence_during_crime_interval():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
    ])

    assert is_present(scenario.suspects[0], scenario) is True

    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:20"),
    ])

    assert is_present(scenario.suspects[0], scenario) is False


def test_has_access_requires_access_permission_at_crime_location():
    scenario = make_scenario([
        evidence_item("E1", "Access Permission", "S1", "L1", None),
    ])

    assert has_access(scenario.suspects[0], scenario) is True

    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
    ])

    assert has_access(scenario.suspects[0], scenario) is False


def test_has_valid_alibi_detects_other_location_during_crime():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L2", "14:30"),
    ])

    assert has_valid_alibi(scenario.suspects[0], scenario) is True
    assert is_available(scenario.suspects[0], scenario) is False


def test_is_available_when_no_conflicting_alibi():
    scenario = make_scenario([
        evidence_item("E1", "Access Permission", "S1", "L1", None),
    ])

    assert is_available(scenario.suspects[0], scenario) is True


def test_reachability_same_location_is_true_when_present():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
    ])

    assert can_reach_crime_scene(scenario.suspects[0], scenario) is True


def test_reachability_uses_available_time():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L2", "14:20"),
    ])

    assert can_reach_crime_scene(scenario.suspects[0], scenario) is True


def test_reachability_fails_when_travel_time_exceeds_available_time():
    scenario = make_scenario(
        [
            evidence_item("E1", "CCTV", "S1", "L3", "14:24"),
        ],
        connections=[
            Connection("P1", "L3", "L2", 3),
            Connection("P2", "L2", "L1", 2),
        ],
    )

    assert can_reach_crime_scene(scenario.suspects[0], scenario) is False


def test_reachability_fails_when_no_location_evidence_exists():
    scenario = make_scenario([
        evidence_item("E1", "Access Permission", "S1", "L1", None),
    ])

    assert can_reach_crime_scene(scenario.suspects[0], scenario) is False


def test_satisfies_all_constraints_requires_every_constraint():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
        evidence_item("E2", "Access Permission", "S1", "L1", None),
    ])

    suspect = scenario.suspects[0]

    assert satisfies_all_constraints(suspect, scenario) is True


def test_satisfies_all_constraints_rejects_valid_alibi():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
        evidence_item("E2", "Access Permission", "S1", "L1", None),
        evidence_item("E3", "CCTV", "S1", "L2", "14:30"),
    ])

    assert satisfies_all_constraints(scenario.suspects[0], scenario) is False


def test_find_possible_suspects_returns_suspect_objects():
    scenario = make_scenario([
        evidence_item("E1", "CCTV", "S1", "L1", "14:30"),
        evidence_item("E2", "Access Permission", "S1", "L1", None),
    ])

    possible = find_possible_suspects(scenario)

    assert [suspect.id for suspect in possible] == ["S1"]


def test_classify_solution():
    assert classify_solution([]) == "NO SOLUTION"
    assert classify_solution([Suspect("S1", "Rahul")]) == "UNIQUE SOLUTION"
    assert classify_solution([
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
    ]) == "MULTIPLE SOLUTIONS"
