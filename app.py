import re
import streamlit as st
from predict import predict_triage

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Explainable AI Emergency Triage",
    layout="wide"
)

# ---------------------------------------------------------
# TRANSLATION DICTIONARIES
# ---------------------------------------------------------
EN_TO_AR_PHRASES = {
    "chest pain, shortness of breath, sweating": "ألم في الصدر، ضيق في التنفس، تعرق",
    "diabetes, hypertension, heart disease": "سكري، ارتفاع ضغط، مرض قلبي",
    "insulin, aspirin": "إنسولين، أسبرين",
    "father had heart attack": "الأب أصيب بجلطة قلبية",
}

AR_TO_EN_PHRASES = {v: k for k, v in EN_TO_AR_PHRASES.items()}

EN_TO_AR_TERMS = {
    "chest pain": "ألم في الصدر",
    "shortness of breath": "ضيق في التنفس",
    "difficulty breathing": "صعوبة في التنفس",
    "sweating": "تعرق",
    "diabetes": "سكري",
    "hypertension": "ارتفاع ضغط",
    "heart disease": "مرض قلبي",
    "insulin": "إنسولين",
    "aspirin": "أسبرين",
    "father": "الأب",
    "mother": "الأم",
    "heart attack": "جلطة قلبية",
    "stroke": "جلطة دماغية",
    "asthma": "ربو",
    "copd": "انسداد رئوي مزمن",
    "kidney disease": "مرض كلوي",
    "fever": "حمى",
    "cough": "سعال",
    "fatigue": "إرهاق",
    "vomiting": "قيء",
    "confusion": "تشوش ذهني",
    "weakness": "ضعف",
    "loss of consciousness": "فقدان الوعي",
    "runny nose": "سيلان الأنف",
    "sore throat": "التهاب الحلق",
}

AR_TO_EN_TERMS = {v: k for k, v in EN_TO_AR_TERMS.items()}

EN_TO_AR_FACTORS = {
    "Low oxygen saturation": "انخفاض تشبع الأكسجين",
    "High heart rate": "ارتفاع معدل نبض القلب",
    "Low systolic blood pressure": "انخفاض ضغط الدم الانقباضي",
    "Borderline low systolic blood pressure": "ضغط الدم الانقباضي منخفض بشكل حدودي",
    "High respiratory rate": "ارتفاع معدل التنفس",
    "High fever": "حمى شديدة",
    "Elderly patient with confusion": "مريض كبير في السن مع تشوش ذهني",
    "Chest pain symptom": "عرض ألم الصدر",
    "Respiratory distress symptom": "عرض ضيق تنفسي",
    "Loss of consciousness symptom": "عرض فقدان الوعي",
    "Neurological red flag": "مؤشر عصبي خطير",
    "Older age may increase clinical risk": "التقدم في العمر قد يزيد الخطورة السريرية",
    "Diabetes increases complication risk": "السكري يزيد خطر المضاعفات",
    "Hypertension increases cardiovascular risk": "ارتفاع الضغط يزيد خطر القلب والأوعية",
    "Asthma may worsen respiratory symptoms": "الربو قد يزيد سوء الأعراض التنفسية",
    "COPD increases respiratory deterioration risk": "مرض الانسداد الرئوي يزيد خطر التدهور التنفسي",
    "Existing heart disease increases cardiac event risk": "وجود مرض قلبي سابق يزيد خطر الحدث القلبي",
    "Kidney disease may increase systemic risk": "مرض الكلى قد يزيد الخطورة العامة",
    "Family history of stroke is clinically relevant": "التاريخ العائلي للجلطة الدماغية مهم سريريًا",
    "Family cardiac history increases caution level": "التاريخ العائلي القلبي يستدعي مزيدًا من الحذر",
    "Blood thinner use may increase emergency complexity": "استخدام مميعات الدم قد يزيد تعقيد الحالة الطارئة",
    "Insulin use suggests higher monitoring need": "استخدام الإنسولين يشير إلى الحاجة لمراقبة أكبر",
    "Chest pain with cardiac history increases concern": "ألم الصدر مع تاريخ قلبي يزيد القلق السريري",
    "Breathing symptoms with respiratory history increase concern": "الأعراض التنفسية مع تاريخ مرضي تنفسي تزيد القلق",
    "Marked tachycardia": "تسارع شديد في نبض القلب",
    "Hypotension / low systolic blood pressure": "هبوط ضغط الدم / انخفاض الضغط الانقباضي",
    "Fever": "حمى",
    "Elevated heart rate": "ارتفاع نبض القلب",
    "Borderline oxygen saturation": "تشبع أكسجين حدودي",
    "Slightly elevated respiratory rate": "ارتفاع طفيف في معدل التنفس",
    "Confusion symptom": "عرض التشوش الذهني",
    "Loss of consciousness": "فقدان الوعي",
    "Neurological warning sign": "علامة تحذير عصبية",
    "Older age risk context": "عامل خطورة متعلق بالعمر",
    "Diabetes comorbidity": "مرض مصاحب: السكري",
    "Hypertension comorbidity": "مرض مصاحب: ارتفاع الضغط",
    "Heart disease history": "تاريخ مرض قلبي",
    "Respiratory disease history": "تاريخ مرض تنفسي",
    "Family cardiac history": "تاريخ عائلي قلبي",
    "Family stroke history": "تاريخ عائلي للجلطة الدماغية",
    "Anticoagulant medication risk": "خطورة مرتبطة بمضادات التخثر",
}

