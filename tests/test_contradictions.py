from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from engine.contradictions import (
    detect_contradictions,
)


def make_base_scenario():
    suspects = [
        Suspect("S1", "Rahul"),
        Suspect("S2", "Aditya"),
    ]

    locations = [
        Location("L1", "Computer Laboratory"),
        Location("L2", "Library"),
        Location("L3", "College Gate"),
    ]

    connections = [
        Connection(
            "P1",
            "L1",
            "L2",
            2,
        ),
        Connection(
            "P2",
            "L2",
            "L3",
            3,
        ),
    ]

    crime = Crime(
        crime_type="Laptop Theft",
        location_id="L1",
        start_time="14:25",
        end_time="14:35",
    )

    evidence = [
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:25",
            "Rahul was seen in the computer laboratory.",
        ),
        Evidence(
            "E2",
            "Access Permission",
            "S1",
            "L1",
            None,
            "Rahul has access to the laboratory.",
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
        id="CONTRADICTION_TEST",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_valid_scenario_has_no_contradictions():
    scenario = make_base_scenario()

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is False
    assert report.count() == 0


def test_report_checks_evidence():
    scenario = make_base_scenario()

    report = detect_contradictions(scenario)

    assert report.checked_evidence == len(
        scenario.evidence
    )


def test_report_checks_connections():
    scenario = make_base_scenario()

    report = detect_contradictions(scenario)

    assert report.checked_connections == len(
        scenario.connections
    )


def test_duplicate_evidence_ids_are_detected():
    scenario = make_base_scenario()

    duplicate_evidence = Evidence(
        "E1",
        "CCTV",
        "S2",
        "L2",
        "14:20",
        "Duplicate evidence ID.",
    )

    scenario.evidence.append(
        duplicate_evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    contradiction_types = {
        contradiction.contradiction_type
        for contradiction in report.contradictions
    }

    assert "DUPLICATE EVIDENCE ID" in contradiction_types


def test_unknown_suspect_reference_is_detected():
    scenario = make_base_scenario()

    invalid_evidence = Evidence(
        "E3",
        "CCTV",
        "S99",
        "L1",
        "14:25",
        "Evidence references an unknown suspect.",
    )

    scenario.evidence.append(
        invalid_evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    descriptions = [
        contradiction.description
        for contradiction in report.contradictions
    ]

    assert any(
        "suspect" in description.lower()
        for description in descriptions
    )


def test_unknown_location_reference_is_detected():
    scenario = make_base_scenario()

    invalid_evidence = Evidence(
        "E3",
        "CCTV",
        "S1",
        "L99",
        "14:25",
        "Evidence references an unknown location.",
    )

    scenario.evidence.append(
        invalid_evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    descriptions = [
        contradiction.description
        for contradiction in report.contradictions
    ]

    assert any(
        "location" in description.lower()
        for description in descriptions
    )


def test_negative_travel_time_is_detected():
    scenario = make_base_scenario()

    scenario.connections.append(
        Connection(
            "P_BAD",
            "L1",
            "L2",
            -5,
        )
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    descriptions = [
        contradiction.description
        for contradiction in report.contradictions
    ]

    assert any(
        "travel" in description.lower()
        for description in descriptions
    )


def test_unknown_connection_source_is_detected():
    scenario = make_base_scenario()

    scenario.connections.append(
        Connection(
            "P_BAD",
            "L99",
            "L1",
            5,
        )
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    descriptions = [
        contradiction.description
        for contradiction in report.contradictions
    ]

    assert any(
        "location" in description.lower()
        or "source" in description.lower()
        for description in descriptions
    )


def test_unknown_connection_destination_is_detected():
    scenario = make_base_scenario()

    scenario.connections.append(
        Connection(
            "P_BAD",
            "L1",
            "L99",
            5,
        )
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    descriptions = [
        contradiction.description
        for contradiction in report.contradictions
    ]

    assert any(
        "location" in description.lower()
        or "destination" in description.lower()
        for description in descriptions
    )


def test_invalid_evidence_time_is_detected():
    scenario = make_base_scenario()

    invalid_evidence = Evidence(
        "E3",
        "CCTV",
        "S1",
        "L1",
        "invalid-time",
        "Invalid timestamp.",
    )

    scenario.evidence.append(
        invalid_evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    contradiction_types = {
        contradiction.contradiction_type
        for contradiction in report.contradictions
    }

    assert "INVALID TIME" in contradiction_types


def test_evidence_with_valid_time_format_is_not_itself_a_contradiction():
    scenario = make_base_scenario()

    evidence = Evidence(
        "E3",
        "CCTV",
        "S1",
        "L1",
        "15:30",
        "Evidence recorded after the crime interval.",
    )

    scenario.evidence.append(
        evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is False


def test_contradiction_count_matches_list_length():
    scenario = make_base_scenario()

    scenario.connections.append(
        Connection(
            "P_BAD",
            "L1",
            "L2",
            -10,
        )
    )

    report = detect_contradictions(scenario)

    assert report.count() == len(
        report.contradictions
    )


def test_contradictions_contain_required_fields():
    scenario = make_base_scenario()

    scenario.connections.append(
        Connection(
            "P_BAD",
            "L1",
            "L2",
            -1,
        )
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    for contradiction in report.contradictions:
        assert contradiction.contradiction_type
        assert contradiction.description
        assert contradiction.severity is not None


def test_location_conflict_is_detected():
    scenario = make_base_scenario()

    conflicting_evidence = Evidence(
        "E3",
        "CCTV",
        "S1",
        "L2",
        "14:25",
        "Rahul was also seen in the library.",
    )

    scenario.evidence.append(
        conflicting_evidence
    )

    report = detect_contradictions(scenario)

    assert report.has_contradictions() is True

    contradiction_types = {
        contradiction.contradiction_type
        for contradiction in report.contradictions
    }

    assert "LOCATION CONFLICT" in contradiction_types