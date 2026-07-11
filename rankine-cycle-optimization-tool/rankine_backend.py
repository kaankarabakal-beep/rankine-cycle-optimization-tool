from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np

# ==========================================================
#                 INPUTS (SI Units)
# ==========================================================

def rankine_cycle(
    P_boiler,
    P_condenser,
    T_turbine_in,
    eta_turbine,
    eta_pump):


    # ==========================================================
    # Validation of input values
    # ==========================================================
    if P_boiler <= 0:
        raise ValueError("Boiler pressure must be positive.")

    if P_condenser <= 0:
        raise ValueError("Condenser pressure must be positive.")

    if P_condenser >= P_boiler:
        raise ValueError("Boiler pressure must be higher than condenser pressure.")

    if not (0 < eta_pump <= 1):
        raise ValueError("Pump efficiency must be between 0 and 1.")

    if not (0 < eta_turbine <= 1):
        raise ValueError("Turbine efficiency must be between 0 and 1.")

    P_critical = PropsSI("PCRIT", "Water")

    if P_boiler >= P_critical:
        raise ValueError(
            f"Boiler pressure must be below critical pressure "
            f"({P_critical / 1e6:.2f} MPa)."
        )

    T_sat = PropsSI("T", "P", P_boiler, "Q", 1, "Water")

    if T_turbine_in <= T_sat:
        raise ValueError(
            f"Turbine inlet temperature must be above saturation temperature. "
            f"Saturation temperature is: {T_sat - 273.15:.2f} °C"
        )


    # ==========================================================
    # STATE 1, SATURATED LIQUID (CONDENSER OUTLET)
    # ==========================================================

    h1 =PropsSI("H","P", P_condenser, "Q", 0, "Water")
    s1 =PropsSI("S","P", P_condenser, "Q", 0, "Water")
    T1=PropsSI("T", "P", P_condenser, "Q", 0, "Water")
    rho1 =PropsSI("D","P", P_condenser, "Q", 0, "Water")
    v1 =1/rho1

    # ==========================================================
    # STATE 2, COMPRESSED LIQUID (BOILER INLET)
    # ==========================================================
    h2s= h1 + v1*(P_boiler-P_condenser)
    h2= h1+ (h2s-h1)/eta_pump
    s2=PropsSI("S", "P", P_boiler, "H", h2, "Water")
    T2=PropsSI("T", "P", P_boiler, "H", h2, "Water")
    rho2 = PropsSI("D", "P", P_boiler, "H", h2, "Water")
    v2 = 1/rho2

    # ==========================================================
    # STATE 3, SUPER-HEATED VAPOR (TURBINE INLET)
    # ==========================================================

    h3 =PropsSI("H","P", P_boiler, "T", T_turbine_in, "Water")
    s3 =PropsSI("S","P", P_boiler, "T", T_turbine_in, "Water")
    rho3 =PropsSI("D","P", P_boiler, "T", T_turbine_in, "Water")
    v3 =1/rho3



    # ==========================================================
    # STATE 4, SUPER-HEATED VAPOR/ SATURATED LIQUID (TURBINE OUTLET)
    # ==========================================================
    s4s=s3
    h4s=PropsSI("H" ,"P", P_condenser, "S", s4s, "Water")
    h4= h3 - eta_turbine*(h3-h4s)
    s4=PropsSI("S", "P", P_condenser, "H", h4, "Water")
    T4=PropsSI("T", "P", P_condenser, "H", h4, "Water")
    x4=PropsSI("Q", "P", P_condenser, "H", h4, "Water")

    # ==========================================================
    # Finding Work, Heat Transfer and Efficiency values.
    # ==========================================================
    w_pump=h2-h1
    w_turbine=h3-h4
    w_net=w_turbine - w_pump
    q_in=h3-h2
    n_thermal= w_net/q_in




    return {
    1: {
        "P": P_condenser,
        "T": T1,
        "h": h1,
        "s": s1,
        "v": v1
    },

    2: {
        "P": P_boiler,
        "T": T2,
        "h": h2,
        "s": s2,
        "v": v2
    },

    3: {
        "P": P_boiler,
        "T": T_turbine_in,
        "h": h3,
        "s": s3,
        "v": v3
    },

    4: {
        "P": P_condenser,
        "T": T4,
        "h": h4,
        "s": s4,
        "x": x4
    },

    "performance": {
        "w_pump": w_pump,
        "w_turbine": w_turbine,
        "w_net": w_net,
        "q_in": q_in,
        "eta": n_thermal
    }
}