TRIAGE_AR = {
    "Critical": "حرج",
    "Urgent": "عاجل",
    "Non-Urgent": "غير عاجل",
}

DEST_AR = {
    "Resuscitation / Critical Care Area": "منطقة الإنعاش / العناية الحرجة",
    "Emergency Room - High Acuity Bed": "غرفة الطوارئ - سرير عالي الخطورة",
    "Emergency Room - Immediate Physician Review": "غرفة الطوارئ - مراجعة طبية فورية",
    "Observation / Respiratory Review Area": "منطقة الملاحظة / تقييم تنفسي",
    "Urgent Care / Emergency Room Standard Bed": "رعاية عاجلة / سرير طوارئ عادي",
    "General Queue / Standard Assessment Area": "الطابور العام / منطقة التقييم العادي",
}

# ---------------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------------
language = st.sidebar.selectbox("Language / اللغة", ["English", "العربية"], key="ui_language")


def is_ar() -> bool:
    return language == "العربية"


def t(en: str, ar: str) -> str:
    return ar if is_ar() else en


# ---------------------------------------------------------
# SAFER RTL FOR ARABIC
# ---------------------------------------------------------
if is_ar():
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            direction: rtl;
        }

        h1, h2, h3, h4, h5, h6, p, label, div, span {
            text-align: right;
        }

        [data-testid="stMarkdownContainer"] {
            direction: rtl !important;
            text-align: right !important;
        }

        textarea, input {
            direction: rtl !important;
            text-align: right !important;
        }

        [data-testid="stSidebar"] * {
            direction: rtl !important;
            text-align: right !important;
        }

        div[data-baseweb="slider"] {
            direction: ltr !important;
        }

        [data-testid="stNumberInput"] input {
            direction: ltr !important;
            text-align: right !important;
        }

        ul, ol {
            direction: rtl !important;
            text-align: right !important;
            padding-right: 1.5rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------
# TEXT CONVERSION HELPERS
# ---------------------------------------------------------
def translate_text_en_to_ar(text: str) -> str:
    if not text:
        return text

    stripped = text.strip()
    if stripped in EN_TO_AR_PHRASES:
        return EN_TO_AR_PHRASES[stripped]

    result = text
    for en_term in sorted(EN_TO_AR_TERMS.keys(), key=len, reverse=True):
        ar_term = EN_TO_AR_TERMS[en_term]
        result = re.sub(rf"\b{re.escape(en_term)}\b", ar_term, result, flags=re.IGNORECASE)

    result = result.replace(",", "،")
    return result


def translate_text_ar_to_en(text: str) -> str:
    if not text:
        return text

    stripped = text.strip()
    if stripped in AR_TO_EN_PHRASES:
        return AR_TO_EN_PHRASES[stripped]

    result = text
    for ar_term in sorted(AR_TO_EN_TERMS.keys(), key=len, reverse=True):
        en_term = AR_TO_EN_TERMS[ar_term]
        result = result.replace(ar_term, en_term)

    result = result.replace("،", ",")
    return result


def display_to_model_text(text: str) -> str:
    return translate_text_ar_to_en(text) if is_ar() else text


def factor_text(text: str) -> str:
    return EN_TO_AR_FACTORS.get(text, text) if is_ar() else text


def triage_text(text: str) -> str:
    return TRIAGE_AR.get(text, text) if is_ar() else text


def destination_text(text: str) -> str:
    return DEST_AR.get(text, text) if is_ar() else text


def explanation_text(english_text: str, triage_level: str, contributing_factors: list[str], contextual_factors: list[str]) -> str:
    if not is_ar():
        return english_text

    reasons = "، ".join([factor_text(x) for x in contributing_factors[:3]]) if contributing_factors else "مؤشرات خطورة مرتفعة"
    context = "، ".join([factor_text(x) for x in contextual_factors[:2]]) if contextual_factors else "لا توجد عوامل خلفية رئيسية"
    triage_ar = triage_text(triage_level)

    if triage_level == "Critical":
        return f"تم تصنيف المريض على أنه {triage_ar} بشكل أساسي بسبب: {reasons}. كما أن السياق الإضافي يتضمن: {context}. ويوصى بإجراء تقييم سريري فوري."
    if triage_level == "Urgent":
        return f"تم تصنيف المريض على أنه {triage_ar} بسبب: {reasons}. كما أن السياق الإضافي يتضمن: {context}. ويوصى بمراجعة طبية مبكرة."
    return f"تم تصنيف المريض على أنه {triage_ar} لأن العلامات الحيوية والأعراض الحالية تبدو أكثر استقرارًا نسبيًا. ومن أبرز العوامل التي تم أخذها بالاعتبار: {reasons}. ولا يزال الحكم السريري مطلوبًا."


def action_text(english_text: str, triage_level: str, symptoms: str, chronic_conditions: str) -> str:
    if not is_ar():
        return english_text

    symptoms_l = translate_text_ar_to_en(symptoms).lower()
    chronic_l = translate_text_ar_to_en(chronic_conditions).lower()

    if triage_level == "Critical":
        if "chest pain" in symptoms_l:
            return "مراجعة طبية فورية، وتقييم قلبي عاجل، مع تدخل طارئ مباشر."
        if "shortness of breath" in symptoms_l:
            return "مراجعة طبية فورية، وتقييم دعم تنفسي عاجل، مع تدخل طارئ مباشر."
        return "مراجعة طبية فورية وتدخل طارئ مباشر."

    if triage_level == "Urgent":
        if "asthma" in chronic_l or "copd" in chronic_l:
            return "تقييم ذو أولوية مع مراجعة تركز على الجهاز التنفسي."
        return "تقييم ذو أولوية خلال فترة انتظار قصيرة."

    return "إدخال الحالة في المسار العادي مع المراقبة والتصعيد إذا ساءت الأعراض."


# ---------------------------------------------------------
# DESTINATION LOGIC
# ---------------------------------------------------------
def get_destination_prediction(triage_level: str, symptoms: str, spo2: int, systolic_bp: int,
                               respiratory_rate: int, chronic_conditions: str) -> str:
    symptoms_l = symptoms.lower()
    chronic_l = chronic_conditions.lower()

    if triage_level == "Critical":
        if "chest pain" in symptoms_l or "loss of consciousness" in symptoms_l or spo2 < 88:
            return "Resuscitation / Critical Care Area"
        if "shortness of breath" in symptoms_l or respiratory_rate > 28:
            return "Emergency Room - High Acuity Bed"
        return "Emergency Room - Immediate Physician Review"

    if triage_level == "Urgent":
        if "asthma" in chronic_l or "copd" in chronic_l or spo2 < 94:
            return "Observation / Respiratory Review Area"
        return "Urgent Care / Emergency Room Standard Bed"

    return "General Queue / Standard Assessment Area"


def triage_rank(level: str) -> int:
    return {"Non-Urgent": 1, "Urgent": 2, "Critical": 3}.get(level, 0)


# ---------------------------------------------------------
# DEFAULT DISPLAY VALUES
# ---------------------------------------------------------
DEFAULTS_EN = {
    "symptoms": "chest pain, shortness of breath, sweating",
    "chronic_conditions": "diabetes, hypertension, heart disease",
    "medications": "insulin, aspirin",
    "family_history": "father had heart attack",
}

DEFAULTS_AR = {
    "symptoms": "ألم في الصدر، ضيق في التنفس، تعرق",
    "chronic_conditions": "سكري، ارتفاع ضغط، مرض قلبي",
    "medications": "إنسولين، أسبرين",
    "family_history": "الأب أصيب بجلطة قلبية",
}

# ---------------------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------------------
if "main_result" not in st.session_state:
    st.session_state.main_result = None

if "main_input" not in st.session_state:
    st.session_state.main_input = None

if "last_language" not in st.session_state:
    st.session_state.last_language = language

for k in ["symptoms", "chronic_conditions", "medications", "family_history"]:
    if k not in st.session_state:
        st.session_state[k] = DEFAULTS_AR[k] if is_ar() else DEFAULTS_EN[k]

numeric_defaults = {
    "age": 68,
    "gender": "M",
    "temperature_c": 37.8,
    "heart_rate": 124,
    "systolic_bp": 92,
    "diastolic_bp": 60,
    "spo2": 87,
    "respiratory_rate": 29,
}
for k, v in numeric_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------
# HANDLE LANGUAGE SWITCH
# ---------------------------------------------------------
if st.session_state.last_language != language:
    old_language = st.session_state.last_language
    st.session_state.last_language = language

    text_keys = ["symptoms", "chronic_conditions", "medications", "family_history"]

    if old_language == "English" and language == "العربية":
        for key in text_keys:
            st.session_state[key] = translate_text_en_to_ar(st.session_state.get(key, ""))
    elif old_language == "العربية" and language == "English":
        for key in text_keys:
            st.session_state[key] = translate_text_ar_to_en(st.session_state.get(key, ""))

    st.session_state.main_result = None
    st.session_state.main_input = None

    st.rerun()

# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------
st.title(t("Explainable AI Emergency Triage & Decision Support System",
           "نظام فرز الطوارئ الذكي القابل للتفسير ودعم القرار"))

st.caption(t("Hackathon prototype for decision support only. Not a medical diagnosis tool.",
             "نموذج أولي للهاكاثون لدعم القرار فقط، وليس أداة تشخيص طبي."))

# ---------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------
col1, col2 = st.columns(2)

# ---------------------------------------------------------
# INPUTS
# ---------------------------------------------------------
with col1:
    st.subheader(t("Patient Input", "بيانات المريض"))

    age = st.number_input(t("Age", "العمر"), min_value=0, max_value=120, key="age")
    gender = st.selectbox(t("Gender", "الجنس"), ["M", "F"], key="gender")

    symptoms = st.text_area(
        t("Symptoms", "الأعراض"),
        key="symptoms"
    )

    chronic_conditions = st.text_area(
        t("Chronic Conditions / Medical History", "الأمراض المزمنة / التاريخ المرضي"),
        key="chronic_conditions"
    )

    medications = st.text_area(
        t("Current Medications", "الأدوية الحالية"),
        key="medications"
    )

    family_history = st.text_area(
        t("Family History / Genetic Risk", "التاريخ العائلي / المخاطر الوراثية"),
        key="family_history"
    )

    temperature_c = st.number_input(t("Temperature (°C)", "الحرارة (°م)"), min_value=30.0, max_value=45.0, step=0.1, key="temperature_c")
    heart_rate = st.number_input(t("Heart Rate (bpm)", "معدل نبض القلب"), min_value=30, max_value=220, key="heart_rate")
    systolic_bp = st.number_input(t("Systolic Blood Pressure", "ضغط الدم الانقباضي"), min_value=50, max_value=250, key="systolic_bp")
    diastolic_bp = st.number_input(t("Diastolic Blood Pressure", "ضغط الدم الانبساطي"), min_value=30, max_value=150, key="diastolic_bp")
    spo2 = st.number_input(t("Oxygen Saturation (SpO2 %)", "تشبع الأكسجين"), min_value=50, max_value=100, key="spo2")
    respiratory_rate = st.number_input(t("Respiratory Rate", "معدل التنفس"), min_value=5, max_value=60, key="respiratory_rate")

    analyze = st.button(t("Analyze Triage", "تشغيل"), use_container_width=True)

# ---------------------------------------------------------
# ANALYZE ONLY WHEN CLICKED
# ---------------------------------------------------------
if analyze:
    model_symptoms = display_to_model_text(st.session_state.symptoms)
    model_conditions = display_to_model_text(st.session_state.chronic_conditions)
    model_meds = display_to_model_text(st.session_state.medications)
    model_family = display_to_model_text(st.session_state.family_history)

    result = predict_triage(
        age=st.session_state.age,
        gender=st.session_state.gender,
        symptoms=model_symptoms,
        temperature_c=st.session_state.temperature_c,
        heart_rate=st.session_state.heart_rate,
        systolic_bp=st.session_state.systolic_bp,
        diastolic_bp=st.session_state.diastolic_bp,
        spo2=st.session_state.spo2,
        respiratory_rate=st.session_state.respiratory_rate,
        chronic_conditions=model_conditions,
        medications=model_meds,
        family_history=model_family,
    )

    st.session_state.main_result = result
    st.session_state.main_input = {
        "age": st.session_state.age,
        "gender": st.session_state.gender,
        "symptoms": model_symptoms,
        "temperature_c": st.session_state.temperature_c,
        "heart_rate": st.session_state.heart_rate,
        "systolic_bp": st.session_state.systolic_bp,
        "diastolic_bp": st.session_state.diastolic_bp,
        "spo2": st.session_state.spo2,
        "respiratory_rate": st.session_state.respiratory_rate,
        "chronic_conditions": model_conditions,
        "medications": model_meds,
        "family_history": model_family,
    }

# ---------------------------------------------------------
# OUTPUTS
# ---------------------------------------------------------
with col2:
    st.subheader(t("AI Output", "مخرجات الذكاء الاصطناعي"))

    if st.session_state.main_result is not None:
        result = st.session_state.main_result
        saved_input = st.session_state.main_input

        triage_level = result["triage_level"]
        model_confidence = result["risk_score"]
        risk_flags = result["risk_flags"]
        contextual_risk_factors = result["contextual_risk_factors"]
        contributing_factors = result["contributing_factors"]
        explanation = result["explanation"]
        action = result["recommended_action"]
        probs = result["class_probabilities"]

        destination = get_destination_prediction(
            triage_level=triage_level,
            symptoms=saved_input["symptoms"],
            spo2=saved_input["spo2"],
            systolic_bp=saved_input["systolic_bp"],
            respiratory_rate=saved_input["respiratory_rate"],
            chronic_conditions=saved_input["chronic_conditions"],
        )

        shown_triage = triage_text(triage_level)
        shown_destination = destination_text(destination)
        shown_explanation = explanation_text(explanation, triage_level, contributing_factors, contextual_risk_factors)
        shown_action = action_text(action, triage_level, st.session_state.symptoms, st.session_state.chronic_conditions)

        if triage_level == "Critical":
            st.error(f"{t('Triage Level', 'مستوى الفرز')}: {shown_triage}")
        elif triage_level == "Urgent":
            st.warning(f"{t('Triage Level', 'مستوى الفرز')}: {shown_triage}")
        else:
            st.success(f"{t('Triage Level', 'مستوى الفرز')}: {shown_triage}")

        st.metric(t("Model Confidence", "ثقة النموذج"), model_confidence)
        st.caption(t(
            "Model confidence shows how certain the AI is about its prediction, on a scale from 0 to 1.",
            "توضح ثقة النموذج مدى تأكد الذكاء الاصطناعي من تنبؤه، على مقياس من 0 إلى 1."
        ))

        st.markdown(f"### {t('Recommended Destination', 'الوجهة المقترحة')}")
        st.write(shown_destination)

        st.markdown(f"### {t('Explanation', 'التفسير')}")
        st.write(shown_explanation)

        st.markdown(f"### {t('Recommended Action', 'الإجراء المقترح')}")
        st.write(shown_action)

        st.markdown(f"### {t('Contributing Factors', 'العوامل المؤثرة')}")
        if contributing_factors:
            for factor in contributing_factors:
                st.write(f"- {factor_text(factor)}")
        else:
            st.write(t("No major contributing factors detected.", "لا توجد عوامل مؤثرة رئيسية."))

        st.markdown(f"### {t('Contextual Risk Factors', 'عوامل الخطورة السياقية')}")
        if contextual_risk_factors:
            for factor in contextual_risk_factors:
                st.write(f"- {factor_text(factor)}")
        else:
            st.write(t("No major contextual risk factors detected.", "لا توجد عوامل خطورة سياقية رئيسية."))

        st.markdown(f"### {t('Risk Flags', 'مؤشرات الخطورة')}")
        if risk_flags:
            for flag in risk_flags:
                st.write(f"- {factor_text(flag)}")
        else:
            st.write(t("No major red flags detected.", "لا توجد مؤشرات خطورة رئيسية."))

        st.markdown(f"### {t('Class Probabilities', 'احتمالات الفئات')}")
        for label, prob in probs.items():
            st.write(f"**{triage_text(label)}:** {prob:.3f}")

        st.markdown("---")
        st.subheader(t("What-If Simulation", "محاكاة ماذا لو"))
        st.caption(t("Simulate how changing vitals may affect the triage result.",
                     "حاكي كيف يمكن أن يؤثر تغيير العلامات الحيوية على نتيجة الفرز."))

        sim_spo2 = st.slider(t("Simulated SpO2", "الأكسجين المتوقع"), 50, 100, int(saved_input["spo2"]), key="sim_spo2")
        sim_heart_rate = st.slider(t("Simulated Heart Rate", "نبض القلب المتوقع"), 30, 220, int(saved_input["heart_rate"]), key="sim_hr")
        sim_systolic_bp = st.slider(t("Simulated Systolic BP", "ضغط الدم الانقباضي المتوقع"), 50, 250, int(saved_input["systolic_bp"]), key="sim_sys")
        sim_respiratory_rate = st.slider(t("Simulated Respiratory Rate", "معدل التنفس المتوقع"), 5, 60, int(saved_input["respiratory_rate"]), key="sim_rr")

        simulate = st.button(t("Run What-If Simulation", "تشغيل المحاكاة"), use_container_width=True)

        if simulate:
            sim_result = predict_triage(
                age=saved_input["age"],
                gender=saved_input["gender"],
                symptoms=saved_input["symptoms"],
                temperature_c=saved_input["temperature_c"],
                heart_rate=sim_heart_rate,
                systolic_bp=sim_systolic_bp,
                diastolic_bp=saved_input["diastolic_bp"],
                spo2=sim_spo2,
                respiratory_rate=sim_respiratory_rate,
                chronic_conditions=saved_input["chronic_conditions"],
                medications=saved_input["medications"],
                family_history=saved_input["family_history"],
            )

            sim_triage = sim_result["triage_level"]
            sim_model_confidence = sim_result["risk_score"]
            sim_destination = get_destination_prediction(
                triage_level=sim_triage,
                symptoms=saved_input["symptoms"],
                spo2=sim_spo2,
                systolic_bp=sim_systolic_bp,
                respiratory_rate=sim_respiratory_rate,
                chronic_conditions=saved_input["chronic_conditions"],
            )

            shown_sim_triage = triage_text(sim_triage)
            shown_sim_destination = destination_text(sim_destination)
            shown_sim_explanation = explanation_text(
                sim_result["explanation"],
                sim_triage,
                sim_result["contributing_factors"],
                sim_result["contextual_risk_factors"],
            )

            st.markdown(f"### {t('Simulated Output', 'الناتج المتوقع')}")

            if sim_triage == "Critical":
                st.error(f"{t('Simulated Triage Level', 'مستوى الفرز المتوقع')}: {shown_sim_triage}")
            elif sim_triage == "Urgent":
                st.warning(f"{t('Simulated Triage Level', 'مستوى الفرز المتوقع')}: {shown_sim_triage}")
            else:
                st.success(f"{t('Simulated Triage Level', 'مستوى الفرز المتوقع')}: {shown_sim_triage}")

            st.metric(t("Simulated Model Confidence", "ثقة النموذج المتوقعة"), sim_model_confidence)

            st.markdown(f"### {t('Simulated Destination', 'الوجهة المتوقعة')}")
            st.write(shown_sim_destination)

            st.markdown(f"### {t('Simulation Explanation', 'تفسير المحاكاة')}")
            st.write(shown_sim_explanation)

            st.markdown(f"### {t('Change Summary', 'ملخص التغيير')}")

            original_rank = triage_rank(triage_level)
            sim_rank = triage_rank(sim_triage)

            if sim_rank > original_rank:
                st.write(t(
                    f"Patient condition escalates from {triage_text(triage_level)} to {triage_text(sim_triage)} under the simulated scenario.",
                    f"تتصاعد حالة المريض من {triage_text(triage_level)} إلى {triage_text(sim_triage)} في هذا السيناريو المتوقع."
                ))
            elif sim_rank < original_rank:
                st.write(t(
                    f"Patient condition de-escalates from {triage_text(triage_level)} to {triage_text(sim_triage)} under the simulated scenario.",
                    f"تنخفض حالة المريض من {triage_text(triage_level)} إلى {triage_text(sim_triage)} في هذا السيناريو المتوقع."
                ))
            else:
                st.write(t(
                    f"Patient remains at {triage_text(triage_level)} under the simulated scenario.",
                    f"تبقى حالة المريض عند مستوى {triage_text(triage_level)} في هذا السيناريو المتوقع."
                ))

            if sim_model_confidence > model_confidence:
                st.write(t(
                    "Model confidence increases in the simulated scenario.",
                    "تزداد ثقة النموذج في هذا السيناريو المتوقع."
                ))
            elif sim_model_confidence < model_confidence:
                st.write(t(
                    "Model confidence decreases in the simulated scenario.",
                    "تنخفض ثقة النموذج في هذا السيناريو المتوقع."
                ))
            else:
                st.write(t(
                    "Model confidence remains unchanged in the simulated scenario.",
                    "تبقى ثقة النموذج دون تغيير في هذا السيناريو المتوقع."
                ))

            if sim_destination != destination:
                st.write(t(
                    f"Recommended destination changes from '{shown_destination}' to '{shown_sim_destination}'.",
                    f"تتغير الوجهة المقترحة من '{shown_destination}' إلى '{shown_sim_destination}'."
                ))

    else:
        st.info(t("Enter patient details and click Analyze Triage.",
                  "أدخل بيانات المريض ثم اضغط تشغيل."))