/* ==========================================================================
   CARE+ SHARED SCRIPT
   Handles frontend interactions for patient-dashboard.html and
   doctor-dashboard.html. No backend calls — placeholders only.
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {
  initSidebarNav();
  initMobileSidebar();
  initDropdown('notifBtn', 'notifPanel');
  initDropdown('profileBtn', 'profilePanel');
  initGlobalDropdownClose();
  initQuickActionToasts();
  initMedicationStatus();
  initCaregiverToggle();
  initConsultationModal();
  initLogout();

  /* Care+ Core Initializers */
  initI18n();
  initAccessibility();
  initVoiceBridge();
  initRoleSwitcher();
  initSmartNotifications();
  initFamilyDashboard();
  initAdminDashboard();
});

/* -------------------- Sidebar active-state navigation -------------------- */
function initSidebarNav() {
  var links = document.querySelectorAll('.sidebar__link[data-nav]');
  var quickNavTargets = document.querySelectorAll('[data-nav]');

  quickNavTargets.forEach(function (el) {
    el.addEventListener('click', function (e) {
      var section = el.getAttribute('data-nav');
      if (!section) return;

      // Only intercept links/buttons that don't already navigate to a real page.
      var href = el.getAttribute('href');
      var isRealPage = href && href !== '#' && !href.startsWith('#');
      if (isRealPage) return;

      // If the link points to an in-page section, scroll smoothly to it
      if (href && href.startsWith('#') && href.length > 1) {
        var targetSection = document.querySelector(href);
        if (targetSection) {
          e.preventDefault();
          links.forEach(function (link) {
            link.classList.remove('is-active');
            link.removeAttribute('aria-current');
          });
          var target = document.querySelector('.sidebar__link[data-nav="' + section + '"]');
          if (target) {
            target.classList.add('is-active');
            target.setAttribute('aria-current', 'page');
          }
          closeAllDropdowns();
          targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          return;
        }
      }

      e.preventDefault();

      // Update active state on matching sidebar link.
      links.forEach(function (link) {
        link.classList.remove('is-active');
        link.removeAttribute('aria-current');
      });
      var target = document.querySelector('.sidebar__link[data-nav="' + section + '"]');
      if (target) {
        target.classList.add('is-active');
        target.setAttribute('aria-current', 'page');
      }

      closeAllDropdowns();

      var label = target ? target.querySelector('span').textContent : section;
      showToast(label + ' section is coming soon.');
    });
  });
}

/* -------------------- Mobile sidebar toggle -------------------- */
function initMobileSidebar() {
  var toggle = document.getElementById('sidebarToggle');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');
  if (!toggle || !sidebar || !overlay) return;

  function openSidebar() {
    sidebar.classList.add('is-open');
    overlay.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    sidebar.classList.remove('is-open');
    overlay.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.addEventListener('click', function () {
    var isOpen = sidebar.classList.contains('is-open');
    isOpen ? closeSidebar() : openSidebar();
  });

  overlay.addEventListener('click', closeSidebar);

  sidebar.querySelectorAll('.sidebar__link').forEach(function (link) {
    link.addEventListener('click', closeSidebar);
  });
}

/* -------------------- Generic dropdown (notifications / profile) -------------------- */
function initDropdown(buttonId, panelId) {
  var button = document.getElementById(buttonId);
  var panel = document.getElementById(panelId);
  if (!button || !panel) return;

  button.addEventListener('click', function (e) {
    e.stopPropagation();
    var isOpen = panel.classList.contains('is-open');
    closeAllDropdowns();
    if (!isOpen) {
      panel.classList.add('is-open');
      button.setAttribute('aria-expanded', 'true');
    }
  });

  panel.addEventListener('click', function (e) {
    e.stopPropagation();
  });
}

function closeAllDropdowns() {
  document.querySelectorAll('.dropdown__panel.is-open').forEach(function (panel) {
    panel.classList.remove('is-open');
  });
  document.querySelectorAll('.header__actions [aria-expanded="true"]').forEach(function (btn) {
    btn.setAttribute('aria-expanded', 'false');
  });
}

function closeAllModals() {
  document.querySelectorAll('.modal-overlay.is-open').forEach(function (modal) {
    modal.classList.remove('is-open');
  });
  document.body.style.overflow = '';
}

function closeModal() {
  closeAllModals();
}

function initGlobalDropdownClose() {
  document.addEventListener('click', closeAllDropdowns);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAllDropdowns();
      closeAllModals();
    }
  });

  // Universal backdrop close on overlay click
  document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) {
        closeAllModals();
      }
    });
  });

  // Universal modal close buttons
  document.querySelectorAll('[data-action="close-modal"], [data-close-modal], .modal__close-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      closeAllModals();
    });
  });
}

/* -------------------- Quick action buttons -------------------- */
function initQuickActionToasts() {
  var actions = document.querySelectorAll('.quick-action[data-toast]');
  actions.forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!btn.hasAttribute('data-nav')) {
        showToast(btn.getAttribute('data-toast'));
      }
    });
  });
}

/* -------------------- Medication status interaction (patient) -------------------- */
function initMedicationStatus() {
  var pill = document.getElementById('medStatusPill');
  if (!pill) return;

  pill.style.cursor = 'pointer';
  pill.setAttribute('role', 'button');
  pill.setAttribute('tabindex', '0');
  pill.title = 'Mark as taken';

  function markTaken() {
    var alreadyTaken = pill.classList.contains('status-pill--success');
    if (alreadyTaken) return;

    pill.classList.remove('status-pill--warning');
    pill.classList.add('status-pill--success');
    pill.innerHTML =
      '<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> Taken';
    showToast('Amlodipine marked as taken. Great job!');
  }

  pill.addEventListener('click', markTaken);
  pill.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      markTaken();
    }
  });
}

/* -------------------- Caregiver notification toggle (patient) -------------------- */
function initCaregiverToggle() {
  var toggle = document.getElementById('caregiverToggle');
  if (!toggle) return;

  toggle.addEventListener('click', function () {
    var isOn = toggle.getAttribute('aria-checked') === 'true';
    toggle.setAttribute('aria-checked', String(!isOn));
    toggle.classList.toggle('is-off', isOn);
    showToast(isOn ? 'Caregiver notifications turned off.' : 'Caregiver notifications turned on.');
  });
}

/* -------------------- Consultation / Join modal -------------------- */
function initConsultationModal() {
  var modal = document.getElementById('consultModal');
  if (!modal) return;

  var titleEl = document.getElementById('consultModalTitle');
  var textEl = document.getElementById('consultModalText');

  // Patient dashboard: single "Join Consultation" button.
  var joinBtn = document.getElementById('joinConsultationBtn');
  if (joinBtn) {
    joinBtn.addEventListener('click', function () {
      openModal();
    });
  }

  // Doctor dashboard: one "Join" button per consultation row.
  var joinRowButtons = document.querySelectorAll('.join-btn');
  joinRowButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var patient = btn.getAttribute('data-patient') || 'your patient';
      if (titleEl) titleEl.textContent = 'Your consultation with ' + patient + ' is ready to begin.';
      if (textEl) {
        textEl.textContent =
          'This is a placeholder screen. Video/voice calling functionality will be connected once the backend and calling service are integrated.';
      }
      openModal();
    });
  });

  modal.querySelectorAll('[data-close-modal], [data-action="close-modal"]').forEach(function (btn) {
    btn.addEventListener('click', closeAllModals);
  });

  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeAllModals();
  });

  function openModal() {
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
}

/* -------------------- Logout -------------------- */
function initLogout() {
  document.querySelectorAll('[data-action="logout"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      closeAllDropdowns();
      if (window.CarePlusAuth && typeof CarePlusAuth.logout === 'function') {
        CarePlusAuth.logout();
      } else {
        localStorage.removeItem('careplus_auth_user');
        localStorage.removeItem('careplus_current_role');
        showToast('Logged out successfully.');
        setTimeout(function () {
          var isSubdir = window.location.pathname.indexOf('/family/') !== -1 || window.location.pathname.indexOf('/admin/') !== -1;
          window.location.href = isSubdir ? '../index.html' : 'index.html';
        }, 400);
      }
    });
  });
}

/* -------------------- Toast helper -------------------- */
var toastTimer = null;
function showToast(message) {
  var toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add('is-open');

  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () {
    toast.classList.remove('is-open');
  }, 3000);
}

/* ==========================================================================
   MULTILINGUAL SYSTEM (COMPREHENSIVE FULL-PAGE MALAYALAM TRANSLATION ENGINE)
   ========================================================================== */