def pressure_sweep_boiler(
        P_start,
        P_end,
        step,
        P_condenser,
        T_turbine_in,
        eta_turbine,
        eta_pump
):
    results=[]

    P=P_start

    while P<=P_end:

        cycle=rankine_cycle(
            P,
            P_condenser,
            T_turbine_in,
            eta_turbine,
            eta_pump
        )
        results.append({
            "P_boiler":P,
            "eta": cycle["performance"]["eta"],
            "w_net":cycle["performance"]["w_net"],
            "q_in": cycle["performance"]["q_in"],
            "x4": cycle[4]["x"]
        })

        P+= step

    return results

def pressure_sweep_condenser(
        P_start,
        P_end,
        step,
        P_boiler,
        T_turbine_in,
        eta_turbine,
        eta_pump
):
    results=[]

    P=P_start

    while P<=P_end:

        cycle=rankine_cycle(
            P_boiler,
            P,
            T_turbine_in,
            eta_turbine,
            eta_pump
        )
        results.append({
            "P_condenser":P,
            "eta": cycle["performance"]["eta"],
            "w_net":cycle["performance"]["w_net"],
            "q_in": cycle["performance"]["q_in"],
            "x4": cycle[4]["x"]
        })

        P+= step

    return results

def temperature_sweep(
        T_start,
        T_end,
        step,
        P_boiler,
        P_condenser,
        eta_turbine,
        eta_pump
):
    results=[]
    T=T_start
    while T<=T_end:
        cycle=rankine_cycle(
            P_boiler,
            P_condenser,
            T,
            eta_turbine,
            eta_pump
        )
        results.append({

            "T_turbine_in":T,
            "eta": cycle["performance"]["eta"],
            "w_net":cycle["performance"]["w_net"],
            "q_in": cycle["performance"]["q_in"],
            "x4": cycle[4]["x"]
        })
        T+=step
    return results


# ==========================================================
# Defining a function to print found values. (1 variable)
# ==========================================================

def print_table(title, data):

    print(f"\n{title}")
    print("-" * 35)

    for key, value in data.items():

        if key == "P":
            print(f"P = {value/1000:.2f} kPa")

        elif key == "T":
            print(f"T = {value-273.15:.2f} °C")

        elif key == "h":
            print(f"h = {value/1000:.2f} kJ/kg")

        elif key == "s":
            print(f"s = {value/1000:.4f} kJ/kg·K")

        elif key == "v":
            print(f"v = {value:.6f} m³/kg")

        elif key == "x":
            print(f"x = {value:.4f}")

        elif key == "w_pump":
            print(f"Pump work = {value/1000:.2f} kJ/kg")

        elif key == "w_turbine":
            print(f"Turbine work = {value/1000:.2f} kJ/kg")

        elif key == "w_net":
            print(f"Net work = {value/1000:.2f} kJ/kg")

        elif key == "q_in":
            print(f"Heat input = {value/1000:.2f} kJ/kg")

        elif key == "eta":
            print(f"Thermal efficiency = {value*100:.2f} %")

def print_sweep_boiler(results):

    print("\nSWEEP RESULTS")
    print("-" * 70)
    print(f"{'P (MPa)':<10}{'η (%)':<10}{'x4':<10}{'Wnet (kJ/kg)':<18}{'Qin (kJ/kg)':<18}")

    for result in results:
        print(
            f"{result['P_boiler']/1e6:<10.1f}"
            f"{result['eta']*100:<10.2f}"
            f"{result['x4']:<10.4f}"
            f"{result['w_net']/1000:<18.2f}"
            f"{result['q_in']/1000:<18.2f}"
        )
