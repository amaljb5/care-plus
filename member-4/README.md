# Care+ Streamlit Healthcare Platform (Member 4)

This directory contains the complete **Care+ Healthcare and Monitoring Platform** powered by **Streamlit**, featuring role-based authentication, eldercare accessibility controls, multilingual support, and interactive dashboards.

---

## 🔐 Dashboard Login Credentials

| Dashboard / Workspace | Username / Email | Password | Role Description |
| :--- | :--- | :--- | :--- |
| 👨‍👩‍👧 **Family Portal** | `family@careplus.org` | `family123` | Senior wellbeing monitoring, vitals telemetry & medication tracking |
| 🛡️ **Admin Console** | `admin@careplus.org` | `admin123` | Professional credential verification, governance & audit logs |
| 🩺 **Doctor Dashboard** | `doctor@careplus.org` | `doctor123` | Clinical patient queue, consultations & prescriptions |
| 🧑 **Patient Dashboard** | `patient@careplus.org` | `patient123` | Daily health tasks, medication checklists & SOS trigger |

> 💡 *Note: The login dialog also includes convenient **Auto Fill** buttons for quick testing of any dashboard.*

---

## 🚀 How to Run with Streamlit

### Option 1: Run from project root
```bash
python -m streamlit run member-4/app.py
```

### Option 2: Run from inside `member-4` directory
```bash
cd member-4
python -m streamlit run app.py
```

---

## 📱 Portals & Features Included

1. **🌟 Care+ Welcome & Role Portal**
   - Central gateway with portal cards, quick demo auto-fill, and role switching.

2. **👨‍👩‍👧 Family Dashboard**
   - Senior wellbeing monitoring, live telemetry (BP, Glucose, Heart Rate, SpO2, Temperature), medication adherence timeline, and emergency contact dialer.

3. **🛡️ Admin Console & Governance**
   - Doctor/caregiver credential verification queue, appointment audit records, and patient privacy controls.

4. **🩺 Doctor Dashboard**
   - Clinical telemetry review, upcoming telehealth appointments, patient consultation records, and prescription issuance.

5. **🧑 Senior Patient Dashboard**
   - Interactive daily medication checklist ("Mark as taken"), caregiver alert toggles, and one-tap emergency calling.

---

## ♿ Preserved Accessibility & Usability Controls
- **High Contrast Mode**: Optimized for low vision and elderly reading.
- **Dynamic Font Scaling (A+ / A-)**: Scalable text sizing.
- **Multilingual Support**: Instant bilingual toggle between **English** and **Malayalam (മലയാളം)**.
- **Voice Assistant**: Hands-free voice recognition modal.
- **Responsive Full-Screen Layout**: Edge-to-edge native resolution without surrounding margins.
