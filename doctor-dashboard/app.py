import os
import json
import requests
from datetime import datetime, date, time
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Care+ | Doctor Dashboard", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme ----------
st.markdown("""
<style>
:root{color-scheme:light} html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#F4F7FB!important;color:#172B4D!important}
[data-testid="stSidebar"],[data-testid="stSidebar"]>div,[data-testid="stSidebarContent"]{background:#E8F4EE!important}
[data-testid="stSidebar"]{border-right:1px solid #D4E7DC!important}[data-testid="stSidebar"] *{color:#17352B}
h1,h2,h3,h4{color:#172B4D!important;letter-spacing:-.02em}p,label,li,[data-testid="stCaptionContainer"],[data-testid="stWidgetLabel"] p{color:#334E68;line-height:1.5}
.block-container{max-width:1500px;padding-top:1.5rem;padding-bottom:3rem}
.doctor-hero{background:linear-gradient(120deg,#123C69,#176B63 60%,#2D9B83);border-radius:24px;padding:28px 32px;color:white;margin:8px 0 24px;box-shadow:0 16px 38px #17365d20}
.doctor-hero h1,.doctor-hero p{color:white!important;margin:0}.doctor-hero h1{font-size:2.05rem;font-weight:800}.doctor-hero p{margin-top:8px;opacity:.93}
div[data-testid="stMetric"]{background:white;border:1px solid #E5EBF3;padding:17px;border-radius:17px;box-shadow:0 5px 16px #1a365d0b}
div[data-testid="stVerticalBlockBorderWrapper"]{background:white;border:1px solid #E5EBF3;border-radius:18px;box-shadow:0 7px 22px #1a365d0b}
div[data-testid="stButton"]>button,div[data-testid="stFormSubmitButton"]>button{border-radius:12px;min-height:42px;font-weight:650}
div[data-testid="stButton"]>button[kind="primary"],div[data-testid="stFormSubmitButton"]>button[kind="primary"]{background:#176B4D!important;color:#fff!important;border:1px solid #176B4D!important}
[data-testid="stSidebar"] [data-testid="stButton"]>button{width:100%;min-height:48px;border-radius:15px;text-align:left;background:#fff;border:1px solid #C7DED1;color:#17352B;font-weight:550;margin-bottom:7px}
[data-testid="stSidebar"] [data-testid="stButton"]>button[kind="primary"]{background:#176B4D!important;border-color:#176B4D!important;color:#fff!important;font-weight:750}
input,textarea,[data-baseweb="select"]>div{border-radius:10px!important}
.patient-card{background:white;border:1px solid #DDE7EF;border-radius:18px;overflow:hidden;box-shadow:0 8px 24px #17365d10;margin-bottom:4px}

.login-shell{max-width:540px;margin:36px auto 0;background:#fff;border:1px solid #E1E8F0;border-radius:24px;padding:30px;box-shadow:0 18px 50px #17365d14}
.login-eyebrow{color:#176B63;font-weight:800;text-transform:uppercase;letter-spacing:.1em;font-size:.75rem}
.login-title{font-size:1.8rem;font-weight:850;color:#172B4D;margin:8px 0}
.login-subtitle{color:#64748B;margin-bottom:20px}

.login-subtitle{color:#64748B;margin-bottom:22px}
.login-shell{
    max-width:480px !important;
    margin:30px auto 0 !important;
    background:#FFFFFF !important;
    border:1px solid #E2E8F0 !important;
    border-radius:22px !important;
    padding:32px 34px 28px !important;
    box-shadow:0 16px 42px rgba(25,45,80,.10) !important;
}
.login-shell + div [data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextInput"] input:hover {
    box-sizing:border-box !important;
    width:100% !important;
    min-height:46px !important;
    border:1px solid #CBD5E1 !important;
    border-radius:12px !important;
    background:#F8FAFC !important;
    color:#172B4D !important;
    padding:10px 14px !important;
    box-shadow:none !important;
    outline:none !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color:#2D8A72 !important;
    box-shadow:0 0 0 3px rgba(45,138,114,.13) !important;
}
div[data-testid="stTextInput"] [data-baseweb="input"],
div[data-testid="stTextInput"] [data-baseweb="base-input"] {
    border:0 !important;
    border-radius:12px !important;
    background:transparent !important;
    box-shadow:none !important;
}
div[data-testid="stTextInput"] [data-testid="stInputRootElement"] {
    border:0 !important;
    border-radius:12px !important;
    background:transparent !important;
}
div[data-testid="stTextInput"] button {
    border-radius:0 12px 12px 0 !important;
    background:#F8FAFC !important;
    border:1px solid #CBD5E1 !important;
    border-left:0 !important;
    color:#64748B !important;
}
div[data-testid="stCheckbox"] label {
    color:#475569 !important;
    font-size:.92rem !important;
}
.login-submit-wrap div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
    min-height:46px !important;
    border-radius:12px !important;
    border:1px solid #176B58 !important;
    background:#176B58 !important;
    color:#FFFFFF !important;
    font-weight:700 !important;
    box-shadow:none !important;
}
div[data-testid="stFormSubmitButton"] > button:hover {
    background:#125744 !important;
    border-color:#125744 !important;
}
.forgot-link-row {
    text-align:right;
    margin:2px 0 16px;
    font-size:.9rem;
}
.forgot-link-row a {
    color:#176B58 !important;
    text-decoration:none !important;
    font-weight:600;
}
.forgot-link-row a:hover { text-decoration:underline !important; }

.st-key-doctor_login_panel{max-width:520px;margin:34px auto 18px!important;padding:30px!important;background:#FFFFFF!important;border:1px solid #DCE5F0!important;border-radius:22px!important;box-shadow:0 18px 48px rgba(23,43,77,.12)!important}
.st-key-doctor_login_panel [data-testid="stTextInput"] input{border-radius:999px!important;min-height:46px!important;background:#F8FAFC!important;border:1px solid #D6DFEB!important;color:#172B4D!important;padding-left:18px!important}
.st-key-doctor_login_panel [data-testid="stButton"] button,.st-key-doctor_login_panel [data-testid="stFormSubmitButton"] button{border-radius:999px!important;min-height:44px!important;font-weight:750!important}
.st-key-doctor_login_panel [data-testid="stFormSubmitButton"] button{background:#172B4D!important;color:#FFFFFF!important;border:0!important}
.st-key-doctor_login_panel [data-testid="stFormSubmitButton"] button:hover{background:#24446F!important;color:#FFFFFF!important}
.login-links{font-size:.85rem;color:#64748B}

.patient-cover{height:72px;background:linear-gradient(120deg,#4778F5,#70A1FF)}.patient-body{padding:0 18px 18px;text-align:center}.patient-avatar{height:64px;width:64px;border-radius:50%;background:#E8F4EE;border:4px solid white;display:flex;align-items:center;justify-content:center;font-size:1.8rem;margin:-32px auto 6px;position:relative}.patient-name{font-weight:800;font-size:1.05rem;color:#172B4D}.patient-id{font-size:.82rem;color:#64748B;margin:5px 0 12px}

/* Fix Streamlit BaseWeb wrappers: style the OUTER field, not just the input */
div[data-testid="stTextInput"] [data-baseweb="input"],
div[data-testid="stTextInput"] [data-baseweb="base-input"],
div[data-testid="stTextInput"] [data-testid="stInputRootElement"],
div[data-testid="stTextInput"] > div > div,
div[data-testid="stTextInput"] > div > div > div {
    background: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    outline: none !important;
    overflow: hidden !important;
}
div[data-testid="stTextInput"] input {
    background: #F8FAFC !important;
    color: #172B4D !important;
    border: 0 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
    outline: none !important;
    min-height: 46px !important;
    padding: 10px 14px !important;
}
div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
div[data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within,
div[data-testid="stTextInput"] [data-testid="stInputRootElement"]:focus-within {
    border-color: #2D8A72 !important;
    box-shadow: 0 0 0 3px rgba(45,138,114,.12) !important;
}
div[data-testid="stTextInput"] button,
div[data-testid="stTextInput"] button:hover,
div[data-testid="stTextInput"] button:focus {
    background: #F8FAFC !important;
    color: #64748B !important;
    border: 0 !important;
    border-radius: 0 12px 12px 0 !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 12px !important;
}


/* Ensure form inputs, especially multiline Address, have readable contrast */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextArea"] textarea {
    border: 1px solid #CBD5E1 !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    min-height: 100px !important;
    box-shadow: none !important;
}
div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] [data-baseweb="textarea"],
div[data-testid="stTextArea"] > div > div {
    background: #FFFFFF !important;
    border: 0 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #2D8A72 !important;
    box-shadow: 0 0 0 3px rgba(45,138,114,.12) !important;
    outline: none !important;
}


/* High-contrast primary buttons: visible labels on green backgrounds */
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stButton"] > button,
button[kind="primary"],
button[kind="secondary"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
    opacity: 1 !important;
    text-shadow: none !important;
}
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stButton"] > button {
    border-radius: 12px !important;
}
div[data-testid="stFormSubmitButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[kind="primary"] {
    background: #176B58 !important;
    border: 1px solid #176B58 !important;
}
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stButton"] > button:hover {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    filter: brightness(.94);
}


/* Explicitly force all multiline textareas (Address, Medical Notes, etc.) to white */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextArea"] textarea:hover {
    background-color: #FFFFFF !important;
    color: #172B4D !important;
    -webkit-text-fill-color: #172B4D !important;
    caret-color: #172B4D !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] [data-baseweb="textarea"],
div[data-testid="stTextArea"] [data-baseweb="textarea"] > div,
div[data-testid="stTextArea"] > div,
div[data-testid="stTextArea"] > div > div {
    background-color: #FFFFFF !important;
    border: 0 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
div[data-testid="stTextArea"] textarea::placeholder {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #2D8A72 !important;
    box-shadow: 0 0 0 2px rgba(45,138,114,.12) !important;
}


/* Sidebar navigation: restore readable labels without changing other buttons */
[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #C7DED1 !important;
    color: #17352B !important;
    -webkit-text-fill-color: #17352B !important;
    text-align: left !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] * {
    color: #17352B !important;
    -webkit-text-fill-color: #17352B !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
    background: #176B4D !important;
    border: 1px solid #176B4D !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    text-align: left !important;
    font-weight: 750 !important;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

</style>""", unsafe_allow_html=True)