var CarePlusI18n = {
  currentLang: 'en',
  textMap: {
  "Care+": "കെയർ+",
  "Welcome to Care+": "കെയർ+ ലേക്ക് സ്വാഗതം",
  "Platform Portals": "പ്ലാറ്റ്ഫോം പോർട്ടലുകൾ",
  "Family Portal": "കുടുംബ പോർട്ടൽ",
  "Family Dashboard": "കുടുംബ ഡാഷ്‌ബോർഡ്",
  "Admin Console": "അഡ്മിൻ കൺസോൾ",
  "Admin Dashboard": "അഡ്മിൻ ഡാഷ്‌ബോർഡ്",
  "Doctor Dashboard": "ഡോക്ടർ ഡാഷ്‌ബോർഡ്",
  "Patient Dashboard": "രോഗി ഡാഷ്‌ബോർഡ്",
  "Senior Citizen": "മുതിർന്ന പൗരൻ",
  "Doctor": "ഡോക്ടർ",
  "Family Member": "കുടുംബാംഗം",
  "Administrator": "അഡ്മിനിസ്ട്രേറ്റർ",
  "Caregiver": "പരിപാലകൻ",
  "Volunteer": "വോളണ്ടിയർ",
  "Dashboard": "ഡാഷ്‌ബോർഡ്",
  "Overview & Vitals": "അവലോകനവും ആരോഗ്യനിലയും",
  "Health & Vitals": "ആരോഗ്യ വിവരങ്ങൾ",
  "My Patients": "എന്റെ രോഗികൾ",
  "Medications": "മരുന്നുകൾ",
  "Medications & Schedule": "മരുന്ന് ഷെഡ്യൂൾ",
  "My Medicines": "എന്റെ മരുന്നുകൾ",
  "Appointments": "അപ്പോയിന്റ്മെന്റുകൾ",
  "Consultations": "കൺസൾട്ടേഷനുകൾ",
  "Consult a Doctor": "ഡോക്ടറെ കാണുക",
  "Medical Records": "മെഡിക്കൽ രേഖകൾ",
  "Prescriptions": "പ്രിസ്ക്രിപ്ഷനുകൾ",
  "Care Network & Contacts": "കെയർ നെറ്റ്‌വർക്കും കോൺടാക്റ്റുകളും",
  "Care Network & Calling": "കെയർ നെറ്റ്‌വർക്കും വിളികളും",
  "Family Contacts": "കുടുംബ കോൺടാക്റ്റുകൾ",
  "Family Account": "കുടുംബ അക്കൗണ്ട്",
  "Family Account Settings": "കുടുംബ അക്കൗണ്ട് ക്രമീകരണങ്ങൾ",
  "Smart Notifications": "സ്മാർട്ട് അറിയിപ്പുകൾ",
  "Notifications": "അറിയിപ്പുകൾ",
  "Accessibility": "പ്രവേശനക്ഷമത",
  "Accessibility Settings": "പ്രവേശനക്ഷമതാ ക്രമീകരണങ്ങൾ",
  "Accessibility Controls": "പ്രവേശനക്ഷമതാ ക്രമീകരണങ്ങൾ",
  "Settings": "ക്രമീകരണങ്ങൾ",
  "Logout": "ലോഗ് ഔട്ട്",
  "Users": "ഉപയോക്താക്കൾ",
  "User Management": "ഉപയോക്തൃ മാനേജ്മെന്റ്",
  "Verifications": "സ്ഥിരീകരണങ്ങൾ",
  "Professional Verifications": "പ്രൊഫഷണൽ സ്ഥിരീകരണങ്ങൾ",
  "Emergencies": "അടിയന്തര സാഹചര്യങ്ങൾ",
  "Emergency Oversight": "അടിയന്തര മേൽനോട്ടം",
  "Reports & Analytics": "റിപ്പോർട്ടുകളും വിശകലനവും",
  "Consent & Privacy": "സമ്മതവും സ്വകാര്യതയും",
  "Patient Consent & Data Privacy": "രോഗിയുടെ സമ്മതവും സ്വകാര്യതയും",
  "Voice Navigation": "വോയ്‌സ് നാവിഗേഷൻ",
  "Voice Navigation Assistant": "വോയ്‌സ് നാവിഗേഷൻ അസിസ്റ്റന്റ്",
  "Voice Assistant": "വോയ്‌സ് അസിസ്റ്റന്റ്",
  "🎙 Voice Nav": "🎙 വോയ്‌സ് നാവിഗേഷൻ",
  "Good Morning, Priya": "സുപ്രഭാതം, പ്രിയ",
  "Good Morning, Dr. Joseph": "സുപ്രഭാതം, ഡോ. ജോസഫ്",
  "Good Morning, Thomas": "സുപ്രഭാതം, തോമസ്",
  "Monitoring Anitha Suresh · All vitals stable": "അനിത സുരേഷിനെ നിരീക്ഷിക്കുന്നു · എല്ലാ ആരോഗ്യനിലയും സുസ്ഥിരം",
  "Monitoring Anitha Suresh": "അനിത സുരേഷിനെ നിരീക്ഷിക്കുന്നു",
  "All vitals stable": "എല്ലാ ആരോഗ്യനിലയും സുസ്ഥിരം",
  "Here is an overview of your patients and consultations today.": "നിങ്ങളുടെ രോഗികളുടെയും ഇന്നത്തെ കൺസൾട്ടേഷനുകളുടെയും അവലോകനം ഇതാ.",
  "Here is your health summary for today. Take care of yourself.": "ഇന്നത്തെ നിങ്ങളുടെ ആരോഗ്യ സംഗ്രഹം ഇതാ. സ്വന്തം ആരോഗ്യം ശ്രദ്ധിക്കുക.",
  "Care+ System Administration": "കെയർ+ സിസ്റ്റം അഡ്മിനിസ്ട്രേഷൻ",
  "Operational governance, professional verification & privacy compliance": "പ്രവർത്തന ഭരണം, പ്രൊഫഷണൽ പരിശോധന & സ്വകാര്യതാ പാലനം",
  "Intelligent Elder Healthcare, Wellbeing Monitoring & Platform Administration. Select a portal below to enter its specialized workspace.": "ബുദ്ധിപരമായ മുതിർന്നവരുടെ ആരോഗ്യ സംരക്ഷണം, ക്ഷേമ നിരീക്ഷണം & പ്ലാറ്റ്‌ഫോം ഭരണം. അനുയോജ്യമായ പോർട്ടൽ തിരഞ്ഞെടുക്കുക.",
  "Real-time senior wellbeing monitoring, daily medication schedule tracking, upcoming doctor appointments, 24/7 safety notifications, and one-tap emergency calling.": "തത്സമയ മുതിർന്നവരുടെ ആരോഗ്യ നിരീക്ഷണം, ദൈനംദിന മരുന്ന് ഷെഡ്യൂൾ ട്രാക്കിംഗ്, വരാനിരിക്കുന്ന ഡോക്ടർ അപ്പോയിന്റ്മെന്റുകൾ, 24/7 സുരക്ഷാ അറിയിപ്പുകൾ, ഒറ്റ ടാപ്പിൽ അടിയന്തര കോളിംഗ്.",
  "Continuous Health Telemetry (BP, Glucose, Pulse)": "തുടർച്ചയായ ആരോഗ്യ വിവരങ്ങൾ (രക്തസമ്മർദ്ദം, ഗ്ലൂക്കോസ്, പൾസ്)",
  "Prescription Schedules & Adherence Timeline": "മരുന്ന് ഷെഡ്യൂളുകളും കൃത്യതാ ടൈംലൈനും",
  "Emergency Contacts with One-Tap & Voice Calling": "ഒറ്റ ടാപ്പിലും വോയ്സ് കോളിലും അടിയന്തര കോൺടാക്റ്റുകൾ",
  "Open Family Dashboard →": "കുടുംബ ഡാഷ്‌ബോർഡ് തുറക്കുക →",
  "System governance, role-based user management, credential verification for healthcare providers, appointment audits, safety logs, and data sharing privacy compliance.": "സിസ്റ്റം ഭരണം, ഉപയോക്തൃ മാനേജ്മെന്റ്, ആരോഗ്യ പ്രവർത്തകരുടെ സർട്ടിഫിക്കറ്റ് പരിശോധന, അപ്പോയിന്റ്മെന്റ് ഓഡിറ്റുകൾ, സുരക്ഷാ ലോഗുകൾ, ഡാറ്റ സ്വകാര്യതാ പാലനം.",
  "User Governance & Role-Based Access Control": "ഉപയോക്തൃ ഭരണവും റോൾ അധിഷ്ഠിത ആക്സസും",
  "Doctor & Caregiver Credential Verification Queue": "ഡോക്ടർമാരുടെയും പരിപാലകരുടെയും സർട്ടിഫിക്കറ്റ് പരിശോധനാ നിര",
  "Audit Logs, Analytics & Patient Privacy Controls": "ഓഡിറ്റ് ലോഗുകൾ, വിശകലനം & രോഗികളുടെ സ്വകാര്യതാ നിയന്ത്രണം",
  "Open Admin Dashboard →": "അഡ്മിൻ ഡാഷ്‌ബോർഡ് തുറക്കുക →",
  "Universal Accessibility & Multilingual Support": "സാർവത്രിക പ്രവേശനക്ഷമതയും ബഹുഭാഷാ പിന്തുണയും",
  "Elder-friendly accessibility controls engineered for senior readability, high contrast visibility, scalable font sizing, and bilingual English & Malayalam interface.": "മുതിർന്നവർക്ക് വായിക്കാൻ എളുപ്പമുള്ള പ്രവേശനക്ഷമതാ ക്രമീകരണങ്ങൾ, ഉയർന്ന കോൺട്രാസ്റ്റ്, മാറ്റാവുന്ന ഫോണ്ട് വലുപ്പം, ഇംഗ്ലീഷ് & മലയാളം ഭാഷാ ഇന്റർഫേസ്.",
  "Dynamic Text Scaling (A+ / A-) & High-Contrast Mode": "ടെക്സ്റ്റ് വലുപ്പം മാറ്റൽ (A+ / A-) & ഹൈ-കോൺട്രാസ്റ്റ് മോഡ്",
  "Large Touch Targets & Simplified Navigation Mode": "വലിയ ടച്ച് ബട്ടണുകളും ലളിതമായ നാവിഗേഷനും",
  "Instant English & Malayalam (മലയാളം) Language Switch": "തൽക്ഷണ ഇംഗ്ലീഷ് & മലയാളം ഭാഷാ മാറ്റം",
  "Open Accessibility Controls →": "പ്രവേശനക്ഷമതാ ക്രമീകരണങ്ങൾ തുറക്കുക →",
  "Hands-free voice recognition enabling seniors and family members to search services, check vital status, view notifications, and connect calls by speaking naturally.": "മുതിർന്നവർക്കും കുടുംബാംഗങ്ങൾക്കും സംസാരിച്ച് സേവനങ്ങൾ തിരയാനും ആരോഗ്യനില പരിശോധിക്കാനും അറിയിപ്പുകൾ കാണാനും കോൺടാക്റ്റുകളെ വിളിക്കാനുമുള്ള വോയ്സ് സഹായം.",
  "Natural Speech Recognition in English & Malayalam": "ഇംഗ്ലീഷിലും മലയാളത്തിലും വോയ്സ് തിരിച്ചറിയൽ",
  "Quick Voice Routing to Health, Schedule & Alerts": "ആരോഗ്യം, ഷെഡ്യൂൾ, അടിയന്തര അറിയിപ്പുകൾ എന്നിവയിലേക്ക് പെട്ടെന്ന് എത്താം",
  "Voice Calling Integration for Emergency Contacts": "അടിയന്തര കോൺടാക്റ്റുകളിലേക്ക് വോയ്സ് കോളിംഗ് സംവിധാനം",
  "Open Voice Navigation →": "വോയ്‌സ് നാവിഗേഷൻ തുറക്കുക →",
  "Senior Wellbeing Vitals": "മുതിർന്നവരുടെ ആരോഗ്യ വിവരങ്ങൾ",
  "Continuous physiological readings · Last synced 10m ago": "തുടർച്ചയായ ആരോഗ്യ പരിശോധനകൾ · 10 മിനിറ്റ് മുമ്പ് അപ്ഡേറ്റ് ചെയ്തു",
  "BLOOD PRESSURE": "രക്തസമ്മർദ്ദം",
  "Blood Pressure": "രക്തസമ്മർദ്ദം",
  "BLOOD SUGAR": "രക്തത്തിലെ പഞ്ചസാര",
  "Blood Sugar": "രക്തത്തിലെ പഞ്ചസാര",
  "HEART RATE": "ഹൃദയമിടിപ്പ്",
  "Heart Rate": "ഹൃദയമിടിപ്പ്",
  "OXYGEN (SPO2)": "ഓക്സിജൻ (SpO2)",
  "Oxygen (SpO2)": "ഓക്സിജൻ (SpO2)",
  "TEMPERATURE": "ശരീര താപനില",
  "Temperature": "ശരീര താപനില",
  "WEIGHT": "ശരീരഭാരം",
  "Weight": "ശരീരഭാരം",
  "Normal": "സാധാരണ",
  "Normal - 8:00 AM": "സാധാരണ നില - 8:00 AM",
  "Normal Fasting": "സാധാരണ ഫാസ്റ്റിംഗ്",
  "Resting Rhythm": "വിശ്രമ താളം",
  "Optimal Oxygen": "മികച്ച ഓക്സിജൻ നില",
  "Normal Temp": "സാധാരണ താപനില",
  "All 6 Metrics Normal": "എല്ലാ 6 പരിശോധനകളും സാധാരണ നിലയിലാണ്",
  "7-Day Vital Trends": "7 ദിവസത്തെ ആരോഗ്യ ട്രെൻഡുകൾ",
  "Blood Pressure Trend": "രക്തസമ്മർദ്ദ ട്രെൻഡ്",
  "Blood Sugar Trend": "രക്തത്തിലെ പഞ്ചസാരയുടെ ട്രെൻഡ്",
  "Heart Rate & SpO2 Trend": "ഹൃദയമിടിപ്പും ഓക്സിജൻ നിലയും",
  "Today's Doses on Track": "ഇന്നത്തെ മരുന്നുകൾ കൃത്യമായി",
  "Next dose: Atorvastatin 10mg scheduled at 8:00 PM with dinner.": "അടുത്ത ഡോസ്: അറ്റോർവാസ്റ്റാറ്റിൻ 10mg രാത്രി 8:00 ന് അത്താഴത്തോടൊപ്പം.",
  "2 of 3 Taken": "3-ൽ 2 എണ്ണം കഴിച്ചു",
  "View Full Schedule →": "പൂർണ്ണ ഷെഡ്യൂൾ കാണുക →",
  "Telehealth Visit": "ടെലിഹെൽത്ത് സന്ദർശനം",
  "Dr. Joseph (Cardiology)": "ഡോ. ജോസഫ് (കാർഡിയോളജി)",
  "Today at 3:00 PM · Video consultation follow-up for blood pressure review.": "ഇന്ന് വൈകുന്നേരം 3:00 ന് · രക്തസമ്മർദ്ദ പരിശോധനയ്ക്കുള്ള വീഡിയോ കൺസൾട്ടേഷൻ.",
  "Confirmed": "സ്ഥിരീകരിച്ചു",
  "Consultation Details →": "കൺസൾട്ടേഷൻ വിവരങ്ങൾ →",
  "Smart Alerts": "സ്മാർട്ട് അറിയിപ്പുകൾ",
  "Home Safety Verified": "വീട്ടിലെ സുരക്ഷ ഉറപ്പാക്കി",
  "Wearable device heartbeat confirmed 4m ago. Battery at 88%. No fall or SOS events.": "സ്മാർട്ട് വാച്ച് സിഗ്നൽ 4 മിനിറ്റ് മുമ്പ് ലഭിച്ചു. ബാറ്ററി 88%. വീഴ്ചയോ അടിയന്തര സാഹചര്യങ്ങളോ ഇല്ല.",
  "Check Notifications →": "അറിയിപ്പുകൾ പരിശോധിക്കുക →",
  "Safety Status": "സുരക്ഷാ നില",
  "Fall Detection Active": "വീഴ്ച കണ്ടെത്തൽ സജീവം",
  "Active Telemetry Stream": "തത്സമയ ആരോഗ്യ ഡാറ്റാ സ്ട്രീം",
  "Battery 88%": "ബാറ്ററി 88%",
  "Medication Adherence & Schedule": "മരുന്ന് കഴിക്കുന്ന വിവരങ്ങളും ഷെഡ്യൂളും",
  "Track senior daily prescriptions, adherence timestamps and dosage reminders": "മുതിർന്നവരുടെ ദൈനംദിന മരുന്നുകൾ, കഴിച്ച സമയം, ഡോസ് ഓർമ്മപ്പെടുത്തലുകൾ എന്നിവ കാണുക",
  "Morning (8:00 AM)": "രാവിലെ (8:00 AM)",
  "Afternoon (1:00 PM)": "ഉച്ചയ്ക്ക് (1:00 PM)",
  "Evening / Night (8:00 PM)": "രാത്രി (8:00 PM)",
  "Taken at 8:05 AM": "രാവിലെ 8:05 ന് കഴിച്ചു",
  "Taken at 1:15 PM": "ഉച്ചയ്ക്ക് 1:15 ന് കഴിച്ചു",
  "Scheduled with dinner": "അത്താഴത്തോടൊപ്പം നിശ്ചയിച്ചിരിക്കുന്നു",
  "Mark as taken": "കഴിച്ചതായി അടയാളപ്പെടുത്തുക",
  "Mark Taken": "കഴിച്ചതായി അടയാളപ്പെടുത്തുക",
  "Taken": "കഴിച്ചു",
  "Due": "കഴിക്കാനുണ്ട്",
  "Upcoming": "വരാനിരിക്കുന്നത്",
  "Pending": "തീർപ്പാക്കാത്തത്",
  "Completed": "പൂർത്തിയായി",
  "Missed": "വിട്ടുപോയി",
  "Care Network & Emergency Contacts": "കെയർ നെറ്റ്‌വർക്കും അടിയന്തര കോൺടാക്റ്റുകളും",
  "Direct voice calling, relationship directory and designated priority responder": "നേരിട്ടുള്ള വോയ്സ് കോളിംഗ്, ബന്ധുക്കളുടെ പട്ടിക, പ്രധാന റെസ്‌പോണ്ടർ",
  "+ Add Contact": "+ കോൺടാക്റ്റ് ചേർക്കുക",
  "Add Care & Emergency Contact": "കെയർ & എമർജൻസി കോൺടാക്റ്റ് ചേർക്കുക",
  "Full Name *": "പൂർണ്ണമായ പേര് *",
  "Relationship / Role *": "ബന്ധം / റോൾ *",
  "Phone Number *": "ഫോൺ നമ്പർ *",
  "Contact Category": "കോൺടാക്റ്റ് വിഭാഗം",
  "Mark as Primary Emergency Responder": "പ്രധാന അടിയന്തര റെസ്‌പോണ്ടറായി അടയാളപ്പെടുത്തുക",
  "Save Contact": "കോൺടാക്റ്റ് സേവ് ചെയ്യുക",
  "Call": "വിളിക്കുക",
  "Voice Call": "വോയ്സ് കോൾ",
  "Primary Responder": "പ്രധാന റെസ്‌പോണ്ടർ",
  "Daughter": "മകൾ",
  "Primary Physician": "പ്രധാന ഡോക്ടർ",
  "Elder Care Nurse": "മുതിർന്നവരുടെ നഴ്സ്",
  "Ambulance & Emergency": "ആംബുലൻസും അടിയന്തര സേവനങ്ങളും",
  "Governance, Verifications & Audit Records": "ഭരണം, പരിശോധനകൾ & ഓഡിറ്റ് രേഖകൾ",
  "System Overview": "സിസ്റ്റം അവലോകനം",
  "Total Registered Users": "ആകെ രജിസ്റ്റർ ചെയ്ത ഉപയോക്താക്കൾ",
  "Pending Verifications": "തീർപ്പാക്കാത്ത പരിശോധനകൾ",
  "Today's Appointments": "ഇന്നത്തെ അപ്പോയിന്റ്മെന്റുകൾ",
  "Active SOS Emergencies": "സജീവമായ അടിയന്തര സാഹചര്യങ്ങൾ",
  "Verification Queue": "പരിശോധനാ നിര",
  "Doctor & Caregiver Credential Verification": "ഡോക്ടർമാരുടെയും പരിപാലകരുടെയും സർട്ടിഫിക്കറ്റ് പരിശോധന",
  "Applicant Name": "അപേക്ഷകന്റെ പേര്",
  "Profession / Role": "തൊഴിൽ / റോൾ",
  "License / Reg No": "ലൈസൻസ് / രജിസ്ട്രേഷൻ നമ്പർ",
  "Submitted Date": "സമർപ്പിച്ച തീയതി",
  "Status": "സ്റ്റാറ്റസ്",
  "Actions": "നടപടികൾ",
  "Approve": "അംഗീകരിക്കുക",
  "Reject": "നിരസിക്കുക",
  "View Certificate": "സർട്ടിഫിക്കറ്റ് കാണുക",
  "Approved": "അംഗീകരിച്ചു",
  "Rejected": "നിരസിച്ചു",
  "Under Review": "പരിശോധനയിലാണ്",
  "User Governance": "ഉപയോക്തൃ ഭരണം",
  "Audit Logs & Security Trail": "ഓഡിറ്റ് ലോഗുകളും സുരക്ഷാ രേഖകളും",
  "Timestamp": "സമയം",
  "User": "ഉപയോക്താവ്",
  "Event": "ഇവന്റ്",
  "IP Address": "IP വിലാസം",
  "Severity": "തീവ്രത",
  "Today's Appointments & Consultations": "ഇന്നത്തെ അപ്പോയിന്റ്മെന്റുകളും കൺസൾട്ടേഷനുകളും",
  "Patient Telemetry Queue": "രോഗികളുടെ ആരോഗ്യ ഡാറ്റാ നിര",
  "Patient Name": "രോഗിയുടെ പേര്",
  "Age / Gender": "പ്രായം / ലിംഗം",
  "Vitals Status": "ആരോഗ്യനില",
  "Scheduled Time": "ഷെഡ്യൂൾ ചെയ്ത സമയം",
  "Consultation Type": "കൺസൾട്ടേഷൻ തരം",
  "Start Video Consultation": "വീഡിയോ കൺസൾട്ടേഷൻ ആരംഭിക്കുക",
  "Join Consultation": "കൺസൾട്ടേഷനിൽ ചേരുക",
  "View Records": "രേഖകൾ കാണുക",
  "Issue Prescription": "പ്രിസ്ക്രിപ്ഷൻ നൽകുക",
  "My Health Summary": "എന്റെ ആരോഗ്യ സംഗ്രഹം",
  "Today's Care Plan": "ഇന്നത്തെ ആരോഗ്യ പരിപാലന പ്ലാൻ",
  "Need Help?": "സഹായം ആവശ്യമുണ്ടോ?",
  "Emergency SOS Button": "അടിയന്തര SOS ബട്ടൺ",
  "Press and hold to notify emergency contacts and dispatch help.": "അടിയന്തര കോൺടാക്റ്റുകളെ അറിയിക്കാൻ ബട്ടൺ അമർത്തിപ്പിടിക്കുക.",
  "Trigger Emergency SOS": "അടിയന്തര SOS നൽകുക",
  "Caregiver Notification": "പരിപാലക അറിയിപ്പുകൾ",
  "Allow daily check-in notifications to your assigned caregiver.": "നിങ്ങൾക്കുള്ള പരിപാലകന് പ്രതിദിന അറിയിപ്പുകൾ നൽകാൻ അനുവദിക്കുക.",
  "Sign In to Care+": "കെയർ+ ലേക്ക് സൈൻ ഇൻ ചെയ്യുക",
  "Select your workspace and enter your credentials.": "നിങ്ങളുടെ വർക്ക്സ്പേസ് തിരഞ്ഞെടുത്ത് ലോഗിൻ വിവരങ്ങൾ നൽകുക.",
  "Username or Email": "ഉപയോക്തൃനാമം അല്ലെങ്കിൽ ഇമെയിൽ",
  "Password": "പാസ്‌വേഡ്",
  "Show/Hide": "കാണിക്കുക/മറയ്ക്കുക",
  "Sign In →": "സൈൻ ഇൻ ചെയ്യുക →",
  "Cancel": "റദ്ദാക്കുക",
  "Save": "സേവ് ചെയ്യുക",
  "Close": "അടയ്ക്കുക",
  "Dismiss": "അടയ്ക്കുക",
  "Switch Care+ Role": "കെയർ+ റോൾ മാറ്റുക",
  "Select a dashboard to view the specialized interface for that role.": "ആ റോളിനായുള്ള പ്രത്യേക ഇന്റർഫേസ് കാണാൻ ഡാഷ്‌ബോർഡ് തിരഞ്ഞെടുക്കുക.",
  "Speak naturally to navigate across health vitals, medication schedule, or family contacts.": "ആരോഗ്യ വിവരങ്ങൾ, മരുന്ന് ഷെഡ്യൂൾ, കോൺടാക്റ്റുകൾ എന്നിവയിലേക്ക് നാവിഗേറ്റ് ചെയ്യാൻ സംസാരിക്കുക.",
  "Listening...": "കേൾക്കുന്നു...",
  "Start Speaking": "സംസാരിക്കാൻ ആരംഭിക്കുക",
  "Stop Listening": "നിർത്തുക",
  "Font Size Scaling": "ഫോണ്ട് വലുപ്പം മാറ്റൽ",
  "Large (A+)": "വലുത് (A+)",
  "Extra Large (A++)": "വളരെ വലുത് (A++)",
  "High Contrast Theme": "ഹൈ-കോൺട്രാസ്റ്റ് തീം",
  "Enhanced contrast for seniors with low vision": "കാഴ്ചക്കുറവുള്ള മുതിർന്നവർക്കായി ഉയർന്ന കോൺട്രാസ്റ്റ്",
  "Large Button Targets": "വലിയ ബട്ടണുകൾ",
  "Easy-to-tap touch areas for older adults": "മുതിർന്നവർക്ക് എളുപ്പത്തിൽ അമർത്താൻ വലിയ ടച്ച് ബട്ടണുകൾ",
  "Voice Assistant Auto-Prompt": "വോയ്സ് അസിസ്റ്റന്റ് ഓട്ടോ-പ്രോംപ്റ്റ്",
  "Automatic voice listening when navigating": "നാവിഗേറ്റ് ചെയ്യുമ്പോൾ തനിയെ വോയ്സ് കേൾക്കൽ",
  "Save Accessibility Preferences": "പ്രവേശനക്ഷമതാ ക്രമീകരണങ്ങൾ സേവ് ചെയ്യുക"
},

  init: function () {
    var savedLang = localStorage.getItem('careplus_lang') || 'en';
    this.currentLang = savedLang;
    this.applyLanguage(savedLang);

    var self = this;
    document.querySelectorAll('.lang-selector, #langSelect').forEach(function (sel) {
      sel.value = savedLang;
      sel.onchange = function () {
        self.setLanguage(sel.value);
        if (typeof showToast === 'function') {
          showToast(sel.value === 'ml' ? 'ഭാഷ മലയാളത്തിലേക്ക് മാറ്റി.' : 'Language switched to English.');
        }
      };
    });
  },

  setLanguage: function (lang) {
    if (lang !== 'en' && lang !== 'ml') lang = 'en';
    this.currentLang = lang;
    localStorage.setItem('careplus_lang', lang);
    document.documentElement.lang = lang;
    this.applyLanguage(lang);

    // Sync all dropdowns on page
    document.querySelectorAll('.lang-selector, #langSelect').forEach(function (sel) {
      sel.value = lang;
    });
  },

  applyLanguage: function (lang) {
    var self = this;
    var isML = (lang === 'ml');

    // Sort keys by descending length to match longest phrases first
    var sortedKeys = Object.keys(self.textMap).sort(function (a, b) {
      return b.length - a.length;
    });

    function translateString(str) {
      if (!str) return str;
      var trimmed = str.trim();
      if (self.textMap[trimmed]) {
        return str.replace(trimmed, self.textMap[trimmed]);
      }
      // Substring check for phrases
      var res = str;
      for (var i = 0; i < sortedKeys.length; i++) {
        var k = sortedKeys[i];
        if (res.indexOf(k) !== -1) {
          res = res.split(k).join(self.textMap[k]);
        }
      }
      return res;
    }

    function walkNode(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        var val = node.nodeValue;
        if (!val || !val.trim()) return;

        if (isML) {
          if (node._origText === undefined) {
            node._origText = val;
          }
          node.nodeValue = translateString(node._origText);
        } else {
          if (node._origText !== undefined) {
            node.nodeValue = node._origText;
          }
        }
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        var tag = node.tagName.toUpperCase();
        if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'CODE') return;

        // Translate placeholders
        if (node.placeholder) {
          if (isML) {
            if (node._origPlaceholder === undefined) node._origPlaceholder = node.placeholder;
            node.placeholder = translateString(node._origPlaceholder);
          } else if (node._origPlaceholder !== undefined) {
            node.placeholder = node._origPlaceholder;
          }
        }

        // Translate input button/submit values
        if (tag === 'INPUT' && (node.type === 'button' || node.type === 'submit')) {
          if (isML) {
            if (node._origValue === undefined) node._origValue = node.value;
            node.value = translateString(node._origValue);
          } else if (node._origValue !== undefined) {
            node.value = node._origValue;
          }
        }

        // Process children
        for (var i = 0; i < node.childNodes.length; i++) {
          walkNode(node.childNodes[i]);
        }
      }
    }

    var root = document.getElementById('app-root') || document.body;
    walkNode(root);

    // Also translate universal modals
    document.querySelectorAll('.modal-overlay').forEach(function (modal) {
      walkNode(modal);
    });
  }
};

