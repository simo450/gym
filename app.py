import streamlit as st
import pandas as pd
from datetime import date
import json
import os

# ── Seitenkonfiguration ──────────────────────────────────────────────────────
st.set_page_config(page_title="💪 Sport Tracker", page_icon="💪", layout="centered")

# ── CSS Styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f0f; }
    h1 { color: #00ff88; font-family: 'Courier New', monospace; }
    .stButton>button {
        background-color: #00ff88;
        color: #0f0f0f;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
    }
    .stButton>button:hover { background-color: #00cc66; }
    .metric-box {
        background: #1a1a2e;
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Datei für gespeicherte Einträge ──────────────────────────────────────────
DATA_FILE = "sport_daten.json"

def lade_daten():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def speichere_daten(daten):
    with open(DATA_FILE, "w") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

# ── Hauptseite ────────────────────────────────────────────────────────────────
st.title("💪 Sport Tracker")
st.markdown("---")

# ── Navigation ────────────────────────────────────────────────────────────────
seite = st.sidebar.radio("📋 Navigation", ["🏋️ Training eintragen", "📊 Fortschritt", "📅 Verlauf"])

daten = lade_daten()

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 1 – Training eintragen
# ══════════════════════════════════════════════════════════════════════════════
if seite == "🏋️ Training eintragen":
    st.header("🏋️ Neues Training")

    col1, col2 = st.columns(2)

    with col1:
        training_datum = st.date_input("📅 Datum", value=date.today())
        sportart = st.selectbox("🏃 Sportart", [
            "Krafttraining", "Laufen", "Radfahren", "Schwimmen",
            "Yoga", "Fußball", "Basketball", "Andere"
        ])

    with col2:
        dauer = st.number_input("⏱️ Dauer (Minuten)", min_value=1, max_value=300, value=45)
        kalorien = st.number_input("🔥 Kalorien verbrannt", min_value=0, max_value=5000, value=300)

    notizen = st.text_area("📝 Notizen (optional)", placeholder="z.B. Heute Bankdrücken 80kg x 5...")

    if st.button("✅ Training speichern"):
        neuer_eintrag = {
            "datum": str(training_datum),
            "sportart": sportart,
            "dauer": dauer,
            "kalorien": kalorien,
            "notizen": notizen
        }
        daten.append(neuer_eintrag)
        speichere_daten(daten)
        st.success(f"✅ Training gespeichert! ({sportart}, {dauer} Min)")
        st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 2 – Fortschritt / Statistiken
# ══════════════════════════════════════════════════════════════════════════════
elif seite == "📊 Fortschritt":
    st.header("📊 Dein Fortschritt")

    if not daten:
        st.info("📭 Noch keine Einträge. Trage zuerst ein Training ein!")
    else:
        df = pd.DataFrame(daten)
        df["datum"] = pd.to_datetime(df["datum"])

        # Statistiken
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏋️ Trainings gesamt", len(df))
        with col2:
            st.metric("⏱️ Stunden gesamt", f"{df['dauer'].sum() // 60}h {df['dauer'].sum() % 60}min")
        with col3:
            st.metric("🔥 Kalorien gesamt", f"{df['kalorien'].sum()} kcal")

        st.markdown("---")

        # Diagramm – Kalorien pro Training
        st.subheader("🔥 Kalorien pro Training")
        chart_data = df[["datum", "kalorien"]].set_index("datum")
        st.line_chart(chart_data)

        # Diagramm – Trainingsdauer
        st.subheader("⏱️ Trainingsdauer (Minuten)")
        dauer_data = df[["datum", "dauer"]].set_index("datum")
        st.bar_chart(dauer_data)

        # Beliebteste Sportart
        st.subheader("🏆 Beliebteste Sportart")
        sportart_count = df["sportart"].value_counts()
        st.bar_chart(sportart_count)

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 3 – Verlauf
# ══════════════════════════════════════════════════════════════════════════════
elif seite == "📅 Verlauf":
    st.header("📅 Trainingsverlauf")

    if not daten:
        st.info("📭 Noch keine Einträge vorhanden.")
    else:
        df = pd.DataFrame(daten)
        df["datum"] = pd.to_datetime(df["datum"]).dt.strftime("%d.%m.%Y")
        df = df.rename(columns={
            "datum": "Datum",
            "sportart": "Sportart",
            "dauer": "Dauer (Min)",
            "kalorien": "Kalorien",
            "notizen": "Notizen"
        })

        st.dataframe(df[::-1], use_container_width=True)

        # Eintrag löschen
        st.markdown("---")
        st.subheader("🗑️ Eintrag löschen")
        if len(daten) > 0:
            index = st.number_input("Eintrag Nr. löschen (1 = ältester)", min_value=1, max_value=len(daten), value=1)
            if st.button("🗑️ Löschen"):
                daten.pop(index - 1)
                speichere_daten(daten)
                st.success("✅ Eintrag gelöscht!")
                st.rerun()