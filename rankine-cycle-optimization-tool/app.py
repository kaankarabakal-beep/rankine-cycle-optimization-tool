import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import streamlit.components.v1 as components

from rankine_backend import run_full_analysis


# ==========================================================
# Page configuration
# ==========================================================

st.set_page_config(
    page_title="Rankine Cycle Optimization Tool",
    page_icon="🔥️",
    layout="wide"
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF8EC, #FFF4DC, #ffffff);
    }

    /* Main primary button: Run Analysis */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #FFD6A6;
        border: 1px solid #FFD6A6;
        color: #4A2A1A;
        font-weight: 700;
        border-radius: 10px;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #FFD6A6;
        border: 1px solid #FFD6A6;
        color: #4A2A1A;
    }

    div[data-testid="stButton"] > button[kind="primary"]:active {
        background-color: #FFD6A6;
        border: 1px solid #FFD6A6;
        color: #4A2A1A;
    }

    /* Number input + / - buttons */
    button[data-testid="stNumberInputStepUp"],
    button[data-testid="stNumberInputStepDown"] {
        color: #4A2A1A !important;
        border-color: #FFD6A6 !important;
    }

    button[data-testid="stNumberInputStepUp"]:hover,
    button[data-testid="stNumberInputStepDown"]:hover {
        background-color: #FFF0BE !important;
        border-color: #FFD6A6 !important;
        color: #4A2A1A !important;
    }

    button[data-testid="stNumberInputStepUp"]:active,
    button[data-testid="stNumberInputStepDown"]:active {
        background-color: #FFD6A6 !important;
        border-color: #FFD6A6 !important;
        color: #4A2A1A !important;
    }

    /* Focus borders for inputs */
    div[data-baseweb="input"]:focus-within {
        border-color: #FFD6A6 !important;
        box-shadow: 0 0 0 1px #FFD6A6 !important;
    }

    /* Selectbox focus color */
    div[data-baseweb="select"]:focus-within {
        border-color: #FFD6A6 !important;
        box-shadow: 0 0 0 1px #FFD6A6 !important;
    }
    
    /* Sidebar expander title color */
        section[data-testid="stSidebar"] details summary p {
        color: #7A2E1D !important;
        font-weight: 800 !important;
        font-size: 1.10rem !important;
    }
    
    
    
    
    </style>
    """,
    unsafe_allow_html=True
)

def render_optimal_design(best):
    design_rows = ""

    if "P_boiler" in best:
        design_rows += f"""
        <div style="display: flex; justify-content: space-between; gap: 14px;">
            <span style="font-weight: 600;">Boiler Pressure</span>
            <span>{best["P_boiler"] / 1e6:.2f} MPa</span>
        </div>
        """

    if "P_condenser" in best:
        design_rows += f"""
        <div style="display: flex; justify-content: space-between; gap: 14px;">
            <span style="font-weight: 600;">Condenser Pressure</span>
            <span>{best["P_condenser"] / 1e3:.2f} kPa</span>
        </div>
        """

    if "T_turbine_in" in best:
        design_rows += f"""
        <div style="display: flex; justify-content: space-between; gap: 14px;">
            <span style="font-weight: 600;">Turbine Inlet Temperature</span>
            <span>{best["T_turbine_in"] - 273.15:.2f} °C</span>
        </div>
        """

    html = f"""
    <div style="
        width: 100%;
        box-sizing: border-box;
        border: 1px solid #FFE1C7;
        border-radius: 14px;
        padding: 20px 22px;
        background: linear-gradient(135deg, #FFFCF7, #FFF8EC, #ffffff);
        font-family: Arial, sans-serif;
    ">
        <h3 style="
            text-align: center;
            text-decoration: underline;
            margin-top: 0;
            margin-bottom: 18px;
            font-size: 1.35rem;
            font-weight: 700;
            color: #1f1f1f;
        ">
            Optimal Design
        </h3>

        <div style="font-size: 1.08rem; line-height: 2.0;">
            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Thermal Efficiency</span>
                <span>{best["eta"] * 100:.2f} %</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Net Work</span>
                <span>{best["w_net"] / 1000:.2f} kJ/kg</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Heat Input</span>
                <span>{best["q_in"] / 1000:.2f} kJ/kg</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Outlet Quality (x4)</span>
                <span>{best["x4"]:.6f}</span>
            </div>
        </div>

        <div style="
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid #eeeeee;
            font-size: 1.08rem;
            line-height: 2.0;
        ">
            <div style="
                text-align: center;
                font-weight: 700;
                margin-bottom: 6px;
            ">
                Design Point
            </div>

            {design_rows}
        </div>
    </div>
    """

    components.html(html, height=430)

def render_metric_ranges(metric_ranges):
    html = f"""
    <div style="
        width: 100%;
        box-sizing: border-box;
        border: 1px solid #FFE1C7;
        border-radius: 14px;
        padding: 20px 22px;
        background: linear-gradient(135deg, #FFFCF7, #FFF8EC, #ffffff);
        font-family: Arial, sans-serif;
    ">
        <h3 style="
            text-align: center;
            text-decoration: underline;
            margin-top: 0;
            margin-bottom: 18px;
            font-size: 1.35rem;
            font-weight: 700;
            color: #1f1f1f;
        ">
            Metric Ranges
        </h3>

        <div style="font-size: 1.08rem; line-height: 2.0;">
            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Outlet Quality (x4) </span>
                <span>{metric_ranges["x4"]["min"]:.6f} – {metric_ranges["x4"]["max"]:.6f}</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Net Work</span>
                <span>{metric_ranges["w_net"]["min"]:.2f} – {metric_ranges["w_net"]["max"]:.2f} kJ/kg</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Heat Input</span>
                <span>{metric_ranges["q_in"]["min"]:.2f} – {metric_ranges["q_in"]["max"]:.2f} kJ/kg</span>
            </div>

            <div style="display: flex; justify-content: space-between; gap: 14px;">
                <span style="font-weight: 600;">Efficiency</span>
                <span>{metric_ranges["eta"]["min"]:.2f} – {metric_ranges["eta"]["max"]:.2f} %</span>
            </div>
        </div>
    </div>
    """

    components.html(html, height=245)



def render_constraint_check(constraints, best):
    rows = ""

    if constraints["min_quality"] is not None:
        status = "Passed" if best["x4"] >= constraints["min_quality"] else "Failed"
        rows += f"""
        <tr>
            <td>Minimum outlet quality</td>
            <td>x4 ≥ {constraints["min_quality"]:.2f}</td>
            <td>{best["x4"]:.6f}</td>
            <td>{status}</td>
        </tr>
        """

    if constraints["min_net_work"] is not None:
        status = "Passed" if best["w_net"] >= constraints["min_net_work"] else "Failed"
        rows += f"""
        <tr>
            <td>Minimum net work</td>
            <td>w_net ≥ {constraints["min_net_work"] / 1000:.2f} kJ/kg</td>
            <td>{best["w_net"] / 1000:.2f} kJ/kg</td>
            <td>{status}</td>
        </tr>
        """

    if constraints["max_heat_input"] is not None:
        status = "Passed" if best["q_in"] <= constraints["max_heat_input"] else "Failed"
        rows += f"""
        <tr>
            <td>Maximum heat input</td>
            <td>q_in ≤ {constraints["max_heat_input"] / 1000:.2f} kJ/kg</td>
            <td>{best["q_in"] / 1000:.2f} kJ/kg</td>
            <td>{status}</td>
        </tr>
        """

    if constraints["min_efficiency"] is not None:
        status = "Passed" if best["eta"] >= constraints["min_efficiency"] else "Failed"
        rows += f"""
        <tr>
            <td>Minimum efficiency</td>
            <td>η ≥ {constraints["min_efficiency"] * 100:.2f} %</td>
            <td>{best["eta"] * 100:.2f} %</td>
            <td>{status}</td>
        </tr>
        """

    if rows == "":
        rows = """
        <tr>
            <td colspan="4" style="text-align: center;">
                No constraints were applied.
            </td>
        </tr>
        """

    html = f"""
    <div style="
        width: 100%;
        box-sizing: border-box;
        border: 1px solid #FFE1C7;
        border-radius: 14px;
        padding: 20px 22px;
        background: linear-gradient(135deg, #FFFCF7, #FFF8EC, #ffffff);
        font-family: Arial, sans-serif;
        margin-top: 18px;
    ">
        <h3 style="
            text-align: center;
            text-decoration: underline;
            margin-top: 0;
            margin-bottom: 18px;
            font-size: 1.35rem;
            font-weight: 700;
            color: #1f1f1f;;
        ">
            Constraint Check
        </h3>

        <table style="
            width: 100%;
            border-collapse: collapse;
            font-size: 1.02rem;
            color: #1f1f1f;
        ">
            <thead>
                <tr style="border-bottom: 1px solid #E8C6B0;">
                    <th style="text-align: left; padding: 10px;">Constraint</th>
                    <th style="text-align: left; padding: 10px;">Limit</th>
                    <th style="text-align: left; padding: 10px;">Actual Value</th>
                    <th style="text-align: left; padding: 10px;">Status</th>
                </tr>
            </thead>

            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """

    components.html(html, height=260)


# ==========================================================
# Header
# ==========================================================

header_html = """
<div style="
    padding: 24px 28px;
    border-radius: 16px;
    background: linear-gradient(90deg, #fff7ed, #ffffff);
    border: 1px solid #f0e6dc;
    font-family: Arial, sans-serif;
">
    <h1 style="
        margin: 0;
        font-size: 2.2rem;
        font-weight: 750;
        color: #1f1f1f;
    ">
        🔥 Rankine Cycle Optimization Tool
    </h1>

    <p style="
        font-size: 1.05rem;
        margin-top: 10px;
        margin-bottom: 0;
        color: #555555;
    ">
        Interactive thermodynamic analysis with parametric sweeps, engineering constraints,
        and objective-based design optimization.
    </p>

    <p style="
        font-size: 0.92rem;
        margin-top: 12px;
        margin-bottom: 0;
        color: #777777;
    ">
        Developed by <b>Kaan Karabakal</b>
    </p>
</div>
"""

components.html(header_html, height=160)


# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.markdown(
    "<div style='text-align: center; margin-bottom: 22px;'>"
    "<div style='font-size: 2.2rem; margin-bottom: 2px;'>🔥</div>"
    "<h2 style='text-align: center; text-decoration: underline; margin-top: 0; margin-bottom: 0; font-size: 2.0rem; font-weight: 800; color: #7A2E1D;'>"
    "Input Panel"
    "</h2>"
    "</div>",
    unsafe_allow_html=True
)

# ----------------------------------------------------------
# Sweep settings
# ----------------------------------------------------------

with st.sidebar.expander("⚙️ **Sweep Configuration**", expanded=True):
    sweep_type_options = {
        "Boiler Pressure vs. Turbine Inlet Temperature": "boiler_pressure_temperature",
        "Condenser Pressure vs. Turbine Inlet Temperature": "condenser_pressure_temperature",
        "Condenser Pressure vs. Boiler Pressure": "condenser_boiler_pressure"
    }

    selected_sweep_type = st.selectbox(
        "Sweep type",
        list(sweep_type_options.keys())
    )

    sweep_type = sweep_type_options[selected_sweep_type]

# ----------------------------------------------------------
# Cycle efficiencies
# ----------------------------------------------------------

with st.sidebar.expander("🔧 **Component Efficiencies**", expanded=True):
    eta_turbine = st.number_input(
        "Turbine Isentropic Efficiency",
        min_value=0.01,
        max_value=1.0,
        value=1.0,
        step=0.01
    )

    eta_pump = st.number_input(
        "Pump Isentropic Efficiency",
        min_value=0.01,
        max_value=1.0,
        value=1.0,
        step=0.01
    )


# ----------------------------------------------------------
# Sweep inputs
# ----------------------------------------------------------

with st.sidebar.expander("📐 **Operating Ranges**", expanded=True):

    if sweep_type == "boiler_pressure_temperature":
        P_boiler_start = st.number_input("Boiler Pressure Start (MPa)", value=8.0)
        P_boiler_end = st.number_input("Boiler Pressure End (MPa)", value=20.0)
        P_boiler_step = st.number_input("Boiler Pressure Step (MPa)", value=0.1)

        T_turbine_start = st.number_input("Turbine Inlet Temperature Start (°C)", value=426.85)
        T_turbine_end = st.number_input("Turbine Inlet Temperature End (°C)", value=526.85)
        T_turbine_step = st.number_input("Turbine Inlet Temperature Step (°C)", value=1.0)

        P_condenser = st.number_input("Condenser Pressure (kPa)", value=10.0)

        sweep_inputs = {
            "P_boiler_start": P_boiler_start * 1e6,
            "P_boiler_end": P_boiler_end * 1e6,
            "P_boiler_step": P_boiler_step * 1e6,

            "T_turbine_start": T_turbine_start + 273.15,
            "T_turbine_end": T_turbine_end + 273.15,
            "T_turbine_step": T_turbine_step,

            "P_condenser": P_condenser * 1e3,

            "eta_turbine": eta_turbine,
            "eta_pump": eta_pump
        }

    elif sweep_type == "condenser_pressure_temperature":
        P_condenser_start = st.number_input("Condenser Pressure Start (kPa)", value=5.0)
        P_condenser_end = st.number_input("Condenser Pressure End (kPa)", value=30.0)
        P_condenser_step = st.number_input("Condenser Pressure Step (kPa)", value=0.5)

        T_turbine_start = st.number_input("Turbine Inlet Temperature Start (°C)", value=426.85)
        T_turbine_end = st.number_input("Turbine Inlet Temperature End (°C)", value=546.85)
        T_turbine_step = st.number_input("Turbine Inlet Temperature Step (K)", value=1.0)

        P_boiler = st.number_input("Boiler Pressure (MPa)", value=12.0)

        sweep_inputs = {
            "P_condenser_start": P_condenser_start * 1e3,
            "P_condenser_end": P_condenser_end * 1e3,
            "P_condenser_step": P_condenser_step * 1e3,

            "T_turbine_start": T_turbine_start + 273.15,
            "T_turbine_end": T_turbine_end + 273.15,
            "T_turbine_step": T_turbine_step,

            "P_boiler": P_boiler * 1e6,

            "eta_turbine": eta_turbine,
            "eta_pump": eta_pump
        }

    elif sweep_type == "condenser_boiler_pressure":
        P_condenser_start = st.number_input("Condenser Pressure Start (kPa)", value=10.0)
        P_condenser_end = st.number_input("Condenser Pressure End (kPa)", value=32.0)
        P_condenser_step = st.number_input("Condenser Pressure Step (kPa)", value=0.5)

        P_boiler_start = st.number_input("Boiler Pressure Start (MPa)", value=8.0)
        P_boiler_end = st.number_input("Boiler Pressure End (MPa)", value=21.0)
        P_boiler_step = st.number_input("Boiler Pressure Step (MPa)", value=0.5)

        T_turbine_in = st.number_input("Turbine Inlet Temperature (°C)", value=376.85)

        sweep_inputs = {
            "P_condenser_start": P_condenser_start * 1e3,
            "P_condenser_end": P_condenser_end * 1e3,
            "P_condenser_step": P_condenser_step * 1e3,

            "P_boiler_start": P_boiler_start * 1e6,
            "P_boiler_end": P_boiler_end * 1e6,
            "P_boiler_step": P_boiler_step * 1e6,

            "T_turbine_in": T_turbine_in + 273.15,

            "eta_turbine": eta_turbine,
            "eta_pump": eta_pump
        }


# ----------------------------------------------------------
# Constraints
# ----------------------------------------------------------

with st.sidebar.expander("✅ **Design Constraints**", expanded=True):
    use_min_quality = st.checkbox("Minimum Turbine Outlet Quality", value=True)
    min_quality = st.number_input("Minimum x4", value=0.75, step=0.01) if use_min_quality else None

    use_min_net_work = st.checkbox("Minimum Net Work", value=False)
    min_net_work = (
        st.number_input("Minimum Net Work (kJ/kg)", value=1100.0, step=50.0) * 1000
        if use_min_net_work
        else None
    )

    use_max_heat_input = st.checkbox("Maximum Heat Input", value=False)
    max_heat_input = (
        st.number_input("Maximum Heat Input (kJ/kg)", value=3400.0, step=50.0) * 1000
        if use_max_heat_input
        else None
    )

    use_min_efficiency = st.checkbox("Minimum Efficiency", value=False)
    min_efficiency = (
        st.number_input("Minimum Efficiency (%)", value=35.0, step=1.0) / 100
        if use_min_efficiency
        else None
    )

constraints = {
    "min_quality": min_quality,
    "min_net_work": min_net_work,
    "max_heat_input": max_heat_input,
    "min_efficiency": min_efficiency
}


# ----------------------------------------------------------
# Objective
# ----------------------------------------------------------

with st.sidebar.expander("🎯 **Optimization Objective**", expanded=True):
    objective_choice = st.selectbox(
        "Objective",
        [
            "Maximize Thermal Efficiency",
            "Maximize Net Work",
            "Minimize Heat Input",
            "Maximize Turbine Outlet Quality"
        ]
    )

    if objective_choice == "Maximize Thermal Efficiency":
        objective = {"key": "eta", "mode": "max"}
    elif objective_choice == "Maximize Net Work":
        objective = {"key": "w_net", "mode": "max"}
    elif objective_choice == "Minimize Heat Input":
        objective = {"key": "q_in", "mode": "min"}
    else:
        objective = {"key": "x4", "mode": "max"}


# ----------------------------------------------------------
# Display options
# ----------------------------------------------------------

with st.sidebar.expander("🖥️ **Display Options**", expanded=False):
    show_metric_ranges = st.checkbox("Show metric ranges in terminal", value=False)


run_button = st.sidebar.button("Run Analysis", type="primary")


# ==========================================================
# Main page content
# ==========================================================

if not run_button:
    welcome_html = """
    <div style="
        border: 1px solid #d9d9d9;
        border-radius: 16px;
        padding: 24px 28px;
        background-color: #ffffff;
        font-family: Arial, sans-serif;
        margin-top: 18px;
    ">
        <h3 style="
            margin-top: 0;
            margin-bottom: 14px;
            font-size: 1.45rem;
            text-decoration: underline;
            color: #1f1f1f;
        ">
            What this tool does
        </h3>

        <p style="
            font-size: 1.05rem;
            line-height: 1.7;
            color: #444444;
            margin-bottom: 12px;
        ">
            🠲 This application performs a two-variable parametric sweep of a simple Rankine cycle,
            applies engineering constraints, and identifies the optimal valid design according
            to the selected objective.
        </p>

        <p style="
            font-size: 1.05rem;
            line-height: 1.7;
            color: #444444;
            margin-bottom: 0;
        ">
            🠲 The contour map shows thermal efficiency. White regions indicate infeasible designs
            under the selected constraints, while the red star marks the selected optimum point.
        </p>
    </div>

    <div style="
        margin-top: 18px;
        padding: 14px 18px;
        border-radius: 12px;
        background-color: #fff7ed;
        border: 1px solid #f0e6dc;
        font-family: Arial, sans-serif;
        font-size: 1rem;
        color: #555555;
    ">
        Configure the sidebar inputs, then click <b>Run Analysis</b> to generate the optimization map.
    </div>
    """

    components.html(welcome_html, height=360)

if run_button:
    try:
        best, fig, metric_ranges = run_full_analysis(
            sweep_type,
            sweep_inputs,
            constraints,
            objective,
            show_metric_ranges=show_metric_ranges
        )

        if best is None:
            st.warning("No valid design found. Try relaxing the constraints or expanding the sweep range.")

        else:
            graph_col, summary_col = st.columns([2.2, 1])
            with graph_col:
                st.markdown(
                    """
                    <h3 style='text-align: center; text-decoration: underline; margin-bottom: 10px;'>
                        Optimization Map
                    </h3>
                    """,
                    unsafe_allow_html=True
                )

                st.pyplot(fig, use_container_width=True)

            with summary_col:
                st.markdown(
                    """
                    <div style='height: 90px;'></div>
                    """,
                    unsafe_allow_html=True
                )

                render_optimal_design(best)

                st.markdown(
                 """
                    <div style='height: 12px;'></div>
                    """,
                    unsafe_allow_html=True
                )

                render_metric_ranges(metric_ranges)

            render_constraint_check(constraints, best)

    except Exception as error:
        st.error(str(error))
