import pandas as pd
import numpy as np
import uuid
import random
import os
from datetime import datetime, timedelta

os.makedirs("../data/raw", exist_ok=True)

# Constants for synthetic data
manufacturers = ["ACME", "NOVA", "SKY", "LUMO", "ORION"]
part_numbers = ["P100","P200","P300","P400","P500"]
test_types = ["TID","SEE_HEAVY_ION","SEE_PROTON","DDD"]
operators = ["Alice","Bob","Charlie","David","Eve"]
test_fixtures = ["FIX1","FIX2","FIX3"]

# Number of rows
N_ROWS = 100_000

# Seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_row(i):
    # Device and test info
    device_id = f"D{i:06d}"
    part_number = random.choice(part_numbers)
    manufacturer = random.choice(manufacturers)
    test_type = random.choice(test_types)
    operator = random.choice(operators)
    test_fixture = random.choice(test_fixtures)

    # Date within last 2 years
    date = datetime.now() - timedelta(days=random.randint(0, 730))

    # Beam energy (MeV)
    beam_energy_MeV = np.random.uniform(1, 150)

    # Dose/Fluence depending on test type
    dose_krad = None
    fluence_cm2 = None
    if test_type == "TID":
        dose_krad = np.random.exponential(scale=15)  # more variability
    if test_type.startswith("SEE"):
        fluence_cm2 = np.random.lognormal(mean=12, sigma=1.2)

    # Voltage and current with noise
    voltage_V = np.random.normal(3.3, 0.15)
    current_mA = np.random.normal(10, 1.5)

    # Random errors
    error_count = np.random.poisson(0.5)

     # Failure probability logic
    failure_prob = 0.01
    if dose_krad:
        failure_prob += min(dose_krad/50, 0.7)  # cap at 70% for TID
    if fluence_cm2:
        failure_prob += min(fluence_cm2/1e6, 0.6)  # cap at 60% for SEE
    failure_prob += error_count * 0.05
    failure = np.random.rand() < min(failure_prob, 0.95)

    # Notes with some metadata errors / typos
    notes_options = ["latchup observed", "burnout detected", "nominal", "minor glitch"]
    notes = random.choice(notes_options)
    # introduce random typos
    if random.random() < 0.05:
        notes = notes.replace("observed", "obseverd")

    # Temperature
    temp_C = np.random.normal(25, 10)  # include outliers

    return {
        "test_id": str(uuid.uuid4()),
        "date": date.isoformat(),
        "device_id": device_id,
        "part_number": part_number,
        "manufacturer": manufacturer,
        "test_type": test_type,
        "beam_energy_MeV": beam_energy_MeV,
        "dose_krad": dose_krad,
        "fluence_cm2": fluence_cm2,
        "voltage_V": voltage_V,
        "current_mA": current_mA,
        "error_count": error_count,
        "failure": failure,
        "notes": notes,
        "test_fixture": test_fixture,
        "temp_C": temp_C,
        "operator": operator
    }

def generate_synthetic_data(n_rows=N_ROWS, filename="/Users/ngtnkiet/Documents/radiation-analyst-project/data/raw/synthetic_radiation_100k.csv"):
    print(f"Generating {n_rows} synthetic radiation test rows...")
    rows = [generate_row(i) for i in range(n_rows)]
    df = pd.DataFrame(rows)
    
    # Introduce some missing values randomly
    for col in ["voltage_V", "current_mA", "temp_C", "dose_krad", "fluence_cm2"]:
        df.loc[df.sample(frac=0.01).index, col] = np.nan  # 1% missing
    
    df.to_csv(filename, index=False)
    print(f"Synthetic data saved to {filename}")

if __name__=="__main__":
    generate_synthetic_data()