function initI18n() {
  CarePlusI18n.init();
}

/* ==========================================================================
   ACCESSIBILITY SYSTEM (ELDER-FRIENDLY & REUSABLE)
   ========================================================================== */
var CarePlusA11y = {
  settings: {
    textSize: 'normal', // 'sm', 'normal', 'lg', 'xl'
    largeButtons: false,
    highContrast: false,
    reduceMotion: false,
    simpleNav: false
  },

  init: function () {
    var saved = localStorage.getItem('careplus_a11y');
    if (saved) {
      try {
        this.settings = Object.assign(this.settings, JSON.parse(saved));
      } catch (e) {
        console.error('Error loading a11y settings', e);
      }
    }
    this.applySettings();
    this.bindEvents();
  },

  save: function () {
    localStorage.setItem('careplus_a11y', JSON.stringify(this.settings));
    this.applySettings();
  },

  applySettings: function () {
    var s = this.settings;
    var html = document.documentElement;
    var body = document.body;

    // Font size scaling
    html.classList.remove('font-size-sm', 'font-size-normal', 'font-size-lg', 'font-size-xl');
    html.classList.add('font-size-' + s.textSize);

    // Boolean classes on body
    body.classList.toggle('high-contrast', !!s.highContrast);
    body.classList.toggle('large-buttons', !!s.largeButtons);
    body.classList.toggle('reduce-motion', !!s.reduceMotion);
    body.classList.toggle('simple-nav', !!s.simpleNav);

    // Update modal controls if open
    var hcCheck = document.getElementById('a11yHighContrast');
    if (hcCheck) hcCheck.checked = !!s.highContrast;

    var lbCheck = document.getElementById('a11yLargeButtons');
    if (lbCheck) lbCheck.checked = !!s.largeButtons;

    var rmCheck = document.getElementById('a11yReduceMotion');
    if (rmCheck) rmCheck.checked = !!s.reduceMotion;

    var snCheck = document.getElementById('a11ySimpleNav');
    if (snCheck) snCheck.checked = !!s.simpleNav;

    var textSizeDisplay = document.getElementById('a11yTextSizeDisplay');
    if (textSizeDisplay) {
      var labels = { sm: 'Small (85%)', normal: 'Default (100%)', lg: 'Large (120%)', xl: 'Extra Large (140%)' };
      textSizeDisplay.textContent = labels[s.textSize] || s.textSize;
    }
  },

  increaseTextSize: function () {
    if (this.settings.textSize === 'sm') this.settings.textSize = 'normal';
    else if (this.settings.textSize === 'normal') this.settings.textSize = 'lg';
    else if (this.settings.textSize === 'lg') this.settings.textSize = 'xl';
    this.save();
    showToast('Text size increased.');
  },

  decreaseTextSize: function () {
    if (this.settings.textSize === 'xl') this.settings.textSize = 'lg';
    else if (this.settings.textSize === 'lg') this.settings.textSize = 'normal';
    else if (this.settings.textSize === 'normal') this.settings.textSize = 'sm';
    this.save();
    showToast('Text size decreased.');
  },

  resetTextSize: function () {
    this.settings.textSize = 'normal';
    this.save();
    showToast('Text size reset to default.');
  },

  toggleHighContrast: function (val) {
    this.settings.highContrast = typeof val === 'boolean' ? val : !this.settings.highContrast;
    this.save();
    showToast(this.settings.highContrast ? 'High Contrast mode enabled.' : 'High Contrast mode disabled.');
  },

  toggleLargeButtons: function (val) {
    this.settings.largeButtons = typeof val === 'boolean' ? val : !this.settings.largeButtons;
    this.save();
    showToast(this.settings.largeButtons ? 'Large Buttons mode enabled.' : 'Large Buttons mode disabled.');
  },

  toggleReduceMotion: function (val) {
    this.settings.reduceMotion = typeof val === 'boolean' ? val : !this.settings.reduceMotion;
    this.save();
    showToast(this.settings.reduceMotion ? 'Reduce Motion enabled.' : 'Reduce Motion disabled.');
  },

  toggleSimpleNav: function (val) {
    this.settings.simpleNav = typeof val === 'boolean' ? val : !this.settings.simpleNav;
    this.save();
    showToast(this.settings.simpleNav ? 'Simple Navigation enabled.' : 'Simple Navigation disabled.');
  },

  bindEvents: function () {
    var self = this;

    // Trigger buttons
    document.querySelectorAll('[data-action="open-a11y"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        self.openModal();
      });
    });

    var incBtn = document.getElementById('a11yIncreaseFont');
    if (incBtn) incBtn.addEventListener('click', function () { self.increaseTextSize(); });

    var decBtn = document.getElementById('a11yDecreaseFont');
    if (decBtn) decBtn.addEventListener('click', function () { self.decreaseTextSize(); });

    var resetBtn = document.getElementById('a11yResetFont');
    if (resetBtn) resetBtn.addEventListener('click', function () { self.resetTextSize(); });

    var hcToggle = document.getElementById('a11yHighContrast');
    if (hcToggle) hcToggle.addEventListener('change', function () { self.toggleHighContrast(hcToggle.checked); });

    var lbToggle = document.getElementById('a11yLargeButtons');
    if (lbToggle) lbToggle.addEventListener('change', function () { self.toggleLargeButtons(lbToggle.checked); });

    var rmToggle = document.getElementById('a11yReduceMotion');
    if (rmToggle) rmToggle.addEventListener('change', function () { self.toggleReduceMotion(rmToggle.checked); });

    var snToggle = document.getElementById('a11ySimpleNav');
    if (snToggle) snToggle.addEventListener('change', function () { self.toggleSimpleNav(snToggle.checked); });
  },

  openModal: function () {
    var modal = document.getElementById('a11yModal');
    if (!modal) return;
    this.applySettings();
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  },

  closeModal: function () {
    var modal = document.getElementById('a11yModal');
    if (!modal) return;
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  }
};

