import joblib
import pandas as pd

MODEL_PATH = "triage_model.pkl"


def get_risk_flags(age, symptoms, temperature_c, heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate):
    flags = []
    s = symptoms.lower()

    if spo2 < 90:
        flags.append("Low oxygen saturation")
    if heart_rate > 120:
        flags.append("High heart rate")
    if systolic_bp < 90:
        flags.append("Low systolic blood pressure")
    elif systolic_bp < 100:
        flags.append("Borderline low systolic blood pressure")
    if respiratory_rate > 24:
        flags.append("High respiratory rate")
    if temperature_c >= 39.0:
        flags.append("High fever")
    if age >= 75 and "confusion" in s:
        flags.append("Elderly patient with confusion")
    if "chest pain" in s:
        flags.append("Chest pain symptom")
    if "shortness of breath" in s or "difficulty breathing" in s:
        flags.append("Respiratory distress symptom")
    if "loss of consciousness" in s:
        flags.append("Loss of consciousness symptom")
    if "slurred speech" in s:
        flags.append("Neurological red flag")

    return flags


def get_contextual_risk_factors(age, symptoms, chronic_conditions, medications, family_history):
    factors = []

    symptoms_l = symptoms.lower()
    chronic_l = chronic_conditions.lower()
    meds_l = medications.lower()
    family_l = family_history.lower()

    if age >= 65:
        factors.append("Older age may increase clinical risk")

    if "diabetes" in chronic_l:
        factors.append("Diabetes increases complication risk")

    if "hypertension" in chronic_l:
        factors.append("Hypertension increases cardiovascular risk")

    if "asthma" in chronic_l:
        factors.append("Asthma may worsen respiratory symptoms")

    if "copd" in chronic_l:
        factors.append("COPD increases respiratory deterioration risk")

    if "heart disease" in chronic_l or "cardiac" in chronic_l:
        factors.append("Existing heart disease increases cardiac event risk")

    if "kidney disease" in chronic_l:
        factors.append("Kidney disease may increase systemic risk")

    if "stroke" in family_l:
        factors.append("Family history of stroke is clinically relevant")

    if "heart attack" in family_l or "cardiac" in family_l:
        factors.append("Family cardiac history increases caution level")

    if "anticoagulant" in meds_l or "warfarin" in meds_l or "blood thinner" in meds_l:
        factors.append("Blood thinner use may increase emergency complexity")

    if "insulin" in meds_l:
        factors.append("Insulin use suggests higher monitoring need")

    if "chest pain" in symptoms_l and ("hypertension" in chronic_l or "heart disease" in chronic_l):
        factors.append("Chest pain with cardiac history increases concern")

    if "shortness of breath" in symptoms_l and ("asthma" in chronic_l or "copd" in chronic_l):
        factors.append("Breathing symptoms with respiratory history increase concern")

    return factors


def get_contributing_factors(age, symptoms, temperature_c, heart_rate, systolic_bp, spo2, respiratory_rate,
                             chronic_conditions, medications, family_history):
    factors = []

    symptoms_l = symptoms.lower()
    chronic_l = chronic_conditions.lower()
    meds_l = medications.lower()
    family_l = family_history.lower()

    if spo2 < 90:
        factors.append(("Low oxygen saturation", 5))
    elif spo2 < 94:
        factors.append(("Borderline oxygen saturation", 3))

    if heart_rate > 120:
        factors.append(("Marked tachycardia", 4))
    elif heart_rate > 100:
        factors.append(("Elevated heart rate", 2))

    if systolic_bp < 90:
        factors.append(("Hypotension / low systolic blood pressure", 4))
    elif systolic_bp < 100:
        factors.append(("Borderline low systolic blood pressure", 2))

    if respiratory_rate > 24:
        factors.append(("High respiratory rate", 4))
    elif respiratory_rate > 20:
        factors.append(("Slightly elevated respiratory rate", 2))

    if temperature_c >= 39:
        factors.append(("High fever", 3))
    elif temperature_c >= 38:
        factors.append(("Fever", 2))

    if "chest pain" in symptoms_l:
        factors.append(("Chest pain symptom", 5))
    if "shortness of breath" in symptoms_l or "difficulty breathing" in symptoms_l:
        factors.append(("Respiratory distress symptom", 5))
    if "confusion" in symptoms_l:
        factors.append(("Confusion symptom", 4))
    if "loss of consciousness" in symptoms_l:
        factors.append(("Loss of consciousness", 5))
    if "slurred speech" in symptoms_l:
        factors.append(("Neurological warning sign", 5))

    if age >= 65:
        factors.append(("Older age risk context", 2))
    if "diabetes" in chronic_l:
        factors.append(("Diabetes comorbidity", 2))
    if "hypertension" in chronic_l:
        factors.append(("Hypertension comorbidity", 2))
    if "heart disease" in chronic_l:
        factors.append(("Heart disease history", 4))
    if "asthma" in chronic_l or "copd" in chronic_l:
        factors.append(("Respiratory disease history", 3))
    if "heart attack" in family_l or "cardiac" in family_l:
        factors.append(("Family cardiac history", 2))
    if "stroke" in family_l:
        factors.append(("Family stroke history", 2))
    if "blood thinner" in meds_l or "warfarin" in meds_l or "anticoagulant" in meds_l:
        factors.append(("Anticoagulant medication risk", 2))

    factors = sorted(factors, key=lambda x: x[1], reverse=True)
    return [factor[0] for factor in factors[:5]]