# ---------- Firestore ----------
@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        if "firebase" in st.secrets:
            cfg = dict(st.secrets["firebase"])
            if "service_account_json" in cfg:
                cred = credentials.Certificate(json.loads(cfg["service_account_json"]))
            else:
                cred = credentials.Certificate(cfg)
            firebase_admin.initialize_app(cred)
        else:
            p = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not p or not os.path.exists(p):
                raise RuntimeError("Firebase credentials are missing. Use your existing .streamlit/secrets.toml.")
            firebase_admin.initialize_app(credentials.Certificate(p))
    return firestore.client()

try:
    db = get_db()
    db_ready = True
except Exception as exc:
    db = None
    db_ready = False
    st.error("Care+ could not connect to Firestore. Check your Firebase configuration.")
    with st.expander("Technical details"):
        st.code(str(exc))


def now_iso(): return datetime.now().astimezone().isoformat(timespec="seconds")

def read_all(collection: str, limit: int = 300):
    if not db_ready: return []
    try:
        out=[]
        for doc in db.collection(collection).limit(limit).stream():
            item=doc.to_dict() or {}; item["id"]=doc.id; out.append(item)
        return out
    except Exception:
        return []

def read_for_patient(collection: str, patient_id: str, limit: int = 300):
    rows=read_all(collection,limit)
    return [r for r in rows if str(r.get("user_id",r.get("patient_id",r.get("elder_id",""))))==str(patient_id)]

def add_record(collection: str, data: dict[str, Any], patient_id: str | None = None):
    payload=dict(data); payload["created_at"]=now_iso()
    if patient_id:
        payload["user_id"]=str(patient_id); payload["patient_id"]=str(patient_id)
    ref=db.collection(collection).document(); ref.set(payload); return ref.id

def update_record(collection: str, record_id: str, data: dict[str, Any]):
    db.collection(collection).document(record_id).update(data)

def table(rows, columns=None, empty="No records found."):
    if not rows: st.info(empty); return
    if columns:
        rows=[{k:r.get(k,"") for k in columns if k in r} | ({"id":r.get("id","")} if "id" in r else {}) for r in rows]
    st.dataframe(rows,use_container_width=True,hide_index=True)

def _format_children(value):
    """Convert common Firestore child/family field shapes into readable names."""
    if value is None or value == "":
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        # A single child object, or a mapping of child IDs to child details.
        direct = value.get("name") or value.get("full_name") or value.get("child_name")
        if direct:
            return str(direct).strip()
        names = []
        for item in value.values():
            if isinstance(item, dict):
                name = item.get("name") or item.get("full_name") or item.get("child_name")
                if name:
                    names.append(str(name).strip())
            elif isinstance(item, str) and item.strip():
                names.append(item.strip())
        return ", ".join(dict.fromkeys(names))
    if isinstance(value, (list, tuple, set)):
        names = []
        for item in value:
            if isinstance(item, str) and item.strip():
                names.append(item.strip())
            elif isinstance(item, dict):
                name = (item.get("name") or item.get("full_name") or
                        item.get("child_name") or item.get("display_name"))
                if name:
                    names.append(str(name).strip())
        return ", ".join(dict.fromkeys(names))
    return str(value).strip()


