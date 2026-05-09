import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Koko's Restaurant Map",
    page_icon="🍽️",
    layout="wide"
)

# ============================================================
# GOOGLE SHEETS CONNECTION
# ============================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_sheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["sheets"]["spreadsheet_id"]).sheet1
    return sheet

def load_data():
    sheet = get_sheet()
    records = sheet.get_all_records()
    if records:
        return pd.DataFrame(records)
    return pd.DataFrame(columns=["name", "cuisine", "city", "koko", "value"])

def add_row(name, cuisine, city, koko, value):
    sheet = get_sheet()
    sheet.append_row([name, cuisine, city, koko, value])

def delete_row(name):
    sheet = get_sheet()
    cell = sheet.find(name)
    if cell:
        sheet.delete_rows(cell.row)

# ============================================================
# HELPERS
# ============================================================
def get_zone(koko, value):
    if koko <= 4:
        if value <= 2:   return "Never Eat Here"
        elif value == 3: return "Below Mid"
        else:            return "Don't Eat This"
    elif koko <= 6:
        if value <= 2:   return "Horror Show"
        elif value == 3: return "Mid"
        else:            return "Solid Eats"
    else:
        if value <= 2:   return "Worth It Once"
        elif value == 3: return "Good Eats"
        else:            return "Go Immediately"

def get_verdict_style(zone):
    return {
        "Never Eat Here":  ("background:#ffe0e0;color:#c0392b;", "🚫"),
        "Below Mid":       ("background:#fff0e0;color:#d35400;", "👎"),
        "Don't Eat This":  ("background:#fff0e0;color:#d35400;", "🙅"),
        "Horror Show":     ("background:#ffe0e0;color:#c0392b;", "😱"),
        "Mid":             ("background:#fff8e0;color:#b7860b;", "🤷"),
        "Solid Eats":      ("background:#e8f8f0;color:#1e8449;", "👌"),
        "Worth It Once":   ("background:#e8f0ff;color:#2c5f9e;", "💸"),
        "Good Eats":       ("background:#e8f8f0;color:#1e8449;", "✅"),
        "Go Immediately":  ("background:#d4f5e9;color:#0e6655;", "🔥"),
    }.get(zone, ("background:#f0f0f0;color:#555;", "•"))

# ============================================================
# STYLES
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

html, body, div, p, span, label, input,
[class*="st-"], [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #f7fdf9 !important;
    background-image:
        radial-gradient(ellipse at 5% 0%, rgba(168,230,207,0.35) 0%, transparent 40%),
        radial-gradient(ellipse at 95% 0%, rgba(155,114,207,0.2) 0%, transparent 40%) !important;
}

.block-container { padding-top: 2rem !important; }

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #1c1c2e !important;
}

