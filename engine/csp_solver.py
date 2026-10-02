from dataclasses import dataclass, field

from data.models import (
    Scenario,
    Suspect
)

from engine.constraints import (
    is_present,
    has_access,
    is_available,
    can_reach_crime_scene
)


# ============================================================
# CSP ASSIGNMENT
# ============================================================

@dataclass
class CSPAssignment:

    culprit_id: str

    def __str__(self) -> str:

        return (
            f"Culprit = {self.culprit_id}"
        )


# ============================================================
# CSP SEARCH RESULT
# ============================================================

@dataclass
class CSPSolution:

    assignments: list[CSPAssignment] = field(
        default_factory=list
    )

    nodes_explored: int = 0

    rejected_assignments: int = 0

    search_trace: list[str] = field(
        default_factory=list
    )


# ============================================================
# CSP SOLVER
# ============================================================

class CrimeCSP:

    def __init__(
        self,
        scenario: Scenario
    ):

        self.scenario = scenario

        # ----------------------------------------------------
        # CSP VARIABLES
        # ----------------------------------------------------

        self.variables = [
            "Culprit"
        ]

        # ----------------------------------------------------
        # DOMAINS
        # ----------------------------------------------------

        self.domains = {

            "Culprit": [
                suspect.id
                for suspect in scenario.suspects
            ]
        }

    # ========================================================
    # GET SUSPECT
    # ========================================================

    def get_suspect(
        self,
        suspect_id: str
    ) -> Suspect | None:

        for suspect in self.scenario.suspects:

            if suspect.id == suspect_id:

                return suspect

        return None

    # ========================================================
    # CHECK CONSTRAINTS
    # ========================================================

    def satisfies_constraints(
        self,
        culprit_id: str
    ) -> tuple[bool, list[str]]:

        suspect = self.get_suspect(
            culprit_id
        )

        if suspect is None:

            return (
                False,
                ["Suspect does not exist."]
            )

        failed_constraints = []

        # ----------------------------------------------------
        # Constraint 1:
        # Culprit must be present
        # ----------------------------------------------------

        if not is_present(
            suspect,
            self.scenario
        ):

            failed_constraints.append(
                "Present(Culprit, CrimeLocation) = False"
            )

        # ----------------------------------------------------
        # Constraint 2:
        # Culprit must have access
        # ----------------------------------------------------

        if not has_access(
            suspect,
            self.scenario
        ):

            failed_constraints.append(
                "Access(Culprit, CrimeLocation) = False"
            )

        # ----------------------------------------------------
        # Constraint 3:
        # Culprit must be available
        # ----------------------------------------------------

        if not is_available(
            suspect,
            self.scenario
        ):

            failed_constraints.append(
                "Available(Culprit) = False"
            )

        # ----------------------------------------------------
        # Constraint 4:
        # Culprit must be reachable
        # ----------------------------------------------------

        if not can_reach_crime_scene(
            suspect,
            self.scenario
        ):

            failed_constraints.append(
                "Reachable(Culprit, CrimeLocation) = False"
            )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        return (
            len(failed_constraints) == 0,
            failed_constraints
        )

    # ========================================================
    # CHECK PARTIAL ASSIGNMENT
    # ========================================================

    def is_consistent(
        self,
        assignment: dict
    ) -> tuple[bool, list[str]]:

        # No culprit assigned yet.
        # A partial assignment is valid so far.

        if "Culprit" not in assignment:

            return True, []

        culprit_id = assignment[
            "Culprit"
        ]

        return self.satisfies_constraints(
            culprit_id
        )

    # ========================================================
    # BACKTRACKING SEARCH
    # ========================================================

    def backtrack(
        self,
        assignment: dict,
        result: CSPSolution
    ):

        # ----------------------------------------------------
        # Complete assignment
        # ----------------------------------------------------

        if len(assignment) == len(
            self.variables
        ):

            culprit_id = assignment[
                "Culprit"
            ]

            result.assignments.append(
                CSPAssignment(
                    culprit_id=culprit_id
                )
            )

            result.search_trace.append(
                f"✓ Complete assignment accepted: "
                f"Culprit = {culprit_id}"
            )

            return

        # ----------------------------------------------------
        # Select unassigned variable
        # ----------------------------------------------------

        variable = None

        for candidate_variable in (
            self.variables
        ):

            if candidate_variable not in assignment:

                variable = candidate_variable

                break

        if variable is None:

            return

        # ----------------------------------------------------
        # Try each domain value
        # ----------------------------------------------------

        for value in self.domains[
            variable
        ]:

            result.nodes_explored += 1

            result.search_trace.append(
                f"→ Trying {variable} = {value}"
            )

            # ------------------------------------------------
            # Create new assignment
            # ------------------------------------------------

            new_assignment = (
                assignment.copy()
            )

            new_assignment[
                variable
            ] = value

            # ------------------------------------------------
            # Constraint propagation
            # ------------------------------------------------

            consistent, failures = (
                self.is_consistent(
                    new_assignment
                )
            )

            if consistent:

                result.search_trace.append(
                    f"  ✓ {variable} = {value} "
                    f"is consistent"
                )

                self.backtrack(
                    new_assignment,
                    result
                )

            else:

                result.rejected_assignments += 1

                result.search_trace.append(
                    f"  ✗ {variable} = {value} "
                    f"rejected"
                )

                for failure in failures:

                    result.search_trace.append(
                        f"      Reason: {failure}"
                    )

    # ========================================================
    # SOLVE
    # ========================================================

    def solve(self) -> CSPSolution:

        result = CSPSolution()

        self.backtrack(
            assignment={},
            result=result
        )

        return result


# ============================================================
# PUBLIC SOLVER FUNCTION
# ============================================================

def solve_crime_csp(
    scenario: Scenario
) -> CSPSolution:

    solver = CrimeCSP(
        scenario
    )

    return solver.solve()


# ============================================================
# GET SOLUTION SUSPECTS
# ============================================================

def get_csp_suspects(
    scenario: Scenario,
    result: CSPSolution
) -> list[Suspect]:

    suspect_ids = {
        assignment.culprit_id
        for assignment in result.assignments
    }

    suspects = []

    for suspect in scenario.suspects:

        if suspect.id in suspect_ids:

            suspects.append(
                suspect
            )

    return suspects


# ============================================================
# CLASSIFY CSP RESULT
# ============================================================

def classify_csp_result(
    result: CSPSolution
) -> str:

    number_of_solutions = len(
        result.assignments
    )

    if number_of_solutions == 0:

        return "NO SOLUTION"

    elif number_of_solutions == 1:

        return "UNIQUE SOLUTION"

    else:

        return "MULTIPLE SOLUTIONS"