function initAccessibility() {
  CarePlusA11y.init();
}

/* ==========================================================================
   VOICE NAVIGATION ASSISTANT (MEMBER 4 SCOPE)
   ========================================================================== */
var CarePlusVoiceBridge = {
  isListening: false,
  customVoiceHandler: null,

  init: function () {
    var self = this;
    window.CarePlusVoiceBridge = this;
    window.CarePlusVoice = {
      openModal: function () { self.openModal(); },
      closeModal: function () { self.closeModal(); },
      handleCommand: function (cmd) { self.executeCommand(cmd); },
      registerVoiceHandler: function (fn) { self.customVoiceHandler = fn; },
      callContact: function (name) { self.callContact(name); },
      openNotifications: function () { self.openNotifications(); },
      openAppointments: function () { self.openAppointments(); },
      openHealthUpdates: function () { self.openHealthUpdates(); },
      changeLanguage: function (lang) { self.changeLanguage(lang); },
      openAccessibility: function () { self.openAccessibility(); },
      openAdminSection: function (sec) { self.openAdminSection(sec); }
    };

    document.querySelectorAll('[data-action="open-voice"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        self.openModal();
      });
    });

    // Handle voice command chip clicks (simulating voice recognition)
    document.querySelectorAll('.voice-chip[data-command]').forEach(function (chip) {
      chip.addEventListener('click', function () {
        var cmd = chip.getAttribute('data-command');
        self.executeCommand(cmd);
      });
    });
  },

  openModal: function () {
    var modal = document.getElementById('voiceModal');
    if (!modal) return;
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  },

  closeModal: function () {
    var modal = document.getElementById('voiceModal');
    if (!modal) return;
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  },

  callContact: function (nameOrId) {
    if (window.CarePlusContacts && typeof CarePlusContacts.getContacts === 'function') {
      var contacts = CarePlusContacts.getContacts();
      var target = null;
      var q = (nameOrId || '').toLowerCase().trim();
      for (var i = 0; i < contacts.length; i++) {
        if (contacts[i].id === nameOrId || contacts[i].name.toLowerCase().indexOf(q) !== -1 || (contacts[i].relation && contacts[i].relation.toLowerCase().indexOf(q) !== -1)) {
          target = contacts[i];
          break;
        }
      }
      if (target) {
        CarePlusContacts.call(target.name, target.phone);
        return;
      }
    }
    showToast('Connecting call to ' + (nameOrId || 'Contact') + '...');
  },

  openNotifications: function () {
    if (typeof window.switchFamilyTab === 'function') {
      window.switchFamilyTab('notifications');
    }
    var sec = document.getElementById('notificationsSection') || document.getElementById('notificationsTab');
    if (sec) sec.scrollIntoView({ behavior: 'smooth' });
    var notifBtn = document.getElementById('notifBtn');
    if (notifBtn && !sec) notifBtn.click();
    showToast('Opening notifications...');
  },

  openAppointments: function () {
    if (typeof window.switchFamilyTab === 'function') {
      window.switchFamilyTab('medications');
    }
    var apptSec = document.getElementById('appointmentSection');
    if (apptSec) {
      apptSec.scrollIntoView({ behavior: 'smooth' });
    }
    showToast('Displaying appointment details...');
  },

  openHealthUpdates: function () {
    if (typeof window.switchFamilyTab === 'function') {
      window.switchFamilyTab('overview');
    }
    var vitalsSec = document.getElementById('vitalsSection') || document.getElementById('healthUpdatesSection');
    if (vitalsSec) {
      vitalsSec.scrollIntoView({ behavior: 'smooth' });
    }
    showToast('Displaying health updates & vitals...');
  },

  changeLanguage: function (lang) {
    if (window.CarePlusI18n && typeof CarePlusI18n.setLanguage === 'function') {
      CarePlusI18n.setLanguage(lang);
      showToast(lang === 'ml' ? 'ഭാഷ മലയാളത്തിലേക്ക് മാറ്റി.' : 'Language changed to English.');
    }
  },

  openAccessibility: function () {
    if (window.CarePlusA11y && typeof CarePlusA11y.openModal === 'function') {
      CarePlusA11y.openModal();
    }
  },

  openAdminSection: function (sectionId) {
    var sec = document.getElementById(sectionId);
    if (sec) {
      sec.scrollIntoView({ behavior: 'smooth' });
      showToast('Navigating to ' + sectionId.replace('Section', '') + '...');
    }
  },

  executeCommand: function (commandText) {
    if (!commandText) return;
    var text = commandText.toLowerCase().trim();

    // If speech engine registered an external handler, delegate to it first
    if (typeof this.customVoiceHandler === 'function') {
      try {
        var handled = this.customVoiceHandler(text);
        if (handled) return;
      } catch (e) {
        console.warn('Custom voice handler error:', e);
      }
    }

    this.closeModal();

    // Built-in navigation / action routing
    if (text.indexOf('health') !== -1 || text.indexOf('vital') !== -1) {
      this.openHealthUpdates();
    } else if (text.indexOf('notification') !== -1 || text.indexOf('alert') !== -1) {
      this.openNotifications();
    } else if (text.indexOf('call') !== -1 || text.indexOf('daughter') !== -1 || text.indexOf('doctor') !== -1) {
      var contactKey = 'Anu';
      if (text.indexOf('doctor') !== -1 || text.indexOf('joseph') !== -1) contactKey = 'Dr. Joseph';
      else if (text.indexOf('rahul') !== -1 || text.indexOf('son') !== -1) contactKey = 'Rahul';
      else if (text.indexOf('mary') !== -1 || text.indexOf('caregiver') !== -1) contactKey = 'Mary';
      this.callContact(contactKey);
    } else if (text.indexOf('appointment') !== -1 || text.indexOf('consultation') !== -1) {
      this.openAppointments();
    } else if (text.indexOf('malayalam') !== -1) {
      this.changeLanguage('ml');
    } else if (text.indexOf('english') !== -1) {
      this.changeLanguage('en');
    } else if (text.indexOf('contrast') !== -1) {
      CarePlusA11y.toggleHighContrast();
    } else if (text.indexOf('button') !== -1) {
      CarePlusA11y.toggleLargeButtons();
    } else if (text.indexOf('user') !== -1) {
      this.openAdminSection('usersSection');
    } else if (text.indexOf('verification') !== -1) {
      this.openAdminSection('verificationsSection');
    } else if (text.indexOf('consent') !== -1 || text.indexOf('privacy') !== -1) {
      this.openAdminSection('consentSection');
    } else {
      showToast('🎙 Voice Command: "' + commandText + '" processed.');
    }
  }
};

