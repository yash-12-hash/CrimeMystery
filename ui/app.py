# ============================================================
# Mathematical Crime Mystery Solver
# Step 12 - Streamlit User Interface
# ============================================================

import sys
from pathlib import Path

# ------------------------------------------------------------
# Add project root to Python path
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

import streamlit as st
import pandas as pd

from main import create_sample_scenario

from engine.constraints import (
    is_present,
    has_access,
    has_valid_alibi,
    is_available,
    can_reach_crime_scene,
    satisfies_all_constraints,
    find_possible_suspects,
)

from engine.set_filter import (
    get_set_analysis,
)

from engine.logic import (
    build_rules,
    evaluate_suspect_logic,
    find_logically_possible_suspects,
)

from graph.scene_graph import (
    build_scene_graph,
    get_reachability_analysis,
)

from engine.csp_solver import (
    solve_crime_csp,
    get_csp_suspects,
    classify_csp_result,
)

from engine.contradictions import (
    detect_contradictions,
)

from engine.solution_validator import (
    validate_solution,
)

from engine.reasoning import (
    generate_reasoning_report,
)

from engine.pipeline import run_full_analysis


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mathematical Crime Mystery Solver",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #777777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 650;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SCENARIO INPUT / LOAD EXAMPLE
# ============================================================

from data.models import (
    Suspect,
    Location,
    Connection,
    Crime,
    Evidence,
    Constraint,
    Scenario,
)


# The mathematical model uses these four constraints for every scenario.
DEFAULT_CONSTRAINTS = [
    Constraint(
        id="C1",
        description="Suspect must be present at the crime location during the crime interval.",
    ),
    Constraint(
        id="C2",
        description="Suspect must have access to the crime location.",
    ),
    Constraint(
        id="C3",
        description="Suspect must not have a valid alibi during the crime interval.",
    ),
    Constraint(
        id="C4",
        description="Suspect must be able to reach the crime scene in time.",
    ),
]


def _initialize_custom_state():
    """Initialize editable custom-scenario state once per browser session."""

    if "custom_solved_scenario" not in st.session_state:
        st.session_state.custom_solved_scenario = None

    if "custom_analysis" not in st.session_state:
        st.session_state.custom_analysis = None


_initialize_custom_state()


st.markdown(
    '<div class="section-title">🕵️ Mystery Scenario</div>',
    unsafe_allow_html=True,
)

scenario_mode = st.radio(
    "Choose how you want to run the solver",
    ["Create Custom Mystery", "Load Example"],
    horizontal=True,
    key="scenario_mode",
)


if scenario_mode == "Load Example":
    scenario = create_sample_scenario()
    analysis = run_full_analysis(scenario)
    st.session_state.custom_solved_scenario = None
    st.session_state.custom_analysis = None

    st.info(
        "The original example scenario is loaded. The analysis below uses the existing mathematical engine unchanged."
    )

