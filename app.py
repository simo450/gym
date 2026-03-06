import streamlit as st
import json, os
from datetime import datetime

# ── Konfiguration ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="GymLog", page_icon="💪", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0A0A0A; color: #F0F0F0; }
section[data-testid="stSidebar"] { background: #0D0D0D; }
.block-container { padding-top: 1.5rem; padding-bottom: 5rem; }
div[data-testid="stMetric"] {
    background: #141414; border: 1px solid #252525;
    border-radius: 12px; padding: 1rem;
}
div[data-testid="stMetricValue"] { color: #E8FF47; font-size: 1.6rem !important; }
.stButton > button {
    background: #1E1E1E; color: #F0F0F0;
    border: 1px solid #252525; border-radius: 10px;
    font-weight: 600; width: 100%; transition: all 0.2s;
}
.stButton > button:hover { border-color: #E8FF47; color: #E8FF47; }
.ex-card {
    background: #141414; border: 1px solid #252525;
    border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;
}
.group-badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 6px; font-size: 10px; font-weight: 700;
    margin-left: 6px; letter-spacing: 1px;
}
hr { border-color: #1E1E1E; }
</style>
""", unsafe_allow_html=True)

# ── Übungsdatenbank ────────────────────────────────────────────────────────────
EXERCISES = {
    "Brust":     ["Bankdrücken LH","Schrägbankdrücken LH","Flachbankdrücken KH","Kabelzüge Brust","Dips","Brust Maschine"],
    "Schultern": ["Schulterdrücken KH","Schulterdrücken LH","Seitheben","Arnold Press","Face Pulls","Upright Row"],
    "Trizeps":   ["Trizeps Rope Pushdown","Overhead Extension KH","Skull Crushers","Dips Trizeps","Trizeps Maschine"],
    "Rücken":    ["Klimmzüge","Latziehen","Rudern LH","Rudern KH","Kreuzheben","Kabelrudern","T-Bar Rudern"],
    "Bizeps":    ["Bizeps Curls LH","Bizeps Curls KH","Hammer Curls","Preacher Curls","Kabel Curls","Konzentrations Curls"],
    "Beine":     ["Kniebeugen","Beinpresse","Rumänisches Kreuzheben","Beinstrecker","Beinbeuger","Wadenheben","Ausfallschritte"],
    "Core":      ["Plank","Crunches","Russian Twists","Beinheben","Ab Wheel","Cable Crunch"],
}
GROUP_COLORS = {
    "Brust":"#FF6B6B","Schultern":"#47B8FF","Trizeps":"#B47BFF",
    "Rücken":"#47FFC8","Bizeps":"#FFD644","Beine":"#FF69B4","Core":"#90EE90",
}
ALL_EXERCISES = {ex: g for g, exs in EXERCISES.items() for ex in exs}

DATA_FILE = "gymlog.json"

# ── Datenspeicherung ───────────────────────────────────────────────────────────
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"history": [], "prs": {}}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load()

# ── Session State ──────────────────────────────────────────────────────────────
if "workout" not in st.session_state:
    st.session_state.workout = None
if "selected_exercises" not in st.session_state:
    st.session_state.selected_exercises = []

# ── Navigation ─────────────────────────────────────────────────────────────────
page = st.sidebar.radio("", ["🏋️ Training", "📋 Verlauf", "📈 PRs"], label_visibility="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 1 – Training
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏋️ Training":
    st.markdown("### 🏋️ Training")

    # ── Kein aktives Training ──────────────────────────────────────────────────
    if st.session_state.workout is None:
        st.markdown("---")
        st.markdown("#### Neues Training starten")

        name = st.text_input("Name des Trainings", placeholder="z.B. Push Day")

        st.markdown("**Übung hinzufügen**")
        gruppe = st.selectbox("Muskelgruppe", list(EXERCISES.keys()))
        uebung = st.selectbox("Übung", EXERCISES[gruppe])
        saetze = st.number_input("Anzahl Sätze", 1, 10, 3)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Hinzufügen"):
                st.session_state.selected_exercises.append({
                    "name": uebung, "group": gruppe, "num_sets": saetze
                })
                st.rerun()
        with col2:
            if st.button("🗑️ Leeren"):
                st.session_state.selected_exercises = []
                st.rerun()

        if st.session_state.selected_exercises:
            st.markdown("**Ausgewählte Übungen:**")
            for ex in st.session_state.selected_exercises:
                color = GROUP_COLORS.get(ex["group"], "#888")
                st.markdown(
                    f'<div class="ex-card">'
                    f'<b>{ex["name"]}</b>'
                    f'<span class="group-badge" style="background:{color}22;color:{color}">{ex["group"]}</span>'
                    f'<br><span style="color:#555;font-size:12px">{ex["num_sets"]} Sätze</span>'
                    f'</div>', unsafe_allow_html=True
                )

            if st.button("🚀 Training starten", type="primary"):
                if not name:
                    name = f"Training {datetime.now().strftime('%d.%m %H:%M')}"
                st.session_state.workout = {
                    "name": name,
                    "start": datetime.now().isoformat(),
                    "exercises": [
                        {"name": ex["name"], "group": ex["group"],
                         "sets": [{"weight": 0.0, "reps": 0, "done": False} for _ in range(ex["num_sets"])]}
                        for ex in st.session_state.selected_exercises
                    ]
                }
                st.session_state.selected_exercises = []
                st.rerun()

    # ── Aktives Training ───────────────────────────────────────────────────────
    else:
        w = st.session_state.workout
        start = datetime.fromisoformat(w["start"])
        dauer = int((datetime.now() - start).total_seconds() // 60)

        col1, col2 = st.columns(2)
        col1.metric("🏋️", w["name"])
        col2.metric("⏱️ Dauer", f"{dauer} Min")
        st.markdown("---")

        for ei, ex in enumerate(w["exercises"]):
            color = GROUP_COLORS.get(ex["group"], "#888")
            st.markdown(
                f'<b style="font-size:15px">{ex["name"]}</b>'
                f'<span class="group-badge" style="background:{color}22;color:{color}">{ex["group"]}</span>',
                unsafe_allow_html=True
            )

            cols_header = st.columns([2, 2, 1])
            cols_header[0].markdown('<span style="color:#555;font-size:11px">KG</span>', unsafe_allow_html=True)
            cols_header[1].markdown('<span style="color:#555;font-size:11px">WDHL</span>', unsafe_allow_html=True)
            cols_header[2].markdown('<span style="color:#555;font-size:11px">✓</span>', unsafe_allow_html=True)

            for si, s in enumerate(ex["sets"]):
                c1, c2, c3 = st.columns([2, 2, 1])
                with c1:
                    weight = st.number_input("kg", min_value=0.0, step=2.5,
                        value=float(s["weight"]), key=f"w_{ei}_{si}", label_visibility="collapsed")
                with c2:
                    reps = st.number_input("Wdhl", min_value=0,
                        value=int(s["reps"]), key=f"r_{ei}_{si}", label_visibility="collapsed")
                with c3:
                    done = st.checkbox("", value=s["done"], key=f"d_{ei}_{si}")
                w["exercises"][ei]["sets"][si] = {"weight": weight, "reps": reps, "done": done}

            st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Abschliessen", type="primary"):
                for ex in w["exercises"]:
                    for s in ex["sets"]:
                        if s["done"] and s["weight"] > 0:
                            n = ex["name"]
                            vol = s["weight"] * s["reps"]
                            if n not in db["prs"] or vol > db["prs"][n].get("vol", 0):
                                db["prs"][n] = {
                                    "weight": s["weight"], "reps": s["reps"],
                                    "vol": vol, "date": datetime.now().isoformat()
                                }
                                s["isPR"] = True

                duration = int((datetime.now() - datetime.fromisoformat(w["start"])).total_seconds())
                volume = sum(s["weight"] * s["reps"] for ex in w["exercises"] for s in ex["sets"] if s["done"])
                db["history"].insert(0, {
                    "date": datetime.now().isoformat(),
                    "dayName": w["name"],
                    "duration": duration,
                    "volume": volume,
                    "exercises": w["exercises"]
                })
                save(db)
                st.session_state.workout = None
                st.success("🎉 Training gespeichert!")
                st.balloons()
                st.rerun()
        with col2:
            if st.button("❌ Abbrechen"):
                st.session_state.workout = None
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 2 – Verlauf
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Verlauf":
    st.markdown("### 📋 Verlauf")

    if not db["history"]:
        st.info("Noch kein Training abgeschlossen.")
    else:
        for i, h in enumerate(db["history"]):
            d = datetime.fromisoformat(h["date"]).strftime("%d.%m.%Y %H:%M")
            mins = h["duration"] // 60
            vol = int(h.get("volume", 0))
            n_sets = sum(len(ex["sets"]) for ex in h["exercises"])

            with st.expander(f"📅 {d} — {h['dayName']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("⏱️ Dauer", f"{mins} Min")
                c2.metric("💪 Sätze", n_sets)
                c3.metric("🔥 Volumen", f"{vol} kg")

                for ex in h["exercises"]:
                    color = GROUP_COLORS.get(ex.get("group", ""), "#888")
                    sets_text = "  ".join(
                        f'<span style="color:{"#E8FF47" if s.get("isPR") else "#47FFC8" if s.get("done") else "#555"}">'
                        f'{s["weight"]}kg×{s["reps"]}{"🏆" if s.get("isPR") else ""}</span>'
                        for s in ex["sets"]
                    )
                    st.markdown(
                        f'<div class="ex-card" style="padding:0.6rem 1rem">'
                        f'<b style="font-size:13px">{ex["name"]}</b>'
                        f'<span class="group-badge" style="background:{color}22;color:{color}">{ex.get("group","")}</span>'
                        f'<div style="margin-top:5px;font-size:12px">{sets_text}</div>'
                        f'</div>', unsafe_allow_html=True
                    )

                if st.button("🗑️ Löschen", key=f"del_{i}"):
                    db["history"].pop(i)
                    save(db)
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# SEITE 3 – PRs
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 PRs":
    st.markdown("### 📈 Persönliche Bestleistungen")

    if not db["prs"]:
        st.info("Noch keine PRs. Fang an zu trainieren! 💪")
    else:
        sorted_prs = sorted(db["prs"].items(), key=lambda x: x[1]["vol"], reverse=True)
        for name, pr in sorted_prs:
            group = ALL_EXERCISES.get(name, "")
            color = GROUP_COLORS.get(group, "#888")
            d = datetime.fromisoformat(pr["date"]).strftime("%d.%m.%Y")
            st.markdown(
                f'<div class="ex-card" style="display:flex;justify-content:space-between;align-items:center">'
                f'<div>'
                f'<b style="font-size:14px">{name}</b>'
                f'<span class="group-badge" style="background:{color}22;color:{color}">{group}</span>'
                f'<div style="color:#555;font-size:11px;margin-top:3px">{d}</div>'
                f'</div>'
                f'<div style="text-align:right">'
                f'<div style="font-size:22px;font-weight:700;color:#E8FF47">{pr["weight"]} kg</div>'
                f'<div style="font-size:11px;color:#555">× {pr["reps"]} Wdhl.</div>'
                f'</div>'
                f'</div>', unsafe_allow_html=True
            )
