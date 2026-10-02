from dataclasses import dataclass, field

from data.models import (
    Scenario,
    Evidence
)


# ============================================================
# CONTRADICTION
# ============================================================

@dataclass
class Contradiction:

    contradiction_type: str

    description: str

    evidence_ids: list[str] = field(
        default_factory=list
    )

    severity: str = "ERROR"

    def __str__(self) -> str:

        return (
            f"[{self.severity}] "
            f"{self.contradiction_type}: "
            f"{self.description}"
        )


# ============================================================
# CONTRADICTION REPORT
# ============================================================

@dataclass
class ContradictionReport:

    contradictions: list[Contradiction] = field(
        default_factory=list
    )

    checked_evidence: int = 0

    checked_connections: int = 0

    def has_contradictions(self) -> bool:

        return len(
            self.contradictions
        ) > 0

    def count(self) -> int:

        return len(
            self.contradictions
        )


# ============================================================
# TIME CONVERSION
# ============================================================

def time_to_minutes(
    time_string: str
) -> int:

    try:

        hours, minutes = map(
            int,
            time_string.split(":")
        )

        if not (
            0 <= hours <= 23
            and 0 <= minutes <= 59
        ):

            raise ValueError

        return (
            hours * 60
            + minutes
        )

    except (ValueError, AttributeError):

        raise ValueError(
            f"Invalid time format: "
            f"{time_string}"
        )


# ============================================================
# CHECK TIME FORMAT
# ============================================================

def check_evidence_times(
    scenario: Scenario,
    report: ContradictionReport
):

    for evidence in scenario.evidence:

        if evidence.time is None:

            continue

        try:

            time_to_minutes(
                evidence.time
            )

        except ValueError:

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID TIME"
                    ),

                    description=(
                        f"Evidence {evidence.id} "
                        f"contains invalid time "
                        f"'{evidence.time}'."
                    ),

                    evidence_ids=[
                        evidence.id
                    ]
                )
            )


# ============================================================
# CHECK CRIME TIME
# ============================================================

def check_crime_time(
    scenario: Scenario,
    report: ContradictionReport
):

    try:

        start = time_to_minutes(
            scenario.crime.start_time
        )

        end = time_to_minutes(
            scenario.crime.end_time
        )

        if start > end:

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID CRIME INTERVAL"
                    ),

                    description=(
                        "Crime start time "
                        "occurs after crime "
                        "end time."
                    ),

                    evidence_ids=[]
                )
            )

    except ValueError as error:

        report.contradictions.append(

            Contradiction(

                contradiction_type=(
                    "INVALID CRIME TIME"
                ),

                description=str(error),

                evidence_ids=[]
            )
        )


# ============================================================
# CHECK LOCATION CONFLICTS
# ============================================================

def check_location_conflicts(
    scenario: Scenario,
    report: ContradictionReport
):

    # --------------------------------------------------------
    # Group evidence by:
    #
    # suspect + time
    #
    # --------------------------------------------------------

    location_claims = {}

    for evidence in scenario.evidence:

        if (
            evidence.suspect_id is None
            or evidence.location_id is None
            or evidence.time is None
        ):

            continue

        key = (
            evidence.suspect_id,
            evidence.time
        )

        if key not in location_claims:

            location_claims[key] = []

        location_claims[key].append(
            evidence
        )

    # --------------------------------------------------------
    # Compare location claims
    # --------------------------------------------------------

    for key, evidence_list in (
        location_claims.items()
    ):

        suspect_id, time = key

        locations = {}

        for evidence in evidence_list:

            location = evidence.location_id

            if location not in locations:

                locations[location] = []

            locations[location].append(
                evidence
            )

        # More than one distinct location
        if len(locations) > 1:

            evidence_ids = [

                evidence.id

                for evidence in evidence_list
            ]

            location_text = ", ".join(
                locations.keys()
            )

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "LOCATION CONFLICT"
                    ),

                    description=(
                        f"Suspect {suspect_id} "
                        f"is assigned to multiple "
                        f"locations ({location_text}) "
                        f"at {time}."
                    ),

                    evidence_ids=evidence_ids
                )
            )


# ============================================================
# CHECK DUPLICATE EVIDENCE IDs
# ============================================================

def check_duplicate_evidence_ids(
    scenario: Scenario,
    report: ContradictionReport
):

    seen = {}

    for evidence in scenario.evidence:

        if evidence.id in seen:

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "DUPLICATE EVIDENCE ID"
                    ),

                    description=(
                        f"Evidence ID "
                        f"{evidence.id} "
                        f"appears more than once."
                    ),

                    evidence_ids=[
                        evidence.id
                    ]
                )
            )

        else:

            seen[evidence.id] = evidence