else:
    st.info(
        "Build your own mystery below. Add suspects, locations, connections, and evidence, then click **Solve Mystery**."
    )

    with st.form("custom_mystery_form"):

        st.markdown("### 1. Crime Details")

        crime_type = st.text_input(
            "Crime type",
            placeholder="Example: Laptop Theft",
        )

        crime_start = st.text_input(
            "Crime start time (HH:MM)",
            placeholder="Example: 14:25",
        )

        crime_end = st.text_input(
            "Crime end time (HH:MM)",
            placeholder="Example: 14:35",
        )

        st.markdown("### 2. Locations")

        location_count = st.number_input(
            "Number of locations",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
        )

        location_names = []

        location_columns = st.columns(2)

        for index in range(int(location_count)):
            with location_columns[index % 2]:
                location_names.append(
                    st.text_input(
                        f"Location {index + 1} name",
                        placeholder=f"Example: Location {index + 1}",
                        key=f"custom_location_name_{index}",
                    )
                )

        filled_location_names = [
            name.strip() if name.strip() else f"Location {index + 1}"
            for index, name in enumerate(location_names)
        ]

        st.markdown("### 3. Crime Location")

        crime_location_name = st.selectbox(
            "Where did the crime occur?",
            filled_location_names,
            key="custom_crime_location",
        )

        st.markdown("### 4. Suspects")

        suspect_count = st.number_input(
            "Number of suspects",
            min_value=1,
            max_value=20,
            value=1,
            step=1,
        )

        st.caption(
            "For every suspect, enter their name, the location where they were "
            "observed, and the time they were there. This information is "
            "automatically converted into evidence for the mathematical solver."
        )

        suspect_rows = []

        for index in range(int(suspect_count)):
            with st.container(border=True):
                st.markdown(f"**Suspect {index + 1}**")

                columns = st.columns(4)

                with columns[0]:
                    suspect_name = st.text_input(
                        "Name",
                        placeholder=f"Example: Suspect {index + 1}",
                        key=f"custom_suspect_name_{index}",
                    )

                with columns[1]:
                    suspect_location = st.selectbox(
                        "Observed location",
                        filled_location_names,
                        key=f"custom_suspect_location_{index}",
                    )

                with columns[2]:
                    suspect_time = st.text_input(
                        "Time observed (HH:MM)",
                        placeholder="Example: 14:25",
                        key=f"custom_suspect_time_{index}",
                    )

                with columns[3]:
                    suspect_has_access = st.checkbox(
                        "Authorized access to crime location",
                        value=False,
                        key=f"custom_suspect_access_{index}",
                        help=(
                            "If checked, the app automatically creates an "
                            "Access Permission evidence record for this suspect."
                        ),
                    )

                suspect_rows.append(
                    {
                        "name": suspect_name,
                        "location": suspect_location,
                        "time": suspect_time.strip(),
                        "has_access": suspect_has_access,
                    }
                )

        suspect_names = [row["name"] for row in suspect_rows]

        st.markdown("### 5. Connections")

        connection_count = st.number_input(
            "Number of connections",
            min_value=0,
            max_value=40,
            value=0,
            step=1,
        )

        connection_rows = []

        for index in range(int(connection_count)):
            with st.container(border=True):
                columns = st.columns(3)

                with columns[0]:
                    source_location = st.selectbox(
                        f"Connection {index + 1} - From",
                        filled_location_names,
                        key=f"custom_connection_from_{index}",
                    )

                with columns[1]:
                    destination_location = st.selectbox(
                        f"Connection {index + 1} - To",
                        filled_location_names,
                        key=f"custom_connection_to_{index}",
                    )

                with columns[2]:
                    travel_time = st.number_input(
                        f"Connection {index + 1} - Travel time (min)",
                        min_value=0,
                        max_value=1440,
                        value=1,
                        step=1,
                        key=f"custom_connection_time_{index}",
                    )

                connection_rows.append(
                    {
                        "source": source_location,
                        "destination": destination_location,
                        "travel_time": int(travel_time),
                    }
                )

        st.markdown("### 6. Additional Evidence")

        st.caption(
            "The suspect location/time entered above already creates a basic "
            "CCTV-style observation for each suspect. Use additional evidence "
            "below for access permissions, access logs, witness statements, "
            "or any other evidence."
        )

        evidence_count = st.number_input(
            "Number of additional evidence records",
            min_value=0,
            max_value=60,
            value=0,
            step=1,
        )

        filled_suspect_names = [
            name.strip() if name.strip() else f"Suspect {index + 1}"
            for index, name in enumerate(suspect_names)
        ]

        evidence_rows = []

        evidence_types = [
            "CCTV",
            "Access Permission",
            "Access Log",
            "Witness Statement",
            "Other",
        ]

        for index in range(int(evidence_count)):
            with st.container(border=True):
                columns = st.columns(5)

                with columns[0]:
                    evidence_type = st.selectbox(
                        f"Evidence {index + 1} - Type",
                        evidence_types,
                        key=f"custom_evidence_type_{index}",
                    )

                with columns[1]:
                    evidence_suspect = st.selectbox(
                        f"Evidence {index + 1} - Suspect",
                        filled_suspect_names,
                        key=f"custom_evidence_suspect_{index}",
                    )

                with columns[2]:
                    evidence_location = st.selectbox(
                        f"Evidence {index + 1} - Location",
                        filled_location_names,
                        key=f"custom_evidence_location_{index}",
                    )

                with columns[3]:
                    evidence_time = st.text_input(
                        f"Evidence {index + 1} - Time",
                        placeholder="HH:MM or leave blank",
                        key=f"custom_evidence_time_{index}",
                    )

                with columns[4]:
                    evidence_statement = st.text_input(
                        f"Evidence {index + 1} - Statement",
                        placeholder="Describe the evidence",
                        key=f"custom_evidence_statement_{index}",
                    )

                evidence_rows.append(
                    {
                        "type": evidence_type,
                        "suspect": evidence_suspect,
                        "location": evidence_location,
                        "time": evidence_time.strip() or None,
                        "statement": evidence_statement.strip(),
                    }
                )

        solve_clicked = st.form_submit_button(
            "🔎 Solve Mystery",
            type="primary",
            use_container_width=True,
        )


    if solve_clicked:
        errors = []

        crime_type_clean = crime_type.strip()
        crime_start_clean = crime_start.strip()
        crime_end_clean = crime_end.strip()

        if not crime_type_clean:
            errors.append("Crime type cannot be empty.")

        if not crime_start_clean:
            errors.append("Crime start time cannot be empty.")

        if not crime_end_clean:
            errors.append("Crime end time cannot be empty.")

        if any(not row["name"].strip() for row in suspect_rows):
            errors.append("Every suspect must have a name.")

        if any(not row["time"].strip() for row in suspect_rows):
            errors.append("Every suspect must have an observation time.")

        if any(not name.strip() for name in location_names):
            errors.append("Every location must have a name.")

        if len({name.strip().lower() for name in suspect_names}) != len(suspect_names):
            errors.append("Suspect names must be unique.")

        if len({name.strip().lower() for name in location_names}) != len(location_names):
            errors.append("Location names must be unique.")

        if not errors:
            suspect_objects = [
                Suspect(
                    id=f"S{index + 1}",
                    name=row["name"].strip(),
                )
                for index, row in enumerate(suspect_rows)
            ]

            location_objects = [
                Location(
                    id=f"L{index + 1}",
                    name=name.strip(),
                )
                for index, name in enumerate(location_names)
            ]

            suspect_id_by_name = {
                suspect.name: suspect.id
                for suspect in suspect_objects
            }

            location_id_by_name = {
                location.name: location.id
                for location in location_objects
            }

            crime_location_id = location_id_by_name[crime_location_name]

            connection_objects = []

            for index, row in enumerate(connection_rows):
                connection_objects.append(
                    Connection(
                        id=f"P{index + 1}",
                        from_location_id=location_id_by_name[row["source"]],
                        to_location_id=location_id_by_name[row["destination"]],
                        travel_time=row["travel_time"],
                    )
                )

            evidence_objects = []

            # Every suspect's location and observation time becomes a
            # basic CCTV-style evidence record. This makes the suspect
            # input section directly useful to the mathematical engine.
            for index, row in enumerate(suspect_rows):
                evidence_objects.append(
                    Evidence(
                        id=f"E{index + 1}",
                        evidence_type="CCTV",
                        suspect_id=suspect_id_by_name[row["name"].strip()],
                        location_id=location_id_by_name[row["location"]],
                        time=row["time"].strip(),
                        statement=(
                            f"{row['name'].strip()} was observed at "
                            f"{row['location']} at {row['time'].strip()}."
                        ),
                    )
                )

            # Automatically create Access Permission evidence for every
            # suspect whose access checkbox was selected. This is separate
            # from the automatically generated CCTV observation because
            # presence at a location does not mathematically imply access.
            for row in suspect_rows:
                if row["has_access"]:
                    evidence_objects.append(
                        Evidence(
                            id=f"E{len(evidence_objects) + 1}",
                            evidence_type="Access Permission",
                            suspect_id=suspect_id_by_name[row["name"].strip()],
                            location_id=crime_location_id,
                            time=None,
                            statement=(
                                f"{row['name'].strip()} has authorized access "
                                f"to {crime_location_name}."
                            ),
                        )
                    )

            # Additional evidence entered by the user starts after the
            # automatically generated suspect-observation and access
            # permission records.
            evidence_start_index = len(evidence_objects)

            for index, row in enumerate(evidence_rows):
                evidence_objects.append(
                    Evidence(
                        id=f"E{evidence_start_index + index + 1}",
                        evidence_type=row["type"],
                        suspect_id=suspect_id_by_name[row["suspect"]],
                        location_id=location_id_by_name[row["location"]],
                        time=row["time"],
                        statement=row["statement"],
                    )
                )

            custom_scenario = Scenario(
                id="CUSTOM-001",
                crime=Crime(
                    crime_type=crime_type_clean,
                    location_id=crime_location_id,
                    start_time=crime_start_clean,
                    end_time=crime_end_clean,
                ),
                suspects=suspect_objects,
                locations=location_objects,
                connections=connection_objects,
                evidence=evidence_objects,
                constraints=list(DEFAULT_CONSTRAINTS),
            )

            custom_analysis = run_full_analysis(custom_scenario)

            st.session_state.custom_solved_scenario = custom_scenario
            st.session_state.custom_analysis = custom_analysis

            st.success("Mystery solved using the complete mathematical analysis pipeline.")

        else:
            for error in errors:
                st.error(error)

    scenario = st.session_state.custom_solved_scenario
    analysis = st.session_state.custom_analysis

    if scenario is None or analysis is None:
        st.warning("Enter your mystery data above and click **Solve Mystery** to see the analysis.")
        st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_suspect_name(suspect_id):
    """Return suspect name from suspect ID."""

    for suspect in scenario.suspects:

        if suspect.id == suspect_id:
            return suspect.name

    return suspect_id


