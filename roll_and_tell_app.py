import streamlit as st
import random
import time
from categories import CATEGORIES

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Roll & Tell",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Lexend', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* SETUP */
.app-title {
    font-size: 3rem;
    font-weight: 900;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0.2rem;
}
.app-subtitle {
    text-align: center;
    color: #888;
    margin-bottom: 2rem;
    font-size: 1rem;
}

/* ROLL screen */
.roll-box {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 28px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 1rem 0;
}
.dice-row {
    font-size: 4rem;
    letter-spacing: 1rem;
    margin-bottom: 0.5rem;
}
.dice-sum {
    font-size: 1.1rem;
    color: #aaa;
    margin-bottom: 1.5rem;
}
.roll-category {
    font-size: 1.6rem;
    font-weight: 900;
    color: #fff;
    margin-bottom: 0.5rem;
}
.roll-letter {
    display: inline-block;
    background: #f59e0b;
    color: #1a1a2e;
    font-size: 3.5rem;
    font-weight: 900;
    border-radius: 16px;
    width: 90px;
    height: 90px;
    line-height: 90px;
    margin: 0.5rem auto;
}
.roll-time {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.75rem;
}
.roll-target {
    color: #fff;
    font-size: 1rem;
    margin-top: 0.3rem;
}

/* READY */
.ready-box {
    background: #1a1a2e;
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
}
.ready-title { font-size: 2rem; font-weight: 900; color: #fff; }
.ready-hint { color: #aaa; margin-top: 0.5rem; font-size: 0.95rem; }

/* PLAYING */
.play-card {
    background: linear-gradient(135deg, #d97706, #f59e0b);
    border-radius: 28px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 0.5rem 0 1rem 0;
    box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
}
.play-letter {
    font-size: 5rem;
    font-weight: 900;
    color: #1a1a2e;
    line-height: 1;
}
.play-category {
    font-size: 1.2rem;
    font-weight: 700;
    color: rgba(26,26,46,0.8);
    margin-top: 0.5rem;
}
.play-target {
    font-size: 1rem;
    color: rgba(26,26,46,0.7);
    margin-top: 0.3rem;
}
.score-badge {
    display: inline-block;
    background: #f0fdf4;
    color: #16a34a;
    border-radius: 99px;
    padding: 0.3rem 1.1rem;
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}
.timer-bar-wrap {
    background: #e5e7eb;
    border-radius: 99px;
    height: 10px;
    margin: 1rem 0 0.5rem 0;
    overflow: hidden;
}
.timer-bar {
    height: 10px;
    border-radius: 99px;
    transition: width 0.9s linear, background 0.5s;
}

/* RESULTS */
.result-win {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 1rem 0;
}
.result-lose {
    background: linear-gradient(135deg, #fff1f2, #ffe4e6);
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    margin: 1rem 0;
}
.result-number {
    font-size: 5rem;
    font-weight: 900;
    line-height: 1;
}
.result-label {
    color: #555;
    font-size: 1rem;
    margin-top: 0.3rem;
}
.result-verdict {
    font-size: 1.5rem;
    font-weight: 900;
    margin-top: 0.75rem;
}

/* Buttons */
div.stButton > button {
    border-radius: 14px;
    font-family: 'Lexend', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.7rem 1.5rem;
    width: 100%;
    border: none;
    cursor: pointer;
    transition: transform 0.1s;
}
div.stButton > button:active { transform: scale(0.97); }
</style>
""", unsafe_allow_html=True)

# ── Dice helpers ──────────────────────────────────────────────────────────────
DICE_FACES = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}

def sum_to_time(total):
    if total <= 3:   return 15
    elif total <= 5: return 20
    elif total <= 7: return 30
    elif total <= 9: return 45
    elif total <= 11: return 55
    else:            return 60

LETTERS = list("ABCDEFGHIJKLMNOPRSTUVZ")  # Slovak-friendly alphabet

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "phase": "setup",
        "die1": 1,
        "die2": 1,
        "category": "",
        "letter": "A",
        "target": 2,
        "timer_duration": 30,
        "start_time": None,
        "score": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ───────────────────────────────────────────────────────────────────
def do_roll():
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    st.session_state.die1 = d1
    st.session_state.die2 = d2
    st.session_state.target = total
    st.session_state.timer_duration = sum_to_time(total)
    st.session_state.category = random.choice(CATEGORIES)
    st.session_state.letter = random.choice(LETTERS)
    st.session_state.score = 0
    st.session_state.phase = "roll"

def begin_round():
    st.session_state.start_time = time.time()
    st.session_state.score = 0
    st.session_state.phase = "playing"

def mark_correct():
    st.session_state.score += 1
    if st.session_state.score >= st.session_state.target:
        st.session_state.phase = "results"

def time_left():
    elapsed = time.time() - st.session_state.start_time
    return max(0, st.session_state.timer_duration - elapsed)

def reset():
    st.session_state.phase = "setup"

# ── PHASES ────────────────────────────────────────────────────────────────────

# ── 1. SETUP ──────────────────────────────────────────────────────────────────
if st.session_state.phase == "setup":
    st.markdown('<div class="app-title">🎲 Roll & Tell</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Hoď kockami — uhádni kategóriu na dané písmeno!</div>', unsafe_allow_html=True)

    st.markdown("### Ako sa hrá")
    st.markdown("""
    1. **Hoď kockami** — súčet = koľko slov musíš povedať
    2. **Dostaneš** kategóriu + písmeno + čas
    3. **Povedz** toľko slov na dané písmeno — kamoška kliká ✅
    4. **Výhra** = povedal si dosť slov včas!
    """)

    st.write("")
    if st.button("🎲 Hodiť kockami!", use_container_width=True):
        do_roll()
        st.rerun()

# ── 2. ROLL ───────────────────────────────────────────────────────────────────
elif st.session_state.phase == "roll":
    d1 = st.session_state.die1
    d2 = st.session_state.die2
    total = d1 + d2

    st.markdown(f"""
    <div class="roll-box">
        <div class="dice-row">{DICE_FACES[d1]} {DICE_FACES[d2]}</div>
        <div class="dice-sum">{d1} + {d2} = <strong style="color:#f59e0b">{total}</strong></div>
        <div class="roll-category">{st.session_state.category}</div>
        <div class="roll-letter">{st.session_state.letter}</div>
        <div class="roll-target">Musíš povedať <strong style="color:#f59e0b">{total} slov</strong> na písmeno <strong style="color:#f59e0b">{st.session_state.letter}</strong></div>
        <div class="roll-time">⏱️ Máš na to <strong style="color:#fff">{st.session_state.timer_duration} sekúnd</strong></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Štart!", use_container_width=True):
            begin_round()
            st.rerun()
    with col2:
        if st.button("🎲 Hodiť znova", use_container_width=True):
            do_roll()
            st.rerun()

# ── 3. PLAYING ────────────────────────────────────────────────────────────────
elif st.session_state.phase == "playing":
    remaining = time_left()

    if remaining <= 0:
        st.session_state.phase = "results"
        st.rerun()

    pct = remaining / st.session_state.timer_duration
    bar_color = "#22c55e" if pct > 0.4 else "#f97316" if pct > 0.15 else "#ef4444"
    bar_width = int(pct * 100)

    st.markdown(f'<div style="text-align:center"><span class="score-badge">✅ {st.session_state.score} / {st.session_state.target}</span></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="play-card">
        <div class="play-letter">{st.session_state.letter}</div>
        <div class="play-category">{st.session_state.category}</div>
        <div class="play-target">povedz {st.session_state.target} slov na toto písmeno</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="timer-bar-wrap">
        <div class="timer-bar" style="width:{bar_width}%; background:{bar_color};"></div>
    </div>
    <div style="text-align:center; font-size:1.5rem; font-weight:900; color:{bar_color}; margin-bottom:1rem;">
        {int(remaining)}s
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅ Správne!", use_container_width=True):
        mark_correct()
        st.rerun()

    time.sleep(0.9)
    st.rerun()

# ── 4. RESULTS ────────────────────────────────────────────────────────────────
elif st.session_state.phase == "results":
    score = st.session_state.score
    target = st.session_state.target
    won = score >= target

    if won:
        st.markdown(f"""
        <div class="result-win">
            <div style="font-size:3rem">🏆</div>
            <div class="result-number" style="color:#16a34a">{score}/{target}</div>
            <div class="result-label">{st.session_state.category} · písmeno {st.session_state.letter}</div>
            <div class="result-verdict" style="color:#16a34a">Vyhrал si!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-lose">
            <div style="font-size:3rem">😬</div>
            <div class="result-number" style="color:#dc2626">{score}/{target}</div>
            <div class="result-label">{st.session_state.category} · písmeno {st.session_state.letter}</div>
            <div class="result-verdict" style="color:#dc2626">Nestihol si to!</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎲 Nové kolo", use_container_width=True):
            do_roll()
            st.rerun()
    with col2:
        if st.button("🏠 Domov", use_container_width=True):
            reset()
            st.rerun()