function initVoiceBridge() {
  CarePlusVoiceBridge.init();
}

/* ==========================================================================
   AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC - MEMBER 4 SCOPE)
   ========================================================================== */
var CarePlusAuth = {
  roles: {
    senior: { title: 'Senior Citizen', url: 'patient-dashboard.html' },
    doctor: { title: 'Doctor', url: 'doctor-dashboard.html' },
    family: { title: 'Family Member', url: 'family/family-dashboard.html' },
    caregiver: { title: 'Caregiver', url: 'family/family-dashboard.html' },
    volunteer: { title: 'Volunteer', url: 'family/family-dashboard.html' },
    admin: { title: 'Administrator', url: 'admin/admin-dashboard.html' }
  },

  init: function () {
    var self = this;
    document.querySelectorAll('[data-action="open-role-switcher"]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        self.openModal();
      });
    });

    document.querySelectorAll('.role-card[data-role]').forEach(function (card) {
      card.addEventListener('click', function () {
        var role = card.getAttribute('data-role');
        self.switchRole(role);
      });
    });
  },

  getCurrentUser: function () {
    var role = localStorage.getItem('careplus_current_role') || 'family';
    var email = localStorage.getItem('careplus_user_email') || (role === 'admin' ? 'admin@careplus.org' : 'priya.suresh@example.com');
    var name = localStorage.getItem('careplus_user_name') || (role === 'admin' ? 'Administrator' : 'Priya Suresh');
    return { role: role, name: name, email: email };
  },

  login: function (roleKey, email, name) {
    if (this.roles[roleKey]) {
      localStorage.setItem('careplus_current_role', roleKey);
      if (email) localStorage.setItem('careplus_user_email', email);
      if (name) localStorage.setItem('careplus_user_name', name);
    }
  },

  logout: function () {
    localStorage.removeItem('careplus_current_role');
    localStorage.removeItem('careplus_user_email');
    localStorage.removeItem('careplus_user_name');
    var isSubdir = window.location.pathname.indexOf('/family/') !== -1 || window.location.pathname.indexOf('/admin/') !== -1;
    window.location.href = isSubdir ? '../index.html' : 'index.html';
  },

  enforceAdminGuard: function () {
    var path = window.location.pathname;
    var isAdminPage = path.indexOf('/admin/') !== -1 || path.indexOf('admin-dashboard.html') !== -1;
    if (!isAdminPage) return;

    var currentRole = localStorage.getItem('careplus_current_role');
    // If a user is logged in with another role (e.g. family or senior), restrict access:
    if (currentRole && currentRole !== 'admin') {
      alert('Access Restricted: You are currently signed in as ' + (this.roles[currentRole] ? this.roles[currentRole].title : currentRole) + '. Administrator privileges are required to view the Admin Console.');
      var isSubdir = path.indexOf('/admin/') !== -1;
      window.location.href = isSubdir ? '../family/family-dashboard.html' : 'family/family-dashboard.html';
    } else {
      localStorage.setItem('careplus_current_role', 'admin');
    }
  },

  openModal: function () {
    var modal = document.getElementById('roleSwitcherModal');
    if (!modal) return;
    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  },

  closeModal: function () {
    var modal = document.getElementById('roleSwitcherModal');
    if (!modal) return;
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  },

  switchRole: function (roleKey) {
    var role = this.roles[roleKey];
    if (!role) return;

    localStorage.setItem('careplus_current_role', roleKey);

    var isSubdir = window.location.pathname.indexOf('/family/') !== -1 || window.location.pathname.indexOf('/admin/') !== -1;
    var targetUrl = role.url;

    if (isSubdir) {
      targetUrl = '../' + targetUrl;
    }

    window.location.href = targetUrl;
  }
};

function initRoleSwitcher() {
  CarePlusAuth.init();
}

/* ==========================================================================
   FAMILY & EMERGENCY CONTACTS MANAGEMENT (MEMBER 4 SCOPE)
   ========================================================================== */