def format_suspect_set(values):
    """Format suspect IDs or suspect objects."""

    if not values:
        return "∅"

    formatted = []

    for value in values:

        if hasattr(value, "id"):

            suspect_id = value.id
            suspect_name = value.name

        else:

            suspect_id = value
            suspect_name = get_suspect_name(
                suspect_id
            )

        formatted.append(
            f"{suspect_id} ({suspect_name})"
        )

    return "{ " + ", ".join(formatted) + " }"


def get_location_name(location_id):
    """Return location name from location ID."""

    for location in scenario.locations:

        if location.id == location_id:
            return location.name

    return location_id


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🔎 Crime Mystery Solver")

st.sidebar.markdown(
    """
    ### Project Modules

    - Constraint Analysis
    - Set Theory
    - Predicate Logic
    - Graph Theory
    - CSP / Backtracking
    - Contradiction Detection
    - Solution Validation
    - Mathematical Reasoning
    """
)

st.sidebar.divider()

show_case = st.sidebar.checkbox(
    "Case Information",
    value=True,
)

show_constraints = st.sidebar.checkbox(
    "Constraint Analysis",
    value=True,
)

show_sets = st.sidebar.checkbox(
    "Set Theory Analysis",
    value=True,
)

show_logic = st.sidebar.checkbox(
    "Predicate Logic",
    value=True,
)