def get_profiles():
    profiles = []
    seen = set()

    # First, read the patient's main profile from the existing profile collections.
    for coll in ["elderly_profiles", "senior_profiles", "patients", "users"]:
        for r in read_all(coll, 500):
            role = str(r.get("role", "")).lower()
            if role and role not in {"elderly", "senior", "patient", "older_adult"} and coll == "users":
                continue
            pid = str(r.get("user_id") or r.get("profile_id") or r.get("id") or "").strip()
            if not pid or pid in seen:
                continue
            seen.add(pid)

            child_value = (
                r.get("children_names") or r.get("childrenNames") or
                r.get("children") or r.get("child_names") or
                r.get("childNames") or r.get("children_name") or
                r.get("child_name") or r.get("childName")
            )
            child_names = _format_children(child_value)

            # In the current Care+ patient schema, the child's name is stored
            # in guardian_name when guardian_relationship is "Child".
            guardian_relationship = str(r.get("guardian_relationship") or "").strip().lower()
            guardian_name = str(r.get("guardian_name") or "").strip()
            if guardian_relationship == "child" and guardian_name:
                child_names = ", ".join(dict.fromkeys(
                    ([child_names] if child_names else []) + [guardian_name]
                ))

            profiles.append({
                "id": pid,
                "name": r.get("name") or r.get("full_name") or r.get("display_name") or "Elderly profile",
                "children": child_names or "Not added",
                "photo": r.get("photo_url") or r.get("profile_photo") or r.get("photo") or "",
            })

    # Some versions of Care+ save children/family members in their own collection.
    # Match those records back to the patient using the common patient ID fields.
    child_collections = ["children", "child_profiles", "family_members", "family_contacts"]
    child_records = []
    for coll in child_collections:
        child_records.extend(read_all(coll, 1000))

    for profile in profiles:
        collected = []
        for child in child_records:
            linked_id = str(
                child.get("patient_id") or child.get("elderly_id") or
                child.get("elder_id") or child.get("profile_id") or
                child.get("user_id") or child.get("patientId") or
                child.get("elderlyId") or ""
            ).strip()
            if linked_id != profile["id"]:
                continue
            child_name = (
                child.get("child_name") or child.get("name") or
                child.get("full_name") or child.get("display_name") or
                child.get("contact_name")
            )
            if child_name:
                collected.append(str(child_name).strip())

        if collected:
            existing = [] if profile["children"] == "Not added" else [
                part.strip() for part in str(profile["children"]).split(",") if part.strip()
            ]
            profile["children"] = ", ".join(dict.fromkeys(existing + collected))

    if not any(p["id"] == "demo-elder-001" for p in profiles):
        profiles.insert(0, {
            "id": "demo-elder-001",
            "name": "Demo elderly profile",
            "children": "Not added",
            "photo": "",
        })
    return profiles

if not db_ready:
    st.stop()

# ---------- Persistent browser session ----------
# Install extra-streamlit-components to keep a secure refresh token in a browser cookie.
try:
    import extra_streamlit_components as stx
    _cookie_manager = stx.CookieManager(key="careplus_doctor_auth_cookies")
    _cookie_support = True
except ImportError:
    _cookie_manager = None
    _cookie_support = False

# ---------- Doctor authentication ----------
def get_doctor_api_key():
    """Read the Firebase Web API key; never store doctor passwords in Firestore."""
    try:
        for section_name in ("firebase_client", "firebase"):
            section = st.secrets.get(section_name, {})
            for key_name in ("api_key", "apiKey", "web_api_key"):
                value = section.get(key_name)
                if value:
                    return str(value)
        value = st.secrets.get("firebase_api_key", "")
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv("FIREBASE_API_KEY", "")

def find_doctor_by_email(email):
    """Find a doctor allowlist/profile record created by the admin."""
    normalized = email.strip().lower()
    for collection_name in ("doctors", "doctor_profiles"):
        try:
            matches = list(db.collection(collection_name).where("email", "==", normalized).limit(2).stream())
            if not matches:
                # Existing records may preserve email casing.
                matches = [d for d in db.collection(collection_name).limit(500).stream()
                           if str((d.to_dict() or {}).get("email", "")).strip().lower() == normalized]
            for doc in matches:
                data = doc.to_dict() or {}
                if data.get("active", True) is False or str(data.get("status", "active")).lower() in {"disabled", "inactive", "suspended"}:
                    continue
                data["id"] = doc.id
                data["email"] = normalized
                return data
        except Exception:
            continue
    return None

def refresh_firebase_session(refresh_token):
    """Exchange a Firebase refresh token for a new short-lived ID token."""
    api_key = get_doctor_api_key()
    if not api_key or not refresh_token:
        return False, "Missing Firebase API key or refresh token."
    try:
        response = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={api_key}",
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=15,
        )
        payload = response.json()
        if response.ok and payload.get("id_token"):
            return True, {
                "idToken": payload.get("id_token"),
                "refreshToken": payload.get("refresh_token", refresh_token),
                "localId": payload.get("user_id", ""),
                "email": payload.get("user_id", ""),
            }
        return False, payload.get("error", {}).get("message", "Session expired.")
    except requests.RequestException:
        return False, "Could not refresh the Firebase session. Check your connection."

def send_firebase_password_reset(email):
    api_key = get_doctor_api_key()
    if not api_key:
        return False, "Firebase Web API key is missing from secrets.toml."
    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}",
            json={"requestType": "PASSWORD_RESET", "email": email.strip()},
            timeout=15,
        )
        payload = response.json()
        if response.ok:
            return True, "If this email belongs to a Firebase account, a password reset email has been requested."
        message = payload.get("error", {}).get("message", "Could not request password reset.")
        return False, message.replace("_", " ").title()
    except requests.RequestException:
        return False, "Could not contact Firebase Authentication. Check your internet connection."

def authenticate_firebase_email_password(email, password):
    api_key = get_doctor_api_key()
    if not api_key:
        return False, "Firebase Web API key is missing. Add api_key to [firebase_client] or [firebase] in .streamlit/secrets.toml."
    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
            json={"email": email.strip(), "password": password, "returnSecureToken": True},
            timeout=15,
        )
        payload = response.json()
        if response.ok and payload.get("idToken"):
            return True, payload
        message = payload.get("error", {}).get("message", "Login failed.")
        friendly = {
            "EMAIL_NOT_FOUND": "This email is not registered in Firebase Authentication.",
            "INVALID_PASSWORD": "The password is incorrect.",
            "INVALID_LOGIN_CREDENTIALS": "The email or password is incorrect.",
            "USER_DISABLED": "This account has been disabled.",
            "INVALID_EMAIL": "Enter a valid email address.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please wait and try again later.",
        }
        return False, friendly.get(message, message.replace("_", " ").title())
    except requests.RequestException:
        return False, "Could not contact Firebase Authentication. Check your internet connection and Firebase configuration."

if "doctor_auth" not in st.session_state:
    st.session_state.doctor_auth = None