def print_sweep_condenser(results):

    print("\nSWEEP RESULTS")
    print("-" * 70)
    print(f"{'P (kPa)':<10}{'η (%)':<10}{'x4':<10}{'Wnet (kJ/kg)':<18}{'Qin (kJ/kg)':<18}")

    for result in results:
        print(
            f"{result['P_condenser']/1e3:<10.1f}"
            f"{result['eta']*100:<10.2f}"
            f"{result['x4']:<10.4f}"
            f"{result['w_net']/1000:<18.2f}"
            f"{result['q_in']/1000:<18.2f}"
        )
def print_sweep_temperature(results):
    print("\nSWEEP RESULTS")
    print("-" * 70)
    print(f"{'T (°C)':<10}{'η (%)':<10}{'x4':<10}{'Wnet (kJ/kg)':<18}{'Qin (kJ/kg)':<18}")

    for result in results:
        print(
            f"{result['T_turbine_in']-273.15:<10.2f}"
            f"{result['eta']*100:<10.2f}"
            f"{result['x4']:<10.4f}"
            f"{result['w_net']/1000:<18.2f}"
            f"{result['q_in']/1000:<18.2f}"
        )

# ==========================================================
# Defining a function to print found values. (2 variable)
# ==========================================================

def boiler_pressure_temperature_sweep(
        P_start,
        P_end,
        P_step,

        T_start,
        T_end,
        T_step,

        P_condenser,
        eta_turbine,
        eta_pump
):
    results=[]
    P=P_start
    while P<=P_end:
        T=T_start
        while T<= T_end:
            cycle=rankine_cycle(
                P,
                P_condenser,
                T,
                eta_turbine,
                eta_pump,
            )
            results.append({
                "P_boiler": P,
                "T_turbine_in": T,
                "eta":cycle["performance"]["eta"],
                "w_net":cycle["performance"]["w_net"],
                "q_in":cycle["performance"]["q_in"],
                "x4":cycle[4]["x"]
            })
            T+=T_step
        P+=P_step
    return results

def condenser_pressure_temperature_sweep(
        P_start,
        P_end,
        P_step,

        T_start,
        T_end,
        T_step,

        P_boiler,
        eta_turbine,
        eta_pump
):
    results=[]
    P=P_start
    while P<=P_end:
        T=T_start
        while T<= T_end:
            cycle=rankine_cycle(
                P_boiler,
                P,
                T,
                eta_turbine,
                eta_pump,
            )
            results.append({
                "P_condenser": P,
                "T_turbine_in": T,
                "eta":cycle["performance"]["eta"],
                "w_net":cycle["performance"]["w_net"],
                "q_in":cycle["performance"]["q_in"],
                "x4":cycle[4]["x"]
            })
            T+=T_step
        P+=P_step
    return results

def condenser_boiler_pressure(
        P_condenser_start,
        P_condenser_end,
        P_condenser_step,

        P_boiler_start,
        P_boiler_end,
        P_boiler_step,

        T_turbine_in,
        eta_turbine,
        eta_pump

):
    results=[]
    Pc=P_condenser_start
    while Pc<=P_condenser_end:
        Pb=P_boiler_start
        while Pb<=P_boiler_end:
            cycle=rankine_cycle(
                Pb,
                Pc,
                T_turbine_in,
                eta_turbine,
                eta_pump
            )
            results.append({
                "P_condenser": Pc,
                "P_boiler": Pb,
                "eta":cycle["performance"]["eta"],
                "w_net":cycle["performance"]["w_net"],
                "q_in":cycle["performance"]["q_in"],
                "x4":cycle[4]["x"]

            })

            Pb+=P_boiler_step
        Pc+=P_condenser_step
    return results


# ==========================================================
# Defining plot functions to use with Sweep Command (1 Variable).
# ==========================================================

