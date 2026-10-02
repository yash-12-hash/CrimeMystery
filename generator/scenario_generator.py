import random
from dataclasses import dataclass

from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario
)

from engine.constraints import (
    find_possible_suspects,
    classify_solution
)

from engine.contradictions import (
    detect_contradictions
)

from engine.csp_solver import (
    solve_crime_csp,
    get_csp_suspects
)


# ============================================================
# CONSTANT DATA
# ============================================================

SUSPECT_NAMES = [
    "Rahul",
    "Aditya",
    "Rohan",
    "Sameer",
    "Arjun",
    "Karan",
    "Vivek",
    "Nikhil",
    "Aman",
    "Sahil"
]


LOCATION_NAMES = [
    "Computer Laboratory",
    "Library",
    "College Gate",
    "Hostel",
    "Parking Area",
    "Seminar Hall",
    "Research Laboratory",
    "Faculty Office",
    "Cafeteria",
    "Workshop"
]


CRIME_TYPES = [
    "Laptop Theft",
    "Equipment Theft",
    "Document Theft",
    "Exam Paper Theft",
    "Research Material Theft",
    "USB Drive Theft",
    "Project File Theft"
]


# ============================================================
# GENERATOR CONFIGURATION
# ============================================================

@dataclass
class GeneratorConfig:

    min_suspects: int = 4

    max_suspects: int = 6

    min_locations: int = 4

    max_locations: int = 6

    max_attempts: int = 100

    add_access_decoy: bool = True


# ============================================================
# SCENARIO GENERATOR
# ============================================================