# Restore login after browser refresh using a Firebase refresh token stored in a browser cookie.
if (
    not st.session_state.doctor_auth
    and _cookie_support
    and not st.session_state.get("doctor_explicitly_signed_out", False)
):
    try:
        _all_saved_cookies = _cookie_manager.get_all() or {}
        _saved_refresh_token = _all_saved_cookies.get("careplus_doctor_refresh_token")
        if _saved_refresh_token:
            _refresh_ok, _refresh_result = refresh_firebase_session(_saved_refresh_token)
            if _refresh_ok:
                _restored_email = str(_refresh_result.get("email", "")).strip().lower()
                # Firebase refresh response does not include email; resolve it from the ID token claims.
                import base64 as _base64
                try:
                    _claims = _refresh_result["idToken"].split(".")[1]
                    _claims += "=" * (-len(_claims) % 4)
                    _restored_email = str(json.loads(_base64.urlsafe_b64decode(_claims.encode()).decode()).get("email", "")).strip().lower()
                except Exception:
                    _restored_email = ""
                _restored_doctor = find_doctor_by_email(_restored_email) if _restored_email else None
                if _restored_doctor:
                    st.session_state.doctor_auth = {
                        "email": _restored_email,
                        "uid": _refresh_result.get("localId", ""),
                        "doctor_record_id": _restored_doctor.get("id", ""),
                        "doctor_name": _restored_doctor.get("name") or _restored_doctor.get("full_name") or "Doctor",
                        "refresh_token": _refresh_result.get("refreshToken", _saved_refresh_token),
                    }
                    try:
                        from datetime import datetime, timedelta
                        _cookie_manager.set(
                            "careplus_doctor_refresh_token",
                            _refresh_result.get("refreshToken", _saved_refresh_token),
                            expires_at=datetime.now() + timedelta(days=30),
                            key="careplus_refresh_doctor_cookie",
                        )
                    except Exception:
                        pass
    except Exception:
        pass

if not st.session_state.doctor_auth:
    st.markdown(
        '<div class="doctor-hero"><h1>🩺 Care+ Doctor Workspace</h1>'
        '<p>Secure access to your assigned patients, appointments and clinical records.</p></div>',
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 1.5, 1])
    with center:
        with st.container(border=True, key="doctor_login_panel"):
            st.markdown(
                '<div class="login-eyebrow">DOCTOR PORTAL</div>'
                '<div class="login-title">Login</div>'
                '<div class="login-subtitle">Sign in to access your assigned patients.</div>',
                unsafe_allow_html=True,
            )
            with st.form("doctor_login_form", clear_on_submit=False):
                login_email = st.text_input("Email", placeholder="doctor@clinic.com", key="doctor_login_email")
                login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="doctor_login_password")
                remember_me = st.checkbox("Remember me", value=True)
                login_submit = st.form_submit_button("Login", type="primary", use_container_width=True)

            st.markdown(
                '<div class="forgot-link-row"><a href="#reset-password">Forgot password?</a></div>',
                unsafe_allow_html=True,
            )
            with st.expander("Reset password", expanded=False):
                reset_email = st.text_input(
                    "Doctor email for password reset",
                    key="doctor_reset_email",
                    placeholder="doctor@example.com",
                )
                if st.button("Send reset link", key="doctor_send_reset_link", use_container_width=True):
                    if not reset_email.strip():
                        st.warning("Enter your doctor email first.")
                    else:
                        reset_ok, reset_message = send_firebase_password_reset(reset_email.strip())
                        if reset_ok:
                            st.success(reset_message)
                        else:
                            st.error(reset_message)

    st.caption("Only active doctor accounts registered in Care+ can access clinical workspaces.")
    if login_submit:
        if not login_email.strip() or not login_password:
            st.error("Enter both your email and password.")
        else:
            doctor_record = find_doctor_by_email(login_email)
            if not doctor_record:
                st.error("This email is not registered as an active doctor in the Care+ doctor database. Contact the admin.")
            else:
                ok, auth_result = authenticate_firebase_email_password(login_email, login_password)
                if not ok:
                    st.error(auth_result)
                else:
                    auth_email = str(auth_result.get("email", login_email)).strip().lower()
                    if auth_email != login_email.strip().lower():
                        st.error("The authenticated email does not match the doctor profile.")
                    else:
                        st.session_state.doctor_explicitly_signed_out = False
                        st.session_state.doctor_auth = {
                            "email": auth_email,
                            "uid": auth_result.get("localId", ""),
                            "doctor_record_id": doctor_record.get("id", ""),
                            "doctor_name": doctor_record.get("name") or doctor_record.get("full_name") or "Doctor",
                            "refresh_token": auth_result.get("refreshToken", ""),
                            "remember_me": bool(remember_me),
                        }
                        if remember_me and _cookie_support and auth_result.get("refreshToken"):
                            try:
                                from datetime import datetime, timedelta
                                _cookie_manager.set(
                                    "careplus_doctor_refresh_token",
                                    auth_result["refreshToken"],
                                    expires_at=datetime.now() + timedelta(days=30),
                                    key="careplus_set_doctor_cookie",
                                )
                            except Exception:
                                st.warning("Login succeeded, but the browser session could not be saved.")
                        elif not _cookie_support:
                            st.warning("For refresh persistence, install extra-streamlit-components.")
                        st.session_state.doctor_patient_id = None
                        st.session_state.doctor_change_patient = False
                        st.session_state.doctor_page = "Overview"
                        st.rerun()
    st.stop()

# Revalidate the admin allowlist on each Streamlit rerun, and use it as the source
# of truth for which patient profiles this doctor is permitted to see.
doctor_auth = st.session_state.doctor_auth
doctor_record = find_doctor_by_email(doctor_auth.get("email", ""))
if not doctor_record:
    st.session_state.doctor_auth = None
    st.session_state.doctor_patient_id = None
    st.error("Your doctor account is no longer active in the Care+ doctor database. Please sign in again or contact the admin.")
    st.stop()

def assigned_patient_ids(record):
    """Support common assignment field names used by admin dashboards."""
    for key in ("assigned_patient_ids", "patient_ids", "assigned_patients", "patients", "elderly_ids"):
        value = record.get(key)
        if isinstance(value, list):
            ids = []
            for item in value:
                if isinstance(item, dict):
                    pid = item.get("patient_id") or item.get("profile_id") or item.get("user_id") or item.get("id")
                    if pid: ids.append(str(pid))
                elif item is not None and str(item).strip():
                    ids.append(str(item).strip())
            return list(dict.fromkeys(ids))
        if isinstance(value, str) and value.strip():
            return [part.strip() for part in value.split(",") if part.strip()]
    return []

