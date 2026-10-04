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
   MULTILINGUAL SYSTEM (ENGLISH + MALAYALAM)
   ========================================================================== */
var CarePlusI18n = {
  currentLang: 'en',
  dictionary: {
    en: {
      nav_dashboard: 'Dashboard',
      nav_senior_overview: 'Senior Overview',
      nav_health_updates: 'Health & Vitals',
      nav_medication_updates: 'Medications & Schedule',
      nav_appointments: 'Appointments',
      nav_emergency: 'Emergency',
      nav_emergency_notifications: 'Emergency Notifications',
      nav_contacts: 'Care Network & Contacts',
      nav_notifications: 'Smart Notifications',
      nav_accessibility: 'Accessibility',
      nav_settings: 'Family Account Settings',
      nav_logout: 'Logout',
      nav_users: 'User Management',
      nav_doctors: 'Doctors',
      nav_caregivers: 'Caregivers',
      nav_volunteers: 'Volunteers',
      nav_reports: 'Reports & Analytics',
      nav_consent: 'Patient Consent & Privacy',
      btn_call: 'Call',
      btn_voice_call: 'Voice Call',
      btn_save: 'Save Preferences',
      btn_cancel: 'Cancel',
      btn_approve: 'Approve',
      btn_reject: 'Reject',
      btn_view: 'View',
      btn_view_appointment: 'View Appointment Details',
      btn_join_consultation: 'Join Consultation',
      btn_switch_role: 'Switch Role',
      btn_add_contact: '+ Add Contact',
      btn_edit: 'Edit',
      btn_delete: 'Delete',
      btn_activate: 'Activate',
      btn_disable: 'Disable',
      btn_mark_read: 'Mark Read',
      btn_mark_all_read: 'Mark all as read',
      btn_clear: 'Clear',
      status_stable: 'Vitals Stable',
      status_safe: 'Safe at Home',
      status_active: 'Active',
      status_disabled: 'Disabled',
      status_pending: 'Pending',
      status_approved: 'Approved',
      status_rejected: 'Rejected',
      status_resolved: 'Resolved',
      status_taken: 'Taken',
      status_upcoming: 'Upcoming',
      status_scheduled: 'Scheduled',
      voice_nav_btn: '🎙 Voice Nav',
      a11y_btn: 'Accessibility',
      senior_wellbeing_title: 'Senior Wellbeing Vitals',
      bp_label: 'Blood Pressure',
      sugar_label: 'Blood Sugar',
      hr_label: 'Heart Rate',
      spo2_label: 'Oxygen (SpO2)',
      temp_label: 'Temperature',
      weight_label: 'Weight',
      no_active_emergency: 'No active emergency',
      emergency_all_clear: 'All systems normal. Senior is in safe zone.',
      admin_overview_title: 'Platform Overview',
      admin_users_title: 'User Management',
      admin_verifications_title: 'Professional Verifications',
      admin_appointments_title: 'Appointment Management',
      admin_emergency_title: 'Emergency Oversight',
      admin_analytics_title: 'Reports & Analytics',
      admin_consent_title: 'Patient Consent & Data Privacy',
      search_placeholder: 'Search by name or email...',
      filter_role: 'All Roles',
      filter_status: 'All Statuses'
    },
    ml: {
      nav_dashboard: 'ഡാഷ്‌ബോർഡ്',
      nav_senior_overview: 'മുതിർന്നവരുടെ അവലോകനം',
      nav_health_updates: 'ആരോഗ്യ വിവരങ്ങൾ',
      nav_medication_updates: 'മരുന്ന് ഷെഡ്യൂൾ',
      nav_appointments: 'അപ്പോയിന്റ്മെന്റുകൾ',
      nav_emergency: 'അടിയന്തര സാഹചര്യം',
      nav_emergency_notifications: 'അടിയന്തര അറിയിപ്പുകൾ',
      nav_contacts: 'കുടുംബ കോൺടാക്റ്റുകൾ',
      nav_notifications: 'അറിയിപ്പുകൾ',
      nav_accessibility: 'പ്രവേശനക്ഷമത',
      nav_settings: 'അക്കൗണ്ട് ക്രമീകരണങ്ങൾ',
      nav_logout: 'ലോഗ് ഔട്ട്',
      nav_users: 'ഉപയോക്തൃ മാനേജ്മെന്റ്',
      nav_doctors: 'ഡോക്ടർമാർ',
      nav_caregivers: 'പരിപാലകർ',
      nav_volunteers: 'വോളണ്ടിയർമാർ',
      nav_reports: 'റിപ്പോർട്ടുകളും വിശകലനവും',
      nav_consent: 'സമ്മതവും സ്വകാര്യതയും',
      btn_call: 'വിളിക്കുക',
      btn_voice_call: 'വോയ്സ് കോൾ',
      btn_save: 'സേവ് ചെയ്യുക',
      btn_cancel: 'റദ്ദാക്കുക',
      btn_approve: 'അംഗീകരിക്കുക',
      btn_reject: 'നിരസിക്കുക',
      btn_view: 'കാണുക',
      btn_view_appointment: 'അപ്പോയിന്റ്മെന്റ് കാണുക',
      btn_join_consultation: 'കൺസൾട്ടേഷനിൽ ചേരുക',
      btn_switch_role: 'റോൾ മാറ്റുക',
      btn_add_contact: '+ കോൺടാക്റ്റ് ചേർക്കുക',
      btn_edit: 'മാറ്റുക',
      btn_delete: 'നീക്കം ചെയ്യുക',
      btn_activate: 'സജീവമാക്കുക',
      btn_disable: 'പ്രവർത്തനരഹിതമാക്കുക',
      btn_mark_read: 'വായിച്ചതായി അടയാളപ്പെടുത്തുക',
      btn_mark_all_read: 'എല്ലാം വായിച്ചതായി അടയാളപ്പെടുത്തുക',
      btn_clear: 'മായ്ക്കുക',
      status_stable: 'സുസ്ഥിരം',
      status_safe: 'സുരക്ഷിതം',
      status_active: 'സജീവം',
      status_disabled: 'പ്രവർത്തനരഹിതം',
      status_pending: 'തീർപ്പാക്കാത്തത്',
      status_approved: 'അംഗീകരിച്ചു',
      status_rejected: 'നിരസിച്ചു',
      status_resolved: 'പരിഹരിച്ചു',
      status_taken: 'കഴിച്ചു',
      status_upcoming: 'വരാനിരിക്കുന്നത്',
      status_scheduled: 'ഷെഡ്യൂൾ ചെയ്തത്',
      voice_nav_btn: 'വോയ്‌സ് നാവിഗേഷൻ',
      a11y_btn: 'പ്രവേശനക്ഷമത',
      senior_wellbeing_title: 'ആരോഗ്യ വിവരങ്ങൾ',
      bp_label: 'രക്തസമ്മർദ്ദം',
      sugar_label: 'രക്തത്തിലെ പഞ്ചസാര',
      hr_label: 'ഹൃദയമിടിപ്പ്',
      spo2_label: 'ഓക്സിജൻ നില',
      temp_label: 'ശരീര താപനില',
      weight_label: 'ശരീരഭാരം',
      no_active_emergency: 'അടിയന്തര സാഹചര്യങ്ങളൊന്നുമില്ല',
      emergency_all_clear: 'എല്ലാം സാധാരണ നിലയിലാണ്. മുതിർന്ന വ്യക്തി സുരക്ഷിതനാണ്.',
      admin_overview_title: 'പ്ലാറ്റ്ഫോം അവലോകനം',
      admin_users_title: 'ഉപയോക്തൃ മാനേജ്മെന്റ്',
      admin_verifications_title: 'പ്രൊഫഷണൽ സ്ഥിരീകരണം',
      admin_appointments_title: 'അപ്പോയിന്റ്മെന്റ് മാനേജ്മെന്റ്',
      admin_emergency_title: 'അടിയന്തര മേൽനോട്ടം',
      admin_analytics_title: 'റിപ്പോർട്ടുകളും വിശകലനവും',
      admin_consent_title: 'രോഗിയുടെ സമ്മതവും സ്വകാര്യതയും',
      search_placeholder: 'പേര് അല്ലെങ്കിൽ ഇമെയിൽ തിരയുക...',
      filter_role: 'എല്ലാ റോളുകളും',
      filter_status: 'എല്ലാ സ്റ്റാറ്റസും'
    }
  },

  init: function () {
    var savedLang = localStorage.getItem('careplus_lang') || 'en';
    this.setLanguage(savedLang);

    var selectors = document.querySelectorAll('.lang-selector, #langSelect');
    selectors.forEach(function (sel) {
      sel.value = savedLang;
      sel.addEventListener('change', function () {
        CarePlusI18n.setLanguage(sel.value);
        showToast(sel.value === 'ml' ? 'ഭാഷ മലയാളത്തിലേക്ക് മാറ്റി.' : 'Language switched to English.');
      });
    });
  },

  t: function (key) {
    var dict = this.dictionary[this.currentLang] || this.dictionary['en'];
    return dict[key] || key;
  },

  setLanguage: function (lang) {
    if (!this.dictionary[lang]) lang = 'en';
    this.currentLang = lang;
    localStorage.setItem('careplus_lang', lang);
    document.documentElement.lang = lang;

    var dict = this.dictionary[lang];
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key]) {
        if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
          el.value = dict[key];
        } else if (el.tagName === 'INPUT' && el.type === 'text') {
          el.placeholder = dict[key];
        } else {
          el.textContent = dict[key];
        }
      }
    });

    // Sync all dropdowns on page
    document.querySelectorAll('.lang-selector, #langSelect').forEach(function (sel) {
      sel.value = lang;
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