show_graph = st.sidebar.checkbox(
    "Graph Analysis",
    value=True,
)

show_csp = st.sidebar.checkbox(
    "CSP Analysis",
    value=True,
)

show_contradictions = st.sidebar.checkbox(
    "Contradiction Detection",
    value=True,
)

show_validation = st.sidebar.checkbox(
    "Solution Validation",
    value=True,
)

show_reasoning = st.sidebar.checkbox(
    "Mathematical Reasoning",
    value=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🔎 Mathematical Crime Mystery Solver'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Scenario Generation and Constraint-Based Analysis '
    'using Discrete Mathematics'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# CASE INFORMATION
# ============================================================

if show_case:

    st.markdown(
        '<div class="section-title">'
        '📋 Case Information'
        '</div>',
        unsafe_allow_html=True,
    )

    crime = scenario.crime

    if crime:

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Crime",
                crime.crime_type,
            )

        with col2:

            st.metric(
                "Crime Location",
                get_location_name(
                    crime.location_id
                ),
            )

        with col3:

            st.metric(
                "Start Time",
                str(crime.start_time),
            )

        with col4:

            st.metric(
                "End Time",
                str(crime.end_time),
            )

    # --------------------------------------------------------
    # Suspects
    # --------------------------------------------------------

    st.markdown("### Suspects")

    suspect_data = []

    for suspect in scenario.suspects:

        suspect_data.append(
            {
                "ID": suspect.id,
                "Name": suspect.name,
            }
        )

    st.dataframe(
        pd.DataFrame(suspect_data),
        width="stretch",
        hide_index=True,
    )

    # --------------------------------------------------------
    # Locations
    # --------------------------------------------------------

    st.markdown("### Locations")

    location_data = []

    for location in scenario.locations:

        location_data.append(
            {
                "ID": location.id,
                "Location": location.name,
            }
        )

    st.dataframe(
        pd.DataFrame(location_data),
        width="stretch",
        hide_index=True,
    )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    st.markdown("### Evidence")

    evidence_data = []

    for evidence in scenario.evidence:

        description = getattr(
            evidence,
            "description",
            getattr(
                evidence,
                "statement",
                "",
            ),
        )

        evidence_data.append(
            {
                "Evidence ID": evidence.id,
                "Type": evidence.evidence_type,
                "Suspect": evidence.suspect_id,
                "Location": get_location_name(
                    evidence.location_id
                ),
                "Time": str(evidence.time)
                if evidence.time is not None
                else "N/A",
                "Description": description,
            }
        )

    st.dataframe(
        pd.DataFrame(evidence_data),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# STEP 3 - CONSTRAINT ANALYSIS
# ============================================================

if show_constraints:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '1️⃣ Constraint Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Each suspect is evaluated against:

        - Presence
        - Access
        - Valid Alibi
        - Availability
        - Reachability
        - All Constraints
        """
    )

    st.dataframe(
        pd.DataFrame(
            analysis.constraint_rows
        ),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "### Constraint-Based Candidates"
    )

    st.info(
        format_suspect_set(
            analysis.constraint_candidates
        )
    )


# ============================================================
# STEP 4 - SET THEORY
# ============================================================

if show_sets:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '2️⃣ Set Theory Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        The solver represents every constraint as a set.

        The final candidate set is obtained through:

        **Possible = Access ∩ Presence ∩ Availability ∩ Reachability**
        """
    )

    set_analysis = analysis.set_analysis

    access_set = set_analysis.get(
        "access",
        set(),
    )

    presence_set = set_analysis.get(
        "presence",
        set(),
    )

    availability_set = set_analysis.get(
        "availability",
        set(),
    )

    reachability_set = set_analysis.get(
        "reachability",
        set(),
    )

    possible_set = set_analysis.get(
        "possible",
        set(),
    )

    set_data = [
        {
            "Set": "Access",
            "Suspects": format_suspect_set(
                access_set
            ),
        },
        {
            "Set": "Presence",
            "Suspects": format_suspect_set(
                presence_set
            ),
        },
        {
            "Set": "Availability",
            "Suspects": format_suspect_set(
                availability_set
            ),
        },
        {
            "Set": "Reachability",
            "Suspects": format_suspect_set(
                reachability_set
            ),
        },
        {
            "Set": "Possible",
            "Suspects": format_suspect_set(
                possible_set
            ),
        },
    ]

    st.dataframe(
        pd.DataFrame(set_data),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "### Mathematical Intersection"
    )

    st.latex(
        r"""
        Possible =
        Access \cap Presence \cap Availability
        \cap Reachability
        """
    )

    st.code(
        "Possible = "
        + str(access_set)
        + " ∩ "
        + str(presence_set)
        + " ∩ "
        + str(availability_set)
        + " ∩ "
        + str(reachability_set)
        + " = "
        + str(possible_set),
        language="text",
    )

    st.success(
        "Final Set-Theoretic Candidate Set: "
        + format_suspect_set(
            possible_set
        )
    )


