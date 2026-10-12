import json
import os
import urllib.error
import urllib.request
from datetime import datetime

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth

# =========================================================
# CARE+ ADMIN DASHBOARD
# Authentication: Firebase Authentication
# Authorization: Firestore document admin_config/admin
# Passwords are NEVER stored in Firestore.
# =========================================================

st.set_page_config(
    page_title="Care+ | Admin Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { color-scheme: light !important; }
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
    background: #F3F7FC !important; color: #183153 !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background: #E7EFFA !important; color: #183153 !important;
}
[data-testid="stHeader"], #MainMenu, footer { visibility: hidden; }
.block-container { max-width: 1400px; padding: 1.6rem 2rem 3rem; }
h1, h2, h3 { color: #16345B !important; }
.admin-hero {
    background: linear-gradient(120deg,#173B70,#2878C7);
    border-radius: 22px; padding: 28px 32px; color: #FFFFFF; margin-bottom: 20px;
}
.admin-hero, .admin-hero * { color: #FFFFFF !important; }
.admin-hero h1 { margin: 0; }
.admin-hero p { margin: 8px 0 0; font-size: 1.05rem; }
.stApp p, .stApp label, .stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stCaptionContainer"] {
    color: #183153 !important;
}
.stApp input, .stApp [data-baseweb="input"] input {
    background: #FFFFFF !important; color: #183153 !important;
    -webkit-text-fill-color: #183153 !important; border: 1px solid #B8CBE2 !important;
}
.stApp input::placeholder { color: #73849B !important; -webkit-text-fill-color: #73849B !important; }
div.stButton > button, div.stFormSubmitButton > button {
    border-radius: 12px !important; min-height: 2.8rem !important;
    font-weight: 700 !important; background: #1E5AA8 !important;
    color: #FFFFFF !important; border: 1px solid #1E5AA8 !important;
}
div.stButton > button *, div.stFormSubmitButton > button * {
    color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important;
}
.metric-card {
    background: white; border: 1px solid #D7E4F4; border-radius: 16px;
    padding: 18px 20px; box-shadow: 0 5px 18px rgba(31,76,130,.05);
}
.metric-label { color: #60758F !important; font-size: .9rem; font-weight: 650; }
.metric-value { color: #173B70 !important; font-size: 2rem; font-weight: 850; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)


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
                "Firebase credentials are missing. Configure the existing [firebase] "
                "Streamlit secrets or GOOGLE_APPLICATION_CREDENTIALS."
            )
        app = firebase_admin.initialize_app(credentials.Certificate(key_path))
    return firestore.client(app=app)


def firebase_api_key():
    cfg = dict(st.secrets.get("firebase", {}))
    return (cfg.get("api_key") or cfg.get("web_api_key") or
            cfg.get("web_apiKey") or cfg.get("apiKey") or
            st.secrets.get("firebase_api_key", ""))


def auth_request(method, body):
    api_key = firebase_api_key()
    if not api_key:
        raise RuntimeError("Firebase Web API key is missing from the existing [firebase] secrets.")
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:{method}?key={api_key}"
    request = urllib.request.Request(
        endpoint, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            message = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", "Authentication failed")
        except Exception:
            message = "Authentication failed"
        for code, friendly in {
            "EMAIL_NOT_FOUND": "Email or password is incorrect.",
            "INVALID_PASSWORD": "Email or password is incorrect.",
            "INVALID_LOGIN_CREDENTIALS": "Email or password is incorrect.",
            "USER_DISABLED": "This Firebase account has been disabled.",
            "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Please wait and try again.",
        }.items():
            if code in message:
                raise ValueError(friendly) from None
        raise ValueError(f"Firebase authentication failed: {message}") from None


def firebase_sign_in(email, password):
    return auth_request("signInWithPassword", {
        "email": email.strip(), "password": password, "returnSecureToken": True
    })


def get_admin_authorization(email):
    """Read the owner-created authorization document; never stores/checks a password."""
    doc = get_db().collection("admin_config").document("admin").get()
    if not doc.exists:
        raise ValueError(
            "Admin authorization is not configured. Create the admin_config/admin "
            "document in Firestore using the README instructions."
        )
    data = doc.to_dict() or {}
    allowed_email = str(data.get("email", "")).strip().lower()
    active = data.get("active") is True
    role = str(data.get("role", "")).strip().lower()
    if not allowed_email or allowed_email != email.strip().lower() or not active or role != "admin":
        raise ValueError("This account is not authorized for Care+ administration.")
    return data


def verify_authenticated_admin(id_token):
    # Firebase ID tokens can be rejected if the token issuer and the runtime clock
    # differ by only a few seconds. Do not bypass token validation or accept
    # unverified tokens; instead allow a small clock-skew tolerance.
    try:
        decoded = auth.verify_id_token(
            id_token, check_revoked=True, clock_skew_seconds=10
        )
    except TypeError:
        # Compatibility fallback for older firebase-admin versions that don't
        # expose clock_skew_seconds. Upgrade firebase-admin in requirements.txt.
        decoded = auth.verify_id_token(id_token, check_revoked=True)
    email = str(decoded.get("email", "")).strip().lower()
    # Demo configuration: email verification is intentionally not required.
    # Access still requires a valid Firebase ID token and an active Firestore admin record.
    get_admin_authorization(email)
    return {"uid": decoded["uid"], "email": email}



def create_firebase_user(email, password, display_name):
    """Create a Firebase Authentication user using the trusted Admin SDK."""
    try:
        user = auth.get_user_by_email(email.strip())
        raise ValueError("A Firebase Authentication account already exists for this email.")
    except auth.UserNotFoundError:
        pass
    user = auth.create_user(
        email=email.strip(),
        password=password,
        display_name=display_name.strip() or None,
        email_verified=False,
        disabled=False,
    )
    return user


def save_team_profile(collection, uid, email, display_name, extra_fields=None):
    """Save a role-specific profile using the existing confirmed collection."""
    payload = {
        "email": email.strip(),
        "name": display_name.strip(),
        "user_id": uid,
        "role": "doctor" if collection == "doctors" else "volunteer",
        "created_at": datetime.now().astimezone().isoformat(),
    }
    if extra_fields:
        payload.update(extra_fields)
    get_db().collection(collection).document(uid).set(payload)
    return payload


def records(collection, limit=500):
    docs = get_db().collection(collection).limit(limit).stream()
    return [{"_document_id": d.id, **(d.to_dict() or {})} for d in docs]


def safe_count(collection):
    try:
        return len(records(collection, limit=1000))
    except Exception:
        return None


def show_metric(label, value, icon):
    text_value = "Unavailable" if value is None else f"{value:,}"
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{icon} {label}</div>'
        f'<div class="metric-value">{text_value}</div></div>',
        unsafe_allow_html=True
    )


def render_login():
    st.markdown("""
    <div class="admin-hero">
      <h1>🛡️ Care+ Administration</h1>
      <p>Secure control centre for the Care+ healthcare ecosystem.</p>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Admin sign in")
    st.write("Sign in with the administrator account authorized in Firestore.")
    with st.form("admin_login_form"):
        email = st.text_input("Admin email", key="admin_login_email")
        password = st.text_input("Password", type="password", key="admin_login_password")
        submitted = st.form_submit_button("Sign in securely", type="primary", use_container_width=True)
    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email and password.")
            return
        try:
            # First check the Firestore authorization document for this email.
            get_admin_authorization(email)
            # Then let Firebase Authentication verify the password.
            result = firebase_sign_in(email, password)
            identity = verify_authenticated_admin(result["idToken"])
            st.session_state["admin_session"] = {
                "uid": identity["uid"],
                "email": identity["email"],
                "id_token": result["idToken"],
            }
            st.rerun()
        except Exception as exc:
            st.error(str(exc))


if "admin_session" not in st.session_state:
    st.session_state["admin_session"] = None

if not st.session_state["admin_session"]:
    try:
        render_login()
    except Exception as exc:
        st.error(f"Admin setup error: {exc}")
    st.stop()

session = st.session_state["admin_session"]
try:
    identity = verify_authenticated_admin(session["id_token"])
except Exception:
    st.session_state["admin_session"] = None
    st.error("Your admin session is no longer valid or authorized. Please sign in again.")
    st.stop()

with st.sidebar:
    st.markdown("## 🛡️ Care+")
    st.caption("Administration")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["Overview", "Appointments", "People & Care Teams", "Clinical Operations", "Emergency & Wellness", "Data Explorer", "Add Doctor / Volunteer"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Signed in as\n{identity['email']}")
    if st.button("Log out", use_container_width=True):
        st.session_state["admin_session"] = None
        st.rerun()

if page == "Overview":
    st.markdown("""
    <div class="admin-hero">
      <h1>Care+ Admin Dashboard</h1>
      <p>System overview · User access · Care operations</p>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Last refreshed: {datetime.now().astimezone().strftime('%d %b %Y, %I:%M %p %Z')}")
    collection_groups = [
        ("patients", "Patients", "👥"),
        ("doctors", "Doctors", "🩺"),
        ("appointments", "Appointments", "📅"),
        ("emergencies", "Emergency records", "🚨"),
        ("caregiver_alerts", "Caregiver alerts", "🔔"),
        ("prescriptions", "Prescriptions", "💊"),
        ("wellness_checks", "Wellness checks", "💙"),
        ("volunteers", "Volunteers", "🤝"),
    ]
    for start in range(0, len(collection_groups), 4):
        cols = st.columns(4, gap="medium")
        for col, (collection, label, icon) in zip(cols, collection_groups[start:start + 4]):
            with col:
                show_metric(label, safe_count(collection), icon)
    st.markdown("### Quick view")
    st.write("Use the sidebar to inspect appointments, care-team directories, clinical operations, emergency activity, and selected Firestore collections.")
    st.info("Counts are live document counts from the confirmed collections, limited to the first 1,000 documents per collection. They are not unique-user counts.")

elif page == "Appointments":
    st.title("📅 Appointment Management")
    try:
        rows = records("appointments")
        if not rows:
            st.info("No appointment documents found.")
        else:
            search = st.text_input("Search by reason, status, user ID, or appointment type")
            statuses = sorted({str(r.get("status", "Unknown")) for r in rows})
            status_filter = st.selectbox("Filter by status", ["All statuses"] + statuses)
            filtered = []
            for r in rows:
                if status_filter != "All statuses" and str(r.get("status", "Unknown")) != status_filter:
                    continue
                searchable = " ".join(str(r.get(k, "")) for k in (
                    "reason", "status", "user_id", "appointment_type", "appointment_date", "preferred_date"
                ))
                if search.lower() in searchable.lower():
                    filtered.append(r)
            st.caption(f"{len(filtered)} matching appointment documents")
            st.dataframe([{
                "Document ID": r.get("_document_id"),
                "Date": r.get("appointment_date") or r.get("preferred_date") or r.get("date"),
                "Time": r.get("appointment_time") or r.get("preferred_time"),
                "Type": r.get("appointment_type"), "Reason": r.get("reason"),
                "Status": r.get("status"), "User ID": r.get("user_id"),
                "Coordinated by": r.get("coordinated_by_role"), "Created": r.get("created_at"),
            } for r in filtered], use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"Could not load appointments: {exc}")

elif page == "People & Care Teams":
    st.title("👥 People & Care Teams")
    left, right = st.columns(2)
    with left:
        st.subheader("Patients")
        try:
            rows = records("patients")
            st.metric("Patient documents", len(rows))
            st.dataframe([{
                "Document ID": r.get("_document_id"),
                "Name": r.get("name") or r.get("full_name"),
                "Email": r.get("email"), "Role": r.get("role"),
                "User ID": r.get("user_id") or r.get("profile_id"),
            } for r in rows], use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not load patients: {exc}")
    with right:
        st.subheader("Doctors")
        try:
            rows = records("doctors")
            st.metric("Doctor documents", len(rows))
            st.dataframe([{
                "Document ID": r.get("_document_id"),
                "Name": r.get("name") or r.get("full_name"),
                "Email": r.get("email"), "Role": r.get("role"),
                "Specialty": r.get("specialty") or r.get("specialization"),
            } for r in rows], use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not load doctors: {exc}")
    st.subheader("Volunteers")
    try:
        rows = records("volunteers")
        st.dataframe([{
            "Document ID": r.get("_document_id"),
            "Name": r.get("name") or r.get("full_name"),
            "Email": r.get("email"), "Role": r.get("role"),
            "Available": r.get("available", r.get("is_available")),
        } for r in rows], use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error(f"Could not load volunteers: {exc}")
    st.caption("People records are read-only until an account/approval schema is confirmed.")

elif page == "Clinical Operations":
    st.title("🩺 Clinical Operations")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Medical records")
        try:
            rows = records("medical_records")
            st.metric("Documents", len(rows))
            st.dataframe([{
                "Document ID": r.get("_document_id"), "Patient ID": r.get("patient_id"),
                "Record type": r.get("record_type"), "Title": r.get("title"),
                "Doctor": r.get("doctor_name"), "Created": r.get("created_at"),
            } for r in rows], use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(str(exc))
    with col2:
        st.subheader("Prescriptions")
        try:
            rows = records("prescriptions")
            st.metric("Documents", len(rows))
            st.dataframe([{
                "Document ID": r.get("_document_id"), "Patient ID": r.get("patient_id"),
                "Medicine": r.get("medication_name") or r.get("medicine_name") or r.get("name"),
                "Status": r.get("status"), "Created": r.get("created_at"),
            } for r in rows], use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(str(exc))
    st.warning("This is an administrative overview, not a clinical decision-support tool.")

elif page == "Emergency & Wellness":
    st.title("🚨 Emergency & Wellness")
    tabs = st.tabs(["Emergencies", "Caregiver alerts", "Wellness checks", "Medicine logs"])
    specs = [
        ("emergencies", ["Document ID", "user_id", "emergency_type", "status", "created_at"]),
        ("caregiver_alerts", ["Document ID", "patient_id", "type", "title", "status", "created_at"]),
        ("wellness_checks", ["Document ID", "user_id", "mood", "pain", "sleep", "check_date", "created_at"]),
        ("medicine_logs", ["Document ID", "user_id", "medication_name", "dose", "status", "taken_at", "created_at"]),
    ]
    for tab, (collection, fields) in zip(tabs, specs):
        with tab:
            try:
                rows = records(collection)
                st.dataframe([{
                    field: (r.get("_document_id") if field == "Document ID" else r.get(field))
                    for field in fields
                } for r in rows], use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(str(exc))

elif page == "Data Explorer":
    st.title("🗂️ Read-only Data Explorer")
    collections = [
        "appointments", "caregiver_alerts", "doctors", "emergencies",
        "emergency_contacts", "medical_records", "medications", "medicine_logs",
        "patients", "prescriptions", "volunteers", "wellness_checks",
    ]
    collection = st.selectbox("Choose a confirmed collection", collections)
    limit = st.select_slider("Maximum documents to load", options=[25, 50, 100, 250, 500], value=100)
    if st.button("Load collection", type="primary"):
        try:
            rows = records(collection, limit=limit)
            st.caption(f"Loaded {len(rows)} documents from `{collection}`.")
            st.dataframe([{
                "Document ID": r.get("_document_id"),
                "Identifier": r.get("user_id") or r.get("patient_id") or r.get("profile_id"),
                "Name/title": r.get("name") or r.get("title") or r.get("reason"),
                "Status": r.get("status"), "Created": r.get("created_at"),
            } for r in rows], use_container_width=True, hide_index=True)
        except Exception as exc:
            st.error(f"Could not load collection: {exc}")


elif page == "Add Doctor / Volunteer":
    st.title("➕ Add Doctor or Volunteer")
    st.write("Create a Firebase Authentication account and a matching profile in the existing Firestore collection.")
    st.info(
        "This action creates a real login account. Share credentials securely with the intended user; "
        "do not commit passwords or store them in Firestore."
    )

    account_type = st.radio("Account type", ["Doctor", "Volunteer"], horizontal=True)
    with st.form("create_team_account_form", clear_on_submit=False):
        full_name = st.text_input("Full name")
        email = st.text_input("Email address")
        password = st.text_input("Temporary password", type="password")
        confirm_password = st.text_input("Confirm temporary password", type="password")
        specialty = ""
        if account_type == "Doctor":
            specialty = st.text_input("Specialty (optional)")
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

    if submitted:
        if not full_name.strip() or not email.strip() or not password:
            st.error("Name, email, and password are required.")
        elif password != confirm_password:
            st.error("The passwords do not match.")
        elif len(password) < 6:
            st.error("Firebase passwords must be at least 6 characters.")
        else:
            created_user = None
            try:
                created_user = create_firebase_user(email, password, full_name)
                collection = "doctors" if account_type == "Doctor" else "volunteers"
                extras = {"specialty": specialty.strip()} if account_type == "Doctor" and specialty.strip() else {}
                save_team_profile(collection, created_user.uid, email, full_name, extras)
                st.success(
                    f"{account_type} account created successfully. "
                    f"Firebase UID: {created_user.uid}. The user can now sign in to the matching dashboard."
                )
                st.warning(
                    "The profile uses the existing collection and a document ID matching the Firebase UID. "
                    "Confirm that the target dashboard looks up profiles by this UID before using this workflow for real accounts."
                )
            except Exception as exc:
                # If profile write fails after account creation, surface UID so the owner can reconcile it.
                if created_user is not None:
                    st.error(
                        f"Firebase Authentication account was created (UID: {created_user.uid}), "
                        f"but saving the Firestore profile failed: {exc}. "
                        "Delete or repair that account/profile manually before retrying."
                    )
                else:
                    st.error(f"Could not create account: {exc}")

st.divider()
st.caption("Care+ Admin Dashboard · Admin access is authorized by Firestore and authenticated by Firebase Authentication.")