# ---------- Patient selection ----------
# Doctors can open existing profiles and register new patients themselves.
all_profiles=get_profiles()
profiles=all_profiles
if "doctor_patient_id" not in st.session_state: st.session_state.doctor_patient_id=None
if st.session_state.get("doctor_change_patient") or not st.session_state.doctor_patient_id:
    st.session_state.doctor_change_patient=False
    st.markdown(f'<div class="doctor-hero"><h1>🩺 Care+ Doctor Workspace</h1><p>Welcome, {escape(str(doctor_auth.get("doctor_name", "Doctor")))}. Select an existing patient or register a new patient.</p></div>',unsafe_allow_html=True)
    st.title("Choose a patient")
    st.caption("Patient profiles are read from Care+ Firestore.")
    if profiles:
        cols=st.columns(3)
        for i,p in enumerate(profiles):
            with cols[i%3]:
                with st.container(border=True):
                    st.markdown(f'<div class="patient-card"><div class="patient-cover"></div><div class="patient-body"><div class="patient-avatar">👤</div><div class="patient-name">{escape(str(p["name"]))}</div><div class="patient-id">Patient ID: {escape(str(p["id"]))}</div></div></div>',unsafe_allow_html=True)
                    st.caption("Children: " + str(p["children"]))
                    if st.button("Open patient workspace →",key="doctor_patient_"+p["id"],use_container_width=True,type="primary"):
                        st.session_state.doctor_patient_id=p["id"]
                        st.session_state.doctor_patient_name=p["name"]
                        st.session_state.doctor_change_patient=False
                        st.session_state.doctor_page="Overview"
                        st.rerun()
    else:
        st.info("No patient profiles found yet. Register your first patient below.")

    with st.expander("＋ Add a new patient", expanded=not bool(profiles)):
        with st.form("doctor_add_patient_selector_form", clear_on_submit=True):
            st.markdown("### Patient details")
            name = st.text_input("Full name *")
            c1,c2,c3 = st.columns(3)
            with c1:
                age = st.number_input("Age", min_value=0, max_value=120, value=65, step=1)
            with c2:
                sex = st.selectbox("Sex", ["Prefer not to say", "Female", "Male", "Intersex", "Other"])
            with c3:
                blood_group = st.selectbox("Blood group", ["Not known", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            c4,c5 = st.columns(2)
            with c4:
                email = st.text_input("Email")
            with c5:
                phone = st.text_input("Phone number")
            guardian_name = st.text_input("Guardian / primary contact name")
            c6,c7 = st.columns(2)
            with c6:
                guardian_phone = st.text_input("Guardian phone")
            with c7:
                guardian_relationship = st.text_input("Relationship to patient")
            address = st.text_area("Address")
            medical_notes = st.text_area("Relevant medical notes (optional)")
            create_patient = st.form_submit_button("Save patient and open workspace", type="primary", use_container_width=True)
        if create_patient:
            if not name.strip():
                st.error("Full name is required.")
            else:
                try:
                    patient_id = db.collection("patients").document().id
                    patient_data = {
                        "profile_id": patient_id, "user_id": patient_id,
                        "name": name.strip(), "full_name": name.strip(),
                        "age": int(age), "sex": sex,
                        "blood_group": "" if blood_group == "Not known" else blood_group,
                        "email": email.strip().lower(), "phone": phone.strip(),
                        "guardian_name": guardian_name.strip(),
                        "guardian_phone": guardian_phone.strip(),
                        "guardian_relationship": guardian_relationship.strip(),
                        "address": address.strip(), "medical_notes": medical_notes.strip(),
                        "role": "patient", "created_by_doctor_email": doctor_auth.get("email", ""),
                        "created_at": now_iso(),
                    }
                    db.collection("patients").document(patient_id).set(patient_data)
                    st.session_state.doctor_patient_id = patient_id
                    st.session_state.doctor_patient_name = name.strip()
                    st.session_state.doctor_change_patient = False
                    st.session_state.doctor_page = "Overview"
                    st.success("Patient profile created.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not create patient: {exc}")
    with st.expander("Open a patient by profile ID"):
        manual_id=st.text_input("Patient profile ID", key="doctor_manual_patient_id")
        if st.button("Open patient", key="doctor_manual_patient_open") and manual_id.strip():
            match=next((p for p in get_profiles() if p["id"]==manual_id.strip()), None)
            if match:
                st.session_state.doctor_patient_id=match["id"]
                st.session_state.doctor_patient_name=match["name"]
                st.session_state.doctor_page="Overview"
                st.rerun()
            else:
                st.error("No patient profile found with that ID.")
    st.stop()

PATIENT_ID=str(st.session_state.doctor_patient_id)
PATIENT_NAME=str(st.session_state.get("doctor_patient_name",PATIENT_ID))
sections=[("Overview","🏠  Overview"),("My Patients","👥  My Patients"),("Appointments","🗓️  Appointments"),("Consultations","🩺  Consultations"),("Medical Records","📋  Medical Records"),("Prescriptions","💊  Prescriptions"),("Notifications","🔔  Notifications"),("Settings","⚙️  Settings")]
if "doctor_page" not in st.session_state: st.session_state.doctor_page="Overview"
with st.sidebar:
    st.markdown("## 🩺 Care+")
    st.caption("Doctor Dashboard")
    st.caption(f"Signed in: {doctor_auth.get('doctor_name', 'Doctor')}")
    st.divider(); st.markdown("**Choose a section**")
    for name,label in sections:
        if st.button(label,key="doctor_nav_"+name,use_container_width=True,type="primary" if st.session_state.doctor_page==name else "secondary"):
            st.session_state.doctor_page=name; st.rerun()
    st.divider(); st.caption(f"Patient: {PATIENT_NAME}"); st.caption(f"Profile ID: {PATIENT_ID}")
    if st.button("↪ Sign out", key="doctor_logout", use_container_width=True):
        st.session_state.doctor_explicitly_signed_out = True
        st.session_state.doctor_auth = None
        st.session_state.doctor_patient_id = None
        st.session_state.doctor_patient_name = None
        st.session_state.doctor_change_patient = False
        st.session_state.doctor_page = "Overview"
        if _cookie_support:
            try:
                _cookie_manager.delete("careplus_doctor_refresh_token")
            except Exception:
                pass
        st.rerun()
    if st.button("↔ Change Patient",key="doctor_change_patient_btn",use_container_width=True):
        st.session_state.doctor_patient_id=None; st.session_state.doctor_change_patient=True; st.rerun()

# All rows filtered by selected patient where applicable
appointments=read_for_patient("appointments",PATIENT_ID)
medications=read_for_patient("medications",PATIENT_ID)
health=read_for_patient("health_readings",PATIENT_ID)
records=read_for_patient("medical_records",PATIENT_ID)
documents=read_for_patient("medical_documents",PATIENT_ID)
prescriptions=read_for_patient("prescriptions",PATIENT_ID)
notifications=read_for_patient("notifications",PATIENT_ID)+read_for_patient("medication_alerts",PATIENT_ID)+read_for_patient("emergencies",PATIENT_ID)
page=st.session_state.doctor_page
st.markdown(f'<div class="doctor-hero"><h1>🩺 Care+ Doctor Dashboard</h1><p>Patient workspace: <b>{escape(PATIENT_NAME)}</b> · Patient ID: {escape(PATIENT_ID)}</p></div>',unsafe_allow_html=True)
st.caption("Clinical workspace prototype. Use professional judgement and follow applicable privacy and clinical rules.")

if page=="Overview":
    st.subheader("Today's Overview")
    pending=[a for a in appointments if str(a.get("status","pending")).lower() in {"pending","requested","new"}]
    active_alerts=[n for n in notifications if str(n.get("status","active")).lower() not in {"resolved","closed","dismissed","completed"}]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Appointments",len(appointments)); c2.metric("Pending requests",len(pending)); c3.metric("Medication plans",len(medications)); c4.metric("Open alerts",len(active_alerts))
    left,right=st.columns([1.4,1])
    with left:
        st.markdown("### Appointment requests")
        table(sorted(appointments,key=lambda r:str(r.get("created_at","")),reverse=True)[:6],["created_at","doctor_name","appointment_date","appointment_time","reason","status"],"No appointment requests for this patient.")
    with right:
        st.markdown("### Alerts needing attention")
        if active_alerts:
            for a in active_alerts[:6]:
                st.warning(f"{a.get('alert_type',a.get('emergency_type','Alert'))}: {a.get('message',a.get('medicine_name',a.get('notes','Please review this alert.')))}")
        else: st.success("No open alerts found.")
    st.markdown("### Recent health readings")
    table(sorted(health,key=lambda r:str(r.get("created_at","")),reverse=True)[:8],["created_at","blood_pressure","systolic","diastolic","blood_sugar","heart_rate","temperature","spo2","weight"],"No health readings recorded yet.")

elif page=="My Patients":
    st.subheader("Patients")
    st.write("View patient details or register a new patient when they visit your clinic.")
    with st.expander("＋ Add a new patient", expanded=False):
        with st.form("doctor_add_patient_form", clear_on_submit=True):
            st.markdown("### Personal information")
            name = st.text_input("Full name *")
            c1,c2,c3 = st.columns(3)
            with c1:
                age = st.number_input("Age", min_value=0, max_value=120, value=65, step=1, key="new_patient_age")
            with c2:
                sex = st.selectbox("Sex", ["Prefer not to say", "Female", "Male", "Intersex", "Other"], key="new_patient_sex")
            with c3:
                blood_group = st.selectbox("Blood group", ["Not known", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], key="new_patient_blood_group")
            c4,c5 = st.columns(2)
            with c4:
                phone = st.text_input("Phone number", key="new_patient_phone")
            with c5:
                address = st.text_input("Address", key="new_patient_address")
            st.markdown("### Guardian / emergency contact")
            c6,c7 = st.columns(2)
            with c6:
                guardian_name = st.text_input("Guardian / primary contact name", key="new_patient_guardian")
            with c7:
                guardian_phone = st.text_input("Guardian phone", key="new_patient_guardian_phone")
            guardian_relationship = st.text_input("Relationship to patient", key="new_patient_guardian_relationship")
            medical_notes = st.text_area("Relevant medical notes (optional)", key="new_patient_medical_notes")

            st.markdown("---")
            st.markdown("### Care+ details")
            st.caption("Create the patient's Care+ sign-in details. The email must be unique and the password should be shared securely with the patient or their guardian.")
            careplus_email = st.text_input("Care+ email *", key="new_patient_careplus_email")
            careplus_password = st.text_input("Care+ password *", type="password", key="new_patient_careplus_password")
            create_patient = st.form_submit_button("Save new patient", type="primary", use_container_width=True)
        if create_patient:
            if not name.strip():
                st.error("Full name is required.")
            elif not careplus_email.strip() or not careplus_password:
                st.error("Enter a Care+ email and password.")
            elif len(careplus_password) < 6:
                st.error("The Care+ password must be at least 6 characters.")
            else:
                try:
                    careplus_email_normalized = careplus_email.strip().lower()
                    # Create an actual Firebase Authentication account for the patient.
                    from firebase_admin import auth as firebase_auth
                    try:
                        patient_auth = firebase_auth.create_user(
                            email=careplus_email_normalized,
                            password=careplus_password,
                            display_name=name.strip(),
                            email_verified=False,
                        )
                    except Exception as auth_exc:
                        st.error(f"Could not create the patient's Care+ login: {auth_exc}")
                        st.stop()

                    patient_id = db.collection("patients").document().id
                    patient_data = {
                        "profile_id": patient_id, "user_id": patient_id,
                        "name": name.strip(), "full_name": name.strip(),
                        "age": int(age), "sex": sex,
                        "blood_group": "" if blood_group == "Not known" else blood_group,
                        "email": careplus_email_normalized,
                        "careplus_email": careplus_email_normalized,
                        "firebase_auth_uid": patient_auth.uid,
                        "phone": phone.strip(),
                        "guardian_name": guardian_name.strip(),
                        "guardian_phone": guardian_phone.strip(),
                        "guardian_relationship": guardian_relationship.strip(),
                        "address": address.strip(), "medical_notes": medical_notes.strip(),
                        "role": "patient", "created_by_doctor_email": doctor_auth.get("email", ""),
                        "created_at": now_iso(),
                    }
                    db.collection("patients").document(patient_id).set(patient_data)
                    st.success(f"Patient {name.strip()} was added. Profile ID: {patient_id}")
                    st.session_state.doctor_patient_id = patient_id
                    st.session_state.doctor_patient_name = name.strip()
                    st.session_state.doctor_page = "Overview"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not create patient: {exc}")
    st.markdown("### Patient directory")
    directory = get_profiles()
    if directory:
        table(directory, ["name", "id", "children"], "No patients registered yet.")
        directory_options = {f'{p["name"]} · {p["id"]}': p for p in directory}
        selected_label = st.selectbox("Select patient", list(directory_options), key="doctor_directory_select")
        if st.button("Open selected patient", type="primary", use_container_width=True):
            selected_patient = directory_options[selected_label]
            st.session_state.doctor_patient_id = selected_patient["id"]
            st.session_state.doctor_patient_name = selected_patient["name"]
            st.session_state.doctor_page = "Overview"
            st.rerun()
    else:
        st.info("No patient profiles have been registered yet.")

elif page=="Appointments":
    st.subheader("Appointments")
    st.write("Review requests and update appointment status. The doctor controls confirmation and scheduling.")
    table(sorted(appointments,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","doctor_name","appointment_date","date","appointment_time","reason","notes","status"],"No appointment requests for this patient.")
    if appointments:
        options={f'{a.get("appointment_date",a.get("date","Date pending"))} · {a.get("appointment_time", "Time pending")} · {a.get("reason","Appointment")} · {a["id"]}':a for a in appointments}
        with st.form("doctor_update_appointment"):
            selected=st.selectbox("Choose appointment",list(options))
            status=st.selectbox("Update status",["Confirmed","Rescheduled","Completed","Cancelled","Pending"])
            new_date=st.date_input("Confirmed / new date",value=date.today())
            new_time=st.time_input("Confirmed / new time",value=time(10,0),format="12h")
            note=st.text_input("Doctor note (optional)")
            submit=st.form_submit_button("Save appointment update",type="primary")
        if submit:
            a=options[selected]
            update_record("appointments",a["id"],{"status":status,"appointment_date":new_date.isoformat(),"date":new_date.isoformat(),"appointment_time":new_time.strftime("%I:%M %p"),"doctor_note":note,"updated_at":now_iso()})
            st.success("Appointment updated."); st.rerun()
    st.markdown("### Add an appointment")
    with st.form("doctor_create_appointment",clear_on_submit=True):
        ap_date=st.date_input("Appointment date",value=date.today(),key="doctor_ap_date")
        ap_time=st.time_input("Appointment time",value=time(10,0),format="12h",key="doctor_ap_time")
        reason=st.selectbox("Reason",["Consultation","Follow-up","Routine check-up","Prescription review","Other"])
        notes=st.text_area("Notes (optional)")
        create=st.form_submit_button("Create appointment",type="primary")
    if create:
        add_record("appointments",{"doctor_name":"Care+ Doctor","doctor":"Care+ Doctor","appointment_date":ap_date.isoformat(),"date":ap_date.isoformat(),"appointment_time":ap_time.strftime("%I:%M %p"),"reason":reason,"notes":notes,"status":"Confirmed","created_by_role":"doctor"},PATIENT_ID)
        st.success("Appointment created."); st.rerun()

elif page=="Consultations":
    st.subheader("Consultations")
    st.write("Track consultation notes for the selected patient. This prototype does not provide live video calling.")
    consults=read_for_patient("consultations",PATIENT_ID)
    table(sorted(consults,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","appointment_id","chief_complaint","notes","follow_up","status"],"No consultations recorded yet.")
    with st.form("doctor_consultation_form",clear_on_submit=True):
        complaint=st.text_input("Chief complaint")
        notes=st.text_area("Consultation notes")
        followup=st.text_input("Follow-up instructions (optional)")
        status=st.selectbox("Status",["In progress","Completed","Follow-up required"])
        save=st.form_submit_button("Save consultation note",type="primary")
    if save:
        add_record("consultations",{"chief_complaint":complaint,"notes":notes,"follow_up":followup,"status":status,"created_by_role":"doctor"},PATIENT_ID)
        st.success("Consultation note saved."); st.rerun()

elif page=="Medical Records":
    st.subheader("Medical records & health readings")
    st.markdown("### Recorded health readings")
    table(sorted(health,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","blood_pressure","systolic","diastolic","blood_sugar","heart_rate","temperature","spo2","weight","notes"],"No health readings available.")
    st.markdown("### Medical records")
    table(sorted(records,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","record_type","title","diagnosis","notes","doctor_name"],"No medical records found.")
    with st.form("doctor_add_medical_record",clear_on_submit=True):
        title=st.text_input("Record title")
        record_type=st.selectbox("Record type",["Diagnosis","Clinical note","Lab interpretation","Follow-up note","Other"])
        diagnosis=st.text_area("Clinical details")
        save=st.form_submit_button("Save medical record",type="primary")
    if save:
        add_record("medical_records",{"title":title,"record_type":record_type,"diagnosis":diagnosis,"doctor_name":"Care+ Doctor","created_by_role":"doctor"},PATIENT_ID)
        st.success("Medical record saved."); st.rerun()
    st.markdown("### Health documents uploaded by patient/caregiver")
    table(documents,["created_at","title","document_type","file_name","notes","storage_path"],"No document metadata found. Actual files may be stored locally by the prototype uploader.")

elif page=="Prescriptions":
    st.subheader("Prescriptions & medication plans")
    st.caption("Medication schedules are doctor-managed. Confirm medicines, dose and timing against the clinical plan before saving.")
    table(sorted(prescriptions,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","medicine_name","dosage","frequency","times","duration","instructions","status"],"No prescriptions recorded yet.")
    st.markdown("### Create prescription / medication schedule")
    with st.form("doctor_prescription_form",clear_on_submit=True):
        medicine=st.text_input("Medicine name")

        dose_col, strength_col = st.columns(2)
        with dose_col:
            dose_value_col, dose_unit_col = st.columns([3, 1])
            with dose_value_col:
                dose_amount = st.text_input(
                    "Dose",
                    placeholder="Enter value",
                    key="prescription_dose_amount",
                )
            with dose_unit_col:
                dose_unit = st.selectbox(
                    "Unit",
                    ["tablets", "strips", "bottle", "packet"],
                    key="prescription_dose_unit",
                    label_visibility="visible",
                )
        with strength_col:
            strength_value_col, strength_unit_col = st.columns([3, 1])
            with strength_value_col:
                strength_amount = st.text_input(
                    "Strength",
                    placeholder="Enter value",
                    key="prescription_strength_amount",
                )
            with strength_unit_col:
                strength_unit = st.selectbox(
                    "Unit",
                    ["mg", "ml"],
                    key="prescription_strength_unit",
                    label_visibility="visible",
                )

        frequency=st.selectbox("Frequency",["Once daily","Twice daily","Three times daily","Four times daily","As prescribed","Other"])
        meal_time=st.selectbox(
            "Time",
            ["Breakfast","Lunch","Dinner"],
            key="prescription_meal_time",
        )

        timing=st.selectbox(
            "When should it be taken?",
            ["Before food","After food","With food","Other"],
            key="prescription_food_timing",
        )

        timing_instruction = timing
        if timing in ("Before food", "After food"):
            offset_col, unit_col, direction_col = st.columns([1, 1.5, 1.5])
            with offset_col:
                timing_offset = st.number_input(
                    "Time to take",
                    min_value=0,
                    value=1,
                    step=1,
                    key="prescription_timing_offset",
                )
            with unit_col:
                timing_unit = st.selectbox(
                    "Unit",
                    ["Mins", "Hours", "Days"],
                    index=1,
                    key="prescription_timing_unit",
                )
            with direction_col:
                timing_direction = st.selectbox(
                    "Before or after",
                    ["before", "after"],
                    key="prescription_timing_direction",
                )
            timing_instruction = f"Take this medicine {timing_offset} {timing_unit.lower()} {timing_direction} food"
        elif timing == "With food":
            timing_instruction = "Take this medicine with food"
        else:
            timing_instruction = st.text_input(
                "Specific timing instructions",
                placeholder='e.g. "1 hour before food" or "at bedtime"',
                help="Enter the exact timing instruction the patient should follow.",
                key="prescription_custom_timing",
            ).strip()

        duration=st.text_input("Duration (e.g. 7 days)")
        instructions=st.text_area("Instructions / precautions")
        save=st.form_submit_button("Save prescription and medication schedule",type="primary")
    if save:
        if not medicine.strip() or not dose_amount.strip() or not strength_amount.strip():
            st.error("Enter the medicine name, dose amount and strength amount.")
        elif timing == "Other" and not timing_instruction:
            st.error("Enter the specific timing instruction for Other.")
        else:
            med_data={
                "medicine_name":medicine.strip(),
                "name":medicine.strip(),
                "dose_amount":dose_amount.strip(),
                "dose_unit":dose_unit,
                "dose":f"{dose_amount.strip()} {dose_unit}",
                "strength_amount":strength_amount.strip(),
                "strength_unit":strength_unit,
                "strength":f"{strength_amount.strip()} {strength_unit}",
                "dosage":f"{dose_amount.strip()} {dose_unit} · {strength_amount.strip()} {strength_unit}",
                "frequency":frequency,
                "meal_time":meal_time,
                "timing":timing,
                "timing_instruction":timing_instruction,
                "times":[],
                "time":timing_instruction,
                "duration":duration.strip(),
                "instructions":instructions.strip(),
                "status":"active",
                "prescribed_by_role":"doctor",
            }
            prescription_id = add_record("prescriptions",med_data,PATIENT_ID)
            med_data["prescription_id"] = prescription_id
            add_record("medications",med_data,PATIENT_ID)
            st.success("Prescription and medication schedule saved."); st.rerun()


    st.markdown("---")
    st.subheader("Manage saved prescriptions")
    st.caption("Deleting a prescription also removes its matching medication schedule so it no longer appears in the elderly dashboard.")
    try:
        saved_prescriptions = list(
            db.collection("prescriptions")
              .where("patient_id", "==", PATIENT_ID)
              .stream()
        )
    except Exception as exc:
        saved_prescriptions = []
        st.error(f"Could not load prescriptions: {exc}")

    if not saved_prescriptions:
        st.info("No saved prescriptions found for this patient.")
    else:
        prescription_data_by_id = {
            doc.id: (doc.to_dict() or {}) for doc in saved_prescriptions
        }
        prescription_options = {}
        for prescription_id, prescription_data in prescription_data_by_id.items():
            medicine_label = (
                prescription_data.get("medicine_name")
                or prescription_data.get("name")
                or "Unnamed medicine"
            )
            dose_label = (
                prescription_data.get("dosage")
                or " ".join(filter(None, [
                    str(prescription_data.get("dose", "")),
                    str(prescription_data.get("strength", "")),
                ]))
            )
            created_label = str(prescription_data.get("created_at", ""))[:19]
            prescription_options[prescription_id] = (
                f"{medicine_label} — {dose_label} · {created_label}"
            ).strip(" —·")

        selected_prescription_id = st.selectbox(
            "Choose a prescription to delete",
            options=list(prescription_options.keys()),
            format_func=lambda item: prescription_options[item],
            key="doctor_delete_prescription_id",
        )
        confirm_delete = st.checkbox(
            "I confirm I want to delete this prescription and its medication schedule",
            key="doctor_confirm_delete_prescription",
        )
        if st.button(
            "Delete prescription and schedule",
            type="secondary",
            disabled=not confirm_delete,
            key="doctor_delete_prescription_button",
        ):
            selected_data = prescription_data_by_id[selected_prescription_id]
            deleted_schedule_count = 0
            try:
                # Remove the prescription record.
                db.collection("prescriptions").document(selected_prescription_id).delete()

                # Remove any schedule explicitly linked to this prescription.
                linked_schedules = list(
                    db.collection("medications")
                      .where("patient_id", "==", PATIENT_ID)
                      .where("prescription_id", "==", selected_prescription_id)
                      .stream()
                )
                for schedule_doc in linked_schedules:
                    schedule_doc.reference.delete()
                    deleted_schedule_count += 1

                # Backward compatibility for schedules created before prescription_id
                # was stored: match this patient's exact medicine + dose + strength.
                if not linked_schedules:
                    try:
                        schedules = list(
                            db.collection("medications")
                              .where("patient_id", "==", PATIENT_ID)
                              .stream()
                        )
                    except Exception:
                        schedules = []

                    target_name = str(
                        selected_data.get("medicine_name") or selected_data.get("name") or ""
                    ).strip().casefold()
                    target_dose = str(selected_data.get("dose") or "").strip().casefold()
                    target_strength = str(selected_data.get("strength") or "").strip().casefold()
                    target_dosage = str(selected_data.get("dosage") or "").strip().casefold()

                    matching = []
                    for schedule_doc in schedules:
                        data = schedule_doc.to_dict() or {}
                        name = str(data.get("medicine_name") or data.get("name") or "").strip().casefold()
                        dose = str(data.get("dose") or "").strip().casefold()
                        strength = str(data.get("strength") or "").strip().casefold()
                        dosage = str(data.get("dosage") or "").strip().casefold()
                        same_medicine = bool(target_name) and name == target_name
                        same_dose = (
                            (target_dose and dose == target_dose)
                            or (target_dosage and dosage == target_dosage)
                            or (target_dose and target_strength and f"{target_dose} · {target_strength}" == dosage)
                        )
                        same_strength = not target_strength or not strength or strength == target_strength
                        if same_medicine and same_dose and same_strength:
                            matching.append(schedule_doc)

                    # Delete one matching legacy schedule only, avoiding removal of
                    # multiple identical medication records by mistake.
                    if matching:
                        selected_created = str(selected_data.get("created_at", ""))
                        matching.sort(
                            key=lambda doc: abs(
                                len(str((doc.to_dict() or {}).get("created_at", "")))
                                - len(selected_created)
                            )
                        )
                        matching[0].reference.delete()
                        deleted_schedule_count += 1

                st.session_state.pop("doctor_confirm_delete_prescription", None)
                st.success(
                    "Prescription deleted. "
                    + (
                        "The matching medication schedule was also removed."
                        if deleted_schedule_count
                        else "No matching medication schedule was found."
                    )
                )
                st.rerun()
            except Exception as exc:
                st.error(f"Could not fully delete the prescription and schedule: {exc}")


elif page=="Notifications":
    st.subheader("Notifications & alerts")
    table(sorted(notifications,key=lambda r:str(r.get("created_at","")),reverse=True),["created_at","alert_type","emergency_type","medicine_name","message","status","notes","latitude","longitude"],"No notifications or alerts found.")
    if notifications:
        alert_options={f'{n.get("created_at","Date unknown")} · {n.get("alert_type",n.get("emergency_type","Alert"))} · {n["id"]}':n for n in notifications}
        with st.form("doctor_resolve_alert"):
            selected=st.selectbox("Choose alert",list(alert_options))
            new_status=st.selectbox("Status",["Reviewed","Resolved","Follow-up required","Active"])
            save=st.form_submit_button("Update alert status",type="primary")
        if save:
            n=alert_options[selected]
            coll="medication_alerts" if n.get("alert_type")=="missed_dose" else ("emergencies" if n.get("emergency_type") else "notifications")
            update_record(coll,n["id"],{"status":new_status,"reviewed_at":now_iso(),"reviewed_by_role":"doctor"})
            st.success("Alert status updated."); st.rerun()

elif page=="Settings":
    st.subheader("Doctor workspace settings")
    st.info("This prototype does not yet implement authenticated doctor accounts or role-based access. Add Firebase Authentication and server-side authorization before using real patient data.")
    st.write("Current selected patient:",PATIENT_NAME)
    st.code(PATIENT_ID)

st.markdown('<div style="margin-top:38px;color:#718096;font-size:.9rem">Care+ prototype · Patient information is sensitive. Do not use this demo as a substitute for a secure clinical system.</div>',unsafe_allow_html=True)
