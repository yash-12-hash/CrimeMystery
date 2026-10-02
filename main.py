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

    is_present,

    has_access,

    has_valid_alibi,

    is_available,

    can_reach_crime_scene,

    satisfies_all_constraints,

    find_possible_suspects

)



from engine.set_filter import (

    get_set_analysis

)



from engine.logic import (

    build_rules,

    evaluate_suspect_logic,

    find_logically_possible_suspects

)



from graph.scene_graph import (

    build_scene_graph,

    get_reachability_analysis

)



from engine.csp_solver import (

    solve_crime_csp,

    get_csp_suspects,

    classify_csp_result

)



from engine.contradictions import (

    detect_contradictions,

    print_contradiction_report

)



from engine.solution_validator import (

    validate_solution,

    print_solution_validation

)


from engine.reasoning import (

    generate_reasoning_report,

    print_reasoning_report

)





# ============================================================
# CREATE SAMPLE SCENARIO*
# ============================================================
def create_sample_scenario():



    suspects = [



        Suspect(

            id="S1",

            name="Rahul"

        ),



        Suspect(

            id="S2",

            name="Aditya"

        ),



        Suspect(

            id="S3",

            name="Rohan"

        ),



        Suspect(

            id="S4",

            name="Sameer"

        )

    ]



    locations = [



        Location(

            id="L1",

            name="Computer Laboratory"

        ),



        Location(

            id="L2",

            name="Library"

        ),



        Location(

            id="L3",

            name="College Gate"

        ),



        Location(

            id="L4",

            name="Hostel"

        )

    ]



    connections = [



        Connection(

            id="P1",

            from_location_id="L1",

            to_location_id="L2",

            travel_time=2

        ),



        Connection(

            id="P2",

            from_location_id="L2",

            to_location_id="L3",

            travel_time=3

        ),



        Connection(

            id="P3",

            from_location_id="L3",

            to_location_id="L4",

            travel_time=4

        )

    ]



    crime = Crime(



        crime_type="Laptop Theft",



        location_id="L1",



        start_time="14:25",



        end_time="14:35"

    )



    evidence = [



        Evidence(

            id="E1",

            evidence_type="CCTV",

            suspect_id="S1",

            location_id="L2",

            time="14:30",

            statement=(

                "Rahul was seen in library "

                "at 14:30."

            ),

            reliability=0.95

        ),



        Evidence(

            id="E2",

            evidence_type="CCTV",

            suspect_id="S3",

            location_id="L3",

            time="14:30",

            statement=(

                "Rohan was seen outside "

                "college at 14:30."

            ),

            reliability=0.95

        ),



        Evidence(

            id="E3",

            evidence_type="CCTV",

            suspect_id="S4",

            location_id="L4",

            time="14:30",

            statement=(

                "Sameer was in hostel "

                "at 14:30."

            ),

            reliability=0.95

        ),



        Evidence(

            id="E4",

            evidence_type="Access Log",

            suspect_id="S2",

            location_id="L1",

            time="14:20",

            statement=(

                "Aditya entered computer "

                "laboratory at 14:20."

            ),

            reliability=1.0

        ),



        Evidence(

            id="E5",

            evidence_type="Access Permission",

            suspect_id="S1",

            location_id="L1",

            time=None,

            statement=(

                "Rahul has access to "

                "computer laboratory."

            ),

            reliability=1.0

        ),



        Evidence(

            id="E6",

            evidence_type="Access Permission",

            suspect_id="S2",

            location_id="L1",

            time=None,

            statement=(

                "Aditya has access to "

                "computer laboratory."

            ),

            reliability=1.0

        )

    ]



    constraints = [



        Constraint(

            id="C1",

            description=(

                "Suspect must be present "

                "at crime location."

            )

        ),



        Constraint(

            id="C2",

            description=(

                "Suspect must have access "

                "to crime location."

            )

        ),



        Constraint(

            id="C3",

            description=(

                "Suspect must not have "

                "a valid alibi."

            )

        ),



        Constraint(

            id="C4",

            description=(

                "Suspect must be able to "

                "reach crime scene."

            )

        )

    ]



    return Scenario(



        id="CASE-001",



        crime=crime,



        suspects=suspects,



        locations=locations,



        connections=connections,



        evidence=evidence,



        constraints=constraints

    )





