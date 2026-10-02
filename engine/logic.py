from dataclasses import dataclass
from typing import Any

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
# PREDICATE
# ============================================================

@dataclass(frozen=True)
class Predicate:

    name: str
    arguments: tuple[Any, ...]

    def __str__(self) -> str:

        args = ", ".join(
            str(argument)
            for argument in self.arguments
        )

        return f"{self.name}({args})"


# ============================================================
# LOGIC RULE
# ============================================================

@dataclass(frozen=True)
class Rule:

    name: str

    antecedent: Predicate

    consequents: tuple[Predicate, ...]


# ============================================================
# LOGIC EVALUATION
# ============================================================

@dataclass
class LogicEvaluation:

    suspect: Suspect

    hypothesis: Predicate

    facts: list[Predicate]

    rules: list[Rule]

    satisfied: bool

    failed_predicates: list[Predicate]


# ============================================================
# BUILD FACTS
# ============================================================

def build_predicate_facts(
    suspect: Suspect,
    scenario: Scenario
) -> list[Predicate]:

    facts = []

    crime_location = (
        scenario.crime.location_id
    )

    crime_time = (
        scenario.crime.start_time
    )

    # --------------------------------------------------------
    # Present
    # --------------------------------------------------------

    if is_present(
        suspect,
        scenario
    ):

        facts.append(
            Predicate(
                "Present",
                (
                    suspect.name,
                    crime_location,
                    crime_time
                )
            )
        )

    # --------------------------------------------------------
    # Access
    # --------------------------------------------------------

    if has_access(
        suspect,
        scenario
    ):

        facts.append(
            Predicate(
                "Access",
                (
                    suspect.name,
                    crime_location
                )
            )
        )

    # --------------------------------------------------------
    # Available
    # --------------------------------------------------------

    if is_available(
        suspect,
        scenario
    ):

        facts.append(
            Predicate(
                "Available",
                (
                    suspect.name,
                )
            )
        )

    # --------------------------------------------------------
    # Reachable
    # --------------------------------------------------------

    if can_reach_crime_scene(
        suspect,
        scenario
    ):

        facts.append(
            Predicate(
                "Reachable",
                (
                    suspect.name,
                    crime_location
                )
            )
        )

    return facts


# ============================================================
# RULES
# ============================================================

def build_rules(
    scenario: Scenario
) -> list[Rule]:

    crime_location = (
        scenario.crime.location_id
    )

    crime_time = (
        scenario.crime.start_time
    )

    return [

        Rule(
            name="Guilty implies presence",

            antecedent=Predicate(
                "Guilty",
                ("x",)
            ),

            consequents=(
                Predicate(
                    "Present",
                    (
                        "x",
                        crime_location,
                        crime_time
                    )
                ),
            )
        ),

        Rule(
            name="Guilty implies access",

            antecedent=Predicate(
                "Guilty",
                ("x",)
            ),

            consequents=(
                Predicate(
                    "Access",
                    (
                        "x",
                        crime_location
                    )
                ),
            )
        ),

        Rule(
            name="Guilty implies availability",

            antecedent=Predicate(
                "Guilty",
                ("x",)
            ),

            consequents=(
                Predicate(
                    "Available",
                    ("x",)
                ),
            )
        ),

        Rule(
            name="Guilty implies reachability",

            antecedent=Predicate(
                "Guilty",
                ("x",)
            ),

            consequents=(
                Predicate(
                    "Reachable",
                    (
                        "x",
                        crime_location
                    )
                ),
            )
        )
    ]


# ============================================================
# INSTANTIATE PREDICATE
# ============================================================

def instantiate_predicate(
    predicate: Predicate,
    suspect: Suspect
) -> Predicate:

    arguments = []

    for argument in predicate.arguments:

        if argument == "x":

            arguments.append(
                suspect.name
            )

        else:

            arguments.append(
                argument
            )

    return Predicate(
        predicate.name,
        tuple(arguments)
    )


# ============================================================
# EVALUATE SUSPECT
# ============================================================

def evaluate_suspect_logic(
    suspect: Suspect,
    scenario: Scenario
) -> LogicEvaluation:

    facts = build_predicate_facts(
        suspect,
        scenario
    )

    rules = build_rules(
        scenario
    )

    fact_set = set(facts)

    hypothesis = Predicate(
        "Guilty",
        (suspect.name,)
    )

    failed_predicates = []

    for rule in rules:

        instantiated_antecedent = (
            instantiate_predicate(
                rule.antecedent,
                suspect
            )
        )

        if (
            instantiated_antecedent
            == hypothesis
        ):

            for consequent in (
                rule.consequents
            ):

                required_fact = (
                    instantiate_predicate(
                        consequent,
                        suspect
                    )
                )

                if required_fact not in fact_set:

                    failed_predicates.append(
                        required_fact
                    )

    return LogicEvaluation(

        suspect=suspect,

        hypothesis=hypothesis,

        facts=facts,

        rules=rules,

        satisfied=(
            len(failed_predicates) == 0
        ),

        failed_predicates=(
            failed_predicates
        )
    )


# ============================================================
# FIND LOGICAL CANDIDATES
# ============================================================

def find_logically_possible_suspects(
    scenario: Scenario
) -> list[Suspect]:

    possible = []

    for suspect in scenario.suspects:

        evaluation = (
            evaluate_suspect_logic(
                suspect,
                scenario
            )
        )

        if evaluation.satisfied:

            possible.append(
                suspect
            )

    return possible