class ScenarioGenerator:

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        seed: int | None = None
    ):

        self.config = (
            config
            if config is not None
            else GeneratorConfig()
        )

        self.random = random.Random(seed)

        self.scenario_counter = 0

    # ========================================================
    # SCENARIO ID
    # ========================================================

    def generate_scenario_id(self) -> str:

        self.scenario_counter += 1

        return (
            f"GEN-{self.scenario_counter:03d}"
        )

    # ========================================================
    # SUSPECT GENERATION
    # ========================================================

    def generate_suspects(self) -> list[Suspect]:

        number_of_suspects = self.random.randint(
            self.config.min_suspects,
            self.config.max_suspects
        )

        selected_names = self.random.sample(
            SUSPECT_NAMES,
            number_of_suspects
        )

        suspects = []

        for index, name in enumerate(
            selected_names,
            start=1
        ):

            suspects.append(
                Suspect(
                    id=f"S{index}",
                    name=name
                )
            )

        return suspects

    # ========================================================
    # LOCATION GENERATION
    # ========================================================

    def generate_locations(self) -> list[Location]:

        number_of_locations = self.random.randint(
            self.config.min_locations,
            self.config.max_locations
        )

        selected_names = self.random.sample(
            LOCATION_NAMES,
            number_of_locations
        )

        locations = []

        for index, name in enumerate(
            selected_names,
            start=1
        ):

            locations.append(
                Location(
                    id=f"L{index}",
                    name=name
                )
            )

        return locations

    # ========================================================
    # GRAPH GENERATION
    # ========================================================

    def generate_connections(
        self,
        locations: list[Location]
    ) -> list[Connection]:

        connections = []

        # ----------------------------------------------------
        # Create a connected chain:
        #
        # L1 <-> L2 <-> L3 <-> L4 ...
        # ----------------------------------------------------

        for index in range(
            len(locations) - 1
        ):

            current_location = locations[index]

            next_location = locations[
                index + 1
            ]

            travel_time = self.random.randint(
                1,
                5
            )

            connections.append(
                Connection(
                    id=(
                        f"P{len(connections) + 1}"
                    ),
                    from_location_id=(
                        current_location.id
                    ),
                    to_location_id=(
                        next_location.id
                    ),
                    travel_time=travel_time
                )
            )

        # ----------------------------------------------------
        # Find additional possible edges
        # ----------------------------------------------------

        possible_edges = []

        for i in range(
            len(locations)
        ):

            for j in range(
                i + 1,
                len(locations)
            ):

                location_a = locations[i].id

                location_b = locations[j].id

                already_exists = False

                for connection in connections:

                    same_direction = (
                        connection.from_location_id
                        == location_a
                        and
                        connection.to_location_id
                        == location_b
                    )

                    reverse_direction = (
                        connection.from_location_id
                        == location_b
                        and
                        connection.to_location_id
                        == location_a
                    )

                    if (
                        same_direction
                        or
                        reverse_direction
                    ):

                        already_exists = True

                        break

                if not already_exists:

                    possible_edges.append(
                        (
                            location_a,
                            location_b
                        )
                    )

        # ----------------------------------------------------
        # Add at most two extra edges
        # ----------------------------------------------------

        self.random.shuffle(
            possible_edges
        )

        extra_edge_count = min(
            2,
            len(possible_edges)
        )

        for edge in possible_edges[
            :extra_edge_count
        ]:

            connections.append(
                Connection(
                    id=(
                        f"P{len(connections) + 1}"
                    ),
                    from_location_id=edge[0],
                    to_location_id=edge[1],
                    travel_time=self.random.randint(
                        1,
                        5
                    )
                )
            )

        return connections

    # ========================================================
    # TIME GENERATION
    # ========================================================

    def generate_crime_time(
        self
    ) -> tuple[str, str, str]:

        start_hour = self.random.randint(
            9,
            17
        )

        start_minute = self.random.choice(
            [
                0,
                5,
                10,
                15,
                20,
                25,
                30,
                35,
                40,
                45,
                50,
                55
            ]
        )

        duration = self.random.choice(
            [
                5,
                10,
                15
            ]
        )

        start_total = (
            start_hour * 60
            + start_minute
        )

        end_total = (
            start_total
            + duration
        )

        end_hour = end_total // 60

        end_minute = end_total % 60

        start_time = (
            f"{start_hour:02d}:"
            f"{start_minute:02d}"
        )

        end_time = (
            f"{end_hour:02d}:"
            f"{end_minute:02d}"
        )

        midpoint_total = (
            start_total
            + duration // 2
        )

        midpoint_hour = (
            midpoint_total // 60
        )

        midpoint_minute = (
            midpoint_total % 60
        )

        crime_time = (
            f"{midpoint_hour:02d}:"
            f"{midpoint_minute:02d}"
        )

        return (
            start_time,
            end_time,
            crime_time
        )

    # ========================================================
    # CRIME GENERATION
    # ========================================================

    def generate_crime(
        self,
        crime_location: Location
    ) -> tuple[Crime, str]:

        (
            start_time,
            end_time,
            crime_time
        ) = self.generate_crime_time()

        crime_type = self.random.choice(
            CRIME_TYPES
        )

        crime = Crime(
            crime_type=crime_type,
            location_id=crime_location.id,
            start_time=start_time,
            end_time=end_time
        )

        return (
            crime,
            crime_time
        )

    # ========================================================
    # EVIDENCE CREATION
    # ========================================================

    def create_evidence(
        self,
        evidence_id: str,
        evidence_type: str,
        suspect_id: str | None,
        location_id: str | None,
        time: str | None,
        statement: str,
        reliability: float = 1.0
    ) -> Evidence:

        return Evidence(
            id=evidence_id,
            evidence_type=evidence_type,
            suspect_id=suspect_id,
            location_id=location_id,
            time=time,
            statement=statement,
            reliability=reliability
        )

    # ========================================================
    # CULPRIT EVIDENCE
    # ========================================================

    def generate_culprit_evidence(
        self,
        culprit: Suspect,
        crime_location: Location,
        crime_time: str
    ) -> list[Evidence]:

        evidence = []

        # ----------------------------------------------------
        # Presence at crime scene
        # ----------------------------------------------------

        evidence.append(
            self.create_evidence(
                evidence_id="E1",
                evidence_type="CCTV",
                suspect_id=culprit.id,
                location_id=crime_location.id,
                time=crime_time,
                statement=(
                    f"{culprit.name} was observed at "
                    f"{crime_location.name} at "
                    f"{crime_time}."
                ),
                reliability=0.95
            )
        )

        # ----------------------------------------------------
        # Access permission
        # ----------------------------------------------------

        evidence.append(
            self.create_evidence(
                evidence_id="E2",
                evidence_type="Access Permission",
                suspect_id=culprit.id,
                location_id=crime_location.id,
                time=None,
                statement=(
                    f"{culprit.name} has authorized "
                    f"access to "
                    f"{crime_location.name}."
                ),
                reliability=1.0
            )
        )

        return evidence

    # ========================================================
    # INNOCENT SUSPECT EVIDENCE
    # ========================================================

    def generate_innocent_evidence(
        self,
        suspect: Suspect,
        location: Location,
        crime_time: str,
        evidence_id: str
    ) -> Evidence:

        return self.create_evidence(
            evidence_id=evidence_id,
            evidence_type="CCTV",
            suspect_id=suspect.id,
            location_id=location.id,
            time=crime_time,
            statement=(
                f"{suspect.name} was observed at "
                f"{location.name} at "
                f"{crime_time}."
            ),
            reliability=0.95
        )

    # ========================================================
    # ACCESS DECOY
    # ========================================================

    def generate_access_decoy(
        self,
        suspect: Suspect,
        crime_location: Location,
        evidence_id: str
    ) -> Evidence:

        return self.create_evidence(
            evidence_id=evidence_id,
            evidence_type="Access Permission",
            suspect_id=suspect.id,
            location_id=crime_location.id,
            time=None,
            statement=(
                f"{suspect.name} also has authorized "
                f"access to "
                f"{crime_location.name}."
            ),
            reliability=1.0
        )

    # ========================================================
    # CONSTRAINT GENERATION
    # ========================================================

    def generate_constraints(
        self
    ) -> list[Constraint]:

        return [

            Constraint(
                id="C1",
                description=(
                    "The culprit must be present "
                    "at the crime location."
                )
            ),

            Constraint(
                id="C2",
                description=(
                    "The culprit must have access "
                    "to the crime location."
                )
            ),

            Constraint(
                id="C3",
                description=(
                    "The culprit must be available "
                    "during the crime."
                )
            ),

            Constraint(
                id="C4",
                description=(
                    "The culprit must be reachable "
                    "from the relevant scene."
                )
            ),

            Constraint(
                id="C5",
                description=(
                    "Exactly one suspect should "
                    "satisfy all required constraints."
                )
            )
        ]

    # ========================================================
    # BUILD CANDIDATE SCENARIO
    # ========================================================

    def build_candidate_scenario(
        self
    ) -> tuple[Scenario, str]:

        # ----------------------------------------------------
        # Suspects
        # ----------------------------------------------------

        suspects = self.generate_suspects()

        # ----------------------------------------------------
        # Locations
        # ----------------------------------------------------

        locations = self.generate_locations()

        # ----------------------------------------------------
        # Connections
        # ----------------------------------------------------

        connections = self.generate_connections(
            locations
        )

        # ----------------------------------------------------
        # Crime location
        #
        # We deliberately choose L1 because it is guaranteed
        # to be part of the generated graph.
        # ----------------------------------------------------

        crime_location = locations[0]

        # ----------------------------------------------------
        # Crime
        # ----------------------------------------------------

        (
            crime,
            crime_time
        ) = self.generate_crime(
            crime_location
        )

        # ----------------------------------------------------
        # Select intended culprit
        # ----------------------------------------------------

        culprit = self.random.choice(
            suspects
        )

        evidence = []

        # ----------------------------------------------------
        # Culprit evidence
        # ----------------------------------------------------

        culprit_evidence = (
            self.generate_culprit_evidence(
                culprit=culprit,
                crime_location=crime_location,
                crime_time=crime_time
            )
        )

        evidence.extend(
            culprit_evidence
        )

        # ----------------------------------------------------
        # Innocent suspects
        # ----------------------------------------------------

        innocent_suspects = [

            suspect

            for suspect in suspects

            if suspect.id != culprit.id
        ]

        # ----------------------------------------------------
        # Locations for alibis
        # ----------------------------------------------------

        alibi_locations = [

            location

            for location in locations

            if location.id
            != crime_location.id
        ]

        self.random.shuffle(
            alibi_locations
        )

        # ----------------------------------------------------
        # Give every innocent suspect an alibi
        # ----------------------------------------------------

        for index, suspect in enumerate(
            innocent_suspects
        ):

            location = alibi_locations[
                index
                % len(alibi_locations)
            ]

            evidence.append(
                self.generate_innocent_evidence(
                    suspect=suspect,
                    location=location,
                    crime_time=crime_time,
                    evidence_id=(
                        f"E{len(evidence) + 1}"
                    )
                )
            )

        # ----------------------------------------------------
        # Optional access decoy
        # ----------------------------------------------------

        if (
            self.config.add_access_decoy
            and innocent_suspects
        ):

            decoy = self.random.choice(
                innocent_suspects
            )

            evidence.append(
                self.generate_access_decoy(
                    suspect=decoy,
                    crime_location=crime_location,
                    evidence_id=(
                        f"E{len(evidence) + 1}"
                    )
                )
            )

        # ----------------------------------------------------
        # Constraints
        # ----------------------------------------------------

        constraints = (
            self.generate_constraints()
        )

        # ----------------------------------------------------
        # Scenario object
        # ----------------------------------------------------

        scenario = Scenario(
            id=self.generate_scenario_id(),
            crime=crime,
            suspects=suspects,
            locations=locations,
            connections=connections,
            evidence=evidence,
            constraints=constraints
        )

        return (
            scenario,
            culprit.id
        )

    # ========================================================
    # VERIFY SCENARIO
    # ========================================================

    def verify_scenario(
        self,
        scenario: Scenario,
        intended_culprit_id: str
    ) -> bool:

        print("\n" + "-" * 70)

        print(
            "VERIFYING GENERATED SCENARIO"
        )

        print("-" * 70)

        print(
            "Scenario:",
            scenario.id
        )

        print(
            "Intended culprit:",
            intended_culprit_id
        )

        # ====================================================
        # FIND INTENDED CULPRIT
        # ====================================================

        culprit = None

        for suspect in scenario.suspects:

            if suspect.id == intended_culprit_id:

                culprit = suspect

                break

        if culprit is None:

            print(
                "✗ Intended culprit does not exist."
            )

            return False

        # ====================================================
        # CONTRADICTION DETECTION
        # ====================================================

        contradiction_report = (
            detect_contradictions(
                scenario
            )
        )

        print(
            "\nContradictions:",
            contradiction_report.count()
        )

        if contradiction_report.has_contradictions():

            print(
                "✗ REJECTED: contradictions found"
            )

            for contradiction in (
                contradiction_report.contradictions
            ):

                print(
                    "  -",
                    contradiction
                )

            return False

        print(
            "✓ No contradictions"
        )

        # ====================================================
        # INDIVIDUAL CONSTRAINT ANALYSIS
        # ====================================================

        from engine.constraints import (
            is_present,
            has_access,
            is_available,
            can_reach_crime_scene
        )

        present = is_present(
            culprit,
            scenario
        )

        access = has_access(
            culprit,
            scenario
        )

        available = is_available(
            culprit,
            scenario
        )

        reachable = can_reach_crime_scene(
            culprit,
            scenario
        )

        print("\n")
        print(
            "INTENDED CULPRIT ANALYSIS"
        )

        print("-" * 70)

        print(
            "Suspect:",
            culprit.id,
            "->",
            culprit.name
        )

        print(
            "Present:",
            present
        )

        print(
            "Access:",
            access
        )

        print(
            "Available:",
            available
        )

        print(
            "Reachable:",
            reachable
        )

        # ====================================================
        # SHOW CULPRIT EVIDENCE
        # ====================================================

        print("\n")
        print(
            "CULPRIT EVIDENCE"
        )

        print("-" * 70)

        for evidence in scenario.evidence:

            if (
                evidence.suspect_id
                == culprit.id
            ):

                print(
                    f"{evidence.id}: "
                    f"{evidence.evidence_type} | "
                    f"Location="
                    f"{evidence.location_id} | "
                    f"Time={evidence.time}"
                )

                print(
                    "   ",
                    evidence.statement
                )

        # ====================================================
        # INDIVIDUAL FAILURE REPORTING
        # ====================================================

        if not present:

            print(
                "\n✗ FAILURE: intended culprit "
                "does not satisfy PRESENCE."
            )

            return False

        if not access:

            print(
                "\n✗ FAILURE: intended culprit "
                "does not satisfy ACCESS."
            )

            return False

        if not available:

            print(
                "\n✗ FAILURE: intended culprit "
                "does not satisfy AVAILABILITY."
            )

            return False

        if not reachable:

            print(
                "\n✗ FAILURE: intended culprit "
                "does not satisfy REACHABILITY."
            )

            return False

        print(
            "\n✓ Intended culprit satisfies "
            "all four constraints."
        )

        # ====================================================
        # BASIC CONSTRAINT ENGINE
        # ====================================================

        possible_suspects = (
            find_possible_suspects(
                scenario
            )
        )

        possible_ids = {
            suspect.id

            for suspect in possible_suspects
        }

        print(
            "\nConstraint engine candidates:",
            possible_ids
        )

        # ====================================================
        # UNIQUENESS CHECK
        # ====================================================

        if len(possible_ids) != 1:

            print(
                "✗ REJECTED: expected exactly "
                "one candidate."
            )

            return False

        print(
            "✓ Exactly one constraint candidate."
        )

        # ====================================================
        # INTENDED CULPRIT CHECK
        # ====================================================

        if (
            intended_culprit_id
            not in possible_ids
        ):

            print(
                "✗ REJECTED: intended culprit "
                "is not the unique candidate."
            )

            return False

        print(
            "✓ Intended culprit is the unique "
            "constraint candidate."
        )

        # ====================================================
        # CSP SOLVER
        # ====================================================

        csp_result = solve_crime_csp(
            scenario
        )

        csp_suspects = get_csp_suspects(
            scenario,
            csp_result
        )

        csp_ids = {
            suspect.id

            for suspect in csp_suspects
        }

        print(
            "\nCSP candidates:",
            csp_ids
        )

        # ====================================================
        # MODEL AGREEMENT
        # ====================================================

        if csp_ids != possible_ids:

            print(
                "✗ REJECTED: Constraint Engine "
                "and CSP disagree."
            )

            print(
                "Constraint Engine:",
                possible_ids
            )

            print(
                "CSP:",
                csp_ids
            )

            print(
                "\nCSP SEARCH TRACE:"
            )

            for line in (
                csp_result.search_trace
            ):

                print(
                    " ",
                    line
                )

            return False

        print(
            "✓ Constraint Engine and CSP agree."
        )

        # ====================================================
        # CSP UNIQUENESS
        # ====================================================

        if len(csp_ids) != 1:

            print(
                "✗ REJECTED: CSP does not have "
                "exactly one solution."
            )

            return False

        print(
            "✓ CSP has exactly one candidate."
        )

        # ====================================================
        # INTENDED CULPRIT VS CSP
        # ====================================================

        if (
            intended_culprit_id
            not in csp_ids
        ):

            print(
                "✗ REJECTED: intended culprit "
                "does not match CSP."
            )

            return False

        print(
            "✓ Intended culprit matches CSP."
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            "\n✓ SCENARIO PASSED VERIFICATION"
        )

        return True

    # ========================================================
    # GENERATE UNIQUE SCENARIO
    # ========================================================

    def generate_unique_scenario(
        self
    ) -> tuple[Scenario, str]:

        print("\n")

        print("=" * 70)

        print(
            "STARTING SCENARIO GENERATION"
        )

        print("=" * 70)

        for attempt in range(
            1,
            self.config.max_attempts + 1
        ):

            print(
                f"\nGeneration attempt "
                f"{attempt}/"
                f"{self.config.max_attempts}"
            )

            (
                scenario,
                intended_culprit_id
            ) = self.build_candidate_scenario()

            if self.verify_scenario(
                scenario,
                intended_culprit_id
            ):

                print(
                    "\n"
                    + "=" * 70
                )

                print(
                    "✓ UNIQUE VALID SCENARIO GENERATED"
                )

                print(
                    "=" * 70
                )

                return (
                    scenario,
                    intended_culprit_id
                )

        raise RuntimeError(
            "Unable to generate a unique valid "
            "scenario within the maximum number "
            "of attempts."
        )