var CarePlusContacts = {
  storageKey: 'careplus_family_contacts',

  defaultContacts: [
    {
      id: 'contact_1',
      name: 'Anu Suresh',
      relation: 'Daughter',
      roleNote: 'Primary Emergency Responder',
      phone: '+91 98471 23456',
      type: 'family',
      isPriority: true,
      initials: 'AS'
    },
    {
      id: 'contact_2',
      name: 'Rahul Suresh',
      relation: 'Son',
      roleNote: 'Family Member',
      phone: '+91 94472 34567',
      type: 'family',
      isPriority: false,
      initials: 'RS'
    },
    {
      id: 'contact_3',
      name: 'Dr. Joseph',
      relation: 'Primary Physician',
      roleNote: 'Cardiology',
      phone: '+91 98460 11223',
      type: 'doctor',
      isPriority: false,
      initials: 'DJ'
    },
    {
      id: 'contact_4',
      name: 'Mary Varghese',
      relation: 'Caregiver',
      roleNote: 'Daily Home Assistance',
      phone: '+91 97455 66778',
      type: 'caregiver',
      isPriority: false,
      initials: 'MV'
    }
  ],

  getContacts: function () {
    var raw = localStorage.getItem(this.storageKey);
    if (!raw) {
      this.saveContacts(this.defaultContacts);
      return this.defaultContacts.slice();
    }
    try {
      var parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    } catch (e) {}
    return this.defaultContacts.slice();
  },

  saveContacts: function (list) {
    localStorage.setItem(this.storageKey, JSON.stringify(list));
  },

  isValidPhoneNumber: function (phone) {
    if (!phone || typeof phone !== 'string') return false;
    var trimmed = phone.trim();
    var digitsOnly = trimmed.replace(/\D/g, '');
    if (digitsOnly.length < 7 || digitsOnly.length > 15) return false;
    return /^(\+?[0-9\s\-()]{7,25})$/.test(trimmed);
  },

  computeInitials: function (name) {
    if (!name) return 'CP';
    var parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  },

  addContact: function (contact) {
    var list = this.getContacts();
    var newId = 'contact_' + Date.now();
    var newContact = {
      id: newId,
      name: contact.name.trim(),
      relation: contact.relation.trim(),
      roleNote: contact.roleNote || (contact.isPriority ? 'Primary Emergency Responder' : ''),
      phone: contact.phone.trim(),
      type: contact.type || 'family',
      isPriority: !!contact.isPriority,
      initials: this.computeInitials(contact.name)
    };
    list.unshift(newContact);
    this.saveContacts(list);
    this.render();
    return newContact;
  },

  updateContact: function (id, updated) {
    var list = this.getContacts();
    for (var i = 0; i < list.length; i++) {
      if (list[i].id === id) {
        list[i].name = updated.name.trim();
        list[i].relation = updated.relation.trim();
        list[i].phone = updated.phone.trim();
        list[i].type = updated.type || list[i].type;
        list[i].isPriority = !!updated.isPriority;
        list[i].roleNote = updated.roleNote || (list[i].isPriority ? 'Primary Emergency Responder' : '');
        list[i].initials = this.computeInitials(updated.name);
        break;
      }
    }
    this.saveContacts(list);
    this.render();
  },

  deleteContact: function (id) {
    var list = this.getContacts().filter(function (c) { return c.id !== id; });
    this.saveContacts(list);
    this.render();
    showToast('Contact removed successfully.');
  },

  call: function (name, phone) {
    var cleanPhone = (phone || '').replace(/[^0-9+]/g, '');
    showToast('Connecting one-tap call to ' + (name || 'Contact') + ' (' + (phone || '') + ')...');
    if (cleanPhone) {
      setTimeout(function () {
        window.location.href = 'tel:' + cleanPhone;
      }, 300);
    }
  },

  voiceCall: function (name) {
    CarePlusVoiceBridge.openModal();
    showToast('🎙 Initiating hands-free voice call with ' + (name || 'Contact') + '...');
  },

  openModal: function (contactId) {
    var modal = document.getElementById('contactModal');
    var form = document.getElementById('contactForm');
    var titleEl = document.getElementById('contactModalTitle');
    var submitBtn = document.getElementById('contactSubmitBtn');
    if (!modal || !form) return;

    if (contactId) {
      var contacts = this.getContacts();
      var c = contacts.find(function (item) { return item.id === contactId; });
      if (c) {
        if (titleEl) titleEl.textContent = 'Edit Care Contact';
        if (submitBtn) submitBtn.textContent = 'Update Contact';
        if (form.elements['contactId']) form.elements['contactId'].value = c.id;
        if (form.elements['contactName']) form.elements['contactName'].value = c.name;
        if (form.elements['contactRelation']) form.elements['contactRelation'].value = c.relation;
        if (form.elements['contactPhone']) form.elements['contactPhone'].value = c.phone;
        if (form.elements['contactType']) form.elements['contactType'].value = c.type;
        if (form.elements['contactPriority']) form.elements['contactPriority'].checked = !!c.isPriority;
      }
    } else {
      if (titleEl) titleEl.textContent = 'Add Care & Emergency Contact';
      if (submitBtn) submitBtn.textContent = 'Save Contact';
      form.reset();
      if (form.elements['contactId']) form.elements['contactId'].value = '';
    }

    modal.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  },

  closeModal: function () {
    var modal = document.getElementById('contactModal');
    if (!modal) return;
    modal.classList.remove('is-open');
    document.body.style.overflow = '';
  },

  render: function () {
    var contacts = this.getContacts();
    var grid = document.getElementById('contactsGrid') || document.querySelector('.contacts-grid');
    var quickBar = document.getElementById('quickContactsBar') || document.querySelector('.quick-contacts-bar');
    var activeBadge = document.getElementById('activeRespondersBadge');
    var tabContactsBadge = document.getElementById('tabContactsBadge');
    var countBtn = document.getElementById('quickContactsCountBtn');

    if (activeBadge) {
      activeBadge.textContent = contacts.length + ' Active Responders';
    }
    if (tabContactsBadge) {
      tabContactsBadge.textContent = contacts.length;
    }
    if (countBtn) {
      countBtn.innerHTML = 'View All ' + contacts.length + ' Contacts &rarr;';
    }

    // Helper for HTML escaping
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // Render full contacts grid
    if (grid) {
      if (contacts.length === 0) {
        grid.innerHTML =
          '<div class="empty-state" style="grid-column: 1 / -1; padding: var(--space-6) var(--space-4);">' +
            '<div class="empty-state__icon accent-icon-blue">' +
              '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>' +
            '</div>' +
            '<h3 class="empty-state__title">No Contacts Saved</h3>' +
            '<p class="empty-state__desc">Add your family members, emergency responders, or doctors for one-tap calling and elder safety.</p>' +
            '<button class="btn btn-primary" data-action="open-add-contact" style="margin-top: var(--space-3);">+ Add First Contact</button>' +
          '</div>';
      } else {
        var gridHtml = '';
        contacts.forEach(function (c) {
          var cleanPhone = (c.phone || '').replace(/[^0-9+]/g, '');
          var typeLabel = c.type === 'doctor' ? 'Doctor' : (c.type === 'caregiver' ? 'Caregiver' : (c.type === 'emergency' ? 'Emergency' : 'Family'));
          gridHtml +=
            '<div class="contact-card" data-id="' + c.id + '">' +
              '<div>' +
                '<div class="contact-card__header">' +
                  '<div class="contact-card__avatar">' + escapeHtml(c.initials) + '</div>' +
                  '<div style="flex:1;">' +
                    '<div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:4px;">' +
                      '<h3 class="contact-card__name" style="margin:0;">' + escapeHtml(c.name) + '</h3>' +
                      (c.isPriority ? '<span class="status-pill status-pill--danger" style="font-size:0.72rem; padding:2px 8px;">Priority Responder</span>' : '<span class="badge" style="background:#F1F5F9; color:#475569; font-size:0.72rem;">' + typeLabel + '</span>') +
                    '</div>' +
                    '<p class="contact-card__meta">' + escapeHtml(c.relation) + (c.roleNote ? ' &middot; ' + escapeHtml(c.roleNote) : '') + '</p>' +
                    '<p class="contact-card__phone">' + escapeHtml(c.phone) + '</p>' +
                  '</div>' +
                '</div>' +
              '</div>' +
              '<div class="contact-card__buttons">' +
                '<a href="tel:' + cleanPhone + '" class="btn btn-primary btn-call" data-name="' + escapeHtml(c.name) + '" data-phone="' + escapeHtml(c.phone) + '">' +
                  '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>' +
                  '<span data-i18n="btn_call">Call</span>' +
                '</a>' +
                '<button class="btn btn-secondary btn-voice-call" data-name="' + escapeHtml(c.name) + '">' +
                  '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>' +
                  '<span data-i18n="btn_voice_call">Voice</span>' +
                '</button>' +
              '</div>' +
              '<div class="contact-card__manage-bar">' +
                '<button class="btn btn-outline btn-sm" data-action="edit-contact" data-id="' + c.id + '">' +
                  '<svg class="icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' +
                  '<span>Edit</span>' +
                '</button>' +
                '<button class="btn btn-outline btn-sm danger" data-action="delete-contact" data-id="' + c.id + '">' +
                  '<svg class="icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' +
                  '<span>Delete</span>' +
                '</button>' +
              '</div>' +
            '</div>';
        });
        grid.innerHTML = gridHtml;
      }
    }

    // Render quick contacts bar (on Overview tab)
    if (quickBar) {
      var quickItems = contacts.slice(0, 4);
      if (quickItems.length === 0) {
        quickBar.innerHTML = '<p style="color:var(--color-text-secondary); font-size:0.9rem; grid-column:1 / -1;">No quick contacts saved yet.</p>';
      } else {
        var quickHtml = '';
        quickItems.forEach(function (c) {
          var cleanPhone = (c.phone || '').replace(/[^0-9+]/g, '');
          quickHtml +=
            '<div class="quick-contact-pill">' +
              '<div class="quick-contact-pill__info">' +
                '<div class="contact-card__avatar" style="width:40px; height:40px; font-size:0.95rem;">' + escapeHtml(c.initials) + '</div>' +
                '<div>' +
                  '<h4 style="margin:0; font-size:0.98rem; font-weight:700;">' + escapeHtml(c.name) + '</h4>' +
                  '<p style="margin:0; font-size:0.8rem; color:var(--color-text-secondary);">' + escapeHtml(c.relation) + (c.isPriority ? ' &middot; Priority' : '') + '</p>' +
                '</div>' +
              '</div>' +
              '<div class="quick-contact-pill__actions">' +
                '<a href="tel:' + cleanPhone + '" class="btn btn-primary btn-sm btn-call" data-name="' + escapeHtml(c.name) + '" data-phone="' + escapeHtml(c.phone) + '" title="Call ' + escapeHtml(c.name) + '">' +
                  '<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>' +
                  '<span>Call</span>' +
                '</a>' +
                '<button class="btn btn-secondary btn-sm btn-voice-call" data-name="' + escapeHtml(c.name) + '" title="Voice Call ' + escapeHtml(c.name) + '">' +
                  '<svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>' +
                '</button>' +
              '</div>' +
            '</div>';
        });
        quickBar.innerHTML = quickHtml;
      }
    }

    this.bindDynamicEvents();
  },

  bindDynamicEvents: function () {
    var self = this;

    // Call buttons
    document.querySelectorAll('.btn-call').forEach(function (btn) {
      btn.onclick = function (e) {
        var name = btn.getAttribute('data-name') || 'Contact';
        var phone = btn.getAttribute('data-phone') || '';
        self.call(name, phone);
      };
    });

    // Voice call buttons
    document.querySelectorAll('.btn-voice-call').forEach(function (btn) {
      btn.onclick = function (e) {
        e.preventDefault();
        var name = btn.getAttribute('data-name') || 'Contact';
        self.voiceCall(name);
      };
    });

    // Edit contact buttons
    document.querySelectorAll('[data-action="edit-contact"]').forEach(function (btn) {
      btn.onclick = function () {
        var id = btn.getAttribute('data-id');
        self.openModal(id);
      };
    });

    // Delete contact buttons
    document.querySelectorAll('[data-action="delete-contact"]').forEach(function (btn) {
      btn.onclick = function () {
        var id = btn.getAttribute('data-id');
        if (confirm('Are you sure you want to remove this contact from the emergency responder list?')) {
          self.deleteContact(id);
        }
      };
    });

    // Add contact buttons
    document.querySelectorAll('[data-action="open-add-contact"]').forEach(function (btn) {
      btn.onclick = function (e) {
        e.preventDefault();
        self.openModal();
      };
    });
  },

  init: function () {
    var self = this;
    this.render();

    // Form submit listener
    var form = document.getElementById('contactForm');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var nameVal = form.elements['contactName'] ? form.elements['contactName'].value.trim() : '';
        var relationVal = form.elements['contactRelation'] ? form.elements['contactRelation'].value.trim() : '';
        var phoneVal = form.elements['contactPhone'] ? form.elements['contactPhone'].value.trim() : '';
        var typeVal = form.elements['contactType'] ? form.elements['contactType'].value : 'family';
        var priorityVal = form.elements['contactPriority'] ? form.elements['contactPriority'].checked : false;
        var existingId = form.elements['contactId'] ? form.elements['contactId'].value : '';

        if (!nameVal) {
          showToast('Please enter a contact name.');
          return;
        }

        if (!self.isValidPhoneNumber(phoneVal)) {
          showToast('Please enter a valid phone number (at least 7 digits, e.g. +91 98471 23456).');
          return;
        }

        var contactData = {
          name: nameVal,
          relation: relationVal,
          phone: phoneVal,
          type: typeVal,
          isPriority: priorityVal
        };

        if (existingId) {
          self.updateContact(existingId, contactData);
          showToast('Contact updated successfully!');
        } else {
          self.addContact(contactData);
          showToast('New care contact added successfully!');
        }

        self.closeModal();
      });
    }
  }
};

