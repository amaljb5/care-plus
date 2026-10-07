import os
import re
import json
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Care+ | Healthcare Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(ROOT_DIR, "database.db") if os.path.exists(os.path.join(ROOT_DIR, "database.db")) else os.path.join(BASE_DIR, "database.db")

# ==============================================================================
# FULL-SCREEN VIEWPORT STYLING (ELIMINATES ALL DARK BORDERS & MARGINS)
# ==============================================================================
st.markdown("""
<style>
    /* Match background to Care+ design tokens */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], section.main, .block-container {
        background-color: #F5F7F6 !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    /* Remove all Streamlit chrome, header, footer, sidebars */
    [data-testid="stHeader"],
    [data-testid="stSidebar"], 
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    footer,
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .element-container, 
    div[data-testid="stCustomComponentV1"] {
        width: 100vw !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Force the embedded iframe to occupy 100% full screen edge-to-edge */
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        min-height: 100vh !important;
        min-width: 100vw !important;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 999999 !important;
        background: #F5F7F6 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# DATABASE INITIALIZER (Seeds if empty)
# ==============================================================================
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                emergency_type TEXT,
                latitude REAL,
                longitude REAL,
                status TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                phone TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caregivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                service TEXT,
                phone TEXT,
                available INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                caregiver_id INTEGER,
                service TEXT,
                booking_date TEXT,
                status TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volunteers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                service TEXT,
                available INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_donors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                blood_group TEXT,
                location TEXT,
                available INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blood_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT,
                blood_group TEXT,
                hospital TEXT,
                location TEXT,
                status TEXT
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM caregivers")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
                INSERT INTO caregivers (name, service, phone, available) VALUES (?, ?, ?, ?)
            """, [
                ("Mary Varghese, RN", "Elder Nursing & Wound Dressing", "+91 98470 12345", 1),
                ("Rajesh Kumar", "Physiotherapy & Mobility Care", "+91 94471 23456", 1),
                ("Sarada Devi", "Daily Living & Medication Support", "+91 98950 34567", 1),
                ("Dr. Anand Menon", "Geriatric Home Consultations", "+91 94460 45678", 1)
            ])
            cursor.executemany("""
                INSERT INTO emergency_contacts (user_id, name, phone) VALUES (?, ?, ?)
            """, [
                (1, "Priya Suresh (Daughter)", "+91 98471 23456"),
                (1, "Dr. Joseph (Primary Physician)", "+91 94470 56789"),
                (1, "Care+ 24x7 Helpline", "+91 1800 425 1122")
            ])
            cursor.executemany("""
                INSERT INTO blood_donors (name, phone, blood_group, location, available) VALUES (?, ?, ?, ?, ?)
            """, [
                ("Arun Nair", "+91 98460 11223", "O+", "Ernakulam", 1),
                ("Fathima Beevi", "+91 94472 33445", "A+", "Kochi", 1),
                ("Rahul Thomas", "+91 98955 66778", "B+", "Kottayam", 1),
                ("Deepa Pillai", "+91 94461 88990", "AB+", "Aluva", 1)
            ])
            cursor.executemany("""
                INSERT INTO volunteers (name, phone, service, available) VALUES (?, ?, ?, ?)
            """, [
                ("Kochi Youth Care Corps", "+91 98473 11111", "Emergency Transport & Groceries", 1),
                ("Anu Kurian", "+91 94475 22222", "Companion Care & Reading", 1),
                ("Gopalakrishnan", "+91 98951 33333", "Medicine Delivery", 1)
            ])
            cursor.executemany("""
                INSERT INTO emergencies (user_id, emergency_type, latitude, longitude, status, created_at) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (1, "SOS - Fall Detected Alert", 9.9816, 76.2999, "RESOLVED", "2026-10-06 09:30:00"),
                (1, "Vitals Anomaly Notice", 9.9816, 76.2999, "VERIFIED", "2026-10-07 08:15:00")
            ])
            conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

# ==============================================================================
# BUNDLE FULL CARE+ SPA APPLICATION WITH CLEAN AUTHENTICATION SYSTEM
# ==============================================================================
@st.cache_data
def build_spa_html():
    css_path = os.path.join(BASE_DIR, "css", "style.css")
    js_path = os.path.join(BASE_DIR, "js", "script.js")
    
    css_content = ""
    js_content = ""
    
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

    files = {
        "welcome": os.path.join(BASE_DIR, "index.html"),
        "family": os.path.join(BASE_DIR, "family", "family-dashboard.html"),
        "admin": os.path.join(BASE_DIR, "admin", "admin-dashboard.html"),
        "doctor": os.path.join(BASE_DIR, "doctor-dashboard.html"),
        "patient": os.path.join(BASE_DIR, "patient-dashboard.html")
    }
    
    pages = {}
    for k, path in files.items():
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            m = re.search(r"<body[^>]*>(.*?)</body>", content, re.DOTALL)
            body = m.group(1) if m else content
            # Clean external script references
            body = re.sub(r'<script\s+src=[\'"][^\'"]*[\'"]\s*></script>', '', body, flags=re.IGNORECASE)
            pages[k] = body.strip()
        else:
            pages[k] = f"<div>Page {k} not found</div>"

    pages_json_str = json.dumps(pages)

    spa_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>Care+ Healthcare Platform</title>
<style>
{css_content}

/* SPA Fullscreen Resolution Optimization */
html, body {{
    min-height: 100vh;
    width: 100%;
    margin: 0;
    padding: 0;
    background-color: var(--color-bg, #F5F7F6);
    overflow-x: hidden;
}}

#app-root {{
    min-height: 100vh;
    width: 100%;
    display: flex;
    flex-direction: column;
}}

.app-shell {{
    min-height: 100vh;
    width: 100%;
    display: flex;
}}

.main {{
    flex: 1;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}}

.content {{
    flex: 1;
}}

/* Clean customized scrollbars */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: #F1F5F9;
}}
::-webkit-scrollbar-thumb {{
    background: #CBD5E1;
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: #94A3B8;
}}

/* ==========================================================================
   AUTHENTICATION MODAL STYLING
   ========================================================================== */
.auth-role-tabs {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 20px;
}}
.auth-role-tab {{
    padding: 10px 6px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    border: 2px solid #E2E8F0;
    border-radius: 10px;
    cursor: pointer;
    background: white;
    transition: all 0.18s ease;
    user-select: none;
}}
.auth-role-tab:hover {{
    border-color: #CBD5E1;
    background: #F8FAFC;
}}
.auth-role-tab.active {{
    border-color: #5F9F68;
    background: #E6F2E8;
    color: #2D5A34;
}}
.auth-error-msg {{
    background: #FEE2E2;
    color: #991B1B;
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 0.88rem;
    margin-bottom: 16px;
    border: 1px solid #FCA5A5;
    display: none;
}}
</style>
</head>
<body>

<div id="app-root"></div>

<!-- UNIVERSAL LOGIN MODAL -->
<div class="modal-overlay" id="carePlusLoginModal" role="dialog" aria-modal="true" aria-labelledby="authModalTitle">
  <div class="modal" style="max-width:480px; text-align:left;">
    <button class="modal__close-btn" onclick="CarePlusAuthManager.closeLoginModal()" aria-label="Close modal">&times;</button>
    
    <div style="text-align:center; margin-bottom:20px;">
      <div class="sidebar__logo-mark" style="width:52px; height:52px; font-size:1.5rem; margin:0 auto 10px;">C+</div>
      <h3 class="modal__title" id="authModalTitle" style="margin:0 0 4px 0; font-size:1.4rem;">Sign In to Care+</h3>
      <p class="modal__text" id="authModalSubtitle" style="margin:0; font-size:0.92rem; color:var(--color-text-secondary);">Select your workspace and enter your credentials.</p>
    </div>

    <!-- ROLE SELECTOR TABS -->
    <div class="auth-role-tabs" id="authRoleTabs">
      <div class="auth-role-tab active" data-auth-role="family">👨‍👩‍👧 Family</div>
      <div class="auth-role-tab" data-auth-role="admin">🛡️ Admin</div>
      <div class="auth-role-tab" data-auth-role="doctor">🩺 Doctor</div>
      <div class="auth-role-tab" data-auth-role="patient">🧑 Patient</div>
    </div>

    <div class="auth-error-msg" id="authErrorMsg"></div>

    <!-- LOGIN FORM -->
    <form id="carePlusLoginForm" onsubmit="CarePlusAuthManager.handleLoginSubmit(event)">
      <input type="hidden" id="loginTargetRole" value="family" />
      
      <div style="margin-bottom:16px;">
        <label for="loginUsername" style="display:block; font-size:0.88rem; font-weight:600; margin-bottom:6px; color:#1F2933;">Username or Email</label>
        <input type="text" id="loginUsername" class="form-input" placeholder="Enter username or email" required style="width:100%;" autocomplete="username" />
      </div>

      <div style="margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <label for="loginPassword" style="font-size:0.88rem; font-weight:600; color:#1F2933;">Password</label>
          <span style="font-size:0.75rem; color:#6B7280; cursor:pointer;" onclick="CarePlusAuthManager.togglePassword()">👁️ Show/Hide</span>
        </div>
        <input type="password" id="loginPassword" class="form-input" placeholder="Enter password" required style="width:100%;" autocomplete="current-password" />
      </div>

      <div class="modal__actions" style="margin-top:24px; display:flex; gap:10px;">
        <button type="button" class="btn btn-outline" style="flex:1;" onclick="CarePlusAuthManager.closeLoginModal()">Cancel</button>
        <button type="submit" class="btn btn-primary" style="flex:2; font-weight:700;">Sign In &rarr;</button>
      </div>
    </form>
  </div>
</div>

<script>
{js_content}
</script>

<script>
(function() {{
    const carePlusPages = {pages_json_str};

    // User credentials database
    window.CAREPLUS_CREDENTIALS = {{
        'family': {{
            usernames: ['family@careplus.org', 'priya.suresh@careplus.org', 'family', 'priya'],
            password: 'family123',
            roleKey: 'family',
            targetPage: 'family',
            displayName: 'Priya Suresh',
            title: 'Family Member'
        }},
        'admin': {{
            usernames: ['admin@careplus.org', 'admin', 'administrator'],
            password: 'admin123',
            roleKey: 'admin',
            targetPage: 'admin',
            displayName: 'System Admin',
            title: 'Administrator'
        }},
        'doctor': {{
            usernames: ['doctor@careplus.org', 'dr.joseph@careplus.org', 'doctor', 'drjoseph'],
            password: 'doctor123',
            roleKey: 'doctor',
            targetPage: 'doctor',
            displayName: 'Dr. Joseph, MD',
            title: 'Doctor'
        }},
        'patient': {{
            usernames: ['patient@careplus.org', 'thomas@careplus.org', 'patient', 'thomas'],
            password: 'patient123',
            roleKey: 'senior',
            targetPage: 'patient',
            displayName: 'Thomas Mathew',
            title: 'Senior Citizen'
        }}
    }};

    window.CarePlusAuthManager = {{
        openLoginModal: function(targetRole) {{
            targetRole = targetRole || 'family';
            var modal = document.getElementById('carePlusLoginModal');
            if (!modal) return;
            
            this.setTargetRole(targetRole);
            this.clearInputs();
            this.clearError();
            modal.classList.add('is-open');
            document.body.style.overflow = 'hidden';
            
            setTimeout(function() {{
                var userInput = document.getElementById('loginUsername');
                if (userInput) userInput.focus();
            }}, 100);
        }},

        closeLoginModal: function() {{
            var modal = document.getElementById('carePlusLoginModal');
            if (modal) modal.classList.remove('is-open');
            document.body.style.overflow = '';
        }},

        clearInputs: function() {{
            var u = document.getElementById('loginUsername');
            var p = document.getElementById('loginPassword');
            if (u) u.value = '';
            if (p) p.value = '';
        }},

        setTargetRole: function(roleKey) {{
            document.getElementById('loginTargetRole').value = roleKey;
            document.querySelectorAll('.auth-role-tab').forEach(function(tab) {{
                tab.classList.toggle('active', tab.getAttribute('data-auth-role') === roleKey);
            }});
            var roleNames = {{ 'family': 'Family', 'admin': 'Admin', 'doctor': 'Doctor', 'patient': 'Patient' }};
            var placeholderRole = roleNames[roleKey] || 'Family';
            var userInput = document.getElementById('loginUsername');
            if (userInput) userInput.placeholder = 'e.g. ' + roleKey.toLowerCase() + '@careplus.org';
        }},

        togglePassword: function() {{
            var input = document.getElementById('loginPassword');
            if (input) {{
                input.type = input.type === 'password' ? 'text' : 'password';
            }}
        }},

        showError: function(msg) {{
            var el = document.getElementById('authErrorMsg');
            if (el) {{
                el.textContent = msg;
                el.style.display = 'block';
            }}
        }},

        clearError: function() {{
            var el = document.getElementById('authErrorMsg');
            if (el) {{
                el.textContent = '';
                el.style.display = 'none';
            }}
        }},

        handleLoginSubmit: function(e) {{
            e.preventDefault();
            var username = document.getElementById('loginUsername').value.trim().toLowerCase();
            var password = document.getElementById('loginPassword').value.trim();

            // Find matching credential
            var matchedRole = null;
            for (var r in window.CAREPLUS_CREDENTIALS) {{
                var cred = window.CAREPLUS_CREDENTIALS[r];
                var userMatches = cred.usernames.some(function(u) {{ return u.toLowerCase() === username; }});
                if (userMatches && cred.password === password) {{
                    matchedRole = cred;
                    break;
                }}
            }}

            if (matchedRole) {{
                // Save authentication session
                sessionStorage.setItem('careplus_logged_in', 'true');
                sessionStorage.setItem('careplus_user_role', matchedRole.roleKey);
                sessionStorage.setItem('careplus_user_name', matchedRole.displayName);
                localStorage.setItem('careplus_current_role', matchedRole.roleKey);
                localStorage.setItem('careplus_user_name', matchedRole.displayName);

                this.closeLoginModal();
                if (typeof showToast === 'function') {{
                    showToast('Welcome back, ' + matchedRole.displayName + '!');
                }}
                window.navigateCarePlus(matchedRole.targetPage);
            }} else {{
                this.showError('Invalid username or password. Please try again.');
            }}
        }},

        logout: function() {{
            sessionStorage.removeItem('careplus_logged_in');
            sessionStorage.removeItem('careplus_user_role');
            sessionStorage.removeItem('careplus_user_name');
            localStorage.removeItem('careplus_current_role');
            localStorage.removeItem('careplus_user_name');
            if (typeof showToast === 'function') showToast('Logged out successfully.');
            setTimeout(function() {{
                window.navigateCarePlus('welcome');
            }}, 300);
        }}
    }};

    // Setup role tab clicks
    document.querySelectorAll('.auth-role-tab').forEach(function(tab) {{
        tab.addEventListener('click', function() {{
            var role = tab.getAttribute('data-auth-role');
            CarePlusAuthManager.setTargetRole(role);
        }});
    }});

    window.navigateCarePlus = function(pageKey) {{
        if (!carePlusPages[pageKey]) {{
            pageKey = 'welcome';
        }}
        
        sessionStorage.setItem('careplus_active_page', pageKey);
        
        var appRoot = document.getElementById('app-root');
        if (!appRoot) return;
        
        // Inject new page HTML
        appRoot.innerHTML = carePlusPages[pageKey];
        
        // Re-run initializers
        try {{ if (typeof initSidebarNav === 'function') initSidebarNav(); }} catch(e) {{}}
        try {{ if (typeof initMobileSidebar === 'function') initMobileSidebar(); }} catch(e) {{}}
        try {{ if (typeof initDropdown === 'function') {{ initDropdown('notifBtn', 'notifPanel'); initDropdown('profileBtn', 'profilePanel'); }} }} catch(e) {{}}
        try {{ if (typeof initGlobalDropdownClose === 'function') initGlobalDropdownClose(); }} catch(e) {{}}
        try {{ if (typeof initQuickActionToasts === 'function') initQuickActionToasts(); }} catch(e) {{}}
        try {{ if (typeof initMedicationStatus === 'function') initMedicationStatus(); }} catch(e) {{}}
        try {{ if (typeof initCaregiverToggle === 'function') initCaregiverToggle(); }} catch(e) {{}}
        try {{ if (typeof initConsultationModal === 'function') initConsultationModal(); }} catch(e) {{}}
        try {{ if (typeof initLogout === 'function') initLogout(); }} catch(e) {{}}
        try {{ if (typeof initI18n === 'function') initI18n(); }} catch(e) {{}}
        try {{ if (typeof initAccessibility === 'function') initAccessibility(); }} catch(e) {{}}
        try {{ if (typeof initVoiceBridge === 'function') initVoiceBridge(); }} catch(e) {{}}
        try {{ if (typeof initRoleSwitcher === 'function') initRoleSwitcher(); }} catch(e) {{}}
        try {{ if (typeof initSmartNotifications === 'function') initSmartNotifications(); }} catch(e) {{}}
        
        if (pageKey === 'family' && typeof initFamilyDashboard === 'function') {{
            try {{ initFamilyDashboard(); }} catch(e) {{}}
        }}
        if (pageKey === 'admin' && typeof initAdminDashboard === 'function') {{
            try {{ initAdminDashboard(); }} catch(e) {{}}
        }}

        // Apply active language to all newly rendered elements
        try {{
            if (typeof CarePlusI18n !== 'undefined') {{
                CarePlusI18n.applyLanguage(CarePlusI18n.currentLang);
            }}
        }} catch(e) {{}}

        // Ensure page is scrolled to top
        window.scrollTo({{ top: 0, behavior: 'instant' }});
    }};

    // Override CarePlusAuth navigation methods to use SPA router and login manager
    if (typeof CarePlusAuth !== 'undefined') {{
        CarePlusAuth.switchRole = function(roleKey) {{
            var roleMap = {{
                'senior': 'patient',
                'doctor': 'doctor',
                'family': 'family',
                'caregiver': 'family',
                'volunteer': 'family',
                'admin': 'admin'
            }};
            var target = roleMap[roleKey] || 'welcome';
            CarePlusAuth.closeModal();
            CarePlusAuthManager.openLoginModal(target);
        }};

        CarePlusAuth.logout = function() {{
            CarePlusAuthManager.logout();
        }};
    }}

    // Global Click Interceptor for seamless in-page routing & Login Triggers
    document.addEventListener('click', function(e) {{
        // Portal Cards on Landing Page
        var portalCard = e.target.closest('.portal-card, a.portal-card');
        if (portalCard) {{
            if (portalCard.classList.contains('portal-card--family')) {{
                e.preventDefault();
                e.stopPropagation();
                CarePlusAuthManager.openLoginModal('family');
                return;
            }}
            if (portalCard.classList.contains('portal-card--admin')) {{
                e.preventDefault();
                e.stopPropagation();
                CarePlusAuthManager.openLoginModal('admin');
                return;
            }}
            var href = portalCard.getAttribute('href');
            if (href && (href.indexOf('family') !== -1 || href.indexOf('family-dashboard') !== -1)) {{
                e.preventDefault();
                e.stopPropagation();
                CarePlusAuthManager.openLoginModal('family');
                return;
            }}
            if (href && (href.indexOf('admin') !== -1 || href.indexOf('admin-dashboard') !== -1)) {{
                e.preventDefault();
                e.stopPropagation();
                CarePlusAuthManager.openLoginModal('admin');
                return;
            }}
        }}

        // Role Switcher Cards
        var roleCard = e.target.closest('.role-card[data-role]');
        if (roleCard) {{
            e.preventDefault();
            e.stopPropagation();
            var role = roleCard.getAttribute('data-role');
            var roleMap = {{ 'senior':'patient', 'doctor':'doctor', 'family':'family', 'admin':'admin' }};
            var target = roleMap[role] || 'family';
            var roleModal = document.getElementById('roleSwitcherModal');
            if (roleModal) roleModal.classList.remove('is-open');
            CarePlusAuthManager.openLoginModal(target);
            return;
        }}

        // Logout Links
        var logoutBtn = e.target.closest('[data-action="logout"]');
        if (logoutBtn) {{
            e.preventDefault();
            e.stopPropagation();
            CarePlusAuthManager.logout();
            return;
        }}

        // General Dashboard Links
        var link = e.target.closest('a');
        if (link) {{
            var href = link.getAttribute('href') || '';
            if (href.indexOf('family/family-dashboard.html') !== -1 || href === 'family-dashboard.html') {{
                e.preventDefault();
                CarePlusAuthManager.openLoginModal('family');
            }} else if (href.indexOf('admin/admin-dashboard.html') !== -1 || href === 'admin-dashboard.html') {{
                e.preventDefault();
                CarePlusAuthManager.openLoginModal('admin');
            }} else if (href.indexOf('doctor-dashboard.html') !== -1) {{
                e.preventDefault();
                CarePlusAuthManager.openLoginModal('doctor');
            }} else if (href.indexOf('patient-dashboard.html') !== -1) {{
                e.preventDefault();
                CarePlusAuthManager.openLoginModal('patient');
            }} else if (href === 'index.html' || href === '../index.html') {{
                e.preventDefault();
                window.navigateCarePlus('welcome');
            }}
        }}
    }}, true);

    // Initial boot
    document.addEventListener('DOMContentLoaded', function() {{
        var initial = sessionStorage.getItem('careplus_active_page') || 'welcome';
        window.navigateCarePlus(initial);
    }});

    // Immediate fallback
    var initial = sessionStorage.getItem('careplus_active_page') || 'welcome';
    window.navigateCarePlus(initial);
}})();
</script>

</body>
</html>
"""
    return spa_html

# ==============================================================================
# RENDER FULL-SCREEN CARE+ APPLICATION
# ==============================================================================
spa_content = build_spa_html()
components.html(spa_content, height=1000, scrolling=True)
