from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)

from graph.scene_graph import (
    build_scene_graph,
    get_reachability_analysis,
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
        Location("L4", "Hostel"),
    ]

    connections = [
        Connection("P1", "L1", "L2", 2),
        Connection("P2", "L2", "L3", 3),
        Connection("P3", "L3", "L4", 4),
    ]

    crime = Crime(
        crime_type="Laptop Theft",
        location_id="L1",
        start_time="14:25",
        end_time="14:35",
    )

    evidence = [
        # S1 is already at the crime scene BEFORE
        # the crime starts.
        #
        # This allows the reachability calculation
        # to determine that S1 can be at L1 at 14:25.
        Evidence(
            "E1",
            "CCTV",
            "S1",
            "L1",
            "14:20",
            "Rahul was seen in the computer laboratory.",
        ),

        # S2 is at L2 at 14:20.
        #
        # L2 -> L1 = 2 minutes.
        # Available time = 14:25 - 14:20 = 5 minutes.
        #
        # Therefore S2 can reach L1.
        Evidence(
            "E2",
            "CCTV",
            "S2",
            "L2",
            "14:20",
            "Aditya was seen in the library.",
        ),

        # S3 is at L4 at 14:20.
        #
        # L4 -> L3 = 4
        # L3 -> L2 = 3
        # L2 -> L1 = 2
        #
        # Total travel time = 9 minutes.
        # Available time = 5 minutes.
        #
        # Therefore S3 cannot reach L1 in time.
        Evidence(
            "E3",
            "CCTV",
            "S3",
            "L4",
            "14:20",
            "Rohan was seen in the hostel.",
        ),

        # S4 has no location evidence.
        Evidence(
            "E4",
            "Access Permission",
            "S4",
            "L1",
            None,
            "Sameer has access to the computer laboratory.",
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
        id="GRAPH_TEST",
        crime=crime,
        suspects=suspects,
        locations=locations,
        connections=connections,
        evidence=evidence,
        constraints=constraints,
    )


def test_build_scene_graph_contains_all_locations():
    scenario = make_scenario()

    graph = build_scene_graph(scenario)

    assert set(graph.nodes) == {
        "L1",
        "L2",
        "L3",
        "L4",
    }


def test_build_scene_graph_contains_all_connections():
    scenario = make_scenario()

    graph = build_scene_graph(scenario)

    assert graph.has_edge("L1", "L2")
    assert graph.has_edge("L2", "L3")
    assert graph.has_edge("L3", "L4")


def test_graph_edges_have_correct_travel_times():
    scenario = make_scenario()

    graph = build_scene_graph(scenario)

    assert graph["L1"]["L2"]["travel_time"] == 2
    assert graph["L2"]["L3"]["travel_time"] == 3
    assert graph["L3"]["L4"]["travel_time"] == 4


def test_same_location_is_reachable():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[0],
        scenario,
    )

    assert result["source"] == "L1"
    assert result["destination"] == "L1"
    assert result["source_time"] == "14:20"
    assert result["available_time"] == 5
    assert result["travel_time"] == 0
    assert result["path"] == ["L1"]
    assert result["reachable"] is True


def test_short_distance_is_reachable():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[1],
        scenario,
    )

    assert result["source"] == "L2"
    assert result["destination"] == "L1"
    assert result["source_time"] == "14:20"
    assert result["available_time"] == 5
    assert result["travel_time"] == 2
    assert result["reachable"] is True


def test_shortest_path_is_returned():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[1],
        scenario,
    )

    assert result["path"] == [
        "L2",
        "L1",
    ]


def test_long_distance_is_not_reachable():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[2],
        scenario,
    )

    assert result["source"] == "L4"
    assert result["destination"] == "L1"
    assert result["available_time"] == 5
    assert result["travel_time"] == 9
    assert result["reachable"] is False


def test_long_distance_returns_correct_path():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[2],
        scenario,
    )

    assert result["path"] == [
        "L4",
        "L3",
        "L2",
        "L1",
    ]


def test_no_location_evidence_is_not_reachable():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[3],
        scenario,
    )

    assert result["source"] is None
    assert result["source_time"] is None
    assert result["destination"] == "L1"
    assert result["available_time"] == 0
    assert result["path"] is None
    assert result["travel_time"] == float("inf")
    assert result["reachable"] is False


def test_reachability_analysis_contains_expected_keys():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[1],
        scenario,
    )

    assert set(result.keys()) == {
        "source",
        "source_time",
        "destination",
        "available_time",
        "path",
        "travel_time",
        "reachable",
    }


def test_reachability_requires_travel_time_within_available_time():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[1],
        scenario,
    )

    assert result["travel_time"] <= result["available_time"]
    assert result["reachable"] is True


def test_reachability_rejects_travel_time_above_available_time():
    scenario = make_scenario()

    result = get_reachability_analysis(
        scenario.suspects[2],
        scenario,
    )

    assert result["travel_time"] > result["available_time"]
    assert result["reachable"] is False