p, span, div, label { color: #1c1c2e !important; }

/* ---- STAT CARDS ---- */
.stat-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.4rem 1rem;
    text-align: center;
    border: 1.5px solid #e0d9f5;
    box-shadow: 0 2px 12px rgba(155,114,207,0.08);
}
.stat-card .num {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #1c1c2e;
    line-height: 1;
    display: block;
}
.stat-card .lbl {
    font-size: 0.7rem;
    color: #7070a0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    display: block;
    margin-top: 0.35rem;
}
.stat-card .sub {
    font-size: 0.72rem;
    font-weight: 500;
    display: block;
    margin-top: 0.15rem;
}
.stat-card.c-mint   { border-top: 3px solid #5cb896; }
.stat-card.c-mint   .sub { color: #3a9e74; }
.stat-card.c-purple { border-top: 3px solid #9b72cf; }
.stat-card.c-purple .sub { color: #7c53b8; }

/* ---- SECTION HEADING ---- */
.sec-head {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 600;
    color: #1c1c2e;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1.5px solid #e0d9f5;
}

/* ---- PANEL STYLING via Streamlit container hack ---- */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border-radius: 20px !important;
    border: 1.5px solid #e0d9f5 !important;
    box-shadow: 0 4px 20px rgba(155,114,207,0.09) !important;
    padding: 1.2rem !important;
}

/* ---- SCORE BOXES ---- */
.score-row {
    display: flex;
    gap: 0.75rem;
    margin: 1rem 0 0.5rem;
}
.sbox {
    flex: 1;
    border-radius: 14px;
    padding: 0.9rem 0.5rem;
    text-align: center;
}
.sbox.mint-box   { background: #e8f8f0; border: 1.5px solid #a8e6cf; }
.sbox.purple-box { background: #f0e9ff; border: 1.5px solid #c9aff5; }
.sbox .snum {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #1c1c2e;
    line-height: 1;
    display: block;
}
.sbox .snum small { font-size: 0.9rem; color: #9090b0; }
.sbox .slbl {
    font-size: 0.65rem;
    color: #7070a0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    display: block;
    margin-top: 0.2rem;
}

/* ---- VERDICT ---- */
.verdict-row {
    margin-top: 0.6rem;
    font-size: 0.85rem;
    color: #4a4a6a;
    font-weight: 500;
}
.vchip {
    display: inline-block;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-left: 0.3rem;
}

/* ---- SLIDER ---- */
[data-testid="stSlider"] label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #4a4a6a !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ---- SUBMIT BUTTON ---- */
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #7c53b8, #9b72cf) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    width: 100% !important;
}
[data-testid="stFormSubmitButton"] button:hover { opacity: 0.87 !important; }

/* ---- TEXT INPUTS ---- */
[data-testid="stTextInput"] input {
    background: #faf8ff !important;
    border: 1.5px solid #e0d9f5 !important;
    border-radius: 10px !important;
    color: #1c1c2e !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #9b72cf !important;
    box-shadow: 0 0 0 3px rgba(155,114,207,0.15) !important;
}
[data-testid="stTextInput"] label {
    color: #4a4a6a !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}

div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

/* ---- TABLE ---- */
.table-wrap {
    background: #ffffff;
    border-radius: 20px;
    padding: 1.6rem;
    border: 1.5px solid #e0d9f5;
    box-shadow: 0 4px 20px rgba(155,114,207,0.07);
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style="text-align:center; padding:1.5rem 0 0.5rem;">
    <h1 style="font-family:'Playfair Display',serif; font-size:3rem; font-weight:700;
               color:#1c1c2e; margin:0; letter-spacing:-0.02em;">
        Koko's <em style="color:#7c53b8;">Restaurant</em> Map
    </h1>
    <p style="color:#9090b0; font-size:0.85rem; letter-spacing:0.14em;
              text-transform:uppercase; margin-top:0.5rem; font-weight:500;">
        flavor × value — the only metrics that matter
    </p>
</div>
<div style="height:2px; background:linear-gradient(90deg,transparent,#5cb896,#9b72cf,transparent);
            width:50%; margin:1rem auto 1.5rem; border-radius:2px; opacity:0.5;"></div>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
with st.spinner("Loading restaurants..."):
    df = load_data()

total    = len(df)
avg_koko = round(df["koko"].mean(), 1) if total > 0 else "—"
worth_it = len(df[df["koko"] >= 7])   if total > 0 else 0
crimes   = len(df[(df["koko"] <= 4) & (df["value"] <= 2)]) if total > 0 else 0

# ============================================================
# STAT CARDS
# ============================================================
c1, c2, c3, c4 = st.columns(4)
for col, cls, num, lbl, sub in [
    (c1, "c-mint",   total,    "Restaurants Rated",  "and counting"),
    (c2, "c-mint",   avg_koko, "Avg Koko Score",     "out of 10"),
    (c3, "c-purple", worth_it, "Worth Recommending", "scored 7 or above"),
    (c4, "c-purple", crimes,   "Crime Scenes",       "bad food + bad value"),
]:
    with col:
        st.markdown(f"""<div class="stat-card {cls}">
            <span class="num">{num}</span>
            <span class="lbl">{lbl}</span>
            <span class="sub">{sub}</span>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# MAIN LAYOUT
# ============================================================
left, right = st.columns([1, 2.2], gap="large")

# ---- LEFT: FORM ----
with left:
    with st.container(border=True):
        st.markdown('<div class="sec-head">Add a Restaurant</div>', unsafe_allow_html=True)

        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Restaurant Name", placeholder="e.g. Trattoria da Pino")
            col_a, col_b = st.columns(2)
            with col_a:
                cuisine = st.text_input("Cuisine", placeholder="Italian")
            with col_b:
                city = st.text_input("City", placeholder="Milan")

            st.markdown("<br>", unsafe_allow_html=True)
            koko  = st.slider("Koko Score — Flavor",          1, 10, 5)
            value = st.slider("Value Score — Price / Volume", 1, 5,  3)

            zone = get_zone(koko, value)
            vstyle, vicon = get_verdict_style(zone)

            st.markdown(f"""
            <div class="score-row">
                <div class="sbox mint-box">
                    <span class="snum">{koko}<small>/10</small></span>
                    <span class="slbl">Flavor</span>
                </div>
                <div class="sbox purple-box">
                    <span class="snum">{value}<small>/5</small></span>
                    <span class="slbl">Value</span>
                </div>
            </div>
            <div class="verdict-row">
                Verdict:
                <span class="vchip" style="{vstyle}">{vicon} {zone}</span>
            </div>
            <br>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button("Add to Map →", use_container_width=True)

            if submitted:
                if not name.strip():
                    st.error("Please enter a restaurant name.")
                else:
                    with st.spinner("Saving..."):
                        add_row(name.strip(), cuisine.strip() or "Unknown",
                                city.strip() or "Unknown", koko, value)
                    st.success(f"'{name.strip()}' added — {zone}")
                    st.rerun()

    if total > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Remove a restaurant"):
            to_delete = st.selectbox("Select restaurant to remove",
                                     df["name"].tolist(),
                                     label_visibility="collapsed")
            if st.button("Remove", use_container_width=True):
                with st.spinner("Removing..."):
                    delete_row(to_delete)
                st.rerun()

# ---- RIGHT: MAP ----
with right:
    with st.container(border=True):
        st.markdown('<div class="sec-head">The Map</div>', unsafe_allow_html=True)

        if df.empty:
            st.markdown("""
            <div style="padding:4rem 2rem; text-align:center;">
                <div style="font-size:3rem; margin-bottom:1rem;">🍽️</div>
                <p style="font-family:'Playfair Display',serif; font-size:1.3rem;
                          color:#4a4a6a; margin:0;">No restaurants yet</p>
                <p style="font-size:0.85rem; color:#9090b0; margin-top:0.4rem;">
                    Add your first one using the form on the left</p>
            </div>""", unsafe_allow_html=True)
        else:
            fig = go.Figure()

            zones = [
                (0.5, 2.5, 0.5, 4.5,  "rgba(220,60,60,0.07)",   "Never Eat Here"),
                (2.5, 3.5, 0.5, 4.5,  "rgba(220,60,60,0.04)",   "Below Mid"),
                (3.5, 5.5, 0.5, 4.5,  "rgba(220,60,60,0.02)",   "Don't Eat This"),
                (0.5, 2.5, 4.5, 6.5,  "rgba(255,170,0,0.07)",   "Horror Show"),
                (2.5, 3.5, 4.5, 6.5,  "rgba(255,170,0,0.05)",   "Mid"),
                (3.5, 5.5, 4.5, 6.5,  "rgba(255,170,0,0.03)",   "Solid Eats"),
                (0.5, 2.5, 6.5, 10.5, "rgba(92,184,150,0.05)",  "Worth It Once"),
                (2.5, 3.5, 6.5, 10.5, "rgba(92,184,150,0.08)",  "Good Eats"),
                (3.5, 5.5, 6.5, 10.5, "rgba(92,184,150,0.14)",  "Go Immediately"),
            ]

            for x0, x1, y0, y1, color, label in zones:
                fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                              fillcolor=color, line_width=0, layer="below")
                fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=label,
                                   showarrow=False, opacity=0.65,
                                   font=dict(size=10, color="#7070a0",
                                             family="Plus Jakarta Sans"))

            for y, label, color in [
                (4.5, "don't bother below here", "rgba(220,80,80,0.45)"),
                (6.5, "worth recommending",       "rgba(92,184,150,0.6)"),
                (7.5, "rare territory",            "rgba(155,114,207,0.6)"),
            ]:
                fig.add_hline(y=y, line_dash="dash", line_color=color,
                              annotation_text=label, annotation_position="top right",
                              annotation_font_size=9)

            for x, label in [(2.5, "fair value"), (3.5, "good value")]:
                fig.add_vline(x=x, line_dash="dot",
                              line_color="rgba(155,114,207,0.35)",
                              annotation_text=label, annotation_position="top",
                              annotation_font_size=9, annotation_font_color="#7c53b8")

            palette = ["#5cb896","#9b72cf","#3aafa9","#c77dff",
                       "#48cae4","#7b5ea7","#80ed99","#b197fc","#52b788","#da77f2"]

            scatter = px.scatter(df, x="value", y="koko", hover_name="name",
                                 hover_data={"cuisine": True, "city": True,
                                             "koko": True, "value": True},
                                 color="cuisine", color_discrete_sequence=palette)
            for trace in scatter.data:
                trace.marker.size = 13
                trace.marker.line = dict(width=2, color="white")
                trace.marker.opacity = 0.92
                trace.hovertemplate = (
                    "<b>%{hovertext}</b><br><br>"
                    "Cuisine: %{customdata[0]}<br>"
                    "City: %{customdata[1]}<br>"
                    "Koko Score: %{y}<br>"
                    "Value: %{x}<br>"
                    "<extra></extra>"
                )       
                fig.add_trace(trace)

            fig.update_layout(
                xaxis=dict(
                    title="Value (Price / Volume)",
                    range=[0.5, 5.5], dtick=1, showgrid=False,
                    gridcolor="rgba(224,217,245,0.8)", zeroline=False,
                    tickfont=dict(size=10, color="#4a4a6a")),
                yaxis=dict(
                    title="Koko Score (Flavor)",
                    range=[0.5, 10.5], dtick=1, showgrid=False,
                    gridcolor="rgba(224,217,245,0.8)", zeroline=False,
                    tickfont=dict(size=10, color="#4a4a6a")),
                plot_bgcolor="white",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(
                    title_text="Cuisine",
                    title_font=dict(color="#4a4a6a"),
                    font=dict(size=10, color="#4a4a6a"),
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="#e0d9f5", borderwidth=1),
                margin=dict(l=10, r=130, t=15, b=10),
                height=540,
                font=dict(family="Plus Jakarta Sans"),
            )
            st.plotly_chart(fig, use_container_width=True)

# ============================================================
# TABLE
# ============================================================
if not df.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="sec-head">All Ratings</div>', unsafe_allow_html=True)

    df_disp = df.copy()
    df_disp["verdict"] = df_disp.apply(
        lambda r: get_zone(r["koko"], r["value"]), axis=1)
    df_disp = df_disp.sort_values("koko", ascending=False).reset_index(drop=True)
    df_disp.index += 1

    st.dataframe(
        df_disp[["name", "cuisine", "city", "koko", "value", "verdict"]],
        use_container_width=True,
        column_config={
            "name":    st.column_config.TextColumn("Restaurant", width="medium"),
            "cuisine": st.column_config.TextColumn("Cuisine"),
            "city":    st.column_config.TextColumn("City"),
            "koko":    st.column_config.ProgressColumn(
                "Koko Score", min_value=0, max_value=10, format="%d / 10"),
            "value":   st.column_config.ProgressColumn(
                "Value Score", min_value=0, max_value=5, format="%d / 5"),
            "verdict": st.column_config.TextColumn("Verdict"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)