# ============================================================
# DISPLAY CASE*
# ============================================================
def display_case(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("MATHEMATICAL CRIME MYSTERY SOLVER")

    print("=" * 65)



    print(

        "\nCASE:",

        scenario.id

    )



    print(

        "Crime:",

        scenario.crime.crime_type

    )



    print(

        "Crime Location:",

        scenario.crime.location_id

    )



    print(

        "Crime Time:",

        scenario.crime.start_time,

        "-",

        scenario.crime.end_time

    )



    print("\nSUSPECTS")



    for suspect in scenario.suspects:



        print(

            f"{suspect.id} -> {suspect.name}"

        )



    print("\nEVIDENCE")



    for evidence in scenario.evidence:



        print(

            f"{evidence.id}: "

            f"{evidence.statement}"

        )





# ============================================================
# STEP 3*
# ============================================================
def run_constraint_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 3 — CONSTRAINT ANALYSIS")

    print("=" * 65)



    for suspect in scenario.suspects:



        present = is_present(

            suspect,

            scenario

        )



        access = has_access(

            suspect,

            scenario

        )



        alibi = has_valid_alibi(

            suspect,

            scenario

        )



        available = is_available(

            suspect,

            scenario

        )



        reachable = can_reach_crime_scene(

            suspect,

            scenario

        )



        satisfies = satisfies_all_constraints(

            suspect,

            scenario

        )



        print(

            f"\n{suspect.name}"

        )



        print(

            "  Present:",

            present

        )



        print(

            "  Access:",

            access

        )



        print(

            "  Valid Alibi:",

            alibi

        )



        print(

            "  Available:",

            available

        )



        print(

            "  Reachable:",

            reachable

        )



        print(

            "  All Constraints:",

            satisfies

        )





# ============================================================
# STEP 4*
# ============================================================
def run_set_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 4 — SET THEORY ANALYSIS")

    print("=" * 65)



    analysis = get_set_analysis(

        scenario

    )



    def names_from_ids(ids):



        return [

            suspect.name

            for suspect in scenario.suspects

            if suspect.id in ids

        ]



    print(

        "\nS = All Suspects"

    )



    print(

        names_from_ids(

            analysis["all"]

        )

    )



    print(

        "\nA = Access Set"

    )



    print(

        names_from_ids(

            analysis["access"]

        )

    )



    print(

        "\nP = Presence Set"

    )



    print(

        names_from_ids(

            analysis["presence"]

        )

    )



    print(

        "\nV = Availability Set"

    )



    print(

        names_from_ids(

            analysis["availability"]

        )

    )



    print(

        "\nR = Reachability Set"

    )



    print(

        names_from_ids(

            analysis["reachability"]

        )

    )



    print(

        "\nPossible = A ∩ P ∩ V ∩ R"

    )



    print(

        names_from_ids(

            analysis["possible"]

        )

    )





# ============================================================
# STEP 5*
# ============================================================
def run_logic_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 5 — PREDICATE LOGIC ANALYSIS")

    print("=" * 65)



    print("\nLOGICAL PREDICATES")



    print(

        "Present(x, location, time)"

    )



    print(

        "Access(x, location)"

    )



    print(

        "Available(x)"

    )



    print(

        "Reachable(x, location)"

    )



    print(

        "Guilty(x)"

    )



    rules = build_rules(

        scenario

    )



    print("\nLOGICAL RULES")



    for rule in rules:



        print(

            f"\n{rule.name}:"

        )



        print(

            f"  {rule.antecedent} -> "

            f"{', '.join(str(c) for c in rule.consequents)}"

        )



    print("\nHYPOTHESIS TESTING")



    for suspect in scenario.suspects:



        evaluation = evaluate_suspect_logic(

            suspect,

            scenario

        )



        print(

            f"\nHypothesis: "

            f"Guilty({suspect.name})"

        )



        for fact in evaluation.facts:



            print(

                f"  ✓ {fact}"

            )



        if evaluation.satisfied:



            print(

                "  ✓ Hypothesis SATISFIED"

            )



        else:



            print(

                "  ✗ Hypothesis REJECTED"

            )



            for predicate in (

                evaluation.failed_predicates

            ):



                print(

                    f"    ✗ {predicate}"

                )





# ============================================================
# STEP 6*
# ============================================================
def run_graph_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 6 — CRIME SCENE GRAPH & REACHABILITY")

    print("=" * 65)



    graph = build_scene_graph(

        scenario

    )



    print("\nGRAPH VERTICES")



    for node in graph.nodes:



        print(

            f"  {node} -> "

            f"{graph.nodes[node]['name']}"

        )



    print("\nGRAPH EDGES")



    for source, target, data in (

        graph.edges(data=True)

    ):



        print(

            f"  {source} <-> {target} "

            f"({data['travel_time']} minutes)"

        )



    print("\nMATHEMATICAL GRAPH")



    print(

        "V =",

        set(graph.nodes)

    )



    print(

        "E =",

        set(graph.edges)

    )



    print(

        "\nG = (V, E)"

    )



    print(

        "\nREACHABILITY ANALYSIS"

    )



    for suspect in scenario.suspects:



        analysis = get_reachability_analysis(

            suspect,

            scenario

        )



        print(

            f"\n{suspect.name}"

        )



        print(

            "  Known Location:",

            analysis["source"]

        )



        print(

            "  Evidence Time:",

            analysis["source_time"]

        )



        print(

            "  Available Time:",

            analysis["available_time"],

            "minutes"

        )



        print(

            "  Shortest Path:",

            analysis["path"]

        )



        print(

            "  Travel Time:",

            analysis["travel_time"],

            "minutes"

        )



        print(

            "  Reachable:",

            analysis["reachable"]

        )





# ============================================================
# STEP 7*
# ============================================================
def run_csp_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 7 — CONSTRAINT SATISFACTION PROBLEM")

    print("=" * 65)



    print("\nCSP MODEL")



    print(

        "Variables:"

    )



    print(

        "  Culprit"

    )



    print(

        "\nDomain:"

    )



    print(

        "  Culprit ∈ {"

        + ", ".join(

            suspect.id

            for suspect in scenario.suspects

        )

        + "}"

    )



    print(

        "\nConstraints:"

    )



    print(

        "  Present(Culprit, CrimeLocation) = True"

    )



    print(

        "  Access(Culprit, CrimeLocation) = True"

    )



    print(

        "  Available(Culprit) = True"

    )



    print(

        "  Reachable(Culprit, CrimeLocation) = True"

    )



    print(

        "  Exactly one culprit"

    )



    result = solve_crime_csp(

        scenario

    )



    print("\nBACKTRACKING SEARCH")



    for trace_line in result.search_trace:



        print(

            trace_line

        )



    print("\nCSP SEARCH STATISTICS")



    print(

        "Nodes explored:",

        result.nodes_explored

    )



    print(

        "Rejected assignments:",

        result.rejected_assignments

    )



    print(

        "Valid assignments:",

        len(result.assignments)

    )



    print("\nCSP SOLUTIONS")



    csp_suspects = get_csp_suspects(

        scenario,

        result

    )



    if csp_suspects:



        for suspect in csp_suspects:



            print(

                f"  {suspect.id} -> "

                f"{suspect.name}"

            )



    else:



        print(

            "  No valid assignments."

        )



    print(

        "\nCSP STATUS:"

    )



    print(

        classify_csp_result(

            result

        )

    )



    return result





# ============================================================
# STEP 8*
# ============================================================
def run_contradiction_analysis(

    scenario: Scenario

):



    print("\n")

    print("=" * 65)

    print("STEP 8 — CONTRADICTION DETECTION")

    print("=" * 65)



    print(

        "\nChecking whether the scenario "

        "contains internally inconsistent information..."

    )



    report = detect_contradictions(

        scenario

    )



    print_contradiction_report(

        report

    )



    return report





# ============================================================
# STEP 9*
# ============================================================
def run_solution_validation(

    scenario: Scenario,

    csp_result,

    contradiction_report

):



    print("\n")

    print("=" * 65)

    print("STEP 9 — UNIQUE / MULTIPLE / NO-SOLUTION VALIDATION")

    print("=" * 65)



    # --------------------------------------------------------*
    # Constraint-engine result*
    # --------------------------------------------------------*
    constraint_candidates = (

        find_possible_suspects(

            scenario

        )

    )



    # --------------------------------------------------------*
    # Logic-engine result*
    # --------------------------------------------------------*
    logic_candidates = (

        find_logically_possible_suspects(

            scenario

        )

    )



    # --------------------------------------------------------*
    # Display intermediate models*
    # --------------------------------------------------------*
    print(

        "\nCONSTRAINT ENGINE:"

    )



    print(

        [

            suspect.name

            for suspect in constraint_candidates

        ]

    )



    print(

        "\nPREDICATE LOGIC ENGINE:"

    )



    print(

        [

            suspect.name

            for suspect in logic_candidates

        ]

    )



    print(

        "\nCSP ENGINE:"

    )



    csp_candidates = (

        get_csp_suspects(

            scenario,

            csp_result

        )

    )



    print(

        [

            suspect.name

            for suspect in csp_candidates

        ]

    )



    # --------------------------------------------------------*
    # Check logic and CSP agreement*
    # --------------------------------------------------------*
    logic_ids = {

        suspect.id

        for suspect in logic_candidates

    }



    csp_ids = {

        suspect.id

        for suspect in csp_candidates

    }



    print(

        "\nLOGIC == CSP:"

    )



    print(

        logic_ids == csp_ids

    )



    # --------------------------------------------------------*
    # Validate*
    # --------------------------------------------------------*
    result = validate_solution(



        scenario=scenario,



        csp_result=csp_result,



        contradiction_report=(

            contradiction_report

        ),



        constraint_candidates=(

            constraint_candidates

        )

    )



    # --------------------------------------------------------*
    # Display validation*
    # --------------------------------------------------------*
    print_solution_validation(

        result

    )



    return result





# ============================================================
# STEP 11 — MATHEMATICAL REASONING ENGINE
# ============================================================

def run_reasoning_analysis(
    scenario: Scenario
):

    print("\n")
    print("=" * 65)
    print("STEP 11 — MATHEMATICAL REASONING ENGINE")
    print("=" * 65)

    reasoning_report = generate_reasoning_report(
        scenario
    )

    print_reasoning_report(
        reasoning_report
    )

    return reasoning_report


# ============================================================
# MAIN
# ============================================================
def main():



    scenario = create_sample_scenario()



    display_case(

        scenario

    )



    run_constraint_analysis(

        scenario

    )



    run_set_analysis(

        scenario

    )



    run_logic_analysis(

        scenario

    )



    run_graph_analysis(

        scenario

    )



    csp_result = run_csp_analysis(

        scenario

    )



    contradiction_report = (

        run_contradiction_analysis(

            scenario

        )

    )



    validation_result = (

        run_solution_validation(

            scenario,

            csp_result,

            contradiction_report

        )

    )
    
    # --------------------------------------------------------
    # STEP 11 — Mathematical reasoning
    # --------------------------------------------------------

    reasoning_report = (
        run_reasoning_analysis(
            scenario
        )
    )

    # --------------------------------------------------------
    # Step 11 — Mathematical reasoning
    # --------------------------------------------------------

    reasoning_report = (
        run_reasoning_analysis(
            scenario
        )
    )




    # --------------------------------------------------------*
    # Final project result*
    # --------------------------------------------------------*
    print("\n")

    print("=" * 65)

    print("PROJECT FINAL RESULT")

    print("=" * 65)



    print(

        "\nSTATUS:",

        validation_result.status

    )



    print(

        "CANDIDATES:",

        [

            suspect.name

            for suspect in validation_result.candidates

        ]

    )





if __name__ == "__main__":



    main()