def plot_results(
        results,
        x_key,
        y_key,
        x_label,
        y_label,
        title,
        x_transform=lambda x: x,
        y_transform=lambda y: y,
        marker="o"
):

    x = []
    y = []

    for result in results:
        x.append(x_transform(result[x_key]))
        y.append(y_transform(result[y_key]))

    plt.figure(figsize=(8,5))

    plt.plot(
        x,
        y,
        marker=marker,
        linewidth=2
    )

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    plt.grid(True)

    plt.tight_layout()

    plt.show()


# ==========================================================
# Defining plot functions to use with Sweep Command (2 Variables).
# ==========================================================

def prepare_contour_data(results, x_key, y_key, z_key, use_constraints=False):
    x_values = sorted(list(set(result[x_key] for result in results)))
    y_values = sorted(list(set(result[y_key] for result in results)))

    X, Y = np.meshgrid(x_values, y_values, indexing="ij")

    Z = np.full(
        (len(x_values), len(y_values)),
        np.nan
    )

    x_index = {}
    for i, value in enumerate(x_values):
        x_index[value] = i

    y_index = {}
    for j, value in enumerate(y_values):
        y_index[value] = j

    for result in results:
        i = x_index[result[x_key]]
        j = y_index[result[y_key]]

        if use_constraints and result.get("valid") == False:
            Z[i, j] = np.nan
        else:
            Z[i, j] = result[z_key]

    return X, Y, Z

def prepare_valid_mask(results, x_key, y_key):
    x_values = sorted(list(set(result[x_key] for result in results)))
    y_values = sorted(list(set(result[y_key] for result in results)))

    valid_mask = np.full(
        (len(x_values), len(y_values)),
        False
    )

    x_index = {}
    for i, value in enumerate(x_values):
        x_index[value] = i

    y_index = {}
    for j, value in enumerate(y_values):
        y_index[value] = j

    for result in results:
        i = x_index[result[x_key]]
        j = y_index[result[y_key]]

        valid_mask[i, j] = result.get("valid", True)

    return valid_mask

def find_optimum(results, objective_key="eta", objective_mode="max"):
    valid_results = []

    for result in results:
        if result.get("valid", True):
            valid_results.append(result)

    if len(valid_results) == 0:
        return None

    if objective_mode == "max":
        best = max(valid_results, key=lambda r: r[objective_key])

    elif objective_mode == "min":
        best = min(valid_results, key=lambda r: r[objective_key])

    else:
        raise ValueError("objective_mode must be either 'max' or 'min'.")

    return best

def print_design_summary(best_point, constraints, objective_key="eta"):
    if best_point is None:
        print("\nNo valid design found.")
        print("Try relaxing the constraints or expanding the sweep range.")
        return

    print("\nOptimal Design Summary")
    print("=" * 45)

    if "P_boiler" in best_point:
        print(f"Boiler pressure: {best_point['P_boiler'] / 1e6:.2f} MPa")

    if "P_condenser" in best_point:
        print(f"Condenser pressure: {best_point['P_condenser'] / 1e3:.2f} kPa")

    if "T_turbine_in" in best_point:
        print(f"Turbine inlet temperature: {best_point['T_turbine_in'] - 273.15:.2f} °C")

    print("-" * 45)
    print(f"Thermal efficiency: {best_point['eta'] * 100:.2f} %")
    print(f"Net work: {best_point['w_net'] / 1000:.2f} kJ/kg")
    print(f"Heat input: {best_point['q_in'] / 1000:.2f} kJ/kg")
    print(f"Turbine outlet quality x4: {best_point['x4']:.6f}")

    print("-" * 45)
    print("Constraint check:")

    if constraints.get("min_quality") is not None:
        print(
            f"x4 >= {constraints['min_quality']:.2f}: "
            f"{best_point['x4'] >= constraints['min_quality']}"
        )

    if constraints.get("min_net_work") is not None:
        print(
            f"w_net >= {constraints['min_net_work'] / 1000:.2f} kJ/kg: "
            f"{best_point['w_net'] >= constraints['min_net_work']}"
        )

    if constraints.get("max_heat_input") is not None:
        print(
            f"q_in <= {constraints['max_heat_input'] / 1000:.2f} kJ/kg: "
            f"{best_point['q_in'] <= constraints['max_heat_input']}"
        )

    if constraints.get("min_efficiency") is not None:
        print(
            f"eta >= {constraints['min_efficiency'] * 100:.2f} %: "
            f"{best_point['eta'] >= constraints['min_efficiency']}"
        )

    print("-" * 45)
    print(f"Objective: optimize {objective_key}")


