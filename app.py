import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Burnout Compass | Prediction & Wellness",
    page_icon="🌿",
    layout="wide",
)

BASE_DIR = Path(__file__).parent

if "page" not in st.session_state:
    st.session_state["page"] = "Home"
if "selected_domain" not in st.session_state:
    st.session_state["selected_domain"] = "Employee"

domain_pages = {
    "Employee": "Employee Burnout",
    "Student": "Student Burnout",
    "Healthcare professional": "Healthcare Burnout",
}
page = st.session_state["page"]


def html(s: str):
    """Render HTML safely in Streamlit (strips indentation/blank lines so
    markdown never turns the HTML into a code block)."""
    st.markdown(
        "\n".join(l.strip() for l in s.splitlines() if l.strip()),
        unsafe_allow_html=True,
    )


# ==========================================
# THEME / CSS
# ==========================================
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

:root { --gx: max(32px, calc((100vw - 1280px) / 2)); }

html, body, .stApp, .stApp * { font-family: 'Manrope', sans-serif; }
.stApp { background-color: #F5F7FB; color: #172033; }
[data-testid="stHeader"] { display: none; }

h1, h2, h3, h4 { color: #111C2E !important; font-weight: 800 !important; letter-spacing: -0.5px; }
.stApp p, .stApp li { color: #566174; line-height: 1.65; }

[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF; border: 1px solid #E6EAF1; border-radius: 16px;
}
[data-testid="stForm"] { padding: 22px; }
[data-testid="stMetric"] {
    background-color: #FFFFFF; border: 1px solid #E6EAF1;
    border-radius: 14px; padding: 18px;
}
[data-testid="stMetricValue"] { color: #1F5FBF !important; font-weight: 700; }

div[data-baseweb="input"] input, div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] textarea {
    background-color: #FFFFFF !important; color: #172033 !important;
    border-color: #DCE2EC !important; border-radius: 9px !important;
}

/* default (blue) buttons used on assessment pages */
.stFormSubmitButton > button, .stButton > button {
    background-color: #1F5FBF; color: #FFFFFF; border: 1px solid #1F5FBF;
    border-radius: 10px; min-height: 46px; font-weight: 700;
}
.stFormSubmitButton > button p, .stButton > button p { color: #FFFFFF !important; font-weight: 700; }
.stFormSubmitButton > button:hover, .stButton > button:hover {
    background-color: #184C99; border-color: #184C99; color: #FFFFFF;
}
</style>
"""

HOME_CSS = """
<style>
.block-container { padding: 0 !important; max-width: 100% !important; }
.block-container > [data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ---------- HERO BAND (nav + hero) ---------- */
.st-key-hero_band {
    background: #F5F7FB; padding: 22px var(--gx) 72px;
    border-bottom: 1px solid #E6EAF1;
}
.st-key-nav { margin-bottom: 36px; }
.bc-brand { font-size: 20px; font-weight: 800; color: #111C2E; letter-spacing: -0.3px; }
.bc-links { display: flex; justify-content: flex-end; gap: 30px; }
.bc-links a {
    color: #1A2536 !important; font-size: 15px; font-weight: 600;
    text-decoration: none !important;
}
.bc-links a:hover { color: #1F5FBF !important; }

.st-key-start_nav { display: flex; justify-content: flex-end; }
.st-key-start_nav button {
    background: #0F1B2D !important; border: 1px solid #0F1B2D !important;
    border-radius: 10px !important; min-height: 42px; padding: 0 20px;
}
.st-key-start_nav button p { color: #fff !important; font-size: 14.5px; }

.bc-pill-top {
    display: inline-block; background: #E6EEFB; color: #1F5FBF;
    font-size: 12.5px; font-weight: 700; padding: 7px 14px;
    border-radius: 999px; margin: 14px 0 22px;
}
.bc-h1 {
    font-size: 60px !important; line-height: 1.04 !important; font-weight: 800 !important;
    letter-spacing: -2px !important; color: #111C2E !important;
    margin: 0 0 22px !important; padding: 0 !important;
}
.bc-lead { font-size: 19px; line-height: 1.6; color: #566174; max-width: 560px; margin-bottom: 26px; }

.st-key-take_checkin button {
    background: #1F5FBF !important; border: 1px solid #1F5FBF !important;
    border-radius: 10px !important; min-height: 50px;
}
.st-key-see_comparison button {
    background: #FFFFFF !important; border: 1px solid #D5DBE5 !important;
    border-radius: 10px !important; min-height: 50px;
}
.st-key-see_comparison button p { color: #111C2E !important; }

/* domain selector card */
.st-key-hero_card {
    background: #FFFFFF; border: 1px solid #E3E8F0; border-radius: 28px;
    padding: 34px 34px 28px; margin-top: 10px;
}
.bc-card-label { font-size: 13px; font-weight: 700; color: #1E2A3C; margin-bottom: 4px; }
.bc-card-note { font-size: 12.5px; color: #778195; margin-top: 8px; }
.st-key-hero_card [data-testid="stRadio"] { width: 100%; }
.st-key-hero_card [data-testid="stRadio"] [role="radiogroup"] { gap: 12px; width: 100%; }
.st-key-hero_card [data-testid="stRadio"] label {
    width: 100%; background: #fff; border: 1.5px solid #DCE2EC; border-radius: 12px;
    padding: 16px 20px; margin: 0; cursor: pointer; box-sizing: border-box;
}
.st-key-hero_card [data-testid="stRadio"] label > div:first-child { display: none !important; }
.st-key-hero_card [data-testid="stRadio"] label p {
    font-weight: 700; font-size: 16px; color: #111C2E; margin: 0;
}
.st-key-hero_card [data-testid="stRadio"] label:has(input:checked) {
    background: #E8F0FE; border-color: #2F6FD6;
}
.st-key-hero_card [data-testid="stRadio"] label:has(input:checked) p { color: #1F5FBF; }

/* never cut button text with "..." */
.st-key-hero_band button p {
    white-space: normal !important; overflow: visible !important;
    text-overflow: clip !important; line-height: 1.2;
}
.st-key-start_nav button p { white-space: nowrap !important; }
.bc-brand { white-space: nowrap; }

/* ---------- GENERIC BANDS ---------- */
.bc-band { padding: 72px var(--gx); }
.bc-band-white { background: #FFFFFF; border-bottom: 1px solid #E6EAF1; }
.bc-band-light { background: #F5F7FB; }
.bc-band-dark { background: #0F1B2D; }
.bc-h2 {
    font-size: 36px !important; font-weight: 800 !important; letter-spacing: -1px !important;
    color: #111C2E !important; margin: 0 0 10px !important; padding: 0 !important;
}
.bc-sub { font-size: 16px; color: #566174; margin-bottom: 36px; }

/* domain cards */
.bc-grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }
.bc-dcard { border: 1px solid #E3E8F0; border-radius: 20px; padding: 30px 32px; background: #fff; }
.bc-tag {
    display: inline-block; font-size: 12.5px; font-weight: 700;
    padding: 6px 13px; border-radius: 999px; margin-bottom: 20px;
}
.bc-dcard .desc { font-size: 15px; line-height: 1.55; color: #566174; margin-bottom: 22px; min-height: 46px; }
.bc-row { display: flex; justify-content: space-between; font-size: 14px; color: #1E2A3C; margin: 14px 0 7px; }
.bc-row b { font-weight: 800; color: #111C2E; }
.bc-track { height: 8px; background: #E3E8F0; border-radius: 99px; overflow: hidden; }
.bc-fill { height: 8px; border-radius: 99px; }

.bc-looks { font-size: 13px; font-weight: 700; color: #1E2A3C; margin-bottom: 12px; }
.bc-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.bc-chip { font-size: 13px; font-weight: 600; padding: 7px 13px; border-radius: 999px; }

/* how it works */
.bc-step-num {
    width: 48px; height: 48px; border-radius: 50%; background: #0F1B2D; color: #fff;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 17px; margin: 36px 0 22px;
}
.bc-step-title { font-size: 20px; font-weight: 700; color: #111C2E; margin-bottom: 8px; }
.bc-step-desc { font-size: 15px; line-height: 1.6; color: #566174; max-width: 360px; }

/* suggestions */
.bc-split { display: grid; grid-template-columns: 1fr 1.45fr; gap: 56px; align-items: start; }
.bc-dark-h2 { font-size: 38px !important; font-weight: 800 !important; letter-spacing: -1px !important;
    color: #FFFFFF !important; margin: 0 0 16px !important; padding: 0 !important; }
.bc-dark-p { font-size: 17px; line-height: 1.6; color: #B9C3D3; max-width: 420px; }
.bc-result { background: #fff; border-radius: 28px; padding: 36px 38px; }
.bc-result-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.bc-result-title { font-size: 20px; font-weight: 700; color: #111C2E; }
.bc-sug-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.bc-sug { background: #FDEBDC; border-radius: 14px; padding: 22px 22px 24px; }
.bc-sug .t { font-size: 15.5px; font-weight: 700; color: #A4510F; margin-bottom: 8px; }
.bc-sug .d { font-size: 14.5px; line-height: 1.55; color: #4B4A52; }

/* footer */
.bc-foot-band { background: #FFFFFF; padding: 60px var(--gx) 70px; }
.bc-foot { font-size: 21px; line-height: 1.6; color: #566174; font-weight: 400; max-width: 1280px; }
.bc-foot b { color: #111C2E; font-weight: 800; }

@media (max-width: 900px) {
    .bc-grid3, .bc-split, .bc-sug-grid { grid-template-columns: 1fr; }
    .bc-h1 { font-size: 40px !important; }
    .bc-links { display: none; }
    .bc-band { padding: 48px var(--gx); }
    .bc-foot { font-size: 17px; }
}
</style>
"""

INNER_CSS = """
<style>
.block-container { max-width: 1200px; padding: 3rem 2rem; }
.footer-container { margin-top: 3rem; padding: 1.5rem 1rem 1rem; text-align: center; }
.footer-line { height: 1px; width: 100%; margin-bottom: 1.5rem;
    background: linear-gradient(90deg, transparent, #64748B, transparent); opacity: .6; }
.footer-brand { font-size: 1.15rem; font-weight: 700; color: #1F5FBF; margin-bottom: .35rem; }
.footer-tagline { font-size: .9rem; color: #566174; margin-bottom: .8rem; }
.footer-disclaimer { font-size: .82rem; color: #778195; margin-bottom: .6rem; }
.footer-warning { font-size: .78rem; line-height: 1.6; color: #778195; max-width: 700px; margin: 0 auto .8rem; }
.footer-copyright { font-size: .75rem; color: #778195; margin-top: 1rem; }

/* phones: less side padding so games and forms fit */
@media (max-width: 640px) {
    .block-container { padding: 2rem 1rem; }
}
</style>
"""

html(BASE_CSS)
html(HOME_CSS if page == "Home" else INNER_CSS)


# ==========================================
# CALM BREAK GAMES
# ==========================================
CALM_GAME = """
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;700&display=swap" rel="stylesheet">
<style>
  body { margin: 0; font-family: 'Manrope', sans-serif; }
  #stage { position: relative; height: 540px; overflow: hidden; border-radius: 24px;
           background: linear-gradient(180deg, #E8F0FE 0%, #DDF3EE 100%); user-select: none; }
  #msg { position: absolute; top: 18px; width: 100%; text-align: center; color: #3B4A63;
         font-weight: 700; font-size: 15px; z-index: 5; pointer-events: none; padding: 0 16px; box-sizing: border-box; }
  #count { position: absolute; bottom: 14px; width: 100%; text-align: center; color: #5A6B85;
           font-weight: 500; font-size: 14px; z-index: 5; pointer-events: none; }
  #breath { position: absolute; left: 50%; top: 50%; width: 170px; height: 170px; margin: -85px 0 0 -85px;
            border-radius: 50%; background: rgba(31, 95, 191, .16); display: flex; align-items: center;
            justify-content: center; color: #1F5FBF; font-weight: 700; font-size: 17px;
            animation: br 8s ease-in-out infinite; pointer-events: none; }
  @keyframes br { 0%, 100% { transform: scale(.7); } 50% { transform: scale(1.35); } }
  .bubble { position: absolute; bottom: -100px; border-radius: 50%; cursor: pointer; z-index: 3;
            background: radial-gradient(circle at 30% 30%, #fff, rgba(110, 165, 240, .38));
            border: 1.5px solid rgba(255, 255, 255, .9); animation: rise linear forwards;
            transition: transform .25s ease, opacity .25s ease; }
  @keyframes rise { to { transform: translateY(-680px); } }
  .bubble.pop { transform: scale(1.5) !important; opacity: 0; animation-play-state: paused; }
</style>
<div id="stage">
  <div id="msg">Pop a bubble. Breathe with the circle. No score, no timer, no rush.</div>
  <div id="breath"><span id="bt">Breathe in</span></div>
  <div id="count">Bubbles popped: 0</div>
</div>
<script>
  const stage = document.getElementById('stage');
  const msg = document.getElementById('msg');
  const count = document.getElementById('count');
  const bt = document.getElementById('bt');
  const kind = ["Nice. Let your shoulders drop.", "Good. Unclench your jaw.",
                "Lovely. Take one slow breath.", "Well done. You can stop whenever you like.",
                "Softly now. You are doing fine."];
  let popped = 0;

  function spawn() {
    const b = document.createElement('div');
    const size = 44 + Math.random() * 56;
    b.className = 'bubble';
    b.style.width = b.style.height = size + 'px';
    b.style.left = Math.random() * (stage.clientWidth - size) + 'px';
    b.style.animationDuration = (9 + Math.random() * 6) + 's';
    b.addEventListener('pointerdown', () => {
      if (b.classList.contains('pop')) return;
      b.classList.add('pop');
      popped++;
      count.textContent = 'Bubbles popped: ' + popped;
      if (popped % 8 === 0) msg.textContent = kind[(popped / 8 - 1) % kind.length | 0];
      setTimeout(() => b.remove(), 250);
    });
    b.addEventListener('animationend', () => b.remove());
    stage.appendChild(b);
  }
  for (let i = 0; i < 5; i++) setTimeout(spawn, i * 500);
  setInterval(spawn, 900);

  let inhale = true;
  setInterval(() => { inhale = !inhale; bt.textContent = inhale ? 'Breathe in' : 'Breathe out'; }, 4000);
</script>
"""


# Mandala Draw: draw with a finger or mouse, strokes are mirrored into a
# symmetrical glowing pattern. Canvas sizes itself to the screen, so it works
# on phones and laptops.
MANDALA_GAME = """
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: sans-serif; }
  #wrap { height: 540px; border-radius: 24px; background: linear-gradient(180deg, #FFF4E8 0%, #E8F0FE 100%);
          display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 10px; }
  #info { color: #3B4A63; font-weight: 700; font-size: 14px; text-align: center; padding: 0 8px; }
  canvas { background: #0F1B2D; border-radius: 50%; touch-action: none; cursor: crosshair;
           box-shadow: 0 8px 30px rgba(31, 95, 191, .25); }
  .row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; align-items: center; }
  .sw { width: 30px; height: 30px; border-radius: 50%; border: 3px solid #fff; cursor: pointer; padding: 0; }
  .sw.on { border-color: #1F5FBF; }
  #rainbow { background: conic-gradient(red, yellow, lime, cyan, blue, magenta, red); }
  button.txt { border: 0; background: #1F5FBF; color: #fff; font-weight: 700; padding: 9px 14px;
               border-radius: 10px; cursor: pointer; font-size: 13px; }
  button.alt { background: #fff; color: #1F5FBF; border: 1.5px solid #B9CCEF; }
  button.alt.on { background: #E8F0FE; border-color: #1F5FBF; }
</style>
<div id="wrap">
  <div id="info">Draw with your finger. Watch your lines bloom into a pattern.</div>
  <canvas id="cv"></canvas>
  <div class="row" id="colors">
    <button class="sw on" id="rainbow" data-c="rainbow"></button>
    <button class="sw" style="background:#6EA5F0" data-c="#6EA5F0"></button>
    <button class="sw" style="background:#7FE0C8" data-c="#7FE0C8"></button>
    <button class="sw" style="background:#FFB27A" data-c="#FFB27A"></button>
    <button class="sw" style="background:#FFFFFF" data-c="#FFFFFF"></button>
  </div>
  <div class="row">
    <button class="txt alt" data-n="6">6 petals</button>
    <button class="txt alt on" data-n="8">8 petals</button>
    <button class="txt alt" data-n="12">12 petals</button>
    <button class="txt" id="clear">Clear</button>
  </div>
</div>
<script>
  const cv = document.getElementById('cv');
  const ctx = cv.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const size = Math.max(200, Math.min(window.innerWidth - 24, 320));
  cv.style.width = cv.style.height = size + 'px';
  cv.width = cv.height = size * dpr;
  let n = 8, color = 'rainbow', hue = 0, last = null, drawing = false;

  function reset() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, cv.width, cv.height);
  }
  function seg(a, b, col) {
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, size * dpr / 2, size * dpr / 2);
    ctx.strokeStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 8;
    ctx.lineWidth = 2.4; ctx.lineCap = 'round';
    for (let i = 0; i < n; i++) {
      for (let m = 0; m < 2; m++) {
        ctx.save();
        ctx.rotate(i * 2 * Math.PI / n);
        if (m) ctx.scale(1, -1);
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        ctx.restore();
      }
    }
    ctx.restore();
  }
  function pos(e) {
    const r = cv.getBoundingClientRect();
    return { x: e.clientX - r.left - size / 2, y: e.clientY - r.top - size / 2 };
  }
  cv.addEventListener('pointerdown', e => {
    drawing = true; last = pos(e); cv.setPointerCapture(e.pointerId);
  });
  cv.addEventListener('pointermove', e => {
    if (!drawing) return;
    const p = pos(e);
    let col = color;
    if (color === 'rainbow') { hue = (hue + 3) % 360; col = 'hsl(' + hue + ',85%,68%)'; }
    seg(last, p, col);
    last = p;
  });
  ['pointerup', 'pointercancel', 'pointerleave'].forEach(ev =>
    cv.addEventListener(ev, () => { drawing = false; }));

  document.querySelectorAll('.sw').forEach(b => b.onclick = () => {
    document.querySelectorAll('.sw').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); color = b.dataset.c;
  });
  document.querySelectorAll('[data-n]').forEach(b => b.onclick = () => {
    document.querySelectorAll('[data-n]').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); n = parseInt(b.dataset.n); reset();
  });
  document.getElementById('clear').onclick = reset;
</script>
"""

SLIDE_GAME = """
<style>
  body { margin: 0; font-family: sans-serif; }
  #wrap { height: 540px; border-radius: 24px; background: linear-gradient(180deg, #DDF3EE 0%, #E8F0FE 100%);
          display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
  #info { color: #3B4A63; font-weight: 700; font-size: 15px; text-align: center; padding: 0 16px; min-height: 22px; }
  #board { display: grid; gap: 8px; width: min(340px, 86vw); height: min(340px, 86vw); }
  .tile { display: flex; align-items: center; justify-content: center; border-radius: 14px; background: #6EA5F0;
          color: #fff; font-weight: 800; cursor: pointer; user-select: none; transition: transform .1s; }
  .tile:active { transform: scale(.95); }
  .tile.empty { background: rgba(255, 255, 255, .45); cursor: default; }
  .row { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; padding: 0 8px; }
  button { border: 0; background: #1F5FBF; color: #fff; font-weight: 700; padding: 10px 18px; border-radius: 10px; cursor: pointer; font-size: 14px; }
  button.alt { background: #fff; color: #1F5FBF; border: 1.5px solid #B9CCEF; }
</style>
<div id="wrap">
  <div id="info"></div>
  <div id="board"></div>
  <div class="row">
    <button class="alt" onclick="setSize(3)">3 x 3 (medium)</button>
    <button class="alt" onclick="setSize(4)">4 x 4 (hard)</button>
    <button onclick="build()">Shuffle again</button>
  </div>
</div>
<script>
  const board = document.getElementById('board');
  const info = document.getElementById('info');
  let n = 3, tiles = [], moves = 0, done = false;
  function setSize(k) { n = k; build(); }
  function neighbours(e) {
    const r = Math.floor(e / n), c = e % n, out = [];
    if (r > 0) out.push(e - n);
    if (r < n - 1) out.push(e + n);
    if (c > 0) out.push(e - 1);
    if (c < n - 1) out.push(e + 1);
    return out;
  }
  function build() {
    tiles = []; for (let i = 1; i < n * n; i++) tiles.push(i); tiles.push(0);
    let e = n * n - 1, prev = -1;
    for (let k = 0; k < 150 * n; k++) {
      const opts = neighbours(e).filter(x => x !== prev);
      const t = opts[Math.floor(Math.random() * opts.length)];
      tiles[e] = tiles[t]; tiles[t] = 0; prev = e; e = t;
    }
    moves = 0; done = false;
    info.textContent = 'Slide the tiles into order, 1 to ' + (n * n - 1) + '. No timer, take your time.';
    render();
  }
  function render() {
    board.style.gridTemplateColumns = 'repeat(' + n + ', 1fr)';
    board.style.gridTemplateRows = 'repeat(' + n + ', 1fr)';
    board.innerHTML = '';
    tiles.forEach((v, i) => {
      const d = document.createElement('div');
      d.className = 'tile' + (v === 0 ? ' empty' : '');
      d.style.fontSize = (n === 3 ? 38 : 30) + 'px';
      d.textContent = v === 0 ? '' : v;
      d.onclick = () => move(i);
      board.appendChild(d);
    });
  }
  function move(i) {
    if (done) return;
    const e = tiles.indexOf(0);
    if (neighbours(e).indexOf(i) === -1) return;
    tiles[e] = tiles[i]; tiles[i] = 0; moves++;
    render();
    if (tiles.slice(0, n * n - 1).every((v, idx) => v === idx + 1)) {
      done = true;
      info.textContent = 'Solved in ' + moves + ' moves. Lovely work. Take a slow breath.';
    } else {
      info.textContent = 'Moves: ' + moves;
    }
  }
  build();
</script>
"""


# ==========================================
# LOAD TRAINED MODELS
# ==========================================
@st.cache_resource
def load_models():
    employee_model = joblib.load(BASE_DIR / "employee_burnout_model.pkl")
    healthcare_data = joblib.load(BASE_DIR / "healthcare_burnout_model.pkl")
    student_model = joblib.load(BASE_DIR / "student_burnout_model.pkl")
    return employee_model, healthcare_data, student_model


try:
    employee_model, healthcare_data, student_model = load_models()
    models_loaded = True
except Exception as error:
    models_loaded = False
    st.error(f"Unable to load the models: {error}")


# ==========================================
# HOME PAGE
# ==========================================
if page == "Home":

    # ---------- NAV + HERO ----------
    with st.container(key="hero_band"):

        with st.container(key="nav"):
            n1, n2, n3 = st.columns([2.2, 5, 1.5], vertical_alignment="center")
            with n1:
                html('<div class="bc-brand">Burnout Compass</div>')
            with n2:
                html("""
                <div class="bc-links">
                <a href="#domains" target="_self">Domains</a>
                <a href="#how" target="_self">How it works</a>
                <a href="#suggestions" target="_self">Suggestions</a>
                <a href="#about" target="_self">About</a>
                </div>
                """)
            with n3:
                if st.button("Start check-in", key="start_nav"):
                    st.session_state["page"] = domain_pages[st.session_state["selected_domain"]]
                    st.rerun()

        hero_left, hero_right = st.columns([1.2, 0.8], gap="large")

        with hero_left:
            html("""
            <div class="bc-pill-top">Research project</div>
            <h1 class="bc-h1">Burnout looks different depending on where you are.</h1>
            <div class="bc-lead">Compare burnout across employees, students and healthcare
            workers, then get suggestions shaped around your own results.</div>
            """)
            b1, b2, _ = st.columns([1.1, 1.1, 0.3])
            with b1:
                if st.button("Take the check-in", key="take_checkin", use_container_width=True):
                    st.session_state["page"] = domain_pages[st.session_state["selected_domain"]]
                    st.rerun()
            with b2:
                if st.button("Take a calm break", key="see_comparison", use_container_width=True):
                    st.session_state["page"] = "Calm Break"
                    st.rerun()

        with hero_right:
            with st.container(key="hero_card"):
                html('<div class="bc-card-label">I am a...</div>')
                st.radio(
                    "Choose your domain",
                    ["Employee", "Student", "Healthcare professional"],
                    key="selected_domain",
                    label_visibility="collapsed",
                )
                html('<div class="bc-card-note">Takes about 3 minutes. Responses are anonymous.</div>')

    # ---------- THREE DOMAINS ----------
    domains = [
        ("Employee", "#E6EEFB", "#1F5FBF",
         "Workload, deadlines and unclear boundaries between work and home.",
         ["Workload", "Overtime", "Job satisfaction", "Team support", "Career growth"]),
        ("Student", "#FDEBDC", "#A4510F",
         "Exam pressure, constant evaluation and irregular sleep.",
         ["Study hours", "Sleep", "Stress and anxiety", "Financial stress", "Family support"]),
        ("Healthcare", "#DDF3EE", "#0E6B5C",
         "Long shifts, emotional load and high-stakes decisions.",
         ["Stress level", "Job satisfaction", "Workplace factors", "Support programs", "Absences"]),
    ]
    cards = ""
    for name, tag_bg, tag_fg, desc, factors in domains:
        chips = "".join(
            f'<span class="bc-chip" style="background:{tag_bg};color:{tag_fg};">{f}</span>'
            for f in factors
        )
        cards += (
            f'<div class="bc-dcard"><span class="bc-tag" style="background:{tag_bg};color:{tag_fg};">{name}</span>'
            f'<div class="desc">{desc}</div>'
            f'<div class="bc-looks">What the check-in looks at</div>'
            f'<div class="bc-chips">{chips}</div></div>'
        )

    html(f"""
    <div class="bc-band bc-band-white" id="domains">
    <h2 class="bc-h2">Three domains, side by side</h2>
    <div class="bc-sub">Each check-in focuses on the factors that matter most in that setting.</div>
    <div class="bc-grid3">{cards}</div>
    </div>
    """)

    # ---------- HOW IT WORKS ----------
    html("""
    <div class="bc-band bc-band-light" id="how">
    <h2 class="bc-h2">How it works</h2>
    <div class="bc-grid3">
    <div><div class="bc-step-num">1</div><div class="bc-step-title">Choose your domain</div>
    <div class="bc-step-desc">Employee, student or healthcare, so the questions fit your daily reality.</div></div>
    <div><div class="bc-step-num">2</div><div class="bc-step-title">Answer a short check-in</div>
    <div class="bc-step-desc">About 12 questions on exhaustion, detachment and sense of efficacy.</div></div>
    <div><div class="bc-step-num">3</div><div class="bc-step-title">Get your plan</div>
    <div class="bc-step-desc">Compare with your domain and receive suggestions made for you.</div></div>
    </div>
    </div>
    """)

    # ---------- SUGGESTIONS ----------
    html("""
    <div class="bc-band bc-band-dark" id="suggestions">
    <div class="bc-split">
    <div>
    <h2 class="bc-dark-h2">Suggestions that fit you</h2>
    <div class="bc-dark-p">Your plan reflects your domain and your scores, not a generic list of wellness tips.</div>
    </div>
    <div class="bc-result">
    <div class="bc-result-head">
    <div class="bc-result-title">Your result (example)</div>
    <span class="bc-tag" style="background:#FDEBDC;color:#A4510F;margin:0;">Student · Moderate burnout</span>
    </div>
    <div class="bc-sug-grid">
    <div class="bc-sug"><div class="t">Protect one study block</div>
    <div class="d">Schedule a fixed focus window and a hard stop, then rest fully.</div></div>
    <div class="bc-sug"><div class="t">Sleep before cramming</div>
    <div class="d">Keep a steady wake-up time during exam weeks.</div></div>
    <div class="bc-sug"><div class="t">Talk to someone</div>
    <div class="d">Reach out to a mentor, friend or campus counsellor this week.</div></div>
    </div>
    </div>
    </div>
    </div>
    """)

    # ---------- FOOTER ----------
    html("""
    <div class="bc-foot-band" id="about">
    <div class="bc-foot"><b>Burnout Compass</b> is part of a research project by Nandana Mini, St Joseph's University.
    It is not a medical diagnosis. If you are struggling, please speak to a qualified professional.</div>
    </div>
    """)


# ==========================================
# ASSESSMENT PAGES (shared back button)
# ==========================================
else:
    if st.button("← Back to Home", key="back_to_home"):
        st.session_state["page"] = "Home"
        st.rerun()


# ==========================================
# EMPLOYEE BURNOUT PREDICTION
# ==========================================
if page == "Employee Burnout":

    st.title("Employee Burnout Prediction")
    st.write("Explore how workplace factors relate to the model's estimated burnout risk score.")

    # The model was trained on 16 features, so all 16 must be sent to it.
    # Only the 8 most relevant are asked; the rest use typical values.
    # TIP: replace these with the mean/median of each column in your training data.
    hidden_defaults = {
        "salary": 30000.0,
        "performance_score": 0.7,
        "project_completion_rate": 0.8,
        "training_participation": 0.5,
        "email_sentiment": 0.5,
        "slack_activity": 50.0,
        "meeting_participation": 0.7,
        "goal_achievement_rate": 0.8,
    }
    feature_order = [
        "tenure_months", "salary", "performance_score", "satisfaction_score",
        "workload_score", "team_sentiment", "project_completion_rate", "overtime_hours",
        "training_participation", "collaboration_score", "email_sentiment", "slack_activity",
        "meeting_participation", "goal_achievement_rate", "role_complexity_score",
        "career_progression_score",
    ]

    if models_loaded:
        values = dict(hidden_defaults)
        with st.form("employee_burnout_form"):
            st.caption("Move each slider to match your situation (0 = very low, 1 = very high).")

            st.subheader("1. Work Details")
            col1, col2 = st.columns(2)
            with col1:
                values["tenure_months"] = float(st.slider("Tenure (months)", 0, 240, 12))
                values["workload_score"] = st.slider("Workload Score", 0.0, 1.0, 0.7, 0.05)
            with col2:
                values["overtime_hours"] = float(st.slider("Overtime Hours", 0, 40, 5))
                values["role_complexity_score"] = st.slider("Role Complexity Score", 0.0, 1.0, 0.5, 0.05)

            st.subheader("2. Well-being and Team")
            col3, col4 = st.columns(2)
            with col3:
                values["satisfaction_score"] = st.slider("Satisfaction Score", 0.0, 1.0, 0.5, 0.05)
                values["team_sentiment"] = st.slider("Team Sentiment", 0.0, 1.0, 0.5, 0.05)
            with col4:
                values["collaboration_score"] = st.slider("Collaboration Score", 0.0, 1.0, 0.7, 0.05)
                values["career_progression_score"] = st.slider("Career Progression Score", 0.0, 1.0, 0.5, 0.05)

            submitted = st.form_submit_button("Predict Burnout Risk", use_container_width=True)

        if submitted:
            employee_input = pd.DataFrame([values])[feature_order]
            try:
                prediction = employee_model.predict(employee_input)
                risk_score = float(prediction[0])

                st.divider()
                st.subheader("Prediction Result")

                if 0 <= risk_score <= 1:
                    percentage = risk_score * 100
                    st.metric("Model-Estimated Burnout Risk Score", f"{percentage:.2f}%")

                    if percentage <= 40:
                        color, risk_label = "#22c55e", "Low Range"
                    elif percentage <= 70:
                        color, risk_label = "#f59e0b", "Moderate Range"
                    else:
                        color, risk_label = "#ef4444", "High Range"

                    min_w = "55px" if percentage > 0 else "0"
                    html(f"""
                    <div style="background-color:#e5e7eb;border-radius:10px;height:32px;width:100%;overflow:hidden;margin-bottom:10px;">
                    <div style="background-color:{color};width:{percentage}%;min-width:{min_w};height:32px;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;box-sizing:border-box;">
                    {percentage:.1f}%</div></div>
                    """)
                    st.markdown(f"**Prediction range: {risk_label}**")
                    st.caption(
                        "These ranges are for displaying model scores and are not clinically "
                        "validated burnout categories. The score is not necessarily a calibrated probability."
                    )
                else:
                    st.metric("Model-Estimated Burnout Score", f"{risk_score:.4f}")

                st.info(
                    "This is a machine-learning estimate, not a diagnosis. "
                    "Do not use it alone for employment or health decisions."
                )

                st.divider()
                st.subheader("Workplace Wellness Suggestions")
                recs = []
                if values["workload_score"] >= 0.7:
                    recs.append(("Workload management",
                        "Prioritize important tasks and discuss workload limits if demands are not manageable."))
                if values["satisfaction_score"] <= 0.4:
                    recs.append(("Job satisfaction",
                        "Consider changes that could improve your work experience and discuss them with someone you trust."))
                if values["overtime_hours"] >= 10:
                    recs.append(("Overtime and rest",
                        "Where possible, protect time for breaks and recovery, and discuss excessive overtime."))
                if values["team_sentiment"] <= 0.4:
                    recs.append(("Team support",
                        "Consider seeking support from a trusted colleague, mentor, or team lead."))
                if values["career_progression_score"] <= 0.4:
                    recs.append(("Career development",
                        "Consider a skill to develop, a relevant course, or a mentor who could support your goals."))
                if not recs:
                    recs.append(("Maintain healthy routines",
                        "Make time for breaks, rest, supportive relationships, and activities outside work."))

                for title, message in recs:
                    with st.container(border=True):
                        st.markdown(f"### {title}")
                        st.write(message)

                st.caption(
                    "Suggestions are based on selected inputs. They do not establish "
                    "causes of burnout or guarantee a score change."
                )
            except Exception as error:
                st.error(f"Prediction failed: {error}")
    else:
        st.warning("The employee prediction form is unavailable because the trained models could not be loaded.")


# ==========================================
# HEALTHCARE WORKER BURNOUT PREDICTION
# ==========================================
elif page == "Healthcare Burnout":

    st.title("Healthcare Worker Burnout Prediction")
    st.write("Explore workplace and well-being factors using the trained healthcare classification model.")

    if models_loaded:
        with st.form("healthcare_burnout_form"):
            st.subheader("Workplace Information")
            st.caption(
                "These category choices are provisional. Replace them with "
                "the original training dataset's categories."
            )
            col1, col2 = st.columns(2)
            with col1:
                employee_type = st.selectbox("Employee Type",
                    ["Nurse", "Doctor", "Administrative", "Support Staff", "Other"])
                department = st.selectbox("Department",
                    ["Emergency", "ICU", "Surgery", "General Medicine", "Other"])
                workplace_factor = st.selectbox("Main Workplace Factor",
                    ["Workload", "Staffing", "Management", "Work Environment", "Other"])
                stress_level = st.slider("Stress Level", 0.0, 10.0, 5.0, 0.5)
            with col2:
                job_satisfaction = st.slider("Job Satisfaction", 0.0, 10.0, 5.0, 0.5)
                access_to_eaps = st.selectbox("Access to Employee Assistance Programs", ["Yes", "No"])
                mental_health_absences = float(st.slider("Mental Health Absences", 0, 30, 0))
                turnover_intention = st.selectbox("Considering Leaving the Job?",
                    ["Never", "Occasionally", "Often"])

            submitted_healthcare = st.form_submit_button("Predict Burnout Risk", use_container_width=True)

        if submitted_healthcare:
            healthcare_input = pd.DataFrame([{
                "Employee Type": employee_type,
                "Department": department,
                "Workplace Factor": workplace_factor,
                "Stress Level": stress_level,
                "Job Satisfaction": job_satisfaction,
                "Access to EAPs": access_to_eaps,
                "Mental Health Absences": mental_health_absences,
                "Turnover Intention": turnover_intention,
            }])
            try:
                healthcare_model = healthcare_data["model"]
                label_encoder = healthcare_data["label_encoder"]
                prediction = healthcare_model.predict(healthcare_input)
                pred_idx = int(prediction[0])
                predicted_label = str(label_encoder.inverse_transform([pred_idx])[0])

                def level_of(name):
                    n = name.lower()
                    if "high" in n or "severe" in n or "often" in n or "always" in n or "frequent" in n:
                        return "high"
                    if "med" in n or "mod" in n or "occasion" in n or "sometimes" in n:
                        return "medium"
                    if "low" in n or "never" in n or n in ("no", "none", "minimal"):
                        return "low"
                    return None

                colors = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}
                texts = {"low": "Low burnout risk", "medium": "Moderate burnout risk",
                         "high": "High burnout risk"}

                st.divider()
                st.subheader("Healthcare Burnout Risk Result")

                level = level_of(predicted_label)
                weights = {"low": 0.0, "medium": 0.5, "high": 1.0}
                score = weights.get(level, 0.5) * 100

                # use class probabilities for a smoother risk score
                try:
                    proba = healthcare_model.predict_proba(healthcare_input)[0]
                    names = [str(label_encoder.inverse_transform([int(c)])[0])
                             for c in healthcare_model.classes_]
                    levels = [level_of(n) for n in names]
                    if all(levels):
                        score = sum(p * weights[l] for p, l in zip(proba, levels)) * 100
                except Exception:
                    pass

                if score <= 40:
                    color, range_label = "#22c55e", "Low Range"
                elif score <= 70:
                    color, range_label = "#f59e0b", "Moderate Range"
                else:
                    color, range_label = "#ef4444", "High Range"

                st.metric("Model-Estimated Burnout Risk Score", f"{score:.2f}%")
                min_w = "55px" if score > 0 else "0"
                html(f"""
                <div style="background-color:#e5e7eb;border-radius:10px;height:32px;width:100%;overflow:hidden;margin-bottom:10px;">
                <div style="background-color:{color};width:{score}%;min-width:{min_w};height:32px;border-radius:10px;
                display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;box-sizing:border-box;">
                {score:.1f}%</div></div>
                """)
                st.markdown(f"**Prediction range: {range_label}**")
                st.caption(
                    "These ranges are for displaying model scores and are not clinically "
                    "validated burnout categories. The score is not necessarily a calibrated probability."
                )

                if level == "high":
                    st.error("Your responses are associated with a higher estimated burnout risk. "
                             "Consider discussing workload, rest and support options with someone you trust.")
                elif level == "medium":
                    st.warning("Your responses are associated with a moderate estimated burnout risk. "
                               "Protect breaks and sleep, and talk to a colleague or supervisor about pressure points.")
                elif level == "low":
                    st.success("Your responses are associated with a lower estimated burnout risk. "
                               "Keep up healthy routines, rest and supportive relationships.")

                st.info(
                    "This is a machine-learning estimate for an educational project, "
                    "not a diagnosis or a basis for employment decisions."
                )
            except Exception as error:
                st.error(f"Healthcare prediction failed: {error}")
    else:
        st.warning("The healthcare prediction form is unavailable because the trained models could not be loaded.")


# ==========================================
# STUDENT BURNOUT PREDICTION
# ==========================================
elif page == "Student Burnout":

    st.title("Student Burnout Prediction")
    st.write("Assess student burnout using academic performance, lifestyle, stress, and personal support factors.")
    st.info("Enter your details below to estimate your burnout level.")

    with st.form("student_burnout_form"):
        st.subheader("1. Personal and Academic Details")
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=15, max_value=100, value=21)
            gender = st.selectbox("Gender", ["Female", "Male", "Other"])
            year = st.selectbox("Year of Study", [1, 2, 3, 4, 5, 6])
            department = st.selectbox("Department",
                ["Computer Science", "Business", "Arts", "Science", "Engineering", "Other"])
            residence = st.selectbox("Residence Type", ["Home", "Hostel", "Rented", "Other"])
            attendance = st.slider("Attendance (%)", 0, 100, 75)
        with col2:
            study_hours = st.number_input("Study Hours Per Day", 0.0, 24.0, 5.0, 0.5)
            gpa = st.number_input("Previous GPA", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            backlogs = st.number_input("Number of Backlogs", min_value=0, max_value=50, value=0)
            sleep = st.number_input("Sleep Hours Per Day", 0.0, 24.0, 7.0, 0.5)
            screen_time = st.number_input("Screen Time (Hours Per Day)", 0.0, 24.0, 6.0, 0.5)
            exercise = st.number_input("Exercise Sessions Per Week", 0, 21, 3)

        st.subheader("2. Well-being and Lifestyle")
        col3, col4 = st.columns(2)
        with col3:
            social_activity = st.slider("Social Activity Score", 0, 10, 5)
            part_time_job = st.selectbox("Do You Have a Part-Time Job?", ["No", "Yes"])
            income = st.selectbox("Family Income Bracket",
                ["Low", "Lower-Middle", "Middle", "Upper-Middle", "High"])
            financial_stress = st.slider("Financial Stress Score", 0, 10, 5)
        with col4:
            family_support = st.slider("Family Support Score", 0, 10, 5)
            stress = st.slider("Stress Level", 0, 10, 5)
            anxiety = st.slider("Anxiety Score", 0, 10, 5)
            motivation = st.slider("Motivation Score", 0, 10, 5)
            peer_pressure = st.slider("Peer Pressure Score", 0, 10, 5)
            counseling = st.selectbox("Access to Counseling?", ["No", "Yes"])

        submitted_student = st.form_submit_button("Predict Burnout Level", use_container_width=True)

    if submitted_student:
        student_input = pd.DataFrame([{
            "Age": age,
            "Gender": gender,
            "Year_of_Study": year,
            "Department": department,
            "Residence_Type": residence,
            "Attendance_Percent": attendance,
            "Study_Hours_Per_Day": study_hours,
            "Previous_GPA": gpa,
            "Backlogs": backlogs,
            "Sleep_Hours": sleep,
            "Screen_Time_Hours": screen_time,
            "Exercise_Freq_Per_Week": exercise,
            "Social_Activity_Score": social_activity,
            "Part_Time_Job": part_time_job,
            "Family_Income_Bracket": income,
            "Financial_Stress_Score": financial_stress,
            "Family_Support_Score": family_support,
            "Stress_Level": stress,
            "Anxiety_Score": anxiety,
            "Motivation_Score": motivation,
            "Peer_Pressure_Score": peer_pressure,
            "Counseling_Access": counseling,
        }])
        try:
            prediction = student_model.predict(student_input)[0]
            st.subheader("Student Burnout Risk Result")

            weights = {"low": 0.0, "medium": 0.5, "high": 1.0}

            def s_level(name):
                n = str(name).lower()
                if "high" in n:
                    return "high"
                if "med" in n or "mod" in n:
                    return "medium"
                return "low"

            score = weights[s_level(prediction)] * 100
            try:
                proba = student_model.predict_proba(student_input)[0]
                levels = [s_level(c) for c in student_model.classes_]
                score = sum(p * weights[l] for p, l in zip(proba, levels)) * 100
            except Exception:
                pass

            if score <= 40:
                color, range_label = "#22c55e", "Low Range"
            elif score <= 70:
                color, range_label = "#f59e0b", "Moderate Range"
            else:
                color, range_label = "#ef4444", "High Range"

            st.metric("Model-Estimated Burnout Risk Score", f"{score:.2f}%")
            min_w = "55px" if score > 0 else "0"
            html(f"""
            <div style="background-color:#e5e7eb;border-radius:10px;height:32px;width:100%;overflow:hidden;margin-bottom:10px;">
            <div style="background-color:{color};width:{score}%;min-width:{min_w};height:32px;border-radius:10px;
            display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;box-sizing:border-box;">
            {score:.1f}%</div></div>
            """)
            st.markdown(f"**Prediction range: {range_label}**")
            st.caption(
                "These ranges are for displaying model scores and are not clinically "
                "validated burnout categories. The score is not necessarily a calibrated probability."
            )

            if prediction == "High":
                st.error("High estimated burnout level")
                st.write(
                    "Your responses indicate a higher estimated burnout level. Consider reducing "
                    "avoidable workload, protecting your sleep, and speaking with a trusted person "
                    "or campus counselor."
                )
            elif prediction == "Medium":
                st.warning("Medium estimated burnout level")
                st.write(
                    "Your responses indicate a moderate estimated burnout level. Try a realistic "
                    "study schedule, regular breaks, consistent sleep, and time for activities "
                    "outside academics."
                )
            else:
                st.success("Low estimated burnout level")
                st.write(
                    "Your responses indicate a lower estimated burnout level. Continue maintaining "
                    "a balanced routine, adequate rest, social connections, and healthy study habits."
                )
            st.caption("This model provides an estimate based on the information entered. It is not a medical diagnosis.")
        except Exception as error:
            st.error(f"Prediction failed: {error}")
            st.write("Please share the error message so we can check the model inputs.")


# ==========================================
# CALM BREAK (stress-free mini game)
# ==========================================
elif page == "Calm Break":
    st.title("Calm Break")
    st.write(
        "Take a minute for yourself. Pick a game below and play at your own pace. "
        "There is no score to beat and no time limit."
    )
    choice = st.radio(
        "Choose a game",
        ["🫧 Bubble pop", "🌸 Mandala draw", "🔢 Sliding puzzle"],
        horizontal=True,
        key="calm_game_choice",
    )
    if choice.endswith("Bubble pop"):
        components.html(CALM_GAME, height=560)
    elif choice.endswith("Mandala draw"):
        components.html(MANDALA_GAME, height=560)
    else:
        components.html(SLIDE_GAME, height=560)
    st.caption("Games version 7 (three games available)")
    st.caption("A short pause is not a treatment, but slow breathing can help you feel calmer in the moment.")


# ==========================================
# FOOTER (assessment pages only; home has its own)
# ==========================================
if page != "Home":
    html("""
    <div class="footer-container">
    <div class="footer-line"></div>
    <div class="footer-brand">🌿 Burnout Compass</div>
    <div class="footer-tagline">Understand your stress. Protect your wellbeing.</div>
    <div class="footer-disclaimer">Research project · AI-assisted burnout risk assessment</div>
    <div class="footer-warning">This tool is for educational and research purposes only and is not
    a medical diagnosis. Please consult a qualified healthcare professional if you need support.</div>
    <div class="footer-copyright">© 2026 Burnout Compass · Built for wellbeing awareness</div>
    </div>
    """)
