# We import libraries:
# random → to generate random values
# pandas → to store data in table format (DataFrame)
import random
import pandas as pd

# Set seed so results are reproducible (same data every run)
random.seed(42)

# -----------------------------
# Symptom categories
# -----------------------------

# These represent HIGH-RISK (critical) cases
CRITICAL_SYMPTOMS = [
    "chest pain, shortness of breath, sweating",
    "severe chest pain radiating to arm",
    "confusion, weakness, low oxygen",
    "shortness of breath, wheezing, chest tightness",
    "high fever, confusion, difficulty breathing",
    "severe abdominal pain, vomiting, low blood pressure",
    "loss of consciousness, weakness",
    "severe headache, slurred speech, dizziness",
]

# MEDIUM severity cases
URGENT_SYMPTOMS = [
    "fever, cough, fatigue",
    "abdominal pain, vomiting",
    "headache, dizziness, nausea",
    "persistent cough, fever, body ache",
    "moderate shortness of breath, cough",
    "back pain, fever",
    "dehydration, vomiting, weakness",
    "migraine, nausea, light sensitivity",
]

# LOW severity cases
NON_URGENT_SYMPTOMS = [
    "sore throat, runny nose",
    "mild fever, cough",
    "ankle pain after fall",
    "minor cut on hand",
    "headache, mild fatigue",
    "ear pain, mild fever",
    "knee pain after exercise",
    "stomach discomfort, bloating",
]

# -----------------------------
# Random gender generator
# -----------------------------
def rand_gender():
    # randomly choose Male or Female
    return random.choice(["M", "F"])

# -----------------------------
# Generate vital signs based on severity
# -----------------------------
def generate_vitals(label: str):
    """
    This function creates realistic vital signs depending on the triage level.
    Critical patients → worse vitals
    Urgent → moderate
    Non-Urgent → normal/stable
    """

    if label == "Critical":
        # Critical patients are usually older and unstable
        age = random.randint(45, 90)
        temperature = round(random.uniform(37.2, 40.2), 1)
        heart_rate = random.randint(110, 145)
        systolic_bp = random.randint(80, 100)
        diastolic_bp = random.randint(50, 65)
        spo2 = random.randint(82, 90)
        respiratory_rate = random.randint(24, 34)

    elif label == "Urgent":
        # Moderate condition
        age = random.randint(20, 75)
        temperature = round(random.uniform(37.0, 39.0), 1)
        heart_rate = random.randint(90, 115)
        systolic_bp = random.randint(100, 130)
        diastolic_bp = random.randint(65, 85)
        spo2 = random.randint(93, 97)
        respiratory_rate = random.randint(18, 25)

    else:
        # Stable patients
        age = random.randint(18, 65)
        temperature = round(random.uniform(36.4, 37.8), 1)
        heart_rate = random.randint(65, 95)
        systolic_bp = random.randint(110, 130)
        diastolic_bp = random.randint(70, 85)
        spo2 = random.randint(97, 100)
        respiratory_rate = random.randint(14, 20)

    # Return all generated values
    return age, temperature, heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate

# -----------------------------
# Build dataset
# -----------------------------
def build_rows(n_critical=120, n_urgent=160, n_non_urgent=180):
    """
    This function creates the full dataset by:
    - generating many patients
    - assigning symptoms + vitals
    - labeling them with triage level
    """

    rows = []

    # Generate CRITICAL patients
    for _ in range(n_critical):
        symptoms = random.choice(CRITICAL_SYMPTOMS)
        age, temperature, heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate = generate_vitals("Critical")

        rows.append({
            "age": age,
            "gender": rand_gender(),
            "symptoms": symptoms,
            "temperature_c": temperature,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
            "triage_label": "Critical",
        })

    # Generate URGENT patients
    for _ in range(n_urgent):
        symptoms = random.choice(URGENT_SYMPTOMS)
        age, temperature, heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate = generate_vitals("Urgent")

        rows.append({
            "age": age,
            "gender": rand_gender(),
            "symptoms": symptoms,
            "temperature_c": temperature,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
            "triage_label": "Urgent",
        })

    # Generate NON-URGENT patients
    for _ in range(n_non_urgent):
        symptoms = random.choice(NON_URGENT_SYMPTOMS)
        age, temperature, heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate = generate_vitals("Non-Urgent")

        rows.append({
            "age": age,
            "gender": rand_gender(),
            "symptoms": symptoms,
            "temperature_c": temperature,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
            "triage_label": "Non-Urgent",
        })

    # Shuffle data so it's not ordered by class
    random.shuffle(rows)

    # Convert list of dictionaries → pandas DataFrame
    return pd.DataFrame(rows)

# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    # Build dataset
    df = build_rows()

    # Save to CSV file
    df.to_csv("triage_data.csv", index=False)

    # Print confirmation
    print("Dataset saved as triage_data.csv")

    # Show first few rows
    print(df.head())