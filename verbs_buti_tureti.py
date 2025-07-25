import streamlit as st
import unicodedata
import random
import re

# Function to normalize Lithuanian characters
def normalize(text):
    text = text.lower()
    nfkd_form = unicodedata.normalize("NFKD", text)
    return (
        "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        .replace("  ", " ")
        .strip()
    )

# Place your VERBS dictionary here (exactly the same as in your Flask app)
# [TRUNCATED HERE TO SAVE SPACE – paste your full VERBS dictionary here]

# Streamlit UI
st.set_page_config(page_title="Lithuanian Verb Practice", layout="centered")
st.title("🇱🇹 Lithuanian Verb Practice")

# Session state
if "selected_verb" not in st.session_state:
    st.session_state.selected_verb = "būti"
    st.session_state.selected_type = "+"
    st.session_state.selected_person = "aš"
    st.session_state.result = None
    st.session_state.user_input = ""
    st.session_state.is_correct = None

# Sidebar selection
with st.sidebar:
    st.header("Choose Verb Form")
    st.session_state.selected_verb = st.selectbox("Verb", list(VERBS.keys()), index=list(VERBS.keys()).index(st.session_state.selected_verb))
    st.session_state.selected_type = st.selectbox("Form", ["+", "-", "?", "?-"], index=["+", "-", "?", "?-"].index(st.session_state.selected_type))
    persons = list(VERBS[st.session_state.selected_verb][st.session_state.selected_type].keys())
    st.session_state.selected_person = st.selectbox("Person", persons, index=persons.index(st.session_state.selected_person))

english, lithuanian = VERBS[st.session_state.selected_verb][st.session_state.selected_type][st.session_state.selected_person]

st.subheader("🔤 Translate this into Lithuanian:")
st.markdown(f"**{english}**")

# Text input
st.session_state.user_input = st.text_input("Your answer:", st.session_state.user_input)

# Submit and check
if st.button("Check Answer"):
    user_input = normalize(st.session_state.user_input)
    correct_normalized = normalize(lithuanian)
    correct_variants = [correct_normalized]

    # Accept jis/ji or jie/jos variations
    if re.search(r"(?i)jis\s*/\s*ji", lithuanian):
        correct_variants.append(normalize(re.sub(r"(?i)jis\s*/\s*ji", "Jis", lithuanian)))
        correct_variants.append(normalize(re.sub(r"(?i)jis\s*/\s*ji", "Ji", lithuanian)))
    if re.search(r"(?i)jie\s*/\s*jos", lithuanian):
        correct_variants.append(normalize(re.sub(r"(?i)jie\s*/\s*jos", "Jie", lithuanian)))
        correct_variants.append(normalize(re.sub(r"(?i)jie\s*/\s*jos", "Jos", lithuanian)))

    # Accept no-subject version
    subject = st.session_state.selected_person.split("/")[0].strip().lower()
    if lithuanian.lower().startswith(subject):
        no_subject_variant = normalize(lithuanian[len(subject):].strip())
        correct_variants.append(no_subject_variant)

    if any(user_input == variant or user_input in variant for variant in correct_variants):
        st.session_state.result = lithuanian
        st.session_state.is_correct = True
    else:
        st.session_state.result = lithuanian
        st.session_state.is_correct = False

# Show result
if st.session_state.result is not None:
    st.markdown("### ✅ Result:")
    if st.session_state.is_correct:
        st.success(f"Correct! 🎉: {st.session_state.result}")
    else:
        st.error(f"Incorrect 😢. Correct answer: {st.session_state.result}")

# Next random question
if st.button("Next"):
    st.session_state.selected_verb = random.choice(list(VERBS.keys()))
    st.session_state.selected_type = random.choice(list(VERBS[st.session_state.selected_verb].keys()))
    st.session_state.selected_person = random.choice(list(VERBS[st.session_state.selected_verb][st.session_state.selected_type].keys()))
    st.session_state.user_input = ""
    st.session_state.result = None
    st.session_state.is_correct = None
    st.experimental_rerun()