def recommended_action(triage_label, symptoms, chronic_conditions):
    symptoms_l = symptoms.lower()
    chronic_l = chronic_conditions.lower()

    if triage_label == "Critical":
        if "chest pain" in symptoms_l:
            return "Immediate physician review, cardiac assessment, and emergency intervention."
        if "shortness of breath" in symptoms_l:
            return "Immediate physician review, respiratory support assessment, and emergency intervention."
        return "Immediate physician review and emergency intervention."

    if triage_label == "Urgent":
        if "asthma" in chronic_l or "copd" in chronic_l:
            return "Prioritized evaluation with respiratory-focused assessment."
        return "Prioritized evaluation within a short waiting window."

    return "Standard queue assessment with monitoring and escalation if symptoms worsen."


def generate_explanation(triage_label, contextual_factors, contributing_factors):
    main_reasons = contributing_factors[:3]

    if triage_label == "Critical":
        return (
            f"Patient is classified as Critical mainly due to: "
            f"{', '.join(main_reasons) if main_reasons else 'high-risk indicators'}. "
            f"Additional context: "
            f"{', '.join(contextual_factors[:2]) if contextual_factors else 'no major background factors identified'}. "
            f"Immediate clinical assessment is recommended."
        )

    if triage_label == "Urgent":
        return (
            f"Patient is classified as Urgent due to: "
            f"{', '.join(main_reasons) if main_reasons else 'moderate-risk indicators'}. "
            f"Additional context: "
            f"{', '.join(contextual_factors[:2]) if contextual_factors else 'limited extra background risk'}. "
            f"Early medical review is advised."
        )

    return (
        f"Patient is classified as Non-Urgent because current vitals and symptoms appear relatively stable. "
        f"Key considered factors: "
        f"{', '.join(main_reasons) if main_reasons else 'stable presentation'}. "
        f"Clinical judgment is still required."
    )


def predict_triage(age, gender, symptoms, temperature_c, heart_rate, systolic_bp, diastolic_bp, spo2,
                   respiratory_rate, chronic_conditions="", medications="", family_history=""):
    model = joblib.load(MODEL_PATH)

    input_df = pd.DataFrame([{
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "temperature_c": temperature_c,
        "heart_rate": heart_rate,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "spo2": spo2,
        "respiratory_rate": respiratory_rate,
    }])

    prediction = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    class_names = model.classes_

    prob_map = {cls: float(prob) for cls, prob in zip(class_names, probabilities)}
    risk_score = max(prob_map.values())

    flags = get_risk_flags(
        age, symptoms, temperature_c, heart_rate,
        systolic_bp, diastolic_bp, spo2, respiratory_rate
    )

    contextual_factors = get_contextual_risk_factors(
        age, symptoms, chronic_conditions, medications, family_history
    )

    contributing_factors = get_contributing_factors(
        age, symptoms, temperature_c, heart_rate, systolic_bp, spo2, respiratory_rate,
        chronic_conditions, medications, family_history
    )

    explanation = generate_explanation(
        prediction, contextual_factors, contributing_factors
    )

    action = recommended_action(prediction, symptoms, chronic_conditions)

    return {
        "triage_level": prediction,
        "risk_score": round(risk_score, 3),
        "class_probabilities": prob_map,
        "risk_flags": flags,
        "contextual_risk_factors": contextual_factors,
        "contributing_factors": contributing_factors,
        "explanation": explanation,
        "recommended_action": action,
    }


if __name__ == "__main__":
    result = predict_triage(
        age=68,
        gender="M",
        symptoms="chest pain, shortness of breath, sweating",
        temperature_c=37.8,
        heart_rate=124,
        systolic_bp=92,
        diastolic_bp=60,
        spo2=87,
        respiratory_rate=29,
        chronic_conditions="diabetes, hypertension, heart disease",
        medications="insulin, aspirin",
        family_history="father had heart attack",
    )
    print(result)