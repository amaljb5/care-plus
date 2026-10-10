import os
import streamlit as st

st.set_page_config(
    page_title="Care+ | Main Portal",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Dashboard URLs can be configured through environment variables or Streamlit secrets.
# Local defaults assume each dashboard is running on its own port.
def configured_url(key: str, default: str) -> str:
    try:
        value = st.secrets.get("dashboard_urls", {}).get(key)
        if value:
            return str(value).rstrip("/")
    except Exception:
        pass
    return os.getenv(f"CAREPLUS_{key.upper()}_URL", default).rstrip("/")

DASHBOARDS = [
    {
        "key": "elderly",
        "title": "Elderly Dashboard",
        "icon": "💚",
        "description": "Manage medicines, health history, appointments, wellbeing, emergency contacts, and SOS.",
        "url": configured_url("elderly", "https://elderly-dash.streamlit.app"),
        "audience": "For older adults",
    },
    {
        "key": "caregiver",
        "title": "Caregiver Dashboard",
        "icon": "🤝",
        "description": "Coordinate care, support medication adherence, manage contacts, and respond to alerts.",
        "url": configured_url("caregiver", "https://caregiver-dash.streamlit.app"),
        "audience": "For family and trusted caregivers",
    },
    {
        "key": "doctor",
        "title": "Doctor Dashboard",
        "icon": "🩺",
        "description": "Review patient health records, manage prescriptions, and coordinate appointments.",
        "url": configured_url("doctor", "https://doctor-dash.streamlit.app"),
        "audience": "For clinicians",
    },
]

st.markdown("""
<style>
:root { color-scheme: light !important; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #F5FAF7 !important;
    color: #17352B !important;
}
[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1180px; padding: 2rem 2rem 3rem 2rem; }
.portal-brand { text-align:center; padding: 1rem 0 1.8rem; }
.portal-heart { font-size: 3.4rem; line-height: 1.1; }
.portal-title { font-size: 3rem; font-weight: 850; color:#123D2E; margin:.25rem 0; }
.portal-subtitle { color:#637D73; font-size:1.12rem; }
.portal-card {
    background:#FFFFFF; border:1px solid #C7DED3; border-radius:22px;
    padding:26px; min-height:255px; box-shadow:0 7px 22px rgba(20,80,60,.07);
}
.portal-card-icon { font-size:2.4rem; margin-bottom:12px; }
.portal-card h2 { font-size:1.45rem; color:#123D2E; margin:0 0 8px; }
.portal-audience { color:#176B4D; font-weight:700; font-size:.9rem; margin-bottom:12px; }
.portal-card p { color:#536C62; font-size:1rem; line-height:1.55; min-height:78px; }
div.stLinkButton > a {
    background:#176B4D !important; color:#FFFFFF !important;
    border:1px solid #176B4D !important; border-radius:13px !important;
    font-weight:750 !important; min-height:3rem !important;
    display:flex; align-items:center; justify-content:center;
}
div.stLinkButton > a p, div.stLinkButton > a span { color:#FFFFFF !important; }
.portal-note {
    background:#E7F3EC; border:1px solid #C7DED3; border-radius:14px;
    padding:14px 18px; color:#315B49; margin-top:1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="portal-brand">
  <div class="portal-heart">💚</div>
  <div class="portal-title">Care+</div>
  <div class="portal-subtitle">Care, connected — choose your workspace to continue</div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(3, gap="large")
for col, dashboard in zip(cols, DASHBOARDS):
    with col:
        st.markdown(f"""
        <div class="portal-card">
          <div class="portal-card-icon">{dashboard["icon"]}</div>
          <h2>{dashboard["title"]}</h2>
          <div class="portal-audience">{dashboard["audience"]}</div>
          <p>{dashboard["description"]}</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button(f"Open {dashboard['title']} →", dashboard["url"], use_container_width=True)

st.markdown("""
<div class="portal-note">
<strong>How this portal works:</strong> Choose a dashboard above, then sign in on that dashboard's own login page.
Each dashboard remains a separate app, so its existing login, styling, and features are not replaced by this portal.
</div>
""", unsafe_allow_html=True)
