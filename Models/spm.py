import numpy as np
import pybamm

COMPOSITIONS = {
    0.125: {"name": "Mn 12.5%", "average_voltage": 3.092, "diffusivity": 1.0e-14},
    0.250: {"name": "Mn 25%",   "average_voltage": 3.065, "diffusivity": 1.0e-14},
    0.500: {"name": "Mn 50%",   "average_voltage": 3.082, "diffusivity": 2.4e-14},
    0.625: {"name": "Mn 62.5%", "average_voltage": 3.831, "diffusivity": 1.0e-14},
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

def build_spm_simulation(composition_x=0.50, experiment=None):
    if composition_x not in COMPOSITIONS:
        raise ValueError(f"Composition x={composition_x} not in dataset.")

    data = COMPOSITIONS[composition_x]
    ocv_fn = get_ocv_function(data["average_voltage"])

    model = pybamm.lithium_ion.SPM()
    params = pybamm.ParameterValues("Ai2020")

    params.update({
        "Positive electrode OCP [V]": ocv_fn,
        "Lower voltage cut-off [V]": 2.2,
        "Upper voltage cut-off [V]": 4.5,
        "Positive particle diffusivity [m2.s-1]": data["diffusivity"],
        "Positive electrode nominal capacity [A.h]": 1.0,
        "Positive particle radius [m]": 1.0e-5,
    })

    if experiment is None:
        experiment = pybamm.Experiment(["Charge at 1C until 4.2V"])

    return pybamm.Simulation(model, parameter_values=params, experiment=experiment)