# ============================================================
# STEP 5 - PREDICATE LOGIC
# ============================================================

if show_logic:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '3️⃣ Predicate Logic Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Predicate logic converts the crime constraints
        into logical rules and evaluates every suspect.
        """
    )

    st.markdown(
        "### Logical Rules"
    )

    for rule in analysis.rules:

        antecedent_text = str(
            rule.antecedent
        )

        consequent_text = ", ".join(
            str(consequent)
            for consequent in rule.consequents
        )

        st.write(
            f"**{rule.name}:** "
            f"{antecedent_text} → "
            f"{consequent_text}"
        )

    st.markdown(
        "### Suspect Evaluation"
    )

    logic_data = []

    for evaluation in analysis.logic_evaluations:

        suspect = evaluation.suspect

        logic_data.append(
            {
                "ID": suspect.id,
                "Suspect": suspect.name,
                "Logically Possible": evaluation.satisfied,
                "Facts": ", ".join(
                    str(fact)
                    for fact in evaluation.facts
                ),
                "Failed Predicates": ", ".join(
                    str(predicate)
                    for predicate in evaluation.failed_predicates
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(logic_data),
        width="stretch",
        hide_index=True,
    )

    st.info(
        "Logical candidates: "
        + format_suspect_set(
            analysis.logical_candidates
        )
    )


# ============================================================
# STEP 6 - GRAPH ANALYSIS
# ============================================================

if show_graph:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '4️⃣ Graph Theory Analysis'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        Locations are represented as graph vertices
        and connections as weighted edges.
        """
    )

    # The graph itself is built by the existing graph module.
    graph = build_scene_graph(
        scenario
    )

    st.markdown(
        "### Graph Vertices"
    )

    node_data = []

    for node in graph.nodes:

        node_data.append(
            {
                "Node ID": node,
                "Location": graph.nodes[node].get(
                    "name",
                    get_location_name(node),
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(node_data),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "### Graph Edges"
    )

    edge_data = []

    for source, target, data in graph.edges(
        data=True
    ):

        edge_data.append(
            {
                "From": source,
                "To": target,
                "Travel Time": data.get(
                    "travel_time",
                    data.get(
                        "weight",
                        "N/A",
                    ),
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(edge_data),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "### Reachability Analysis"
    )

    reachability_data = []

    for item in analysis.graph_results:

        suspect = item["Suspect"]
        result = item["Result"]

        path = result.get(
            "path",
            [],
        )

        reachability_data.append(
            {
                "ID": item["ID"],
                "Suspect": suspect,
                "Source": result.get(
                    "source",
                    "N/A",
                ),
                "Source Time": str(
                    result.get(
                        "source_time",
                        "N/A",
                    )
                ),
                "Available Time": str(
                    result.get(
                        "available_time",
                        "N/A",
                    )
                ),
                "Path": " → ".join(
                    str(node)
                    for node in path
                )
                if path
                else "None",
                "Travel Time": result.get(
                    "travel_time",
                    "N/A",
                ),
                "Reachable": result.get(
                    "reachable",
                    False,
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(reachability_data),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# STEP 7 - CSP ANALYSIS
# ============================================================

if show_csp:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '5️⃣ Constraint Satisfaction Problem'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        The crime investigation is represented as a
        Constraint Satisfaction Problem.

        The solver uses backtracking to search for
        valid assignments.
        """
    )

    csp_result = analysis.csp_result
    csp_suspects = analysis.csp_candidates
    csp_classification = analysis.csp_classification

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "CSP Candidates",
            len(csp_suspects),
        )

    with col2:

        st.metric(
            "Classification",
            str(csp_classification),
        )

    st.markdown(
        "### CSP Candidates"
    )

    st.info(
        format_suspect_set(
            csp_suspects
        )
    )

    st.markdown(
        "### Search Statistics"
    )

    search_data = [
        {
            "Metric": "Nodes Explored",
            "Value": csp_result.nodes_explored,
        },
        {
            "Metric": "Rejected Assignments",
            "Value": csp_result.rejected_assignments,
        },
        {
            "Metric": "Valid Assignments",
            "Value": len(
                csp_result.assignments
            ),
        },
    ]

    st.dataframe(
        pd.DataFrame(search_data),
        width="stretch",
        hide_index=True,
    )


# ============================================================
# STEP 8 - CONTRADICTION DETECTION
# ============================================================

if show_contradictions:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '6️⃣ Contradiction Detection'
        '</div>',
        unsafe_allow_html=True,
    )

    contradiction_report = analysis.contradiction_report
    contradictions = contradiction_report.contradictions

    st.write(
        f"Checked evidence: "
        f"{contradiction_report.checked_evidence}"
    )

    st.write(
        f"Checked connections: "
        f"{contradiction_report.checked_connections}"
    )

    if contradictions:

        st.warning(
            f"{len(contradictions)} "
            "contradiction(s) detected."
        )

        contradiction_data = []

        for contradiction in contradictions:

            contradiction_data.append(
                {
                    "Type": contradiction.contradiction_type,
                    "Severity": contradiction.severity,
                    "Description": contradiction.description,
                    "Evidence IDs": ", ".join(
                        contradiction.evidence_ids
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(
                contradiction_data
            ),
            width="stretch",
            hide_index=True,
        )

    else:

        st.success(
            "No contradictions detected "
            "in the current scenario."
        )


# ============================================================
# STEP 9 - SOLUTION VALIDATION
# ============================================================

if show_validation:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '7️⃣ Solution Validation'
        '</div>',
        unsafe_allow_html=True,
    )

    validation = analysis.validation

    validation_data = [
        {
            "Validation": "Status",
            "Result": validation.status,
        },
        {
            "Validation": "Candidates",
            "Result": format_suspect_set(
                validation.candidates
            ),
        },
        {
            "Validation": "Candidate Count",
            "Result": validation.candidate_count,
        },
        {
            "Validation": "Contradiction Count",
            "Result": validation.contradiction_count,
        },
        {
            "Validation": "CSP Solution Count",
            "Result": validation.csp_solution_count,
        },
        {
            "Validation": "Constraint Model Agrees",
            "Result": validation.constraint_model_agrees,
        },
        {
            "Validation": "Explanation",
            "Result": validation.explanation,
        },
    ]

    validation_df = pd.DataFrame(validation_data)

    # Keep the Result column Arrow-compatible.
    # It contains strings, integers, and booleans in the validation table.
    validation_df["Result"] = validation_df["Result"].astype(str)

    st.dataframe(
        validation_df,
        width="stretch",
        hide_index=True,
    )

    if validation.warnings:

        for warning in validation.warnings:

            st.warning(warning)


# ============================================================
# STEP 11 - MATHEMATICAL REASONING
# ============================================================

if show_reasoning:

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '8️⃣ Mathematical Reasoning'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        The reasoning engine explains why each suspect
        survives or fails the mathematical constraints.
        """
    )

    reasoning_report = analysis.reasoning_report

    st.markdown(
        "### Set-Based Reasoning"
    )

    st.latex(
        r"""
        Possible =
        Access \cap Presence \cap Availability
        \cap Reachability
        """
    )

    st.success(
        "Final Possible Set: "
        + format_suspect_set(
            reasoning_report.possible_set
        )
    )

    st.markdown(
        "### Reasoning Trace"
    )

    reasoning_data = []

    for step in reasoning_report.reasoning_steps:

        reasoning_data.append(
            {
                "Step": step.number,
                "Title": step.title,
                "Mathematical Expression": step.mathematical_expression,
                "Explanation": step.explanation,
                "Remaining": format_suspect_set(
                    step.remaining_suspects
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(reasoning_data),
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        "### Suspect-by-Suspect Reasoning"
    )

    for suspect_reason in reasoning_report.suspect_reasons:

        suspect_id = suspect_reason.suspect_id
        suspect_name = suspect_reason.suspect_name

        if suspect_reason.status == "CANDIDATE":

            st.success(
                f"✅ {suspect_name} "
                f"({suspect_id}) satisfies "
                "all constraints."
            )

        else:

            st.error(
                f"❌ {suspect_name} "
                f"({suspect_id}) is eliminated."
            )

        for reason in suspect_reason.reasons:

            st.write(
                f"• {reason}"
            )

    st.info(
        f"Reasoning status: "
        f"{reasoning_report.final_status}. "
        f"{reasoning_report.final_explanation}"
    )


# ============================================================
# FINAL RESULT
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '🎯 Final Mathematical Result'
    '</div>',
    unsafe_allow_html=True,
)

final_candidates = analysis.final_candidates
final_status = analysis.final_status

if final_status == "INCONSISTENT SCENARIO":

    st.error(
        "INCONSISTENT SCENARIO — "
        "Contradictory evidence prevents a validated result."
    )

elif final_status == "NO SOLUTION":

    st.error(
        "NO SOLUTION — No suspect satisfies "
        "all constraints."
    )

elif final_status == "UNIQUE SOLUTION":

    candidate = final_candidates[0]

    st.success(
        f"UNIQUE SOLUTION — Candidate: "
        f"{candidate.name} ({candidate.id})"
    )

else:

    st.warning(
        "MULTIPLE SOLUTIONS — More than one "
        "suspect satisfies all constraints."
    )

    st.info(
        "Candidates: "
        + format_suspect_set(
            final_candidates
        )
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#777777;">

    <b>Mathematical Crime Mystery Solver</b><br>

    Discrete Mathematics Course Project<br>

    Constraint Satisfaction • Set Theory • Predicate Logic •
    Graph Theory • CSP • Mathematical Reasoning

    </div>
    """,
    unsafe_allow_html=True,
)