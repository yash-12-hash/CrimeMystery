import networkx as nx

from data.models import (
    Scenario,
    Suspect,
    Connection
)


# ============================================================
# CREATE CRIME SCENE GRAPH
# ============================================================

def build_scene_graph(
    scenario: Scenario
) -> nx.Graph:

    graph = nx.Graph()

    # --------------------------------------------------------
    # Add vertices
    # --------------------------------------------------------

    for location in scenario.locations:

        graph.add_node(
            location.id,
            name=location.name
        )

    # --------------------------------------------------------
    # Add edges
    # --------------------------------------------------------

    for connection in scenario.connections:

        graph.add_edge(
            connection.from_location_id,
            connection.to_location_id,
            travel_time=connection.travel_time,
            connection_id=connection.id
        )

    return graph


# ============================================================
# TIME CONVERSION
# ============================================================

def time_to_minutes(
    time_string: str
) -> int:

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


# ============================================================
# AVAILABLE TIME
# ============================================================

def calculate_available_time(
    evidence_time: str,
    crime_time: str
) -> int:

    evidence_minutes = time_to_minutes(
        evidence_time
    )

    crime_minutes = time_to_minutes(
        crime_time
    )

    return crime_minutes - evidence_minutes


# ============================================================
# SHORTEST PATH
# ============================================================

def get_shortest_path(
    scenario: Scenario,
    source_location: str,
    target_location: str
) -> tuple[list[str] | None, float]:

    graph = build_scene_graph(
        scenario
    )

    # Same location
    if source_location == target_location:

        return [source_location], 0

    # Check whether both locations exist
    if (
        source_location not in graph
        or target_location not in graph
    ):

        return None, float("inf")

    # Check connectivity
    if not nx.has_path(
        graph,
        source_location,
        target_location
    ):

        return None, float("inf")

    path = nx.shortest_path(
        graph,
        source=source_location,
        target=target_location,
        weight="travel_time"
    )

    distance = nx.shortest_path_length(
        graph,
        source=source_location,
        target=target_location,
        weight="travel_time"
    )

    return path, distance


# ============================================================
# CHECK REACHABILITY
# ============================================================

def is_location_reachable(
    scenario: Scenario,
    source_location: str,
    target_location: str,
    available_time: int
) -> bool:

    path, travel_time = get_shortest_path(
        scenario,
        source_location,
        target_location
    )

    if path is None:

        return False

    return travel_time <= available_time


# ============================================================
# GET SUSPECT'S KNOWN LOCATION
# ============================================================

def get_latest_known_location(
    suspect: Suspect,
    scenario: Scenario
) -> tuple[str | None, str | None]:

    suspect_evidence = []

    for evidence in scenario.evidence:

        if (
            evidence.suspect_id == suspect.id
            and evidence.location_id is not None
            and evidence.time is not None
        ):

            suspect_evidence.append(
                evidence
            )

    if not suspect_evidence:

        return None, None

    # Sort according to time
    suspect_evidence.sort(
        key=lambda evidence:
        time_to_minutes(evidence.time)
    )

    latest = suspect_evidence[-1]

    return (
        latest.location_id,
        latest.time
    )


# ============================================================
# SUSPECT REACHABILITY
# ============================================================

def can_suspect_reach_crime_scene(
    suspect: Suspect,
    scenario: Scenario
) -> bool:

    location_id, evidence_time = (
        get_latest_known_location(
            suspect,
            scenario
        )
    )

    if (
        location_id is None
        or evidence_time is None
    ):

        return False

    crime_location = (
        scenario.crime.location_id
    )

    available_time = (
        calculate_available_time(
            evidence_time,
            scenario.crime.start_time
        )
    )

    # If evidence occurs after crime starts,
    # suspect cannot travel backwards in time.
    if available_time < 0:

        return False

    return is_location_reachable(
        scenario,
        location_id,
        crime_location,
        available_time
    )


# ============================================================
# DETAILED REACHABILITY ANALYSIS
# ============================================================

def get_reachability_analysis(
    suspect: Suspect,
    scenario: Scenario
) -> dict:

    location_id, evidence_time = (
        get_latest_known_location(
            suspect,
            scenario
        )
    )

    crime_location = (
        scenario.crime.location_id
    )

    if (
        location_id is None
        or evidence_time is None
    ):

        return {
            "source": None,
            "source_time": None,
            "destination": crime_location,
            "available_time": 0,
            "path": None,
            "travel_time": float("inf"),
            "reachable": False
        }

    available_time = (
        calculate_available_time(
            evidence_time,
            scenario.crime.start_time
        )
    )

    path, travel_time = (
        get_shortest_path(
            scenario,
            location_id,
            crime_location
        )
    )

    reachable = (
        available_time >= 0
        and path is not None
        and travel_time <= available_time
    )

    return {
        "source": location_id,
        "source_time": evidence_time,
        "destination": crime_location,
        "available_time": available_time,
        "path": path,
        "travel_time": travel_time,
        "reachable": reachable
    }


# ============================================================
# GRAPH SUMMARY
# ============================================================

def get_graph_summary(
    scenario: Scenario
) -> dict:

    graph = build_scene_graph(
        scenario
    )

    return {
        "vertices": list(
            graph.nodes
        ),

        "edges": list(
            graph.edges
        ),

        "number_of_vertices": (
            graph.number_of_nodes()
        ),

        "number_of_edges": (
            graph.number_of_edges()
        )
    }