# ============================================================
# PRINT GENERATED SCENARIO
# ============================================================

def print_generated_scenario(
    scenario: Scenario,
    intended_culprit_id: str
):

    print("\n")

    print("=" * 70)

    print(
        "GENERATED CRIME MYSTERY"
    )

    print("=" * 70)

    # ========================================================
    # CASE ID
    # ========================================================

    print(
        "\nCASE ID:"
    )

    print(
        scenario.id
    )

    # ========================================================
    # CRIME
    # ========================================================

    print(
        "\nCRIME:"
    )

    print(
        scenario.crime.crime_type
    )

    # ========================================================
    # CRIME LOCATION
    # ========================================================

    crime_location = None

    for location in scenario.locations:

        if (
            location.id
            == scenario.crime.location_id
        ):

            crime_location = location

            break

    if crime_location is not None:

        print(
            "Location:",
            crime_location.name
        )

    # ========================================================
    # CRIME TIME
    # ========================================================

    print(
        "Time:",
        scenario.crime.start_time,
        "-",
        scenario.crime.end_time
    )

    # ========================================================
    # SUSPECTS
    # ========================================================

    print(
        "\nSUSPECTS:"
    )

    for suspect in scenario.suspects:

        print(
            f"  {suspect.id} -> "
            f"{suspect.name}"
        )

    # ========================================================
    # LOCATIONS
    # ========================================================

    print(
        "\nLOCATIONS:"
    )

    for location in scenario.locations:

        print(
            f"  {location.id} -> "
            f"{location.name}"
        )

    # ========================================================
    # GRAPH CONNECTIONS
    # ========================================================

    print(
        "\nSCENE GRAPH CONNECTIONS:"
    )

    for connection in scenario.connections:

        print(
            f"  {connection.id}: "
            f"{connection.from_location_id} "
            f"<-> "
            f"{connection.to_location_id} "
            f"("
            f"{connection.travel_time}"
            f" min)"
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    print(
        "\nEVIDENCE:"
    )

    for evidence in scenario.evidence:

        print(
            f"\n  {evidence.id}"
        )

        print(
            f"    Type: "
            f"{evidence.evidence_type}"
        )

        print(
            f"    Suspect: "
            f"{evidence.suspect_id}"
        )

        print(
            f"    Location: "
            f"{evidence.location_id}"
        )

        print(
            f"    Time: "
            f"{evidence.time}"
        )

        print(
            f"    Reliability: "
            f"{evidence.reliability}"
        )

        print(
            f"    Statement: "
            f"{evidence.statement}"
        )

    # ========================================================
    # CONSTRAINTS
    # ========================================================

    print(
        "\nCONSTRAINTS:"
    )

    for constraint in scenario.constraints:

        print(
            f"  {constraint.id} -> "
            f"{constraint.description}"
        )

    # ========================================================
    # VERIFICATION SUMMARY
    # ========================================================

    print("\n")

    print("=" * 70)

    print(
        "GENERATOR VERIFICATION SUMMARY"
    )

    print("=" * 70)

    print(
        "\nIntended solution:",
        intended_culprit_id
    )

    possible_suspects = (
        find_possible_suspects(
            scenario
        )
    )

    print(
        "Constraint engine:",
        [
            suspect.id
            for suspect in possible_suspects
        ]
    )

    csp_result = solve_crime_csp(
        scenario
    )

    csp_suspects = get_csp_suspects(
        scenario,
        csp_result
    )

    print(
        "CSP engine:",
        [
            suspect.id
            for suspect in csp_suspects
        ]
    )

    contradiction_report = (
        detect_contradictions(
            scenario
        )
    )

    print(
        "Contradictions:",
        contradiction_report.count()
    )

    print(
        "Final classification:",
        classify_solution(
            possible_suspects
        )
    )

    if (
        len(possible_suspects) == 1
        and
        possible_suspects[0].id
        == intended_culprit_id
        and
        len(csp_suspects) == 1
        and
        csp_suspects[0].id
        == intended_culprit_id
        and
        contradiction_report.count() == 0
    ):

        print(
            "\n✓ GENERATED SCENARIO IS VALID"
        )

        print(
            "✓ UNIQUE SOLUTION VERIFIED"
        )

    else:

        print(
            "\n✗ GENERATED SCENARIO FAILED "
            "FINAL VALIDATION"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    generator = ScenarioGenerator(
        seed=None
    )

    (
        scenario,
        intended_culprit_id
    ) = generator.generate_unique_scenario()

    print_generated_scenario(
        scenario,
        intended_culprit_id
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()