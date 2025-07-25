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

# Verb data structure
VERBS = {
    "būti": {
        "+": {
            "aš": ("I am at home", "Aš esu namie"),
            "tu": ("You (singular) are at home", "Tu esi namie"),
            "jis/ji": ("He/She is at home", "Jis / Ji yra namie"),
            "mes": ("We are at home", "Mes esame namie"),
            "jūs": ("You (plural/formal) are at home", "Jūs esate namie"),
            "jie/jos": ("They are at home", "Jie / Jos yra namie"),
        },
        "-": {
            "aš": ("I am not at home", "Aš nesu namie"),
            "tu": ("You (singular) are not at home", "Tu nesi namie"),
            "jis/ji": ("He/She is not at home", "Jis / Ji nėra namie"),
            "mes": ("We are not at home", "Mes nesame namie"),
            "jūs": ("You (plural/formal) are not at home", "Jūs nesate namie"),
            "jie/jos": ("They are not at home", "Jie / Jos nėra namie"),
        },
        "?": {
            "aš": ("Am I at home?", "Ar aš esu namie?"),
            "tu": ("Are you (singular) at home?", "Ar tu esi namie?"),
            "jis/ji": ("Is he/she at home?", "Ar jis / ji yra namie?"),
            "mes": ("Are we at home?", "Ar mes esame namie?"),
            "jūs": ("Are you (plural/formal) at home?", "Ar jūs esate namie?"),
            "jie/jos": ("Are they at home?", "Ar jie / jos yra namie?"),
        },
        "?-": {
            "aš": ("Aren’t I at home?", "Ar aš nesu namie?"),
            "tu": ("Aren’t you(singular) at home?", "Ar tu nesi namie?"),
            "jis/ji": ("Isn’t he/she at home?", "Ar jis / ji nėra namie?"),
            "mes": ("Aren’t we at home?", "Ar mes nesame namie?"),
            "jūs": ("Aren’t you (plural/formal) at home?", "Ar jūs nesate namie?"),
            "jie/jos": ("Aren’t they at home?", "Ar jie / jos nėra namie?"),
        },
    },
    "turėti": {
        "+": {
            "aš": ("I have a book.", "Aš turiu knygą."),
            "tu": ("You (singular) have a book.", "Tu turi knygą."),
            "jis/ji": ("He/She has a book.", "Jis / Ji turi knygą."),
            "mes": ("We have books.", "Mes turime knygas."),
            "jūs": ("You (plural/formal) have books.", "Jūs turite knygas."),
            "jie/jos": ("They have books.", "Jie / Jos turi knygas."),
        },
        "-": {
            "aš": ("I don’t have a book.", "Aš neturiu knygos."),
            "tu": ("You (singular) don’t have a book.", "Tu neturi knygos."),
            "jis/ji": ("He/She doesn’t have a book.", "Jis / Ji neturi knygos."),
            "mes": ("We don’t have books.", "Mes neturime knygų."),
            "jūs": ("You (plural/formal)don’t have books.", "Jūs neturite knygų."),
            "jie/jos": ("They don’t have books.", "Jie / Jos neturi knygų."),
        },
        "?": {
            "aš": ("Do I have a book?", "Ar aš turiu knygą?"),
            "tu": ("Do you (singular) have a book?", "Ar tu turi knygą?"),
            "jis/ji": ("Does he/she have a book?", "Ar jis / ji turi knygą?"),
            "mes": ("Do we have books?", "Ar mes turime knygas?"),
            "jūs": ("Do you (plural/formal) have books?", "Ar jūs turite knygas?"),
            "jie/jos": ("Do they have books?", "Ar jie / jos turi knygas?"),
        },
        "?-": {
            "aš": ("Don’t I have a book?", "Ar aš neturiu knygos?"),
            "tu": ("Don’t you (singular) have a book?", "Ar tu neturi knygos?"),
            "jis/ji": ("Doesn’t he/she have a book?", "Ar jis / ji neturi knygos?"),
            "mes": ("Don’t we have books?", "Ar mes neturime knygų?"),
            "jūs": ("Don’t you (plural/formal) have books?", "Ar jūs neturite knygų?"),
            "jie/jos": ("Don’t they have books?", "Ar jie / jos neturi knygų?"),
        },
    },
    "eiti": {
        "+": {
            "aš": ("I go to school.", "Aš einu į mokyklą."),
            "tu": ("You (singular) go to school.", "Tu eini į mokyklą."),
            "jis/ji": ("He/She goes to school.", "Jis / Ji eina į mokyklą."),
            "mes": ("We go to school.", "Mes einame į mokyklą."),
            "jūs": ("You (plural/formal) to school.", "Jūs einate į mokyklą."),
            "jie/jos": ("They go to school.", "Jie / Jos eina į mokyklą."),
        },
        "-": {
            "aš": ("I do not go to school.", "Aš neinu į mokyklą."),
            "tu": ("You (singular) do not go to school.", "Tu neini į mokyklą."),
            "jis/ji": ("He/She does not go to school.", "Jis / Ji neina į mokyklą."),
            "mes": ("We do not go to school.", "Mes neiname į mokyklą."),
            "jūs": (
                "You (plural/formal) do not go to school.",
                "Jūs neinate į mokyklą.",
            ),
            "jie/jos": ("They do not go to school.", "Jie / Jos neina į mokyklą."),
        },
        "?": {
            "aš": ("Do I go to school?", "Ar aš einu į mokyklą?"),
            "tu": ("Do you (singular) go to school?", "Ar tu eini į mokyklą?"),
            "jis/ji": ("Does he/she go to school?", "Ar jis / ji eina į mokyklą?"),
            "mes": ("Do we go to school?", "Ar mes einame į mokyklą?"),
            "jūs": ("Do you (plural/formal) go to school?", "Ar jūs einate į mokyklą?"),
            "jie/jos": ("Do they go to school?", "Ar jie / jos eina į mokyklą?"),
        },
        "?-": {
            "aš": ("Don’t I go to school?", "Ar aš neinu į mokyklą?"),
            "tu": ("Don’t you (singular) go to school?", "Ar tu neini į mokyklą?"),
            "jis/ji": ("Doesn’t he/she go to school?", "Ar jis / ji neina į mokyklą?"),
            "mes": ("Don’t we go to school?", "Ar mes neiname į mokyklą?"),
            "jūs": (
                "Don’t you (plural/formal) go to school?",
                "Ar jūs neinate į mokyklą?",
            ),
            "jie/jos": ("Don’t they go to school?", "Ar jie / jos neina į mokyklą?"),
        },
    },
    "mėgti": {
        "+": {
            "aš": ("I like tea.", "Aš mėgstu arbatą."),
            "tu": ("You (singular) like tea.", "Tu mėgsti arbatą."),
            "jis/ji": ("He/She likes tea.", "Jis / Ji mėgsta arbatą."),
            "mes": ("We like tea.", "Mes mėgstame arbatą."),
            "jūs": ("You (plural/formal) like tea.", "Jūs mėgstate arbatą."),
            "jie/jos": ("They like tea.", "Jie / Jos mėgsta arbatą."),
        },
        "-": {
            "aš": ("I don’t like tea.", "Aš nemėgstu arbatos."),
            "tu": ("You (singular) don’t like tea.", "Tu nemėgsti arbatos."),
            "jis/ji": ("He/She doesn’t like tea.", "Jis / Ji nemėgsta arbatos."),
            "mes": ("We don’t like tea.", "Mes nemėgstame arbatos."),
            "jūs": ("You (plural/formal) don’t like tea.", "Jūs nemėgstate arbatos."),
            "jie/jos": ("They don’t like tea.", "Jie / Jos nemėgsta arbatos."),
        },
        "?": {
            "aš": ("Do I like tea?", "Ar aš mėgstu arbatą?"),
            "tu": ("Do you (singular) like tea?", "Ar tu mėgsti arbatą?"),
            "jis/ji": ("Does he/she like tea?", "Ar jis / ji mėgsta arbatą?"),
            "mes": ("Do we like tea?", "Ar mes mėgstame arbatą?"),
            "jūs": ("Do you (plural/formal) like tea?", "Ar jūs mėgstate arbatą?"),
            "jie/jos": ("Do they like tea?", "Ar jie / jos mėgsta arbatą?"),
        },
        "?-": {
            "aš": ("Don’t I like tea?", "Ar aš nemėgstu arbatos?"),
            "tu": ("Don’t you (singular) like tea?", "Ar tu nemėgsti arbatos?"),
            "jis/ji": ("Doesn’t he/she like tea?", "Ar jis / ji nemėgsta arbatos?"),
            "mes": ("Don’t we like tea?", "Ar mes nemėgstame arbatos?"),
            "jūs": (
                "Don’t you (plural/formal) like tea?",
                "Ar jūs nemėgstate arbatos?",
            ),
            "jie/jos": ("Don’t they like tea?", "Ar jie / jos nemėgsta arbatos?"),
        },
    },
    "norėti": {
        "+": {
            "aš": ("I want coffee.", "Aš noriu kavos."),
            "tu": ("You (singular) want coffee.", "Tu nori kavos."),
            "jis/ji": ("He/She wants coffee.", "Jis / Ji nori kavos."),
            "mes": ("We want coffee.", "Mes norime kavos."),
            "jūs": ("You (plural/formal) want coffee.", "Jūs norite kavos."),
            "jie/jos": ("They want coffee.", "Jie / Jos nori kavos."),
        },
        "-": {
            "aš": ("I don’t want coffee.", "Aš nenoriu kavos."),
            "tu": ("You (singular) don’t want coffee.", "Tu nenori kavos."),
            "jis/ji": ("He/She doesn’t want coffee.", "Jis / Ji nenori kavos."),
            "mes": ("We don’t want coffee.", "Mes nenorime kavos."),
            "jūs": ("You (plural/formal) don’t want coffee.", "Jūs nenorite kavos."),
            "jie/jos": ("They don’t want coffee.", "Jie / Jos nenori kavos."),
        },
        "?": {
            "aš": ("Do I want coffee?", "Ar aš noriu kavos?"),
            "tu": ("Do you (singular) want coffee?", "Ar tu nori kavos?"),
            "jis/ji": ("Does he/she want coffee?", "Ar jis / ji nori kavos?"),
            "mes": ("Do we want coffee?", "Ar mes norime kavos?"),
            "jūs": ("Do you (plural/formal) want coffee?", "Ar jūs norite kavos?"),
            "jie/jos": ("Do they want coffee?", "Ar jie / jos nori kavos?"),
        },
        "?-": {
            "aš": ("Don’t I want coffee?", "Ar aš nenoriu kavos?"),
            "tu": ("Don’t you (singular) want coffee?", "Ar tu nenori kavos?"),
            "jis/ji": ("Doesn’t he/she want coffee?", "Ar jis / ji nenori kavos?"),
            "mes": ("Don’t we want coffee?", "Ar mes nenorime kavos?"),
            "jūs": ("Don’t you (plural/formal) want coffee?", "Ar jūs nenorite kavos?"),
            "jie/jos": ("Don’t they want coffee?", "Ar jie / jos nenori kavos?"),
        },
    },
    "mokytis": {
        "+": {
            "aš": ("I study Lithuanian.", "Aš mokausi lietuvių kalbos."),
            "tu": ("You (singular) study Lithuanian.", "Tu mokaisi lietuvių kalbos."),
            "jis/ji": (
                "He/She studies Lithuanian.",
                "Jis / Ji mokosi lietuvių kalbos.",
            ),
            "mes": ("We study Lithuanian.", "Mes mokomės lietuvių kalbos."),
            "jūs": (
                "You (plural/formal) study Lithuanian.",
                "Jūs mokotės lietuvių kalbos.",
            ),
            "jie/jos": ("They study Lithuanian.", "Jie / Jos mokosi lietuvių kalbos."),
        },
        "-": {
            "aš": ("I don’t study Lithuanian.", "Aš nesimokau lietuvių kalbos."),
            "tu": (
                "You (singular) don’t study Lithuanian.",
                "Tu nesimokai lietuvių kalbos.",
            ),
            "jis/ji": (
                "He/She doesn’t study Lithuanian.",
                "Jis / Ji nesimoko lietuvių kalbos.",
            ),
            "mes": ("We don’t study Lithuanian.", "Mes nesimokome lietuvių kalbos."),
            "jūs": (
                "You (plural/formal) don’t study Lithuanian.",
                "Jūs nesimokote lietuvių kalbos.",
            ),
            "jie/jos": (
                "They don’t study Lithuanian.",
                "Jie / Jos nesimoko lietuvių kalbos.",
            ),
        },
        "?": {
            "aš": ("Do I study Lithuanian?", "Ar aš mokausi lietuvių kalbos?"),
            "tu": (
                "Do you (singular) study Lithuanian?",
                "Ar tu mokaisi lietuvių kalbos?",
            ),
            "jis/ji": (
                "Does he/she study Lithuanian?",
                "Ar jis / ji mokosi lietuvių kalbos?",
            ),
            "mes": ("Do we study Lithuanian?", "Ar mes mokomės lietuvių kalbos?"),
            "jūs": (
                "Do you (plural/formal) study Lithuanian?",
                "Ar jūs mokotės lietuvių kalbos?",
            ),
            "jie/jos": (
                "Do they study Lithuanian?",
                "Ar jie / jos mokosi lietuvių kalbos?",
            ),
        },
        "?-": {
            "aš": ("Don’t I study Lithuanian?", "Ar aš nesimokau lietuvių kalbos?"),
            "tu": (
                "Don’t you (singular) study Lithuanian?",
                "Ar tu nesimokai lietuvių kalbos?",
            ),
            "jis/ji": (
                "Doesn’t he/she study Lithuanian?",
                "Ar jis / ji nesimoko lietuvių kalbos?",
            ),
            "mes": ("Don’t we study Lithuanian?", "Ar mes nesimokome lietuvių kalbos?"),
            "jūs": (
                "Don’t you (plural/formal) study Lithuanian?",
                "Ar jūs nesimokote lietuvių kalbos?",
            ),
            "jie/jos": (
                "Don’t they study Lithuanian?",
                "Ar jie / jos nesimoko lietuvių kalbos?",
            ),
        },
    },
}



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
    st.rerun()  # ✅ Safe here
