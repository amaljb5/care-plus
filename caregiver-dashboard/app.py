import os
import json
import textwrap
import requests
from html import escape as html_escape
from urllib.parse import quote
from datetime import datetime, date, time
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(
    page_title="Care+ | Caregiver Dashboard",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_ELDER_ID = "demo-elder-001"  # Fallback profile for this prototype.
ELDER_ID = st.session_state.get("selected_elder_id", DEFAULT_ELDER_ID)

st.markdown(
    """
    <style>
    :root { color-scheme: light !important; }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] { background:#F5FAF7 !important; color:#17352B !important; }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] { background:#E8F3ED !important; color:#17352B !important; }
    [data-testid="stSidebar"] * { color:#17352B !important; }
    [data-testid="stSidebar"] hr { border-color:#B7D2C3 !important; }
    .block-container { max-width:1500px; padding:1.4rem 2rem 3rem 2rem; }
    h1,h2,h3,h4,h5,h6 { color:#123D2E !important; }
    p,label,li,[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"] p { color:#17352B !important; font-size:1.05rem; line-height:1.5; }
    /* Copied from the elderly dashboard: rounded sidebar navigation buttons. */
    div[data-testid="stSidebar"] div.stButton > button {
        min-height:3.8rem !important; width:100%; border-radius:15px !important;
        font-size:1.05rem !important; font-weight:700 !important; padding:.65rem .8rem !important;
        white-space:normal !important; background:#FFFFFF !important; color:#174734 !important;
        border:1.5px solid #9BBEAA !important;
    }
    div[data-testid="stSidebar"] div.stButton > button p,
    div[data-testid="stSidebar"] div.stButton > button span { color:#174734 !important; }
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background:#176B4D !important; color:#FFFFFF !important; border-color:#176B4D !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] span { color:#FFFFFF !important; }
    div.stButton > button, div.stFormSubmitButton > button, [data-testid="stLinkButton"] a {
        min-height:2.8rem; border-radius:12px; font-weight:650;
        border:1px solid #A7CDB8; color:#174734; background:#FFFFFF;
    }
    div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] {
        color:#FFFFFF !important; background:#176B4D !important; border-color:#176B4D !important;
    }
    input, textarea, [data-baseweb="select"] > div { color:#17352B !important; background:#FFFFFF !important; border-radius:10px !important; }
    [data-testid="stMetricValue"] { color:#14583F !important; }

    /* Elderly profile cards: explicit styling was missing, causing the HTML to
       render as unstyled text instead of the intended modern cards. */
    .elder-social-card {
        position:relative; overflow:hidden; width:100%; min-height:300px;
        background:#FFFFFF; border:1px solid #E0E8F1; border-radius:22px;
        box-shadow:0 10px 28px rgba(23,43,77,.08); margin:0 0 12px;
        transition:transform .18s ease, box-shadow .18s ease;
    }
    .elder-social-card:hover { transform:translateY(-2px); box-shadow:0 16px 34px rgba(23,43,77,.12); }
    .elder-cover {
        height:104px; width:100%;
        background:linear-gradient(120deg,#D7F3E7 0%,#DDEBFF 52%,#E8E2FF 100%);
        background-size:cover; background-position:center;
    }
    .elder-social-content { position:relative; padding:0 22px 22px; }
    .elder-avatar-wrap { margin-top:-42px; margin-bottom:10px; height:76px; }
    .elder-avatar {
        display:flex; align-items:center; justify-content:center; width:76px; height:76px;
        object-fit:cover; border-radius:50%; border:4px solid #FFFFFF;
        background:#E7F5EF; color:#176B63; font-size:2rem;
        box-shadow:0 4px 14px rgba(23,43,77,.12);
    }
    .elder-avatar-fallback { display:flex; }
    .elder-profile-name { color:#172B4D; font-size:1.25rem; font-weight:800; line-height:1.35; margin:0 0 4px; }
    .elder-profile-subtitle { color:#718096; font-size:.92rem; margin-bottom:16px; }
    .elder-profile-details { display:flex; flex-wrap:wrap; gap:10px; }
    .elder-profile-details > div {
        display:flex; flex-direction:column; gap:4px; min-width:120px; flex:1;
        background:#F6F9FC; border:1px solid #E8EEF5; border-radius:12px; padding:10px 12px;
        overflow-wrap:anywhere;
    }
    .elder-profile-details span { color:#718096; font-size:.68rem; font-weight:800; letter-spacing:.08em; }
    .elder-profile-details strong { color:#243B53; font-size:.88rem; font-weight:650; }
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.elder-social-card) {
        background:transparent !important; border:0 !important; box-shadow:none !important;
        padding:0 !important;
    }
    div[data-testid="stButton"]:has(button[key^="open_elder_profile_"]) > button,
    div[data-testid="stButton"] > button[kind="primary"] {
        background:linear-gradient(120deg,#176B63,#238A72) !important;
        color:#FFFFFF !important; border:0 !important;
    }
    [data-testid="stHeader"], #MainMenu, footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        if "firebase" in st.secrets:
            cfg = dict(st.secrets["firebase"])
            if "service_account_json" in cfg:
                info = json.loads(cfg["service_account_json"])
                cred = credentials.Certificate(info)
            else:
                cred = credentials.Certificate(cfg)
            firebase_admin.initialize_app(cred)
        else:
            path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not path or not os.path.exists(path):
                raise RuntimeError(
                    "Firebase credentials are missing. Add your existing .streamlit/secrets.toml "
                    "or set GOOGLE_APPLICATION_CREDENTIALS."
                )
            firebase_admin.initialize_app(credentials.Certificate(path))
    return firestore.client()

try:
    db = get_db()
    firebase_ready = True
except Exception as exc:
    db = None
    firebase_ready = False
    st.error("Care+ could not connect to Firestore. Check your Firebase configuration.")
    with st.expander("Technical details"):
        st.code(str(exc))

def caregiver_firebase_api_key() -> str:
    cfg = dict(st.secrets.get("firebase", {}))
    return (cfg.get("api_key") or cfg.get("web_api_key") or cfg.get("web_apiKey")
            or cfg.get("apiKey") or st.secrets.get("firebase_api_key", ""))


# Persist the Firebase refresh token in a browser cookie so a page refresh does not
# erase the signed-in session. Firebase refresh tokens are exchanged for a fresh ID token.
def get_caregiver_cookie_manager():
    # CookieManager is a Streamlit widget/component and must not be created
    # inside a cached function. Creating it here avoids CachedWidgetWarning.
    return stx.CookieManager(key="caregiver_auth_cookie_manager")


def caregiver_refresh_session(refresh_token: str):
    api_key = caregiver_firebase_api_key()
    if not api_key or not refresh_token:
        return None
    response = requests.post(
        f"https://securetoken.googleapis.com/v1/token?key={api_key}",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=15,
    )
    payload = response.json()
    if response.status_code != 200:
        return None
    return {
        "email": payload.get("user_email", ""),
        "uid": payload.get("user_id", ""),
        "id_token": payload.get("id_token", ""),
        "refresh_token": payload.get("refresh_token", refresh_token),
        "remember": True,
    }


caregiver_cookie_manager = get_caregiver_cookie_manager()
# Cookie reads may be None during the first Streamlit render while the component initializes.
if not st.session_state.get("caregiver_auth"):
    try:
        saved_refresh_token = caregiver_cookie_manager.get(cookie="caregiver_refresh_token")
        if saved_refresh_token:
            restored_auth = caregiver_refresh_session(saved_refresh_token)
            if restored_auth and restored_auth.get("uid"):
                st.session_state["caregiver_auth"] = restored_auth
                caregiver_cookie_manager.set(
                    cookie="caregiver_refresh_token",
                    val=restored_auth["refresh_token"],
                    expires_at=datetime.now().astimezone().replace(year=datetime.now().year + 1),
                )
    except Exception:
        # If cookies are unavailable, ordinary sign-in still works for this session.
        pass


def caregiver_sign_in(email: str, password: str):
    api_key = caregiver_firebase_api_key()
    if not api_key:
        raise RuntimeError("Firebase Web API key is missing. Add it under [firebase] as api_key in .streamlit/secrets.toml.")
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
        json={"email": email.strip().lower(), "password": password, "returnSecureToken": True}, timeout=15,
    )
    payload = response.json()
    if response.status_code != 200:
        message = payload.get("error", {}).get("message", "Sign-in failed.")
        if message in ("EMAIL_NOT_FOUND", "INVALID_LOGIN_CREDENTIALS"):
            raise ValueError("Email or password is incorrect.")
        if message == "USER_DISABLED":
            raise ValueError("This account has been disabled.")
        raise ValueError(message.replace("_", " ").title())
    return payload


def render_caregiver_login():
    st.markdown("""
    <div class="careplus-hero"><h1>💚 Care+ Caregiver Portal</h1>
    <p>Welcome back. Sign in to support your loved one.</p></div>
    """, unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        with st.container(border=True):
            st.subheader("Sign in")
            with st.form("caregiver_login_form"):
                email = st.text_input("Email", placeholder="caregiver@example.com")
                password = st.text_input("Password", type="password")
                remember = st.checkbox("Remember me", value=True)
                submitted = st.form_submit_button("Sign in to Care+", type="primary", use_container_width=True)
            if submitted:
                if not email.strip() or not password:
                    st.error("Enter your email and password.")
                else:
                    try:
                        auth = caregiver_sign_in(email, password)
                        st.session_state["caregiver_auth"] = {
                            "email": auth.get("email", email.strip().lower()),
                            "uid": auth.get("localId", ""),
                            "id_token": auth.get("idToken", ""),
                            "refresh_token": auth.get("refreshToken", ""),
                            "remember": remember,
                        }
                        if remember and auth.get("refreshToken"):
                            caregiver_cookie_manager.set(
                                cookie="caregiver_refresh_token",
                                val=auth["refreshToken"],
                                expires_at=datetime.now().astimezone().replace(year=datetime.now().year + 1),
                            )
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))


if not st.session_state.get("caregiver_auth"):
    render_caregiver_login()
    st.stop()

def discover_elderly_profiles():
    """Discover elderly profiles in common Care+ Firestore collections."""
    if not db:
        return []
    profiles = []
    seen = set()
    for collection_name in ("elderly_profiles", "senior_profiles", "patients", "users"):
        try:
            for snap in db.collection(collection_name).limit(250).stream():
                data = snap.to_dict() or {}
                role = str(data.get("role", data.get("user_type", ""))).lower()
                # Profile collections are accepted directly; users are filtered by role where present.
                if collection_name == "users" and role and not any(word in role for word in ("elder", "senior", "patient")):
                    continue
                profile_id = str(data.get("uid") or data.get("user_id") or snap.id)
                if profile_id in seen:
                    continue
                seen.add(profile_id)
                name = (
                    data.get("full_name") or data.get("name") or data.get("display_name")
                    or data.get("elderly_name") or data.get("patient_name") or "Elderly profile"
                )
                profiles.append({
                    "id": profile_id,
                    "name": str(name),
                    "phone": str(data.get("phone") or data.get("phone_number") or ""),
                    "collection": collection_name,
                    "children_names": data.get("children_names") or data.get("children") or data.get("family_members") or [],
                    "photo_url": data.get("profile_photo_url") or data.get("photo_url") or data.get("photo") or data.get("avatar_url") or "",
                })
        except Exception:
            # A collection may not exist or may not be readable in the current prototype.
            continue
    # Keep the current prototype profile selectable while other profiles are being added.
    if DEFAULT_ELDER_ID not in seen:
        profiles.append({
            "id": DEFAULT_ELDER_ID,
            "name": "Demo elderly profile",
            "phone": "",
            "collection": "prototype",
            "children_names": [],
            "photo_url": "",
        })
    return profiles

if not firebase_ready:
    st.stop()

# First screen: visual cards for choosing an elderly person.
if not st.session_state.get("caregiver_profile_chosen", False):
    st.markdown(
        """
        <div class="careplus-hero">
          <h1>💚 Care+</h1>
          <p style="font-size:1.08rem;">Caregiver workspace · Family, trusted caregivers and volunteers</p>
        </div>
        <h2 style="text-align:center;font-size:2rem;">Who are you caring for today?</h2>
        <p style="text-align:center;color:#58776A;">Select a profile card to continue to that person's care dashboard.</p>
        """,
        unsafe_allow_html=True,
    )

    profiles = discover_elderly_profiles()
    if not profiles:
        profiles = [{
            "id": DEFAULT_ELDER_ID, "name": "Demo elderly profile", "phone": "",
            "collection": "prototype", "children_names": [], "photo_url": ""
        }]

    # Enrich profile cards with children/family names and an optional profile photo.
    for profile in profiles:
        profile.setdefault("children_names", [])
        profile.setdefault("photo_url", "")
        try:
            collection_name = profile.get("collection")
            if db and collection_name and collection_name != "prototype":
                snap = db.collection(collection_name).document(profile["id"]).get()
                data = (snap.to_dict() or {}) if snap.exists else {}
                profile["children_names"] = data.get("children_names") or data.get("children") or data.get("family_members") or []
                if isinstance(profile["children_names"], str):
                    profile["children_names"] = [profile["children_names"]]
                if isinstance(profile["children_names"], list):
                    profile["children_names"] = [
                        str(child.get("name", child.get("full_name", ""))) if isinstance(child, dict) else str(child)
                        for child in profile["children_names"]
                    ]
                profile["photo_url"] = (
                    data.get("profile_photo_url") or data.get("photo_url")
                    or data.get("photo") or data.get("avatar_url") or ""
                )
        except Exception:
            pass

    for offset in range(0, len(profiles), 2):
        cols = st.columns(2, gap="large")
        for col, profile in zip(cols, profiles[offset:offset + 2]):
            with col:
                profile_id = str(profile.get("id", DEFAULT_ELDER_ID))
                profile_name = str(profile.get("name", "Elderly profile"))
                children = profile.get("children_names", [])
                child_text = ", ".join(str(x) for x in children) if children else "Not added"
                phone_text = str(profile.get("phone", "") or "")
                photo = str(profile.get("photo_url", "") or "")

                with st.container(border=True):
                    if photo.startswith(("https://", "http://")):
                        safe_photo = html_escape(photo, quote=True)
                        cover = (
                            f'<div class="elder-cover" style="background-image:linear-gradient(125deg,rgba(71,120,245,.10),rgba(108,155,255,.10)),url(&quot;{safe_photo}&quot;);"></div>'
                        )
                        avatar = f'<img class="elder-avatar" src="{safe_photo}" alt="Profile photo">'
                    else:
                        cover = '<div class="elder-cover"></div>'
                        avatar = '<div class="elder-avatar elder-avatar-fallback">👤</div>'

                    details_html = (
                        f'<div class="elder-profile-details">'
                        f'<div><span>PROFILE ID</span><strong>{html_escape(profile_id)}</strong></div>'
                        f'<div><span>CHILDREN</span><strong>{html_escape(child_text)}</strong></div>'
                        f'{f"<div><span>CONTACT</span><strong>{html_escape(phone_text)}</strong></div>" if phone_text else ""}'
                        '</div>'
                    )
                    card_html = (
                        '<div class="elder-social-card">'
                        f'{cover}'
                        '<div class="elder-social-content">'
                        f'<div class="elder-avatar-wrap">{avatar}</div>'
                        f'<div class="elder-profile-name">{html_escape(profile_name)}</div>'
                        '<div class="elder-profile-subtitle">Care+ elderly profile</div>'
                        f'{details_html}'
                        '</div></div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

                    if st.button(
                        "Visit dashboard  →",
                        key=f"open_elder_profile_{profile_id}",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state["selected_elder_id"] = profile_id
                        st.session_state["selected_elder_name"] = profile_name
                        st.session_state["caregiver_profile_chosen"] = True
                        st.rerun()

    with st.expander("Can't find the elderly person? Enter profile ID"):
        st.caption("The ID must match the one used by the elderly dashboard.")
        with st.form("manual_elder_profile"):
            manual_id = st.text_input("Elderly profile ID", placeholder="e.g. demo-elder-001")
            manual_go = st.form_submit_button("Open this profile", type="primary", use_container_width=True)
        if manual_go:
            if not manual_id.strip():
                st.error("Enter a profile ID.")
            else:
                st.session_state["selected_elder_id"] = manual_id.strip()
                st.session_state["selected_elder_name"] = "Selected elderly profile"
                st.session_state["caregiver_profile_chosen"] = True
                st.rerun()
    st.stop()

ELDER_ID = st.session_state.get("selected_elder_id", DEFAULT_ELDER_ID)

def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")

def add_record(collection: str, data: dict[str, Any]) -> str:
    if not db:
        raise RuntimeError("Firestore is not connected.")
    payload = dict(data)
    payload.setdefault("elderly_user_id", ELDER_ID)
    payload.setdefault("created_at", now_iso())
    ref = db.collection(collection).document()
    ref.set(payload)
    return ref.id

def list_records(collection: str, limit: int = 250, elder_filter: bool = True) -> list[dict[str, Any]]:
    if not db:
        return []
    query = db.collection(collection)
    # Query locally for compatibility with records created by older prototype versions.
    rows = []
    for snap in query.limit(limit).stream():
        row = snap.to_dict() or {}
        row["id"] = snap.id
        if (
            not elder_filter
            or str(row.get("elderly_user_id", "")) == str(ELDER_ID)
            or str(row.get("user_id", "")) == str(ELDER_ID)
            or str(row.get("patient_id", "")) == str(ELDER_ID)
        ):
            rows.append(row)
    return rows

def update_record(collection: str, record_id: str, changes: dict[str, Any]) -> None:
    if not db:
        raise RuntimeError("Firestore is not connected.")
    db.collection(collection).document(record_id).update({**changes, "updated_at": now_iso()})

SOS_MEET_URL = "https://meet.google.com/dis-vmxc-cxr"


def render_sos_alerts(rows: list[dict]):
    """Show SOS details and open a saved Google Meet URL when available."""
    if not rows:
        st.info("No SOS alerts recorded.")
        return
    for alert in rows:
        with st.container(border=True):
            st.subheader(str(alert.get("emergency_type") or "SOS emergency"))
            st.caption(f"Created: {alert.get('created_at', 'Unknown time')}")
            st.write(f"**Status:** {alert.get('status', 'ACTIVE')}")
            details = alert.get("details") or alert.get("message")
            if details:
                st.write(f"**Emergency details:** {details}")
            meet_url = str(alert.get("meet_url") or alert.get("emergency_contact") or SOS_MEET_URL).strip()
            if meet_url.startswith("https://meet.google.com/"):
                st.link_button("🎥 Join SOS Google Meet", meet_url, use_container_width=True)
            elif meet_url:
                st.write(f"**Emergency contact:** {meet_url}")


def page_table(rows: list[dict], fields: list[str], empty: str):
    if not rows:
        st.info(empty)
        return
    st.dataframe(
        [{field.replace("_", " ").title(): row.get(field, "") for field in fields} for row in rows],
        use_container_width=True, hide_index=True,
    )

st.sidebar.markdown("# 💚 Care+")
st.sidebar.caption("Caregiver Dashboard")
st.sidebar.markdown("---")
st.sidebar.caption(f"Signed in as {st.session_state['caregiver_auth'].get('email', 'Caregiver')}")
if st.sidebar.button("🚪 Log out", key="caregiver_logout", use_container_width=True):
    try:
        caregiver_cookie_manager.delete(cookie="caregiver_refresh_token")
    except Exception:
        pass
    st.session_state.pop("caregiver_auth", None)
    st.session_state.pop("caregiver_profile_chosen", None)
    st.session_state.pop("selected_elder_id", None)
    st.session_state.pop("selected_elder_name", None)
    st.rerun()
# Sidebar navigation follows the elderly dashboard's button-based layout and styling.
caregiver_nav_items = [
    ("🏠 Overview", "Overview"),
    ("💗 Elderly Profile & Health", "Elderly Profile & Health"),
    ("💊 Medication Support", "Medication Support"),
    ("😊 Send Wellbeing Check-in", "Send Wellbeing Check-in"),
    ("🗓️ Appointments", "Appointments"),
    ("🆘 SOS & Care Requests", "SOS & Care Requests"),
    ("📞 Family & Emergency Contacts", "Family & Emergency Contacts"),
    ("📄 Health Documents", "Health Documents"),
]
if "caregiver_page" not in st.session_state:
    st.session_state["caregiver_page"] = "Overview"
for nav_label, nav_page in caregiver_nav_items:
    if st.sidebar.button(
        nav_label,
        key=f"caregiver_sidebar_{nav_page}",
        use_container_width=True,
        type="primary" if st.session_state["caregiver_page"] == nav_page else "secondary",
    ):
        st.session_state["caregiver_page"] = nav_page
        st.rerun()
page = st.session_state["caregiver_page"]
st.sidebar.markdown("---")
st.sidebar.caption("For family members, trusted caregivers and volunteers — not a doctor/nurse workspace.")
st.sidebar.caption(f"Currently supporting: {st.session_state.get('selected_elder_name', 'Elderly profile')}")
st.sidebar.caption(f"Profile ID: {ELDER_ID}")

top_spacer, top_action = st.columns([5, 1.35], vertical_alignment="center")
with top_action:
    if st.button("↔  Change Patient", key="change_patient_top", use_container_width=True):
        st.session_state["caregiver_profile_chosen"] = False
        st.rerun()

st.markdown(
    f"""
    <div class="careplus-hero">
      <h1>💚 Care+ Caregiver Dashboard</h1>
      <p>Supporting <b>{html_escape(str(st.session_state.get('selected_elder_name', 'the selected older adult')))}</b> · Profile ID: {html_escape(str(ELDER_ID))}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Support the older adult's daily care, communication and safety. This dashboard does not diagnose or prescribe.")

# Fetch common records; these are scoped to the selected elderly profile.
health = sorted(list_records("health_readings"), key=lambda x: x.get("created_at", ""), reverse=True)
# Doctor-entered records may be stored separately from measured health readings.
# Keep existing readings and add matching doctor records from the shared health-record collections.
doctor_health_records = []
for health_collection in ("health_records", "medical_records"):
    try:
        doctor_health_records.extend(list_records(health_collection))
    except Exception:
        pass
# De-duplicate documents if the same record is reachable through multiple supported sources.
doctor_health_records = list({str(row.get("id")): row for row in doctor_health_records}.values())
doctor_health_records.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
meds = list_records("medications")
dose_logs = sorted(list_records("medicine_logs"), key=lambda x: x.get("created_at", ""), reverse=True)
appointments = sorted(list_records("appointments"), key=lambda x: x.get("created_at", ""), reverse=True)
# Load wellbeing check-ins for the selected elderly profile. Older app versions may
# save the check-in under the patient's profile ID, Firestore document ID, or auth UID.
wellness = []
wellness_ids = {str(ELDER_ID).strip()}
try:
    for patient_doc in db.collection("patients").limit(500).stream():
        patient_data = patient_doc.to_dict() or {}
        known_ids = {
            str(patient_doc.id).strip(),
            str(patient_data.get("profile_id", "")).strip(),
            str(patient_data.get("user_id", "")).strip(),
            str(patient_data.get("uid", "")).strip(),
            str(patient_data.get("auth_uid", "")).strip(),
            str(patient_data.get("firebase_uid", "")).strip(),
        }
        known_ids.discard("")
        if str(ELDER_ID).strip() in known_ids:
            wellness_ids.update(known_ids)
            break
except Exception:
    pass

try:
    for wellness_doc in db.collection("wellness_checks").limit(500).stream():
        wellness_row = wellness_doc.to_dict() or {}
        owner_ids = {
            str(wellness_row.get(key, "")).strip()
            for key in ("user_id", "elderly_user_id", "patient_id", "elder_id", "profile_id", "uid", "auth_uid")
        }
        owner_ids.discard("")
        if owner_ids.intersection(wellness_ids):
            wellness_row["id"] = wellness_doc.id
            wellness.append(wellness_row)
except Exception:
    # Keep the dashboard usable if this collection cannot be read.
    wellness = []

wellness.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
emergencies = sorted(list_records("emergencies"), key=lambda x: x.get("created_at", ""), reverse=True)
care_requests = sorted(list_records("care_requests"), key=lambda x: x.get("created_at", ""), reverse=True)
contacts = list_records("emergency_contacts")
documents = sorted(list_records("medical_documents"), key=lambda x: x.get("created_at", ""), reverse=True)
reminders = list_records("wellness_reminders")

if page == "Overview":
    st.subheader("Overview")
    st.write("A practical place for family, trusted caregivers and volunteers to coordinate support for the linked older adult.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Medication records", len(meds))
    c2.metric("Appointment requests", len(appointments))
    c3.metric("Open SOS alerts", sum(1 for x in emergencies if str(x.get("status", "ACTIVE")).upper() not in ("CLOSED", "RESOLVED", "CANCELLED")))
    c4.metric("Care requests", len(care_requests))
    st.markdown("### Needs attention")
    open_sos = [x for x in emergencies if str(x.get("status", "ACTIVE")).upper() not in ("CLOSED", "RESOLVED", "CANCELLED")]
    if open_sos:
        st.error(f"{len(open_sos)} SOS alert(s) need follow-up.")
        page_table(open_sos[:8], ["created_at", "emergency_type", "details", "status"], "No active alerts.")
    else:
        st.success("No active SOS alerts recorded.")
    if care_requests:
        st.info(f"There are {len(care_requests)} care request(s) recorded.")
    st.markdown("### Recent activity")
    recent = []
    for kind, rows in [
        ("Health reading", health), ("Dose log", dose_logs), ("Wellbeing check", wellness),
        ("Appointment", appointments), ("SOS", emergencies), ("Care request", care_requests),
    ]:
        if rows:
            r = dict(rows[0])
            r["activity_type"] = kind
            recent.append(r)
    recent.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    page_table(recent[:10], ["created_at", "activity_type", "status", "notes", "details"], "No recent activity found yet.")

elif page == "Elderly Profile & Health":
    st.subheader("Elderly profile & health")
    st.info("This section is for viewing and helping coordinate care. Only enter readings that were actually measured; do not use this dashboard to diagnose.")
    st.markdown("### Latest recorded readings")
    latest = {}
    for item in health:
        key = item.get("reading_type") or item.get("type") or item.get("metric") or "Reading"
        if key not in latest:
            latest[key] = item
    if latest:
        cols = st.columns(min(4, max(1, len(latest))))
        for idx, (label, item) in enumerate(latest.items()):
            with cols[idx % len(cols)]:
                st.metric(label.replace("_", " ").title(), str(item.get("value", item.get("reading", "—"))), str(item.get("unit", "")))
                st.caption(str(item.get("created_at", ""))[:19])
    else:
        st.info("No health readings have been recorded for this profile yet.")
    st.markdown("### Health history")
    # Combine measured health readings and doctor-entered health records in one history table.
    history_rows = []
    for reading in health:
        history_rows.append({
            "Date": reading.get("created_at") or reading.get("recorded_at") or reading.get("date") or "",
            "Record": reading.get("reading_type") or reading.get("type") or "Health reading",
            "Diagnosis / details": reading.get("value", ""),
            "Unit": reading.get("unit", ""),
            "Notes": reading.get("notes", ""),
            "Added by": reading.get("doctor_name") or reading.get("created_by_role") or "",
        })
    for record in doctor_health_records:
        history_rows.append({
            "Date": record.get("created_at") or record.get("recorded_at") or record.get("date") or "",
            "Record": record.get("title") or record.get("record_type") or record.get("type") or record.get("health_record_type") or "Health record",
            "Diagnosis / details": record.get("diagnosis") or record.get("details") or record.get("description") or record.get("value") or "",
            "Unit": record.get("unit", ""),
            "Notes": record.get("notes") or record.get("instructions") or "",
            "Added by": record.get("doctor_name") or record.get("created_by") or record.get("created_by_role") or "Doctor",
        })
    history_rows.sort(key=lambda row: str(row.get("Date", "")), reverse=True)
    if history_rows:
        st.dataframe(history_rows[:150], use_container_width=True, hide_index=True)
    else:
        st.info("No health history available.")

    st.markdown("### Daily wellbeing history")
    page_table(
        wellness[:50],
        ["created_at", "check_date", "mood", "feeling", "pain", "sleep", "notes", "status"],
        "No wellbeing check-ins recorded yet."
    )

elif page == "Medication Support":
    st.subheader("Medication overview")
    st.write("View the medication plan entered by the doctor. Caregivers can monitor adherence, but cannot add or change medicines, doses, or schedules.")

    if meds:
        page_table(meds, ["name", "medicine_name", "dosage", "dose", "instructions", "time", "times", "frequency", "status"],
                   "No medicines have been added by the doctor yet.")
    else:
        st.info("No medication schedule is available yet. A doctor must add the prescribed medicines and timing.")

    st.markdown("### Send a medicine reminder")
    st.caption("Creates an in-app alert for the selected elderly profile. It does not change the prescription and is not an SMS/push notification.")
    if meds:
        med_options = {
            f"{item.get('name') or item.get('medicine_name') or 'Medicine'} — {item.get('dose') or item.get('dosage') or 'dose not specified'}": item
            for item in meds
        }
        with st.form("send_medicine_reminder_form", clear_on_submit=True):
            selected_med_label = st.selectbox("Choose medicine", list(med_options.keys()))
            reminder_message = st.text_input("Message (optional)", placeholder="Please check your scheduled dose")
            send_reminder = st.form_submit_button("🔔 Send reminder", type="primary", use_container_width=True)
        if send_reminder:
            selected_med = med_options[selected_med_label]
            med_name = str(selected_med.get("name") or selected_med.get("medicine_name") or "your medicine")
            try:
                add_record("caregiver_alerts", {
                    "patient_id": ELDER_ID, "user_id": ELDER_ID,
                    "type": "caregiver_medicine_reminder",
                    "title": "Medicine reminder from your caregiver",
                    "message": reminder_message.strip() or f"Your caregiver reminds you to check your schedule for {med_name}.",
                    "medicine_name": med_name, "medication_id": selected_med.get("id", ""),
                    "status": "unread", "read": False, "source": "caregiver_dashboard",
                    "sent_by_uid": st.session_state["caregiver_auth"].get("uid", ""),
                })
                st.success("Reminder saved to the selected patient's Care+ alerts.")
            except Exception as exc:
                st.error(f"Could not send the reminder: {exc}")
    else:
        st.info("A reminder can be sent after the doctor's medication list is available.")

    st.markdown("### Dose activity")
    page_table(dose_logs[:30], ["created_at", "medicine_name", "medication_name", "scheduled_time", "status", "taken", "notes"],
               "No dose activity has been recorded yet.")

    st.markdown("### Missed-dose alerts")
    st.caption("Overdue doses can be recorded as patient alerts. Automatic SMS/push delivery requires a notification service to be configured.")

    from datetime import datetime as _datetime
    now_local = _datetime.now()
    today_str = now_local.date().isoformat()
    alert_candidates = []
    for med in meds:
        if str(med.get("status", "active")).lower() in {"inactive", "stopped", "discontinued"}:
            continue
        raw_times = med.get("times", med.get("time", ""))
        if isinstance(raw_times, list):
            scheduled_times = [str(t).strip() for t in raw_times if str(t).strip()]
        else:
            scheduled_times = [t.strip() for t in str(raw_times or "").replace(";", ",").split(",") if t.strip()]
        for scheduled in scheduled_times:
            try:
                try:
                    scheduled_dt = _datetime.strptime(scheduled, "%H:%M").replace(
                        year=now_local.year, month=now_local.month, day=now_local.day)
                except ValueError:
                    scheduled_dt = _datetime.strptime(scheduled.upper(), "%I:%M %p").replace(
                        year=now_local.year, month=now_local.month, day=now_local.day)
            except ValueError:
                continue
            if now_local <= scheduled_dt:
                continue
            med_name = str(med.get("name") or med.get("medicine_name") or "Medicine")
            taken = any(
                str(log.get("medicine_name") or log.get("medication_name") or "").lower() == med_name.lower()
                and today_str in str(log.get("created_at", ""))
                and (log.get("taken") is True or str(log.get("status", "")).lower() in {"taken", "completed", "done"})
                for log in dose_logs
            )
            if not taken:
                alert_candidates.append({"medicine": med_name, "scheduled": scheduled})

    if alert_candidates:
        for item in alert_candidates:
            st.warning(f"Missed dose: **{item['medicine']}** was scheduled for **{item['scheduled']}**.")
        if st.button("Save missed-dose alert for patient", type="primary", key="save_missed_dose_alerts"):
            try:
                existing_alerts = list_records("medication_alerts")
                saved_count = 0
                for item in alert_candidates:
                    duplicate = any(
                        str(a.get("medicine_name", "")).lower() == item["medicine"].lower()
                        and str(a.get("scheduled_time", "")) == item["scheduled"]
                        and str(a.get("due_date", "")) == today_str
                        for a in existing_alerts
                    )
                    if not duplicate:
                        add_record("medication_alerts", {
                            "medicine_name": item["medicine"], "scheduled_time": item["scheduled"],
                            "due_date": today_str, "alert_type": "missed_dose",
                            "message": f"Your {item['medicine']} dose scheduled for {item['scheduled']} may have been missed. Please follow your doctor's instructions.",
                            "recipient_user_id": ELDER_ID, "status": "pending",
                            "created_by_role": "caregiver_system",
                        })
                        saved_count += 1
                st.success(f"Saved {saved_count} new missed-dose alert(s) for the patient.")
                st.info("The alert is stored in Firestore; it is not a push/SMS notification until a notification provider is connected.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save missed-dose alert: {exc}")
    else:
        st.success("No overdue doses detected from the medication times currently saved.")

elif page == "Send Wellbeing Check-in":
    st.subheader("Send a wellbeing check-in now")
    st.write("Send an immediate in-app prompt to the selected elderly person's Care+ dashboard.")
    st.info("This creates an in-app alert immediately. It is not an SMS, email, or push notification.")

    with st.form("send_wellbeing_checkin_now_form", clear_on_submit=True):
        prompt_title = st.text_input("Title", value="Your caregiver is checking in")
        prompt_message = st.text_area(
            "Message to the patient",
            value="How are you feeling today? Please open Care+ and complete your daily wellbeing check-in.",
            height=110,
        )
        send_now = st.form_submit_button("😊 Send check-in now", type="primary", use_container_width=True)

    if send_now:
        if not prompt_message.strip():
            st.error("Please enter a message before sending.")
        else:
            try:
                add_record("caregiver_alerts", {
                    "patient_id": ELDER_ID,
                    "user_id": ELDER_ID,
                    "type": "caregiver_wellbeing_checkin",
                    "title": prompt_title.strip() or "Your caregiver is checking in",
                    "message": prompt_message.strip(),
                    "target_section": "wellbeing",
                    "action_label": "Open How Am I Feeling?",
                    "status": "unread",
                    "read": False,
                    "source": "caregiver_dashboard",
                    "sent_by_uid": st.session_state.get("caregiver_auth", {}).get("uid", ""),
                })
                st.success("Wellbeing message sent. When the patient opens it, they can go to their existing “How Am I Feeling?” section.")
            except Exception as exc:
                st.error(f"Could not send the wellbeing check-in: {exc}")

elif page == "Appointments":
    st.subheader("Appointments")
    st.write("View appointment requests created by the elderly user. This dashboard does not provide medical advice or replace a clinician.")
    page_table(appointments, ["created_at", "doctor_name", "doctor", "appointment_date", "date", "appointment_time", "reason", "status"], "No appointment requests found.")
    with st.expander("Update appointment coordination status"):
        choices = [x for x in appointments if x.get("id")]
        if choices:
            selected = st.selectbox("Choose appointment", choices, format_func=lambda x: f'{x.get("doctor_name", x.get("doctor", "Doctor"))} — {x.get("appointment_date", x.get("date", x.get("created_at", "")))}')
            status = st.selectbox("Coordination status", ["Requested", "Confirmed", "Reschedule needed", "Completed", "Cancelled"])
            if st.button("Save appointment status", type="primary"):
                try:
                    update_record("appointments", selected["id"], {"status": status, "coordinated_by_role": "caregiver"})
                    st.success("Appointment status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update appointment: {exc}")
        else:
            st.info("There are no appointments to update.")

elif page == "SOS & Care Requests":
    st.subheader("SOS alerts & requests for help")
    st.markdown("### SOS alerts")
    render_sos_alerts(emergencies)
    with st.expander("Mark an SOS alert as followed up"):
        active = [x for x in emergencies if x.get("id") and str(x.get("status", "ACTIVE")).upper() not in ("CLOSED", "RESOLVED", "CANCELLED")]
        if active:
            selected = st.selectbox("SOS alert", active, format_func=lambda x: f'{x.get("emergency_type", "SOS")} — {x.get("created_at", "")}')
            new_status = st.selectbox("Follow-up status", ["ACTIVE", "CONTACTED", "RESOLVED"])
            if st.button("Update SOS follow-up", type="primary"):
                try:
                    update_record("emergencies", selected["id"], {"status": new_status, "caregiver_followup_at": now_iso()})
                    st.success("SOS follow-up status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update alert: {exc}")
        else:
            st.info("No active SOS alerts to update.")
    st.markdown("### Requests for care")
    page_table(care_requests, ["created_at", "service", "care_type", "details", "preferred_date", "preferred_time", "status"], "No care requests recorded.")
    with st.expander("Update care request status"):
        if care_requests:
            selected_request = st.selectbox("Care request", care_requests, format_func=lambda x: f'{x.get("service", x.get("care_type", "Care request"))} — {x.get("created_at", "")}')
            req_status = st.selectbox("Request status", ["New", "Acknowledged", "In progress", "Completed", "Unable to fulfil"])
            if st.button("Save care request status", type="primary"):
                try:
                    update_record("care_requests", selected_request["id"], {"status": req_status, "handled_by_role": "caregiver"})
                    st.success("Care request status updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not update request: {exc}")

elif page == "Family & Emergency Contacts":
    st.subheader("Family & emergency contacts")
    st.write("Add or update trusted family members, helpers and emergency contacts for the linked older adult.")
    page_table(contacts, ["name", "relationship", "role", "phone", "priority", "created_at"], "No contacts saved yet.")
    with st.form("contact_form", clear_on_submit=True):
        st.markdown("### Add a contact")
        name = st.text_input("Contact name")
        relationship = st.selectbox("Relationship to elderly person", ["Child", "Other family", "Friend", "Volunteer", "Trusted caregiver", "Other"])
        phone = st.text_input("Phone number")
        priority = st.selectbox("Contact priority", ["Primary emergency contact", "Secondary contact", "General contact"])
        notes = st.text_input("Notes (optional)")
        save_contact = st.form_submit_button("Save contact", type="primary", use_container_width=True)
    if save_contact:
        if not name.strip() or not phone.strip():
            st.error("Enter a name and phone number.")
        else:
            try:
                add_record("emergency_contacts", {
                    "name": name.strip(), "relationship": relationship,
                    "role": "caregiver_contact", "phone": phone.strip(),
                    "priority": priority, "notes": notes.strip(),
                    "added_by_role": "caregiver",
                })
                st.success("Contact saved.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save contact: {exc}")

elif page == "Health Documents":
    st.subheader("Health documents")
    st.write("Caregivers can help upload and organise existing prescriptions, lab reports and medical documents. Use only files shared with permission.")
    page_table(documents, ["created_at", "title", "document_type", "url", "notes", "added_by_role"], "No health documents have been added yet.")
    with st.form("document_form", clear_on_submit=True):
        title = st.text_input("Document title")
        doc_type = st.selectbox("Document type", ["Prescription", "Lab report", "Discharge summary", "Insurance", "Other"])
        url = st.text_input("Secure document URL (if already uploaded)")
        notes = st.text_area("Notes (optional)")
        save_doc = st.form_submit_button("Save document details", type="primary", use_container_width=True)
    if save_doc:
        if not title.strip() or not url.strip():
            st.error("Enter the document title and a secure URL.")
        else:
            try:
                add_record("medical_documents", {
                    "title": title.strip(), "document_type": doc_type,
                    "url": url.strip(), "notes": notes.strip(),
                    "added_by_role": "caregiver",
                })
                st.success("Document details saved.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save document details: {exc}")

st.divider()
st.caption("Care+ prototype. Protect the older adult's privacy, obtain consent, and use real emergency services for urgent situations.")
