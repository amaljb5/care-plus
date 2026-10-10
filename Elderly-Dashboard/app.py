import os
import json
import queue
import time as time_module
import textwrap
import urllib.request
import urllib.error
import requests
from datetime import datetime, date, time
from typing import Any

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# =========================================================
# CARE+ ELDERLY DASHBOARD
# Based on the uploaded Member 3 and Member 4 project files.
# Streamlit + Firebase Cloud Firestore
# =========================================================

st.set_page_config(
    page_title="Care+ | Elderly Dashboard",
    page_icon="💚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Force a consistent, high-contrast Care+ light theme, including the sidebar. */
:root { color-scheme: light !important; }
html, body, .stApp,
[data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: #F5FAF7 !important;
    color: #17352B !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background: #E8F3ED !important;
    color: #17352B !important;
}
[data-testid="stSidebar"] * {
    color: #17352B !important;
}
[data-testid="stSidebar"] hr {
    border-color: #B7D2C3 !important;
}
.block-container { max-width: 1250px; padding: 1.4rem 2rem 3rem 2rem; }
h1, h2, h3, h4, h5, h6,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #123D2E !important;
}
h1 { font-size: 2.35rem !important; line-height: 1.2 !important; }
h2 { font-size: 1.85rem !important; }
h3 { font-size: 1.4rem !important; }
p, label, li, .stMarkdown, [data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"] p {
    font-size: 1.12rem !important;
    line-height: 1.5 !important;
    color: #17352B !important;
}
/* Readable navigation buttons in both selected and unselected states. */
div[data-testid="stSidebar"] div.stButton > button {
    min-height: 3.8rem !important;
    width: 100%;
    border-radius: 15px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: .65rem .8rem !important;
    white-space: normal !important;
    background: #FFFFFF !important;
    color: #174734 !important;
    border: 1.5px solid #9BBEAA !important;
}
div[data-testid="stSidebar"] div.stButton > button p,
div[data-testid="stSidebar"] div.stButton > button span {
    color: #174734 !important;
}
div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
    background: #176B4D !important;
    color: #FFFFFF !important;
    border-color: #176B4D !important;
}
div[data-testid="stSidebar"] div.stButton > button[kind="primary"] p,
div[data-testid="stSidebar"] div.stButton > button[kind="primary"] span {
    color: #FFFFFF !important;
}
div.stButton > button, div.stFormSubmitButton > button,
[data-testid="stLinkButton"] a {
    min-height: 4rem !important;
    width: 100%;
    border-radius: 16px !important;
    font-size: 1.15rem !important;
    font-weight: 750 !important;
    padding: .7rem 1rem !important;
    border: 2px solid #C5DCD0 !important;
    white-space: normal !important;
    background: #FFFFFF !important;
    color: #174734 !important;
}
div.stButton > button p, div.stFormSubmitButton > button p {
    color: inherit !important;
}
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: #176B4D !important;
    color: #FFFFFF !important;
    border-color: #176B4D !important;
}
div.stButton > button[kind="primary"] p,
div.stFormSubmitButton > button[kind="primary"] p {
    color: #FFFFFF !important;
}
input, textarea, [data-baseweb="select"], [data-baseweb="input"] {
    font-size: 1.08rem !important;
    min-height: 3rem !important;
    color: #17352B !important;
    background-color: #FFFFFF !important;
}
[data-testid="stMetricValue"] { font-size: 1.7rem !important; color: #123D2E !important; }
[data-testid="stAlert"] { border-radius: 14px !important; font-size: 1.08rem !important; }
[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
button:focus, input:focus, textarea:focus {
    outline: 3px solid #176B4D !important; outline-offset: 2px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 18px; }

/* Elderly login card */
.elder-login-wrap { max-width: 560px; margin: 3.2rem auto 1rem auto; }
.elder-login-card {
    background: #FFFFFF; border: 1px solid #D7E7DE; border-radius: 26px;
    padding: 2rem 2rem 1.4rem 2rem; box-shadow: 0 18px 48px rgba(23,53,43,.10);
}
.elder-login-eyebrow { color: #176B4D; font-size: .82rem; font-weight: 800; letter-spacing: .13em; }
.elder-login-title { color: #123D2E; font-size: 2rem; font-weight: 850; margin: .45rem 0 .35rem 0; }
.elder-login-subtitle { color: #64748B; font-size: 1rem; margin-bottom: 1.2rem; }


/* Elderly portal login — one aligned, polished card */
.elder-login-wrap {
    max-width: 500px !important;
    margin: 2.8rem auto 0.8rem auto !important;
}
.elder-login-card {
    background: #FFFFFF !important;
    border: 1px solid #D9E4EF !important;
    border-radius: 24px 24px 0 0 !important;
    padding: 2rem 2rem 0.65rem 2rem !important;
    box-shadow: 0 18px 48px rgba(20, 43, 77, .09) !important;
    margin: 0 !important;
}
.elder-login-eyebrow {
    color: #087E80 !important;
    font-size: .73rem !important;
    font-weight: 800 !important;
    letter-spacing: .15em !important;
    text-transform: uppercase !important;
}
.elder-login-title {
    color: #142B4D !important;
    font-size: 1.85rem !important;
    line-height: 1.2 !important;
    font-weight: 800 !important;
    margin: .55rem 0 .45rem 0 !important;
}
.elder-login-subtitle {
    color: #718096 !important;
    font-size: .96rem !important;
    margin-bottom: 0 !important;
}
div[data-testid="stForm"] {
    box-sizing: border-box !important;
    max-width: 500px !important;
    margin: 0 auto !important;
    background: #FFFFFF !important;
    border: 1px solid #D9E4EF !important;
    border-top: 0 !important;
    border-radius: 0 0 24px 24px !important;
    padding: 1rem 2rem 1.7rem 2rem !important;
    box-shadow: 0 18px 48px rgba(20, 43, 77, .09) !important;
}
div[data-testid="stForm"] label,
div[data-testid="stForm"] p {
    color: #405570 !important;
    font-size: .91rem !important;
}
div[data-testid="stForm"] input {
    box-sizing: border-box !important;
    background: #F8FAFC !important;
    color: #142B4D !important;
    -webkit-text-fill-color: #142B4D !important;
    border: 1px solid #CCD8E6 !important;
    border-radius: 12px !important;
    min-height: 44px !important;
    box-shadow: none !important;
}
div[data-testid="stForm"] input::placeholder {
    color: #8795A8 !important;
    -webkit-text-fill-color: #8795A8 !important;
    opacity: 1 !important;
}
div[data-testid="stForm"] input:focus {
    border-color: #1B7D70 !important;
    box-shadow: 0 0 0 3px rgba(27,125,112,.10) !important;
}
div[data-testid="stForm"] [data-testid="stCheckbox"] label {
    color: #5A6E85 !important;
}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
    background: #192F55 !important;
    border: 1px solid #192F55 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    border-radius: 999px !important;
    min-height: 44px !important;
    margin-top: .15rem !important;
    transition: background .15s ease, transform .15s ease !important;
}
div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
    background: #223D6A !important;
    border-color: #223D6A !important;
    transform: translateY(-1px) !important;
}
.elder-forgot-link {
    max-width: 500px !important;
    box-sizing: border-box !important;
    margin: 0 auto 1.5rem auto !important;
    padding: .85rem 1.25rem !important;
    text-align: right !important;
    background: #FFFFFF !important;
    border: 1px solid #D9E4EF !important;
    border-top: 0 !important;
    border-radius: 0 0 24px 24px !important;
}
.elder-forgot-link a {
    color: #087E80 !important;
    text-decoration: none !important;
    font-size: .9rem !important;
    font-weight: 700 !important;
}
.elder-forgot-link a:hover { text-decoration: underline !important; }

</style>
""", unsafe_allow_html=True)

# -------------------- Firebase / Firestore --------------------
@st.cache_resource
def get_db():
    if firebase_admin._apps:
        app = firebase_admin.get_app()
    elif "firebase" in st.secrets:
        cfg = dict(st.secrets["firebase"])
        if "service_account_json" in cfg:
            cred = credentials.Certificate(json.loads(cfg["service_account_json"]))
        else:
            cred = credentials.Certificate(cfg)
        app = firebase_admin.initialize_app(cred)
    else:
        key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not key_path or not os.path.isfile(key_path):
            raise RuntimeError(
                "Firebase credentials are missing. Copy your existing .streamlit/secrets.toml "
                "into this project, or set GOOGLE_APPLICATION_CREDENTIALS."
            )
        app = firebase_admin.initialize_app(credentials.Certificate(key_path))
    return firestore.client(app=app)

try:
    db = get_db()
    firebase_ready = True
except Exception as exc:
    db = None
    firebase_ready = False
    st.error("Care+ could not connect to Firestore. Check your Firebase configuration.")
    with st.expander("Technical details"):
        st.code(str(exc))


def firebase_email_password_login(email: str, password: str) -> dict:
    """Sign in using Firebase Authentication's email/password REST endpoint."""
    cfg = dict(st.secrets.get("firebase", {}))
    api_key = cfg.get("api_key") or cfg.get("web_api_key") or cfg.get("web_apiKey")
    if not api_key:
        raise RuntimeError(
            "Firebase Web API key is missing. Add api_key = \"YOUR_FIREBASE_WEB_API_KEY\" "
            "inside your existing [firebase] section in .streamlit/secrets.toml."
        )
    endpoint = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={api_key}"
    )
    body = json.dumps({
        "email": email.strip(),
        "password": password,
        "returnSecureToken": True,
    }).encode("utf-8")
    request = urllib.request.Request(
        endpoint, data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
            message = detail.get("error", {}).get("message", "Login failed")
        except Exception:
            message = "Login failed"
        if "EMAIL_NOT_FOUND" in message or "INVALID_PASSWORD" in message or "INVALID_LOGIN_CREDENTIALS" in message:
            raise ValueError("Email or password is incorrect.") from None
        if "USER_DISABLED" in message:
            raise ValueError("This account has been disabled. Please contact the Care+ administrator.") from None
        raise ValueError(f"Firebase sign-in failed: {message}") from None


def find_elderly_patient_by_email(email: str):
    """Only allow patient emails; explicitly reject any email registered as a doctor."""
    normalized_email = email.strip().lower()

    # Doctor records take precedence: a doctor account must never enter this portal,
    # even if the same email was accidentally entered on a patient record.
    doctor_matches = list(
        db.collection("doctors").where("email", "==", normalized_email).limit(1).stream()
    )
    if doctor_matches:
        return None

    matches = list(
        db.collection("patients").where("email", "==", normalized_email).limit(2).stream()
    )
    if not matches:
        return None
    doc = matches[0]
    patient = doc.to_dict() or {}
    if str(patient.get("role", "patient")).strip().lower() not in {
        "patient", "elderly", "senior", "older_adult"
    }:
        return None
    patient_id = str(patient.get("profile_id") or patient.get("user_id") or doc.id)
    return {
        "id": patient_id,
        "name": patient.get("name") or patient.get("full_name") or "Care+ User",
        "email": str(patient.get("email") or email).strip().lower(),
    }


# ---------- Persistent elderly login ("Remember me") ----------
# Browser cookies survive Streamlit reruns and page refreshes. The cookie stores
# only Firebase's refresh token, never the user's password.
try:
    import extra_streamlit_components as stx
    _elder_cookie_manager = stx.CookieManager(key="careplus_elderly_auth_cookies")
    _elder_cookie_support = True
except ImportError:
    _elder_cookie_manager = None
    _elder_cookie_support = False


def get_firebase_api_key():
    cfg = dict(st.secrets.get("firebase", {}))
    return (cfg.get("api_key") or cfg.get("web_api_key") or
            cfg.get("web_apiKey") or cfg.get("apiKey") or
            cfg.get("apiKey".lower()) or
            st.secrets.get("firebase_api_key", ""))


def refresh_elder_firebase_session(refresh_token: str):
    api_key = get_firebase_api_key()
    if not api_key or not refresh_token:
        return None
    try:
        response = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={api_key}",
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=15,
        )
        if response.status_code != 200:
            return None
        tokens = response.json()
        id_token = tokens.get("id_token")
        if not id_token:
            return None
        lookup = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}",
            json={"idToken": id_token},
            timeout=15,
        )
        if lookup.status_code != 200:
            return None
        users = lookup.json().get("users", [])
        if not users:
            return None
        email = str(users[0].get("email", "")).strip().lower()
        patient = find_elderly_patient_by_email(email)
        if not patient:
            return None
        return {
            "patient": patient,
            "auth_uid": users[0].get("localId", ""),
            "id_token": id_token,
            "refresh_token": tokens.get("refresh_token", refresh_token),
        }
    except Exception:
        return None


def restore_elderly_session_from_cookie():
    if not _elder_cookie_support:
        return False
    try:
        saved = _elder_cookie_manager.get("careplus_elderly_refresh_token")
        if not saved:
            return False
        restored = refresh_elder_firebase_session(str(saved))
        if not restored:
            try:
                _elder_cookie_manager.delete(
                    cookie="careplus_elderly_refresh_token",
                    key="clear_invalid_elderly_refresh_token",
                )
            except Exception:
                pass
            return False
        patient = restored["patient"]
        st.session_state.elder_logged_in = True
        st.session_state.elder_uid = patient["id"]
        st.session_state.elder_name = patient["name"]
        st.session_state.elder_email = patient["email"]
        st.session_state.elder_auth_uid = restored["auth_uid"]
        st.session_state.elder_id_token = restored["id_token"]
        st.session_state.elder_refresh_token = restored["refresh_token"]
        st.session_state.elder_remember_me = True
        st.session_state.page = st.session_state.get("page", "medicines")
        _elder_cookie_manager.set(
            cookie="careplus_elderly_refresh_token",
            val=restored["refresh_token"],
            key="refresh_elderly_refresh_token",
        )
        return True
    except Exception:
        return False


def render_elderly_login():
    st.markdown(
        """
        <div class="elder-login-wrap">
          <div class="elder-login-card">
            <div class="elder-login-eyebrow">CARE+ · ELDERLY PORTAL</div>
            <div class="elder-login-title">Welcome back</div>
            <div class="elder-login-subtitle">Sign in to access your medicines and care information.</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("elderly_login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="Enter your registered email", key="elder_login_email")
        password = st.text_input("Password", placeholder="Enter your password", type="password", key="elder_login_password")
        remember = st.checkbox("Remember me", value=True, key="elder_login_remember")
        submitted = st.form_submit_button("Sign in to Care+", type="primary", use_container_width=True)

    st.markdown(
        '<div class="elder-forgot-link"><a href="?elder_forgot_password=1">Forgot password?</a></div>',
        unsafe_allow_html=True,
    )

    if submitted:
        if not email.strip() or not password:
            st.error("Enter both your email and password.")
            return
        try:
            auth_result = firebase_email_password_login(email.strip(), password)
            patient = find_elderly_patient_by_email(email)
            if not patient:
                # Do not allow a doctor/admin Firebase account to enter this portal.
                st.error("This login is not linked to an elderly patient profile. Please use the correct elderly account or contact the Care+ administrator.")
                return
            st.session_state.elder_logged_in = True
            st.session_state.elder_logout_requested = False
            st.session_state.elder_uid = patient["id"]
            st.session_state.elder_name = patient["name"]
            st.session_state.elder_email = patient["email"]
            st.session_state.elder_auth_uid = auth_result.get("localId", "")
            st.session_state.elder_id_token = auth_result.get("idToken", "")
            st.session_state.elder_refresh_token = auth_result.get("refreshToken", "")
            st.session_state.elder_remember_me = remember
            if _elder_cookie_support:
                try:
                    if remember and auth_result.get("refreshToken"):
                        _elder_cookie_manager.set(
                            cookie="careplus_elderly_refresh_token",
                            val=auth_result["refreshToken"],
                            key="save_elderly_refresh_token",
                        )
                    else:
                        _elder_cookie_manager.delete(
                            cookie="careplus_elderly_refresh_token",
                            key="delete_elderly_refresh_token",
                        )
                except Exception:
                    st.warning("Login succeeded, but Remember me could not be saved. Install extra-streamlit-components to keep the session after refresh.")
            elif remember:
                st.warning("To keep you signed in after refresh, install extra-streamlit-components.")
            st.session_state.page = "medicines"
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(str(exc))


if "elder_logged_in" not in st.session_state:
    st.session_state.elder_logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "medicines"

# On refresh, Streamlit's in-memory session can reset. Restore it from the
# Firebase refresh-token cookie when Remember me was selected.
if not firebase_ready:
    st.stop()
# Do not immediately restore a cookie session after the user explicitly logged out.
if (
    not st.session_state.elder_logged_in
    and not st.session_state.get("elder_logout_requested", False)
    and _elder_cookie_support
):
    restore_elderly_session_from_cookie()
if not st.session_state.elder_logged_in:
    render_elderly_login()
    st.stop()

def now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def add_record(collection: str, data: dict[str, Any]) -> str:
    data = dict(data)
    data["user_id"] = st.session_state.elder_uid
    data["created_at"] = now_iso()
    ref = db.collection(collection).document()
    ref.set(data)
    return ref.id

def my_records(collection: str, limit: int = 100) -> list[dict[str, Any]]:
    docs = db.collection(collection).where(
        "user_id", "==", st.session_state.elder_uid
    ).limit(limit).stream()
    rows = []
    for doc in docs:
        row = doc.to_dict()
        row["id"] = doc.id
        rows.append(row)
    return rows

def all_records(collection: str, limit: int = 100) -> list[dict[str, Any]]:
    return [{"id": d.id, **(d.to_dict() or {})}
            for d in db.collection(collection).limit(limit).stream()]

def set_page(page: str):
    st.session_state.page = page

def top_bar():
    st.title("💚 Care+")
    if st.session_state.get("elder_name"):
        st.caption(f"Welcome, {st.session_state.elder_name}")

# Sidebar navigation: medicines opens first whenever the app starts.
with st.sidebar:
    st.title("💚 Care+")
    st.caption("Elderly Dashboard")
    st.markdown("---")
    nav_items = [
        ("💊 My Medicines", "medicines"),
        ("❤️ My Health", "health"),
        ("📅 My Appointments", "appointments"),
        ("📞 Call Family or Doctor", "contacts"),
        ("🤝 Ask for Care", "care"),
        ("😊 How Am I Feeling?", "wellbeing"),
        ("📄 My Health Documents", "documents"),
    ]
    for nav_label, nav_page in nav_items:
        if st.button(nav_label, key=f"sidebar_{nav_page}", use_container_width=True,
                     type="primary" if st.session_state.page == nav_page else "secondary"):
            set_page(nav_page)
            st.rerun()

    st.markdown("---")
    if st.button("🚪 Log out", key="elder_logout", use_container_width=True):
        # Prevent cookie-based auto-login during the logout rerun.
        st.session_state["elder_logout_requested"] = True

        # Clear the in-memory login before rendering anything else.
        for key in (
            "elder_logged_in", "elder_uid", "elder_name", "elder_email",
            "elder_auth_uid", "elder_id_token", "elder_refresh_token",
            "elder_profile", "elder_profile_id",
        ):
            st.session_state.pop(key, None)

        st.session_state["elder_logged_in"] = False
        st.session_state["page"] = "login"

        # Remove the persistent refresh-token cookie so refresh cannot sign the user back in.
        if _elder_cookie_support:
            try:
                _elder_cookie_manager.delete(
                    cookie="careplus_elderly_refresh_token",
                    key="logout_elderly_refresh_token",
                )
            except Exception:
                pass

        st.rerun()

# Floating voice-assistant control: native Streamlit button, fixed to viewport bottom-right.
st.markdown("""
<style>
/* Target the voice widget by Streamlit key and by its button help label,
   so the styling still works across Streamlit DOM versions. */
div[data-testid="stElementContainer"].st-key-careplus_voice_float_button,
.st-key-careplus_voice_float_button,
div[data-testid="stElementContainer"]:has(button[aria-label*="Activate Care+ voice assistant"]) {
    position: fixed !important;
    right: 24px !important;
    bottom: 24px !important;
    width: 64px !important;
    height: 64px !important;
    min-width: 64px !important;
    max-width: 64px !important;
    z-index: 1000000 !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stElementContainer"].st-key-careplus_voice_float_button > div,
.st-key-careplus_voice_float_button > div,
.st-key-careplus_voice_float_button [data-testid="stButton"] {
    width: 64px !important;
    height: 64px !important;
    margin: 0 !important;
    padding: 0 !important;
}
.st-key-careplus_voice_float_button button,
div[data-testid="stElementContainer"]:has(button[aria-label*="Activate Care+ voice assistant"]) button {
    width: 64px !important;
    min-width: 64px !important;
    max-width: 64px !important;
    height: 64px !important;
    min-height: 64px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: #176B4D !important;
    color: #FFFFFF !important;
    border: 3px solid #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(0,0,0,.22) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 28px !important;
    line-height: 1 !important;
}
.st-key-careplus_voice_float_button button *,
div[data-testid="stElementContainer"]:has(button[aria-label*="Activate Care+ voice assistant"]) button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    fill: #FFFFFF !important;
    margin: 0 !important;
    padding: 0 !important;
    font-size: 28px !important;
    line-height: 1 !important;
}
.st-key-careplus_voice_float_button button:hover,
div[data-testid="stElementContainer"]:has(button[aria-label*="Activate Care+ voice assistant"]) button:hover {
    background: #12563E !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

_voice_float_clicked = st.button("🎙️", key="careplus_voice_float_button", help="Activate Care+ voice assistant")
if _voice_float_clicked:
    st.session_state.page = "voice"
    st.session_state["careplus_voice_auto_listen"] = True
    st.rerun()

# Activate the voice system automatically once after the user signs in.
# The floating microphone remains available to start it again later.
if not st.session_state.get("careplus_voice_initial_run_done", False):
    st.session_state["careplus_voice_initial_run_done"] = True
    st.session_state.page = "voice"
    st.session_state["careplus_voice_auto_listen"] = True

# -------------------- Header --------------------
top_bar()
page = st.session_state.page

if not firebase_ready:
    st.stop()

# Medicine reminder: every 10 minutes while the elderly dashboard is open.
# Browser sound autoplay can be blocked until the user interacts with the page.
@st.fragment(run_every="10m")
def medicine_reminder_popup():
    try:
        active_medicines = [
            item for item in my_records("medications")
            if item.get("active", True)
        ]
        if not active_medicines:
            st.caption("Medicine reminders are ready when your doctor adds a medication schedule.")
            return

        now = datetime.now().astimezone()
        now_ts = now.timestamp()
        last_ts = float(st.session_state.get("medicine_reminder_last_ts", 0) or 0)
        if last_ts and now_ts - last_ts < 600:
            return

        names = [
            str(item.get("name") or item.get("medicine_name") or "your medicine")
            for item in active_medicines[:5]
        ]
        medicine_names = ", ".join(names)
        if len(active_medicines) > 5:
            medicine_names += f" and {len(active_medicines) - 5} more"

        st.session_state["medicine_reminder_last_ts"] = now_ts
        st.toast(
            f"💊 Medicine reminder: Please check whether it is time to take {medicine_names}.",
            icon="💚",
        )
        st.warning(
            f"Medicine reminder: Please check your medication schedule for {medicine_names}. "
            "Only mark a dose as taken after you have taken it."
        )

        # Attempt a short beep. Modern browsers may require a prior click/tap to allow audio.
        try:
            import streamlit.components.v1 as components
            components.html(
                """<script>
                try {
                  const ctx = new (window.AudioContext || window.webkitAudioContext)();
                  const osc = ctx.createOscillator();
                  const gain = ctx.createGain();
                  osc.connect(gain); gain.connect(ctx.destination);
                  osc.frequency.value = 880; gain.gain.value = 0.12;
                  osc.start();
                  setTimeout(() => { osc.stop(); ctx.close(); }, 350);
                } catch (e) {}
                </script>""",
                height=0,
            )
        except Exception:
            pass

        # Notify caregivers by adding a Firestore alert document. Keep this scoped to
        # the patient so caregiver dashboards can query patient_id/user_id and unread alerts.
        patient_id = str(
            st.session_state.get("elder_profile_id")
            or st.session_state.get("elder_uid")
            or st.session_state.get("elder_auth_uid")
            or ""
        )
        alert_key = f"{patient_id}:{int(now_ts // 600)}"
        if patient_id and st.session_state.get("medicine_caregiver_alert_key") != alert_key:
            try:
                alert_data = {
                    "patient_id": patient_id,
                    "user_id": patient_id,
                    "type": "medicine_reminder_unconfirmed",
                    "title": "Medicine reminder",
                    "message": f"Care+ reminded the patient to check their medicine: {medicine_names}. The patient has not confirmed the dose in this reminder cycle.",
                    "medicine_names": names,
                    "status": "unread",
                    "read": False,
                    "created_at": now.isoformat(),
                }
                db.collection("caregiver_alerts").add(alert_data)
                st.session_state["medicine_caregiver_alert_key"] = alert_key
            except Exception:
                st.caption("Caregiver alert could not be saved. Check Firestore permissions and the caregiver dashboard alert collection.")
    except Exception:
        # Do not block the rest of the dashboard if a reminder check fails.
        pass

medicine_reminder_popup()

# Daily wellbeing reminder: caregiver/doctor configures wellness_reminders/{document}
# with user_id, reminder_time="HH:MM", active=true. The reminder appears prominently
# when the elderly user's local clock reaches the configured time while the app is open.
try:
    current_hhmm = datetime.now().astimezone().strftime("%H:%M")
    reminders = [r for r in my_records("wellness_reminders") if r.get("active", True)]
    due_reminder = any(str(r.get("reminder_time", ""))[:5] == current_hhmm for r in reminders)
except Exception:
    due_reminder = False

if due_reminder and page != "wellbeing":
    st.markdown("<div style='text-align:center; padding:22px; border-radius:20px; background:#FFF0B3; border:3px solid #E6B422; margin:10px 0 24px 0;'>"
                "<div style='font-size:2.2rem; font-weight:800; color:#533D00;'>😊 TIME FOR YOUR DAILY CHECK-IN</div>"
                "<div style='font-size:1.3rem; color:#533D00; margin-top:8px;'>Please tell us how you are feeling today.</div></div>",
                unsafe_allow_html=True)
    if st.button("Start my wellbeing check-in", type="primary", use_container_width=True):
        set_page("wellbeing")
        st.rerun()

# ---------------- SOS: one confirmation, then open call immediately ----------------
SOS_MEET_URL = "https://meet.google.com/dis-vmxc-cxr"  # Opens Google Meet to start a meeting.

# Floating circular SOS button on the top-right of every page.
st.markdown(
    """
    <style>
    .careplus-sos-float {
        position: fixed;
        top: 18px;
        right: 26px;
        z-index: 999999;
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: #B91C1C;
        border: 3px solid #FFFFFF;
        box-shadow: 0 4px 14px rgba(0,0,0,.22);
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none !important;
        font-size: 30px;
        font-weight: 900;
    }
    .careplus-sos-float:hover { background: #991B1B; color: #FFFFFF !important; }
    </style>
    <a class="careplus-sos-float" href="?sos=1" title="SOS — I Need Help" aria-label="SOS — I Need Help">SOS</a>
    """,
    unsafe_allow_html=True,
)

# Query parameter routes the floating button to the SOS confirmation page.
try:
    if st.query_params.get("sos") == "1":
        page = "emergency"
        st.session_state.sos_confirmation = True
except Exception:
    pass

if page == "emergency":
    st.header("🚨 SOS — I Need Help")

    st.markdown(
        """
        <div style="background:#FCE8E6;border:2px solid #C62828;border-radius:18px;
                    padding:24px;text-align:center;margin:12px 0 20px 0;">
          <div style="font-size:1.7rem;font-weight:900;color:#8E1717;">
            Need help connecting with your caregiver?
          </div>
          <div style="font-size:1.1rem;color:#5C2020;margin-top:8px;">
            Tap YES to open Google Meet. This prototype opens Meet; it does not automatically notify or join your caregiver.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "sos_confirmation" not in st.session_state:
        st.session_state.sos_confirmation = True
    if "sos_submitted_id" not in st.session_state:
        st.session_state.sos_submitted_id = None

    if st.session_state.sos_confirmation:
        yes_col, no_col = st.columns(2)
        with yes_col:
            if st.button("✅ YES — CALL NOW", type="primary", use_container_width=True):
                try:
                    alert_id = add_record("emergencies", {
                        "emergency_type": "SOS",
                        "details": f"SOS activated. Google Meet opened: {SOS_MEET_URL}",
                        "emergency_contact": SOS_MEET_URL,
                        "status": "ACTIVE",
                    })
                    st.session_state.sos_submitted_id = alert_id
                except Exception:
                    # Still proceed to the call if Firestore is unavailable.
                    st.warning("Could not save the SOS alert, but you can still call now.")
                st.markdown(
                    f'<meta http-equiv="refresh" content="0;url={SOS_MEET_URL}">',
                    unsafe_allow_html=True,
                )
                st.link_button("🎥 JOIN SOS GOOGLE MEET", SOS_MEET_URL, use_container_width=True)
                st.info("This opens the shared Care+ SOS Google Meet link. Your caregiver can use the same link to join.")
                st.session_state.sos_confirmation = False
        with no_col:
            if st.button("❌ NO — CANCEL", use_container_width=True):
                st.session_state.sos_confirmation = False
                st.rerun()

    if not st.session_state.sos_confirmation and not st.session_state.sos_submitted_id:
        st.success("SOS cancelled.")
        if st.button("Show SOS confirmation again", use_container_width=True):
            st.session_state.sos_confirmation = True
            st.rerun()

    st.markdown("### My emergency alerts")
    alerts = sorted(my_records("emergencies"), key=lambda x: x.get("created_at", ""), reverse=True)
    if alerts:
        st.dataframe(
            [{"Date": a.get("created_at"), "Type": a.get("emergency_type"),
              "Status": a.get("status")} for a in alerts[:10]],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No emergency alerts saved yet.")

# ---------------- Offline Voice Assistant ----------------
elif page == "voice":
    st.header("🎙️ Care+ Voice Assistant")
    st.write("Care+ Voice is activated. Speak a command in English and the matching section will open.")
    st.info("The offline assistant listens for a short command whenever it starts. Use the round microphone button at the bottom-right to activate it again.")

    # Locate the model whether it is beside this app.py or remains in the starter folder.
    _voice_model_name = "vosk-model-small-en-in-0.4"
    _voice_model_candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), _voice_model_name),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "careplus_voice_offline_starter", _voice_model_name),
        os.path.join(os.getcwd(), _voice_model_name),
        os.path.join(os.getcwd(), "careplus_voice_offline_starter", _voice_model_name),
    ]
    _voice_model_path = next(
        (candidate for candidate in _voice_model_candidates
         if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "am", "final.mdl"))),
        None,
    )

    def _careplus_voice_recognize(seconds: int = 6) -> str:
        try:
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer
        except ImportError as exc:
            raise RuntimeError(
                "Voice packages are missing. Run: pip install vosk sounddevice pyttsx3"
            ) from exc
        if not _voice_model_path:
            raise RuntimeError(
                "Could not find the Vosk model. Put `vosk-model-small-en-in-0.4` "
                "beside this app.py, or inside `careplus_voice_offline_starter` beside the app."
            )

        model = Model(_voice_model_path)
        recognizer = KaldiRecognizer(model, 16000)
        audio_queue = queue.Queue()

        def _audio_callback(indata, frames, callback_time, status):
            audio_queue.put(bytes(indata))

        transcript_parts = []
        deadline = time_module.monotonic() + seconds
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=_audio_callback,
        ):
            while time_module.monotonic() < deadline:
                try:
                    audio_data = audio_queue.get(timeout=0.25)
                except queue.Empty:
                    continue
                if recognizer.AcceptWaveform(audio_data):
                    result = json.loads(recognizer.Result())
                    if result.get("text"):
                        transcript_parts.append(result["text"])
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get("text"):
                transcript_parts.append(final_result["text"])
        return " ".join(transcript_parts).strip()

    def _careplus_voice_speak(text: str):
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            # Keep the on-screen response available if OS text-to-speech is unavailable.
            pass

    def _careplus_route_voice_command(transcript: str):
        normalized = transcript.lower().strip()
        command_routes = [
            # SOS is checked first and still requires confirmation.
            (("sos", "emergency", "help me", "i need help", "emergency help"), "emergency",
             "You asked for emergency help. Please confirm on the SOS screen before opening Google Meet."),
            (("my health documents", "health documents", "medical documents", "my documents", "documents", "health files"), "documents",
             "Opening My Health Documents."),
            (("ask for care", "request care", "i need care", "need a caregiver", "get me a caregiver", "care request"), "care",
             "Opening Ask for Care."),
            (("my health", "show my health", "health history", "my health history", "health records", "health profile"), "health",
             "Opening My Health."),
            (("medicine", "medicines", "my pills", "my medication", "my medications", "show my medicines", "open medicines"), "medicines",
             "Opening My Medicines. Follow the schedule provided by your clinician."),
            (("appointment", "appointments", "show my appointments", "open appointments", "next appointment"), "appointments",
             "Opening My Appointments."),
            (("wellbeing", "well being", "how am i feeling", "check in", "feeling", "daily wellbeing", "daily wellness"), "wellbeing",
             "Opening How Am I Feeling."),
            (("call family", "call my family", "call doctor", "call my doctor", "call family or doctor", "contacts", "family", "phone my doctor"), "contacts",
             "Opening Call Family or Doctor."),
        ]
        for phrases, destination, response_text in command_routes:
            if any(phrase in normalized for phrase in phrases):
                return destination, response_text
        return "", (
            "Sorry, I didn't recognize that."
        )

    _voice_should_listen = bool(st.session_state.pop("careplus_voice_auto_listen", False)) or not st.session_state.get("careplus_voice_initial_greeting_done", False)
    if _voice_should_listen:
        try:
            _careplus_voice_speak("Voice system active")
            st.session_state["careplus_voice_initial_greeting_done"] = True
            with st.spinner("Voice system activated. Listening for your command…"):
                _voice_transcript = _careplus_voice_recognize(6)
            if not _voice_transcript:
                st.warning("I didn't hear a command. Tap the round microphone button at the bottom-right and try again.")
            else:
                st.session_state["careplus_last_voice_transcript"] = _voice_transcript
                _voice_destination, _voice_response = _careplus_route_voice_command(_voice_transcript)
                st.session_state["careplus_last_voice_response"] = _voice_response
                _careplus_voice_speak(_voice_response)
                if _voice_destination == "emergency":
                    st.session_state.sos_confirmation = True
                    st.session_state.page = "emergency"
                    st.rerun()
                elif _voice_destination:
                    st.session_state.page = _voice_destination
                    st.rerun()
        except Exception as _voice_exc:
            st.error(f"Voice assistant could not start: {_voice_exc}")

    if st.session_state.get("careplus_last_voice_transcript"):
        st.subheader("I heard")
        st.write(f"“{st.session_state['careplus_last_voice_transcript']}”")
    if st.session_state.get("careplus_last_voice_response"):
        st.success(st.session_state["careplus_last_voice_response"])

    with st.expander("Commands you can say"):
        st.markdown(
            "- **My Medicines:** “Show my medicines” / “Open medicines”\\n"
            "- **My Health:** “Show my health” / “Health history”\\n"
            "- **My Appointments:** “Show my appointments” / “Next appointment”\\n"
            "- **Call Family or Doctor:** “Call my family” / “Call my doctor”\\n"
            "- **Ask for Care:** “Ask for care” / “I need a caregiver”\\n"
            "- **How Am I Feeling?:** “How am I feeling?” / “Daily wellbeing”\\n"
            "- **My Health Documents:** “Open my health documents” / “Show my documents”\\n"
            "- **SOS:** “I need help” (opens the existing SOS confirmation page)"
        )
# ---------------- Medicines: Member 2 planned data model ----------------
elif page == "medicines":
    st.header("💊 My Medicines")
    st.write("Your doctor or care team can add medication details. Here you can record doses you have taken.")
    medicines = [m for m in my_records("medications") if m.get("active", True)]
    if medicines:
        for med in medicines:
            with st.container(border=True):
                st.subheader(med.get("name") or med.get("medicine_name", "Medicine"))
                st.write(f"**Dose:** {med.get('dose', 'Not specified')}")
                meal_time = med.get("meal_time")
                timing_instruction = med.get("timing_instruction")
                if timing_instruction:
                    timing_text = timing_instruction
                else:
                    timing_text = med.get("timing", "Not specified")
                if meal_time:
                    timing_text = f"{meal_time} · {timing_text}"
                st.write(f"**When to take it:** {timing_text}")
                if st.button("✅ I took this medicine", key=f"taken_{med['id']}", use_container_width=True):
                    add_record("medicine_logs", {
                        "medication_id": med["id"], "medication_name": med.get("name", "Medicine"),
                        "dose": med.get("dose", ""), "status": "TAKEN", "taken_at": now_iso()
                    })
                    st.success("Dose recorded.")
                    st.rerun()
    else:
        st.info("No medicines have been added to your profile yet. Your doctor or care team can add them.")
    logs = sorted(my_records("medicine_logs"), key=lambda x: x.get("created_at", ""), reverse=True)
    st.subheader("Recent doses")
    if logs:
        st.dataframe([{"Date": x.get("created_at"), "Medicine": x.get("medication_name"), "Dose": x.get("dose"), "Status": x.get("status")} for x in logs[:20]], use_container_width=True, hide_index=True)
    else:
        st.info("No doses recorded yet.")

# ---------------- Health: read-only profile and readings ----------------
elif page == "health":
    st.header("❤️ My Health")
    st.write("These details are maintained by your caregiver or doctor.")
    profile = []
    for collection in ("senior_profiles", "elderly_profiles", "profiles"):
        try:
            profile.extend(my_records(collection, 5))
        except Exception:
            pass
    if profile:
        p = profile[0]
        for label, keys in [("Name", ("name", "full_name")), ("Date of birth", ("date_of_birth", "dob")),
                            ("Blood group", ("blood_group",)), ("Address", ("address",)),
                            ("Allergies", ("allergies",)), ("Medical conditions", ("medical_conditions", "conditions"))]:
            val = next((p.get(k) for k in keys if p.get(k) not in (None, "", [])), None)
            if val is not None:
                st.markdown(f"**{label}:** {val}")
    else:
        st.info("Your profile details will appear here after your caregiver or doctor adds them.")
    # Doctor-entered medical records are saved in the shared "medical_records"
    # collection, keyed by patient_id (the patient's Firestore profile/document ID).
    st.subheader("Medical records from my doctor")
    medical_records = []
    patient_keys = {
        str(st.session_state.get("elder_uid", "")).strip(),
        str(st.session_state.get("elder_profile_id", "")).strip(),
        str(st.session_state.get("elder_auth_uid", "")).strip(),
    }
    patient_keys.discard("")
    try:
        for patient_key in patient_keys:
            try:
                docs = db.collection("medical_records").where("patient_id", "==", patient_key).limit(100).stream()
                medical_records.extend(
                    {"id": doc.id, **(doc.to_dict() or {})}
                    for doc in docs
                )
            except Exception:
                pass
        # Include records written with the elderly user's auth UID, if that schema is used.
        try:
            docs = db.collection("medical_records").where(
                "user_id", "==", st.session_state.get("elder_uid", "")
            ).limit(100).stream()
            medical_records.extend({"id": doc.id, **(doc.to_dict() or {})} for doc in docs)
        except Exception:
            pass
    except Exception:
        medical_records = []

    # De-duplicate records because a record may match more than one query.
    medical_records = list({record["id"]: record for record in medical_records}.values())
    medical_records.sort(key=lambda record: str(record.get("created_at", "")), reverse=True)
    if medical_records:
        for record in medical_records:
            with st.container(border=True):
                st.subheader(record.get("title") or record.get("record_type") or "Medical record")
                if record.get("record_type"):
                    st.caption(f"Record type: {record['record_type']}")
                if record.get("diagnosis"):
                    st.write(f"**Clinical details:** {record['diagnosis']}")
                if record.get("notes"):
                    st.write(f"**Notes:** {record['notes']}")
                if record.get("doctor_name"):
                    st.write(f"**Added by:** {record['doctor_name']}")
                if record.get("created_at"):
                    st.caption(f"Added: {record['created_at']}")
    else:
        st.info("No medical records from your doctor are available yet.")

    readings = sorted(my_records("health_readings"), key=lambda x: x.get("created_at", ""), reverse=True)
    st.subheader("My health readings")
    if readings:
        st.dataframe([{"Date": r.get("recorded_at", r.get("created_at")), "Measurement": r.get("reading_type"), "Value": f"{r.get('value')} {r.get('unit','')}", "Note": r.get("notes", "")} for r in readings[:40]], use_container_width=True, hide_index=True)
        numeric_types = sorted({r.get("reading_type") for r in readings if isinstance(r.get("value"), (float, int))})
        if numeric_types:
            graph_type = st.selectbox("View health trend", numeric_types)
            graph_values = [r["value"] for r in reversed(readings) if r.get("reading_type") == graph_type and isinstance(r.get("value"), (float, int))]
            if graph_values:
                st.line_chart({graph_type: graph_values})
    else:
        st.info("No health readings have been added by your care team yet.")

# ---------------- Appointments: Member 1 planned feature ----------------
elif page == "appointments":
    st.header("📅 My Appointments")
    with st.form("appointment_form"):
        reason = st.text_input("What would you like to discuss with the doctor?")
        preferred_date = st.date_input("Preferred date", min_value=date.today())
        preferred_time = st.time_input("Preferred time", value=time(10, 0))
        kind = st.selectbox("Appointment type", ["In person", "Audio call", "Video call"])
        submit = st.form_submit_button("Request appointment", use_container_width=True)
    if submit:
        if not reason.strip():
            st.error("Please enter a short reason.")
        else:
            req_id = add_record("appointments", {"reason": reason.strip(), "preferred_date": preferred_date.isoformat(), "preferred_time": preferred_time.strftime("%H:%M"), "appointment_type": kind, "status": "PENDING"})
            st.success(f"Appointment request saved. Reference: {req_id}")
            st.info("This demo records the request; it does not yet send the doctor a notification or start a call.")
    rows = sorted(my_records("appointments"), key=lambda x: x.get("preferred_date", ""), reverse=True)
    st.subheader("My appointment requests")
    if rows:
        st.dataframe([{"Date": r.get("preferred_date"), "Time": r.get("preferred_time"), "Type": r.get("appointment_type"), "Reason": r.get("reason"), "Status": r.get("status")} for r in rows], use_container_width=True, hide_index=True)
    else:
        st.info("No appointment requests yet.")

# ---------------- Contacts: Member 3 emergency contacts + Member 4 family links ----------------
elif page == "contacts":
    st.header("📞 Call Family or Doctor")
    st.write("Your caregiver or doctor manages these contacts. Tap a button to call when needed.")
    # Contacts are created by the caregiver dashboard with elderly_user_id.
    # The elderly portal's other records use user_id, so query this collection separately
    # and match against all known IDs for the currently signed-in profile.
    contact_owner_ids = {
        str(st.session_state.get("elder_uid", "")).strip(),
        str(st.session_state.get("elder_profile_id", "")).strip(),
        str(st.session_state.get("elder_auth_uid", "")).strip(),
    }
    profile_data = st.session_state.get("elder_profile", {})
    if isinstance(profile_data, dict):
        for key in ("id", "user_id", "uid", "auth_uid", "profile_id", "firebase_uid"):
            value = str(profile_data.get(key, "")).strip()
            if value:
                contact_owner_ids.add(value)
    contact_owner_ids.discard("")

    contacts = []
    try:
        for contact_doc in db.collection("emergency_contacts").limit(500).stream():
            contact = contact_doc.to_dict() or {}
            owners = {
                str(contact.get(key, "")).strip()
                for key in ("elderly_user_id", "user_id", "patient_id", "elder_id", "profile_id", "uid", "auth_uid")
            }
            owners.discard("")
            if owners.intersection(contact_owner_ids):
                contact["id"] = contact_doc.id
                contacts.append(contact)
    except Exception as exc:
        st.error(f"Could not load emergency contacts: {exc}")

    if contacts:
        for c in contacts:
            with st.container(border=True):
                st.subheader(c.get("name", "Contact"))
                st.write(c.get("relationship", "Family / care contact"))
                phone = str(c.get("phone") or c.get("phone_number") or "").strip()
                if phone:
                    st.link_button(f"📞 Call {c.get('name', 'contact')}", f"tel:{phone}", use_container_width=True)
                if c.get("email"):
                    st.caption(f"Email: {c.get('email')}")
    else:
        st.info("No contacts have been saved for this profile yet.")

# ---------------- Caregiver / volunteer booking: Member 3 ----------------
elif page == "care":
    st.header("🤝 Ask for Care")

    # Caregiver/volunteer profiles may be stored in either collection in this prototype.
    # Merge both sources and deduplicate by document ID, without showing explicitly unavailable profiles.
    caregiver_profiles = []
    seen_caregiver_ids = set()
    for collection_name in ("caregivers", "volunteers"):
        try:
            for profile in all_records(collection_name):
                profile_id = str(profile.get("id") or profile.get("uid") or profile.get("email") or "")
                if not profile_id:
                    profile_id = f"{collection_name}:{profile.get('name', '')}:{profile.get('phone', '')}"
                availability = profile.get("available", profile.get("is_available", True))
                availability_text = str(availability).strip().lower()
                if availability_text in ("false", "0", "no", "unavailable", "inactive", "disabled"):
                    continue
                if profile_id not in seen_caregiver_ids:
                    profile["_source_collection"] = collection_name
                    caregiver_profiles.append(profile)
                    seen_caregiver_ids.add(profile_id)
        except Exception:
            # Continue loading from the other supported collection if one is unavailable.
            continue

    service = st.selectbox("What help do you need?", ["Home-care visit", "Nurse", "Physiotherapist", "Hospital accompaniment", "Volunteer assistance"])
    st.subheader("Available caregivers")
    if caregiver_profiles:
        for cg in caregiver_profiles:
            # Wide, full-width profile card for each available caregiver.
            with st.container(border=True):
                caregiver_card_html = textwrap.dedent(f"""
                    <div style="
                        width:100%;
                        box-sizing:border-box;
                        padding:22px 26px;
                        border-radius:16px;
                        background:#FFFFFF;
                        border:1px solid #C7DED3;
                        box-shadow:0 4px 14px rgba(20,80,60,0.07);
                    ">
                        <div style="font-size:1.35rem;font-weight:700;color:#123F35;margin-bottom:14px;">
                            {cg.get('name') or cg.get('full_name') or cg.get('display_name') or 'Caregiver'}
                        </div>
                        <div style="font-size:1rem;line-height:1.9;color:#24463D;">
                            <div><strong>Service:</strong> {cg.get('service') or cg.get('services') or cg.get('role') or ('Volunteer assistance' if cg.get('_source_collection') == 'volunteers' else 'Home care')}</div>
                            {f"<div><strong>Phone:</strong> {cg.get('phone') or cg.get('phone_number')}</div>" if (cg.get('phone') or cg.get('phone_number')) else ""}
                            {f"<div><strong>Email:</strong> {cg.get('email')}</div>" if cg.get('email') else ""}
                        </div>
                    </div>
                """).strip()
                st.html(caregiver_card_html)
    else:
        st.info("No caregiver profiles are listed yet. Caregiver or volunteer profiles must be saved in the Firestore `caregivers` or `volunteers` collection to appear here.")
    with st.form("care_booking_form"):
        requested_date = st.date_input("Preferred date", min_value=date.today())
        notes = st.text_area("Additional details (optional)", height=90)
        submit = st.form_submit_button("Send care request", use_container_width=True)
    if submit:
        req_id = add_record("care_requests", {"service": service, "preferred_date": requested_date.isoformat(), "details": notes.strip(), "status": "PENDING"})
        st.success(f"Care request saved. Reference: {req_id}")
    st.subheader("My care requests")
    requests = sorted(my_records("care_requests"), key=lambda x: x.get("created_at", ""), reverse=True)
    if requests:
        st.dataframe([{"Date": r.get("preferred_date"), "Service": r.get("service"), "Status": r.get("status")} for r in requests], use_container_width=True, hide_index=True)
    else:
        st.info("No care requests yet.")

# ---------------- Daily wellbeing ----------------
elif page == "wellbeing":
    st.header("😊 Daily Wellbeing")

    st.info("Your caregiver or doctor sets the daily reminder time. When it is time, a large reminder appears here in Care+ while the website is open.")
    with st.form("wellbeing_form"):
        mood = st.radio("How are you feeling today?", ["Good", "Okay", "Not feeling well"])
        pain = st.radio("Are you in pain?", ["No", "A little", "A lot"])
        sleep = st.radio("How did you sleep?", ["Well", "Not too well", "Poorly"])
        note = st.text_area("Optional note", height=80)
        submit = st.form_submit_button("Save my check-in", use_container_width=True)
    if submit:
        add_record("wellness_checks", {"mood": mood, "pain": pain, "sleep": sleep, "notes": note.strip(), "check_date": date.today().isoformat()})
        st.success("Your wellbeing check-in has been saved.")
        if mood == "Not feeling well" or pain == "A lot":
            st.warning("Please contact your doctor or caregiver if you are concerned or symptoms are severe.")
    checks = sorted(my_records("wellness_checks"), key=lambda x: x.get("created_at", ""), reverse=True)
    if checks:
        st.subheader("Recent check-ins")
        st.dataframe([{"Date": r.get("check_date"), "Feeling": r.get("mood"), "Pain": r.get("pain"), "Sleep": r.get("sleep")} for r in checks[:14]], use_container_width=True)

# ---------------- Read-only medical documents ----------------
elif page == "documents":
    st.header("📄 My Health Documents")
    st.write("Your caregiver or doctor adds documents here. You can view them below.")
    docs = sorted(my_records("medical_documents"), key=lambda x: x.get("created_at", ""), reverse=True)
    if docs:
        for d in docs:
            with st.container(border=True):
                st.subheader(d.get("title", "Document"))
                st.write(d.get("document_type", "Document"))
                if d.get("notes"):
                    st.write(d["notes"])
                if str(d.get("url", "")).startswith("https://"):
                    st.link_button("📄 View document", d["url"], use_container_width=True)
                elif d.get("file_url") and str(d.get("file_url")).startswith("https://"):
                    st.link_button("📄 View document", d["file_url"], use_container_width=True)
    else:
        st.info("No health documents have been added by your caregiver or doctor yet.")

st.divider()
st.caption("Care+ college prototype. Medicine reminder popups repeat every 10 minutes while this dashboard is open. Notifications when the website is closed are not configured. This dashboard is not monitored continuously and must not be relied on as an emergency service.")