def create_boundaries_from_constraints(
        constraints,
        Z_eta,
        Z_x4,
        Z_w_net,
        Z_q_in
):
    boundaries = []

    if constraints.get("min_quality") is not None:
        boundaries.append({
            "Z": Z_x4,
            "level": constraints["min_quality"],
            "label": f"x4 = {constraints['min_quality']:.2f}",
            "color": "black",
            "linestyle": "solid"
        })

    if constraints.get("min_net_work") is not None:
        boundaries.append({
            "Z": Z_w_net / 1000,
            "level": constraints["min_net_work"] / 1000,
            "label": f"w_net = {constraints['min_net_work'] / 1000:.0f} kJ/kg",
            "color": "blue",
            "linestyle": "dashed"
        })

    if constraints.get("max_heat_input") is not None:
        boundaries.append({
            "Z": Z_q_in / 1000,
            "level": constraints["max_heat_input"] / 1000,
            "label": f"q_in = {constraints['max_heat_input'] / 1000:.0f} kJ/kg",
            "color": "green",
            "linestyle": "dashed"
        })

    if constraints.get("min_efficiency") is not None:
        boundaries.append({
            "Z": Z_eta * 100,
            "level": constraints["min_efficiency"] * 100,
            "label": f"eta = {constraints['min_efficiency'] * 100:.0f}%",
            "color": "purple",
            "linestyle": "dotted"
        })

    return boundaries

def plot_contour(
        X,
        Y,
        Z,
        x_label,
        y_label,
        z_label,
        title,
        x_transform=lambda x: x,
        y_transform=lambda y: y,
        z_transform=lambda z: z,
        boundaries=None,
        best_point=None,
        best_x_key=None,
        best_y_key=None,
        valid_mask=None
):
    fig, ax = plt.subplots(figsize=(8, 6))

    contour = ax.contourf(
        x_transform(X),
        y_transform(Y),
        z_transform(Z),
        levels=20
    )

    fig.colorbar(contour, ax=ax, label=z_label)

    # Invalid region overlay
    if valid_mask is not None:
        invalid_mask = np.where(valid_mask, np.nan, 1)

        ax.contourf(
            x_transform(X),
            y_transform(Y),
            invalid_mask,
            levels=[0.5, 1.5],
            colors="white",
            alpha=0.75
        )

    # Constraint boundary lines
    if boundaries is not None:
        for boundary_data in boundaries:
            boundary = ax.contour(
                x_transform(X),
                y_transform(Y),
                boundary_data["Z"],
                levels=[boundary_data["level"]],
                colors=boundary_data["color"],
                linewidths=2,
                linestyles=boundary_data.get("linestyle", "solid")
            )

            ax.clabel(
                boundary,
                inline=True,
                fontsize=9,
                fmt={boundary_data["level"]: boundary_data["label"]}
            )

    if best_point is not None:
        x_best = x_transform(best_point[best_x_key])
        y_best = y_transform(best_point[best_y_key])

        ax.plot(
            x_best,
            y_best,
            marker="*",
            markersize=18,
            color="red"
        )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    ax.grid(True)

    fig.tight_layout()

    return fig

# ==========================================================
# Constraints
# ==========================================================

def is_valid_design(result, constraints):
    min_quality = constraints.get("min_quality")
    min_net_work = constraints.get("min_net_work")
    max_heat_input = constraints.get("max_heat_input")
    min_efficiency = constraints.get("min_efficiency")

    if min_quality is not None:
        if result["x4"] < min_quality:
            return False

    if min_net_work is not None:
        if result["w_net"] < min_net_work:
            return False

    if max_heat_input is not None:
        if result["q_in"] > max_heat_input:
            return False

    if min_efficiency is not None:
        if result["eta"] < min_efficiency:
            return False

    return True


