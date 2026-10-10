CARE+ MAIN PORTAL

This portal links to the three existing, separately run Streamlit dashboards.
It does not replace their login pages or alter their code.

1. Install Streamlit if needed:
     pip install streamlit

2. Run each dashboard in a separate terminal, using your real filenames:
     streamlit run <elderly-dashboard-file.py> --server.port 8501
     streamlit run <caregiver-dashboard-file.py> --server.port 8502
     streamlit run <doctor-dashboard-file.py> --server.port 8503

3. Run the portal in another terminal:
     streamlit run portal.py --server.port 8500

4. Open http://localhost:8500

The portal's default links are localhost ports 8501, 8502, and 8503.
If your dashboard ports or deployed URLs differ, configure them in
.streamlit/secrets.toml as documented inside the app's expander.

IMPORTANT:
- Replace the example dashboard filenames with the actual filenames on your computer.
- Keep each dashboard's own login/authentication intact.
- This portal only links to dashboards; it does not provide centralized authentication.