# ============================================================
# CHECK CONNECTIONS
# ============================================================

def check_connections(
    scenario: Scenario,
    report: ContradictionReport
):

    report.checked_connections = (
        len(scenario.connections)
    )

    location_ids = {
        location.id
        for location in scenario.locations
    }

    for connection in scenario.connections:

        # ----------------------------------------------------
        # Negative travel time
        # ----------------------------------------------------

        if connection.travel_time < 0:

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID TRAVEL TIME"
                    ),

                    description=(
                        f"Connection "
                        f"{connection.id} "
                        f"has negative travel "
                        f"time."
                    ),

                    evidence_ids=[]
                )
            )

        # ----------------------------------------------------
        # Unknown source
        # ----------------------------------------------------

        if (
            connection.from_location_id
            not in location_ids
        ):

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID GRAPH EDGE"
                    ),

                    description=(
                        f"Connection "
                        f"{connection.id} "
                        f"references unknown "
                        f"source location "
                        f"{connection.from_location_id}."
                    ),

                    evidence_ids=[]
                )
            )

        # ----------------------------------------------------
        # Unknown destination
        # ----------------------------------------------------

        if (
            connection.to_location_id
            not in location_ids
        ):

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID GRAPH EDGE"
                    ),

                    description=(
                        f"Connection "
                        f"{connection.id} "
                        f"references unknown "
                        f"destination location "
                        f"{connection.to_location_id}."
                    ),

                    evidence_ids=[]
                )
            )


# ============================================================
# CHECK SUSPECT REFERENCES
# ============================================================

def check_evidence_references(
    scenario: Scenario,
    report: ContradictionReport
):

    suspect_ids = {
        suspect.id
        for suspect in scenario.suspects
    }

    location_ids = {
        location.id
        for location in scenario.locations
    }

    for evidence in scenario.evidence:

        # ----------------------------------------------------
        # Unknown suspect
        # ----------------------------------------------------

        if (
            evidence.suspect_id is not None
            and evidence.suspect_id
            not in suspect_ids
        ):

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID EVIDENCE REFERENCE"
                    ),

                    description=(
                        f"Evidence "
                        f"{evidence.id} "
                        f"references unknown "
                        f"suspect "
                        f"{evidence.suspect_id}."
                    ),

                    evidence_ids=[
                        evidence.id
                    ]
                )
            )

        # ----------------------------------------------------
        # Unknown location
        # ----------------------------------------------------

        if (
            evidence.location_id is not None
            and evidence.location_id
            not in location_ids
        ):

            report.contradictions.append(

                Contradiction(

                    contradiction_type=(
                        "INVALID EVIDENCE LOCATION"
                    ),

                    description=(
                        f"Evidence "
                        f"{evidence.id} "
                        f"references unknown "
                        f"location "
                        f"{evidence.location_id}."
                    ),

                    evidence_ids=[
                        evidence.id
                    ]
                )
            )


# ============================================================
# MAIN CONTRADICTION DETECTOR
# ============================================================

def detect_contradictions(
    scenario: Scenario
) -> ContradictionReport:

    report = ContradictionReport()

    report.checked_evidence = (
        len(scenario.evidence)
    )

    # --------------------------------------------------------
    # Run all checks
    # --------------------------------------------------------

    check_evidence_times(
        scenario,
        report
    )

    check_crime_time(
        scenario,
        report
    )

    check_location_conflicts(
        scenario,
        report
    )

    check_duplicate_evidence_ids(
        scenario,
        report
    )

    check_connections(
        scenario,
        report
    )

    check_evidence_references(
        scenario,
        report
    )

    return report


# ============================================================
# PRINT REPORT
# ============================================================

def print_contradiction_report(
    report: ContradictionReport
):

    print("\n")
    print("=" * 65)
    print("CONTRADICTION DETECTION REPORT")
    print("=" * 65)

    print(
        "\nEvidence checked:",
        report.checked_evidence
    )

    print(
        "Connections checked:",
        report.checked_connections
    )

    print(
        "Contradictions found:",
        report.count()
    )

    if not report.has_contradictions():

        print(
            "\n✓ NO CONTRADICTIONS DETECTED"
        )

        return

    print(
        "\nCONTRADICTIONS:"
    )

    for index, contradiction in enumerate(
        report.contradictions,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{contradiction}"
        )

        if contradiction.evidence_ids:

            print(
                "   Evidence:",
                ", ".join(
                    contradiction.evidence_ids
                )
            )