def apply_constraints(results, constraints):
    for result in results:
        result["valid"] = is_valid_design(
            result,
            constraints
        )

    return results

def run_analysis(
        results,
        constraints,
        objective,
        x_key,
        y_key,
        x_label,
        y_label,
        title,
        x_transform=lambda x: x,
        y_transform=lambda y: y,
        show_metric_ranges=True
):
    # 1. Apply constraints
    results = apply_constraints(
        results,
        constraints
    )

    # 2. Find optimum
    best = find_optimum(
        results,
        objective_key=objective["key"],
        objective_mode=objective["mode"]
    )

    # 3. Print design summary
    print_design_summary(
        best,
        constraints,
        objective_key=objective["key"]
    )

    # 4. Prepare contour data
    X, Y, Z_eta = prepare_contour_data(
        results,
        x_key=x_key,
        y_key=y_key,
        z_key="eta",
        use_constraints=False
    )

    X, Y, Z_x4 = prepare_contour_data(
        results,
        x_key=x_key,
        y_key=y_key,
        z_key="x4",
        use_constraints=False
    )

    X, Y, Z_w_net = prepare_contour_data(
        results,
        x_key=x_key,
        y_key=y_key,
        z_key="w_net",
        use_constraints=False
    )

    X, Y, Z_q_in = prepare_contour_data(
        results,
        x_key=x_key,
        y_key=y_key,
        z_key="q_in",
        use_constraints=False
    )

    # 5. Print metric ranges
    if show_metric_ranges:
        print("\nMetric ranges in sweep domain:")
        print("-" * 45)
        print(f"x4 min/max: {np.nanmin(Z_x4):.6f} / {np.nanmax(Z_x4):.6f}")
        print(f"w_net min/max: {np.nanmin(Z_w_net) / 1000:.2f} / {np.nanmax(Z_w_net) / 1000:.2f} kJ/kg")
        print(f"q_in min/max: {np.nanmin(Z_q_in) / 1000:.2f} / {np.nanmax(Z_q_in) / 1000:.2f} kJ/kg")
        print(f"eta min/max: {np.nanmin(Z_eta) * 100:.2f} / {np.nanmax(Z_eta) * 100:.2f} %")

    # 6. Prepare mask
    valid_mask = prepare_valid_mask(
        results,
        x_key=x_key,
        y_key=y_key
    )

    # 7. Prepare boundaries
    boundaries = create_boundaries_from_constraints(
        constraints,
        Z_eta,
        Z_x4,
        Z_w_net,
        Z_q_in
    )

    # 8. Plot
    fig = plot_contour(
        X,
        Y,
        Z_eta,

        x_label=x_label,
        y_label=y_label,
        z_label="Thermal Efficiency (%)",

        title=title,

        x_transform=x_transform,
        y_transform=y_transform,
        z_transform=lambda z: z * 100,

        boundaries=boundaries,

        best_point=best,
        best_x_key=x_key,
        best_y_key=y_key,

        valid_mask=valid_mask
    )

    metric_ranges = {
    "x4": {
        "min": np.nanmin(Z_x4),
        "max": np.nanmax(Z_x4),
        "unit": ""
    },
    "w_net": {
        "min": np.nanmin(Z_w_net) / 1000,
        "max": np.nanmax(Z_w_net) / 1000,
        "unit": "kJ/kg"
    },
    "q_in": {
        "min": np.nanmin(Z_q_in) / 1000,
        "max": np.nanmax(Z_q_in) / 1000,
        "unit": "kJ/kg"
    },
    "eta": {
        "min": np.nanmin(Z_eta) * 100,
        "max": np.nanmax(Z_eta) * 100,
        "unit": "%"
    }
    }

    return best, fig, metric_ranges