/* ==========================================================================
   SMART NOTIFICATIONS SYSTEM (MEMBER 4 SCOPE)
   ========================================================================== */
var CarePlusNotifications = {
  storageKey: 'careplus_notifications',

  defaultNotifications: [
    {
      id: 'notif_1',
      category: 'medication',
      title: 'Morning medication taken',
      desc: 'Anitha took Amlodipine 5mg on time.',
      time: '15 minutes ago',
      unread: true,
      iconType: 'medication'
    },
    {
      id: 'notif_2',
      category: 'appointment',
      title: 'Consultation today at 3:00 PM',
      desc: 'With Dr. Joseph (Cardiology). Telehealth room opens 10m early.',
      time: '1 hour ago',
      unread: true,
      iconType: 'appointment'
    },
    {
      id: 'notif_3',
      category: 'health',
      title: 'Vitals stable',
      desc: 'Morning blood pressure reading 120/80 mmHg logged.',
      time: '3 hours ago',
      unread: true,
      iconType: 'health'
    },
    {
      id: 'notif_4',
      category: 'medication',
      title: 'Upcoming dose reminder',
      desc: 'Evening medication Atorvastatin due at 8:00 PM.',
      time: '5 hours ago',
      unread: false,
      iconType: 'medication'
    },
    {
      id: 'notif_5',
      category: 'emergency',
      title: 'Routine safety check',
      desc: 'Device heartbeat confirmed, battery at 88%.',
      time: 'Yesterday',
      unread: false,
      iconType: 'emergency'
    },
    {
      id: 'notif_6',
      category: 'family',
      title: 'Weekly Care Summary',
      desc: 'Senior medication adherence was 95.2% this week.',
      time: 'Yesterday',
      unread: false,
      iconType: 'family'
    }
  ],

  getNotifications: function () {
    var raw = localStorage.getItem(this.storageKey);
    if (!raw) {
      this.saveNotifications(this.defaultNotifications);
      return this.defaultNotifications.slice();
    }
    try {
      var parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    } catch (e) {}
    return this.defaultNotifications.slice();
  },

  saveNotifications: function (list) {
    localStorage.setItem(this.storageKey, JSON.stringify(list));
  },

  markRead: function (id) {
    var list = this.getNotifications();
    for (var i = 0; i < list.length; i++) {
      if (list[i].id === id) {
        list[i].unread = false;
        break;
      }
    }
    this.saveNotifications(list);
    this.updateBadges();
    showToast('Notification marked as read.');
  },

  markAllRead: function () {
    var list = this.getNotifications();
    list.forEach(function (n) { n.unread = false; });
    this.saveNotifications(list);
    this.render();
    this.updateBadges();
    showToast('All notifications marked as read.');
  },

  clearNotification: function (id) {
    var list = this.getNotifications().filter(function (n) { return n.id !== id; });
    this.saveNotifications(list);
    this.render();
    this.updateBadges();
    showToast('Notification cleared.');
  },

  updateBadges: function () {
    var list = this.getNotifications();
    var unreadCount = list.filter(function (n) { return n.unread; }).length;

    var headerBadge = document.getElementById('notifCountBadge');
    if (headerBadge) {
      headerBadge.textContent = unreadCount;
      headerBadge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }

    var tabBadge = document.getElementById('tabNotifBadge');
    if (tabBadge) {
      tabBadge.textContent = unreadCount;
      tabBadge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }

    // Update filter tab counts
    var totalCount = list.length;
    var allTab = document.querySelector('.notif-tab[data-category="all"]');
    if (allTab) allTab.textContent = 'All (' + totalCount + ')';

    var categories = ['health', 'medication', 'appointment', 'emergency', 'family'];
    categories.forEach(function (cat) {
      var catTab = document.querySelector('.notif-tab[data-category="' + cat + '"]');
      if (catTab) {
        var cCount = list.filter(function (n) { return n.category === cat; }).length;
        var label = cat.charAt(0).toUpperCase() + cat.slice(1);
        catTab.textContent = label + ' (' + cCount + ')';
      }
    });
  },

  render: function () {
    var container = document.getElementById('smartNotifContainer');
    if (!container) return;

    var list = this.getNotifications();
    if (list.length === 0) {
      container.innerHTML =
        '<div class="empty-state" style="padding: var(--space-6) var(--space-4);">' +
          '<div class="empty-state__icon accent-icon-green">' +
            '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>' +
          '</div>' +
          '<h3 class="empty-state__title">All Caught Up!</h3>' +
          '<p class="empty-state__desc">There are no unread notifications or active safety alerts at this time.</p>' +
        '</div>';
      return;
    }

    var activeTab = document.querySelector('.notif-tab.is-active');
    var activeCategory = activeTab ? activeTab.getAttribute('data-category') : 'all';

    var html = '';
    list.forEach(function (n) {
      var isVisible = activeCategory === 'all' || n.category === activeCategory;
      var iconHtml = '';
      var catClass = 'category-' + n.category;
      var catLabel = n.category.charAt(0).toUpperCase() + n.category.slice(1);

      if (n.category === 'medication') {
        iconHtml = '<div class="notification-item__icon accent-icon-green"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="3"/><path d="M5 12h14"/></svg></div>';
      } else if (n.category === 'appointment') {
        iconHtml = '<div class="notification-item__icon accent-icon-blue"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/></svg></div>';
      } else if (n.category === 'health') {
        iconHtml = '<div class="notification-item__icon accent-icon-teal"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>';
      } else if (n.category === 'emergency') {
        iconHtml = '<div class="notification-item__icon accent-icon-amber"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>';
      } else {
        iconHtml = '<div class="notification-item__icon accent-icon-purple"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>';
      }

      html +=
        '<div class="smart-notif-item ' + (n.unread ? 'is-unread' : '') + '" data-category="' + n.category + '" data-id="' + n.id + '" style="display: ' + (isVisible ? 'flex' : 'none') + ';">' +
          '<div class="smart-notif-item__body">' +
            iconHtml +
            '<div>' +
              '<span class="smart-notif-item__category ' + catClass + '">' + catLabel + '</span>' +
              '<p class="notification-item__text"><strong>' + n.title + '</strong>: ' + n.desc + '</p>' +
              '<p class="notification-item__time">' + n.time + '</p>' +
            '</div>' +
          '</div>' +
          '<div class="smart-notif-item__actions">' +
            (n.unread ? '<button class="btn btn-outline btn-sm" data-action="mark-read">Mark Read</button>' : '') +
            '<button class="icon-button" data-action="clear-notif" aria-label="Clear notification" style="width:34px; height:34px;">' +
              '<svg class="icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' +
            '</button>' +
          '</div>' +
        '</div>';
    });

    container.innerHTML = html;
    this.bindEvents();
  },

  bindEvents: function () {
    var self = this;

    document.querySelectorAll('.smart-notif-item [data-action="mark-read"]').forEach(function (btn) {
      btn.onclick = function (e) {
        e.stopPropagation();
        var item = btn.closest('.smart-notif-item');
        if (item) {
          var id = item.getAttribute('data-id');
          item.classList.remove('is-unread');
          btn.remove();
          self.markRead(id);
        }
      };
    });

    document.querySelectorAll('.smart-notif-item [data-action="clear-notif"]').forEach(function (btn) {
      btn.onclick = function (e) {
        e.stopPropagation();
        var item = btn.closest('.smart-notif-item');
        if (item) {
          var id = item.getAttribute('data-id');
          item.style.opacity = '0';
          setTimeout(function () {
            self.clearNotification(id);
          }, 200);
        }
      };
    });
  },

  init: function () {
    var self = this;
    this.render();
    this.updateBadges();

    // Category filter tabs
    document.querySelectorAll('.notif-tab[data-category]').forEach(function (tab) {
      tab.addEventListener('click', function () {
        document.querySelectorAll('.notif-tab[data-category]').forEach(function (t) { t.classList.remove('is-active'); });
        tab.classList.add('is-active');

        var cat = tab.getAttribute('data-category');
        document.querySelectorAll('.smart-notif-item').forEach(function (item) {
          if (cat === 'all' || item.getAttribute('data-category') === cat) {
            item.style.display = 'flex';
          } else {
            item.style.display = 'none';
          }
        });
      });
    });

    var markAllBtn = document.getElementById('markAllReadBtn');
    if (markAllBtn) {
      markAllBtn.addEventListener('click', function () {
        self.markAllRead();
      });
    }
  }
};

function initSmartNotifications() {
  CarePlusNotifications.init();
}

/* ==========================================================================
   FAMILY DASHBOARD SPECIFIC INTERACTIONS (MEMBER 4 SCOPE)
   ========================================================================== */
function initFamilyDashboard() {
  // Tab Switching
  function switchFamilyTab(tabId) {
    var tabBtns = document.querySelectorAll('.dashboard-tab-btn[data-tab]');
    var tabPanes = document.querySelectorAll('.tab-pane[data-tab-pane]');
    var sideLinks = document.querySelectorAll('.sidebar__link[data-family-tab]');

    tabBtns.forEach(function (btn) {
      btn.classList.toggle('is-active', btn.getAttribute('data-tab') === tabId);
    });

    tabPanes.forEach(function (pane) {
      pane.classList.toggle('is-active', pane.getAttribute('data-tab-pane') === tabId);
    });

    sideLinks.forEach(function (link) {
      link.classList.toggle('is-active', link.getAttribute('data-family-tab') === tabId);
    });

    var tabContainer = document.getElementById('familyDashboardTabs');
    if (tabContainer && window.scrollY > tabContainer.offsetTop + 80) {
      tabContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
  window.switchFamilyTab = switchFamilyTab;

  document.querySelectorAll('.dashboard-tab-btn[data-tab]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      switchFamilyTab(btn.getAttribute('data-tab'));
    });
  });

  document.querySelectorAll('[data-switch-tab]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      switchFamilyTab(el.getAttribute('data-switch-tab'));
    });
  });

  document.querySelectorAll('.sidebar__link[data-family-tab]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      switchFamilyTab(link.getAttribute('data-family-tab'));
      closeAllDropdowns();
    });
  });

  // Initialize Contacts Subsystem
  CarePlusContacts.init();

  // Family Account Form Persistence
  var accountForm = document.getElementById('familyAccountForm');
  if (accountForm) {
    var savedAcc = localStorage.getItem('careplus_family_account');
    if (savedAcc) {
      try {
        var data = JSON.parse(savedAcc);
        if (data.name && accountForm.elements['memberName']) accountForm.elements['memberName'].value = data.name;
        if (data.email && accountForm.elements['memberEmail']) accountForm.elements['memberEmail'].value = data.email;
        if (data.phone && accountForm.elements['memberPhone']) accountForm.elements['memberPhone'].value = data.phone;
        if (data.relation && accountForm.elements['memberRelation']) accountForm.elements['memberRelation'].value = data.relation;
      } catch (e) {}
    }

    accountForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var accData = {
        name: accountForm.elements['memberName'] ? accountForm.elements['memberName'].value : '',
        email: accountForm.elements['memberEmail'] ? accountForm.elements['memberEmail'].value : '',
        phone: accountForm.elements['memberPhone'] ? accountForm.elements['memberPhone'].value : '',
        relation: accountForm.elements['memberRelation'] ? accountForm.elements['memberRelation'].value : ''
      };
      localStorage.setItem('careplus_family_account', JSON.stringify(accData));
      showToast('Family account settings saved successfully!');
    });
  }

  // Appointment Modal View
  document.querySelectorAll('#viewAppointmentBtn, [data-action="view-appointment"]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var modal = document.getElementById('appointmentDetailModal');
      if (modal) {
        modal.classList.add('is-open');
        document.body.style.overflow = 'hidden';
      } else {
        showToast('Appointment Details: Dr. Joseph, Today at 3:00 PM.');
      }
    });
  });
}

