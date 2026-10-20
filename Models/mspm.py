import numpy as np
import pybamm

COMPOSITIONS = {
    0.125: {
        "name": "Mn 12.5%",
        "average_voltage": 3.092,
        "volume_change": 6.6875,
        "youngs_modulus": 175.39e9,
        "poisson_ratio": 0.253,
        "diffusivity": 1.0e-14,
    },
    0.250: {
        "name": "Mn 25%",
        "average_voltage": 3.065,
        "volume_change": 9.2712,
        "youngs_modulus": 91.27e9,
        "poisson_ratio": 0.018,
        "diffusivity": 1.0e-14,
    },
    0.500: {
        "name": "Mn 50%",
        "average_voltage": 3.082,
        "volume_change": 1.9897,
        "youngs_modulus": 124.76e9,
        "poisson_ratio": 0.259,
        "diffusivity": 2.4e-14,
    },
    0.625: {
        "name": "Mn 62.5%",
        "average_voltage": 3.831,
        "volume_change": 19.9143,
        "youngs_modulus": 167.03e9,
        "poisson_ratio": 0.266,
        "diffusivity": 1.0e-14,
    },
}

def get_ocv_function(avg_voltage):
    socs = np.linspace(0.005, 0.995, 200)
    voltages = (
        avg_voltage
        + 0.35 * (1.0 - 2.0 * socs)
        + 0.12 * np.log((1.0 - socs) / socs)
        - 0.05 * np.exp(-15.0 * socs)
    )

    def ocv(stoich):
        return pybamm.Interpolant(socs, voltages, stoich)

    return ocv

def compute_partial_molar_volume(volume_change_pct, max_volume_change=19.9143):
    return 1.0e-7 + 1.8e-6 * (volume_change_pct / max_volume_change)

def build_mspm_simulation(composition_x=0.50, experiment=None):
    if composition_x not in COMPOSITIONS:
        raise ValueError(f"Composition x={composition_x} not in dataset.")

    data = COMPOSITIONS[composition_x]
    ocv_fn = get_ocv_function(data["average_voltage"])
    molar_vol = compute_partial_molar_volume(data["volume_change"])

    model_options = {
        "particle mechanics": "swelling only",
        "stress-induced diffusion": "true",
    }
    model = pybamm.lithium_ion.SPM(model_options)
    params = pybamm.ParameterValues("Ai2020")

    params.update({
        "Positive electrode OCP [V]": ocv_fn,
        "Lower voltage cut-off [V]": 2.2,
        "Upper voltage cut-off [V]": 4.5,
        "Positive particle diffusivity [m2.s-1]": data["diffusivity"],
        "Positive electrode Young's modulus [Pa]": data["youngs_modulus"],
        "Positive electrode Poisson's ratio": data["poisson_ratio"],
        "Positive electrode partial molar volume [m3.mol-1]": molar_vol,
        "Positive electrode nominal capacity [A.h]": 1.0,
        "Positive particle radius [m]": 1.0e-5,
    })

    if experiment is None:
        experiment = pybamm.Experiment(["Charge at 1C until 4.2V"])

    return pybamm.Simulation(model, parameter_values=params, experiment=experiment)