def run_full_analysis(
        sweep_type,
        sweep_inputs,
        constraints,
        objective,
        show_metric_ranges=True
):
    # 1. Run selected sweep
    results = run_sweep(
        sweep_type,
        sweep_inputs
    )

    # 2. Get automatic plot settings
    settings = get_plot_settings(
        sweep_type
    )

    # 3. Run analysis and plot
    best, fig, metric_ranges = run_analysis(
        results,
        constraints,
        objective,

        x_key=settings["x_key"],
        y_key=settings["y_key"],

        x_label=settings["x_label"],
        y_label=settings["y_label"],

        title=settings["title"],

        x_transform=settings["x_transform"],
        y_transform=settings["y_transform"],

        show_metric_ranges=show_metric_ranges
    )

    return best, fig, metric_ranges


def run_sweep(sweep_type, sweep_inputs):
    if sweep_type == "boiler_pressure_temperature":
        return boiler_pressure_temperature_sweep(
            sweep_inputs["P_boiler_start"],
            sweep_inputs["P_boiler_end"],
            sweep_inputs["P_boiler_step"],

            sweep_inputs["T_turbine_start"],
            sweep_inputs["T_turbine_end"],
            sweep_inputs["T_turbine_step"],

            sweep_inputs["P_condenser"],
            sweep_inputs["eta_turbine"],
            sweep_inputs["eta_pump"]
        )

    elif sweep_type == "condenser_pressure_temperature":
        return condenser_pressure_temperature_sweep(
            sweep_inputs["P_condenser_start"],
            sweep_inputs["P_condenser_end"],
            sweep_inputs["P_condenser_step"],

            sweep_inputs["T_turbine_start"],
            sweep_inputs["T_turbine_end"],
            sweep_inputs["T_turbine_step"],

            sweep_inputs["P_boiler"],
            sweep_inputs["eta_turbine"],
            sweep_inputs["eta_pump"]
        )

    elif sweep_type == "condenser_boiler_pressure":
        return condenser_boiler_pressure(
            sweep_inputs["P_condenser_start"],
            sweep_inputs["P_condenser_end"],
            sweep_inputs["P_condenser_step"],

            sweep_inputs["P_boiler_start"],
            sweep_inputs["P_boiler_end"],
            sweep_inputs["P_boiler_step"],

            sweep_inputs["T_turbine_in"],
            sweep_inputs["eta_turbine"],
            sweep_inputs["eta_pump"]
        )

    else:
        raise ValueError("Unknown sweep type.")

def get_plot_settings(sweep_type):
    if sweep_type == "boiler_pressure_temperature":
        return {
            "x_key": "P_boiler",
            "y_key": "T_turbine_in",
            "x_label": "Boiler Pressure (MPa)",
            "y_label": "Turbine Inlet Temperature (°C)",
            "title": "Rankine Cycle Optimization - Boiler Pressure vs Turbine Temperature",
            "x_transform": lambda x: x / 1e6,
            "y_transform": lambda y: y - 273.15
        }

    elif sweep_type == "condenser_pressure_temperature":
        return {
            "x_key": "P_condenser",
            "y_key": "T_turbine_in",
            "x_label": "Condenser Pressure (kPa)",
            "y_label": "Turbine Inlet Temperature (°C)",
            "title": "Rankine Cycle Optimization - Condenser Pressure vs Turbine Temperature",
            "x_transform": lambda x: x / 1e3,
            "y_transform": lambda y: y - 273.15
        }

    elif sweep_type == "condenser_boiler_pressure":
        return {
            "x_key": "P_condenser",
            "y_key": "P_boiler",
            "x_label": "Condenser Pressure (kPa)",
            "y_label": "Boiler Pressure (MPa)",
            "title": "Rankine Cycle Optimization - Condenser Pressure vs Boiler Pressure",
            "x_transform": lambda x: x / 1e3,
            "y_transform": lambda y: y / 1e6
        }

    else:
        raise ValueError("Unknown sweep type.")







# ==========================================================
# INPUT
# ==========================================================



















