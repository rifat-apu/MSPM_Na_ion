import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pybamm
from Models.spm import build_spm_simulation, COMPOSITIONS
from Models.mspm import build_mspm_simulation

def main():
    composition_x = 0.50
    comp_info = COMPOSITIONS[composition_x]
    print(f"Running comparative simulation for {comp_info['name']} (x = {composition_x})...")

    protocol = pybamm.Experiment(["Charge at 1C until 4.2V"])

    print("\n1. Solving Standard Single Particle Model (SPM)...")
    sim_spm = build_spm_simulation(composition_x=composition_x, experiment=protocol)
    sol_spm = sim_spm.solve()
    t_spm = sol_spm["Time [s]"].entries[-1]
    v_spm = sol_spm["Terminal voltage [V]"].entries[-1]
    print(f"   SPM completed in {t_spm / 60.0:.2f} min (Final Voltage: {v_spm:.3f} V)")

    print("\n2. Solving Modified Single Particle Model (MSPM with stress)...")
    sim_mspm = build_mspm_simulation(composition_x=composition_x, experiment=protocol)
    sol_mspm = sim_mspm.solve()
    t_mspm = sol_mspm["Time [s]"].entries[-1]
    v_mspm = sol_mspm["Terminal voltage [V]"].entries[-1]

    stress_key = "X-averaged positive particle surface tangential stress [Pa]"
    max_stress = None
    try:
        max_stress = max(sol_mspm[stress_key].entries) / 1e6
        print(f"   MSPM completed in {t_mspm / 60.0:.2f} min (Final Voltage: {v_mspm:.3f} V)")
        print(f"   Peak Surface Tangential Stress: {max_stress:.2f} MPa")
    except Exception:
        print(f"   MSPM completed in {t_mspm / 60.0:.2f} min (Final Voltage: {v_mspm:.3f} V)")

    print("\n--- Summary Comparison ---")
    print(f"Composition: {comp_info['name']}")
    print(f"SPM Charge Time:  {t_spm / 60.0:.2f} min, Final Voltage: {v_spm:.3f} V")
    print(f"MSPM Charge Time: {t_mspm / 60.0:.2f} min, Final Voltage: {v_mspm:.3f} V")
    if max_stress is not None:
        print(f"MSPM Peak Surface Tangential Stress: {max_stress:.2f} MPa")
    print("Simulation finished successfully.")

if __name__ == "__main__":
    main()