/* ==========================================================================
   ADMIN DASHBOARD INTERACTIONS & OVERSIGHT (MEMBER 4 SCOPE)
   ========================================================================== */
var CarePlusAdmin = {
  usersKey: 'careplus_admin_users',
  verificationsKey: 'careplus_admin_verifications',
  consentKey: 'careplus_admin_consent',

  getStoredUsers: function () {
    try {
      return JSON.parse(localStorage.getItem(this.usersKey)) || {};
    } catch (e) { return {}; }
  },

  saveStoredUsers: function (obj) {
    localStorage.setItem(this.usersKey, JSON.stringify(obj));
  },

  getStoredVerifications: function () {
    try {
      return JSON.parse(localStorage.getItem(this.verificationsKey)) || {};
    } catch (e) { return {}; }
  },

  saveStoredVerifications: function (obj) {
    localStorage.setItem(this.verificationsKey, JSON.stringify(obj));
  },

  getStoredConsent: function () {
    try {
      return JSON.parse(localStorage.getItem(this.consentKey)) || {};
    } catch (e) { return {}; }
  },

  saveStoredConsent: function (obj) {
    localStorage.setItem(this.consentKey, JSON.stringify(obj));
  },

  init: function () {
    this.initUserManagement();
    this.initVerificationQueue();
    this.initConsentManagement();
  },

  initUserManagement: function () {
    var self = this;
    var searchInput = document.getElementById('userSearchInput');
    var roleFilter = document.getElementById('userRoleFilter');
    var statusFilter = document.getElementById('userStatusFilter');
    var userRows = document.querySelectorAll('.user-row');

    // Restore persisted status
    var storedUsers = this.getStoredUsers();
    userRows.forEach(function (row) {
      var email = row.getAttribute('data-email');
      if (email && storedUsers[email]) {
        var status = storedUsers[email];
        row.setAttribute('data-status', status);
        var pill = row.querySelector('.status-pill');
        var btn = row.querySelector('[data-action="toggle-user-status"]');
        if (pill && btn) {
          if (status === 'active') {
            pill.className = 'status-pill status-pill--success';
            pill.textContent = 'Active';
            btn.textContent = 'Disable';
            btn.className = 'btn btn-outline btn-sm danger';
          } else {
            pill.className = 'status-pill status-pill--warning';
            pill.textContent = 'Disabled';
            btn.textContent = 'Enable';
            btn.className = 'btn btn-outline btn-sm';
          }
        }
      }
    });

    function filterUsers() {
      var q = searchInput ? searchInput.value.toLowerCase().trim() : '';
      var r = roleFilter ? roleFilter.value : 'all';
      var s = statusFilter ? statusFilter.value : 'all';

      userRows.forEach(function (row) {
        var name = (row.getAttribute('data-name') || '').toLowerCase();
        var email = (row.getAttribute('data-email') || '').toLowerCase();
        var role = row.getAttribute('data-role') || '';
        var status = row.getAttribute('data-status') || '';

        var matchesSearch = !q || name.indexOf(q) !== -1 || email.indexOf(q) !== -1;
        var matchesRole = r === 'all' || role === r;
        var matchesStatus = s === 'all' || status === s;

        row.style.display = (matchesSearch && matchesRole && matchesStatus) ? '' : 'none';
      });
    }

    if (searchInput) searchInput.addEventListener('input', filterUsers);
    if (roleFilter) roleFilter.addEventListener('change', filterUsers);
    if (statusFilter) statusFilter.addEventListener('change', filterUsers);

    // Toggle User Status
    document.querySelectorAll('[data-action="toggle-user-status"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var row = btn.closest('.user-row');
        if (!row) return;

        var email = row.getAttribute('data-email') || row.getAttribute('data-name');
        var currentStatus = row.getAttribute('data-status');
        var newStatus = currentStatus === 'active' ? 'disabled' : 'active';
        row.setAttribute('data-status', newStatus);

        var pill = row.querySelector('.status-pill');
        if (pill) {
          if (newStatus === 'active') {
            pill.className = 'status-pill status-pill--success';
            pill.textContent = 'Active';
            btn.textContent = 'Disable';
            btn.className = 'btn btn-outline btn-sm danger';
          } else {
            pill.className = 'status-pill status-pill--warning';
            pill.textContent = 'Disabled';
            btn.textContent = 'Enable';
            btn.className = 'btn btn-outline btn-sm';
          }
        }

        var usersMap = self.getStoredUsers();
        if (email) usersMap[email] = newStatus;
        self.saveStoredUsers(usersMap);

        showToast('User account status updated to: ' + newStatus);
      });
    });

    // View User Modal
    document.querySelectorAll('[data-action="view-user"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var row = btn.closest('.user-row');
        var name = row ? row.getAttribute('data-name') : 'User';
        var modal = document.getElementById('adminUserModal');
        var nameEl = document.getElementById('adminUserModalName');
        if (modal && nameEl) {
          nameEl.textContent = name;
          modal.classList.add('is-open');
          document.body.style.overflow = 'hidden';
        } else {
          showToast('Viewing record for ' + name);
        }
      });
    });
  },

  initVerificationQueue: function () {
    var self = this;
    var vTabs = document.querySelectorAll('.v-tab-btn[data-vtab]');
    var vCards = document.querySelectorAll('.verification-card[data-vtype]');

    // Restore persisted verification statuses
    var storedV = this.getStoredVerifications();
    vCards.forEach(function (card) {
      var name = card.getAttribute('data-name');
      if (name && storedV[name]) {
        var st = storedV[name];
        var pill = card.querySelector('.status-pill');
        var actions = card.querySelector('.verification-card__actions');
        if (st === 'approved') {
          if (pill) {
            pill.className = 'status-pill status-pill--success';
            pill.textContent = 'Approved';
          }
          if (actions) {
            actions.innerHTML = '<span class="status-pill status-pill--success"><svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> Approved</span>';
          }
        } else if (st === 'rejected') {
          if (pill) {
            pill.className = 'status-pill status-pill--danger';
            pill.textContent = 'Rejected';
          }
          if (actions) {
            actions.innerHTML = '<span class="status-pill status-pill--danger">Rejected</span>';
          }
        }
      }
    });

    // Tab switching
    vTabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        vTabs.forEach(function (t) { t.classList.remove('is-active'); });
        tab.classList.add('is-active');

        var type = tab.getAttribute('data-vtab');
        vCards.forEach(function (card) {
          if (type === 'all' || card.getAttribute('data-vtype') === type) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });

    // Verification Approve / Reject
    document.querySelectorAll('[data-action="approve-verification"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var card = btn.closest('.verification-card');
        var name = card ? card.getAttribute('data-name') : 'Applicant';
        var pill = card ? card.querySelector('.status-pill') : null;
        if (pill) {
          pill.className = 'status-pill status-pill--success';
          pill.textContent = 'Approved';
        }
        var actions = card ? card.querySelector('.verification-card__actions') : null;
        if (actions) {
          actions.innerHTML = '<span class="status-pill status-pill--success"><svg class="icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> Approved</span>';
        }

        var map = self.getStoredVerifications();
        if (name) map[name] = 'approved';
        self.saveStoredVerifications(map);

        showToast('Application approved for ' + name);
      });
    });

    document.querySelectorAll('[data-action="reject-verification"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var card = btn.closest('.verification-card');
        var name = card ? card.getAttribute('data-name') : 'Applicant';
        var pill = card ? card.querySelector('.status-pill') : null;
        if (pill) {
          pill.className = 'status-pill status-pill--danger';
          pill.textContent = 'Rejected';
        }
        var actions = card ? card.querySelector('.verification-card__actions') : null;
        if (actions) {
          actions.innerHTML = '<span class="status-pill status-pill--danger">Rejected</span>';
        }

        var map = self.getStoredVerifications();
        if (name) map[name] = 'rejected';
        self.saveStoredVerifications(map);

        showToast('Application rejected for ' + name);
      });
    });
  },

  initConsentManagement: function () {
    var self = this;
    var storedC = this.getStoredConsent();

    // Restore consent records
    document.querySelectorAll('#consentSection table tbody tr').forEach(function (row, idx) {
      var key = 'consent_row_' + idx;
      if (storedC[key]) {
        var cData = storedC[key];
        var levelEl = row.querySelector('.consent-level');
        var statusEl = row.querySelector('.consent-status');
        var revokeBtn = row.querySelector('[data-action="revoke-consent-access"]');
        if (levelEl && cData.level) levelEl.textContent = cData.level;
        if (statusEl && cData.status === 'revoked') {
          statusEl.className = 'status-pill status-pill--danger consent-status';
          statusEl.textContent = 'Revoked';
          if (revokeBtn) {
            revokeBtn.disabled = true;
            revokeBtn.textContent = 'Revoked';
          }
        }
      }
    });

    document.querySelectorAll('[data-action="update-consent-access"]').forEach(function (btn, idx) {
      btn.addEventListener('click', function () {
        var row = btn.closest('tr');
        var levelEl = row ? row.querySelector('.consent-level') : null;
        if (levelEl) {
          var current = levelEl.textContent.trim();
          var next = current === 'Full Access' ? 'Summary Only' : 'Full Access';
          levelEl.textContent = next;

          var key = 'consent_row_' + idx;
          var map = self.getStoredConsent();
          map[key] = map[key] || {};
          map[key].level = next;
          self.saveStoredConsent(map);

          showToast('Data sharing access tier updated to: ' + next);
        }
      });
    });

    document.querySelectorAll('[data-action="revoke-consent-access"]').forEach(function (btn, idx) {
      btn.addEventListener('click', function () {
        var row = btn.closest('tr');
        var statusEl = row ? row.querySelector('.consent-status') : null;
        if (statusEl) {
          statusEl.className = 'status-pill status-pill--danger consent-status';
          statusEl.textContent = 'Revoked';
          btn.disabled = true;
          btn.textContent = 'Revoked';

          var key = 'consent_row_' + idx;
          var map = self.getStoredConsent();
          map[key] = map[key] || {};
          map[key].status = 'revoked';
          self.saveStoredConsent(map);

          showToast('Consent revoked. Family member access has been suspended.');
        }
      });
    });
  }
};

function initAdminDashboard() {
  CarePlusAuth.enforceAdminGuard();
  CarePlusAdmin.init();
}

