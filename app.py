import streamlit as st
import requests
import json
import io

st.set_page_config(page_title="AI Resume Rebuilder", layout="wide")

# Fixed backend URL (not editable in UI for normal users)
backend_url = "http://localhost:8000"

# Restore session token from URL query parameters on app load
query_params = st.experimental_get_query_params()
if "token" in query_params:
    st.session_state.token = query_params["token"][0]

# If a token exists in session_state, persist it to the URL
if st.session_state.get("token"):
    st.experimental_set_query_params(token=st.session_state.token)

def _init_state():
    for key, val in {
        'structured_text': None,
        'original_text': None,
        'tailored_text': None,
        'extracted_preview': None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val
    # session token storage
    if 'session_token' not in st.session_state:
        st.session_state['session_token'] = None
    # ensure we only attempt auto-create once per user entrance
    if 'session_initialized' not in st.session_state:
        st.session_state['session_initialized'] = False


_init_state()

# Persist session token into query params if available, so reloads keep the same token
if st.session_state.get('session_token'):
    st.experimental_set_query_params(token=st.session_state['session_token'])

# Attempt to restore session token from query params on load
try:
    q = st.experimental_get_query_params()
    qtoken = q.get('token', [None])[0]
    if qtoken and not st.session_state.get('session_token'):
        st.session_state['session_token'] = qtoken
        try:
            headers = {'Authorization': f"Bearer {qtoken}"}
            resp = requests.get(f"{backend_url}/session-info", headers=headers, timeout=5)
            if resp.status_code == 200:
                st.session_state['session_info'] = resp.json()
        except Exception:
            pass
except Exception:
    pass

def _create_initial_session_if_missing():
    """Try to create a demo session once when the user first opens the app.

    This avoids the problem where the first protected call runs before a session exists.
    If the backend is unreachable we mark initialization done so we don't spam requests.
    """
    if st.session_state.get('session_token'):
        st.session_state['session_initialized'] = True
        return
    if st.session_state.get('session_initialized'):
        return
    try:
        # short timeout so page load isn't blocked for long if backend down
        # request a larger demo quota so new users won't exhaust the session immediately
        sresp = requests.post(f"{backend_url}/session", data={'ttl_minutes': 60, 'max_uses': 4}, timeout=4)
        if sresp.status_code == 200:
            st.session_state['session_token'] = sresp.json().get('token')
            # fetch authoritative session info (uses / remaining) and store it
            try:
                info = fetch_session_info()
                if info:
                    st.session_state['session_info'] = info
            except Exception:
                pass
    except Exception:
        # ignore errors here; we just don't have a session yet
        pass
    finally:
        # mark initialized (whether success or not) to avoid repeated attempts
        st.session_state['session_initialized'] = True


# ensure a demo session exists immediately on first open
# Restore token from query params if present so refreshes keep the same session
try:
    q = st.st.query_params()
    qtoken = q.get('token', [None])[0]
    if qtoken and not st.session_state.get('session_token'):
        st.session_state['session_token'] = qtoken
        # try to fetch authoritative session info
        try:
            info = None
            info = requests.get(f"{backend_url}/session-info", headers={'Authorization': f"Bearer {qtoken}"}, timeout=5)
            if info and info.status_code == 200:
                st.session_state['session_info'] = info.json()
        except Exception:
            pass
except Exception:
    pass

# Now attempt auto-create if we still don't have a token
_create_initial_session_if_missing()

# Sidebar: settings for non-developers
st.sidebar.title("Settings")
st.sidebar.markdown("Paste an admin token below if you have one. Normal users don't need to change backend settings.")
st.sidebar.markdown("---")
st.sidebar.markdown("Steps: 1) Upload PDF → 2) Review/Edit → 3) Tailor (optional) → 4) Generate PDF")


def _headers():
    h = {}
    # Use session token (Bearer) if available
    if st.session_state.get('session_token'):
        h['Authorization'] = f"Bearer {st.session_state['session_token']}"
    return h


st.title("AI Resume Rebuilder — Easy Mode")
st.markdown("A simple, step-by-step interface to extract, review, tailor, and generate ATS-friendly resumes. Follow the steps below.")

# Helper to fetch session info from backend and store in session_state
def fetch_session_info():
    token = st.session_state.get('session_token')
    if not token:
        return None
    try:
        headers = {'Authorization': f"Bearer {token}"}
        resp = requests.get(f"{backend_url}/session-info", headers=headers, timeout=5)
        if resp.status_code == 200:
            info = resp.json()
            st.session_state['session_info'] = info
            return info
    except Exception:
        return None
    return None

# Display current session usage if available
session_info = st.session_state.get('session_info') or fetch_session_info()

# Show a transient toast message if set by actions (extraction/tailor/generate)
# Toast placeholder: display one-off messages set by actions
toast_ph = st.empty()
if st.session_state.get('toast_msg'):
    try:
        msg = st.session_state.pop('toast_msg')
        toast_ph.success(msg)
    except Exception:
        st.session_state.pop('toast_msg', None)

if session_info:
    uses = session_info.get('uses')
    max_uses = session_info.get('max_uses')
    remaining = session_info.get('remaining')
    st.info(f"Session uses: {uses}/{max_uses} — {remaining} remaining")
    if st.button("Refresh session info", key='refresh_session'):
        new_info = fetch_session_info()
        if new_info:
            st.success("Session info updated")
        else:
            st.error("Could not refresh session info")


## Step 1: Upload and extract
st.header("Step 1 — Upload CV (PDF)")
st.info("Upload a clean PDF of your resume. The app will extract text and try to parse contact and structured sections.")
uploaded_file = st.file_uploader("Choose a PDF file to upload", type=["pdf"]) 

if uploaded_file is not None:
    # Show file info but do NOT auto-run extraction — require explicit user action
    try:
        size_mb = uploaded_file.size / (1024*1024)
    except Exception:
        size_mb = None
    st.markdown(f"**Selected file:** {uploaded_file.name} ({size_mb:.2f} MB)" if size_mb else f"**Selected file:** {uploaded_file.name}")
    if size_mb and size_mb > 10:
        st.warning("File is larger than 10 MB — extraction may take longer or fail.")

    if st.button("Extract and parse", key='extract_button'):
        # Ensure we have a session token before calling model-backed endpoints so the server can increment usage
        if not st.session_state.get('session_token'):
            try:
                sresp = requests.post(f"{backend_url}/session", data={'ttl_minutes': 60, 'max_uses': 100}, timeout=10)
                if sresp.status_code == 200:
                    st.session_state['session_token'] = sresp.json().get('token')
                    # Persist token in URL query params
                    st.experimental_set_query_params(token=st.session_state['session_token'])
                    # populate session info immediately
                    try:
                        info = fetch_session_info()
                        if info:
                            st.session_state['session_info'] = info
                    except Exception:
                        pass
                    st.success("Demo session started (100 uses)")
                else:
                    st.info("Could not create demo session automatically; protected endpoints will require a token.")
            except Exception:
                st.info("Could not create demo session automatically; protected endpoints will require a token.")

        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        try:
            with st.spinner("Uploading and extracting — this may take a moment..."):
                resp = requests.post(f"{backend_url}/extract-cv-json/", files=files, headers=_headers(), timeout=180)
            if resp.status_code == 200:
                data = resp.json()
                structured = data.get("structured_data")
                original_contact = data.get("original_contact")
                extracted = data.get("extracted_text")
                st.success("Extraction complete")
                st.session_state['extracted_preview'] = extracted[:2000] if extracted else None
                # populate editable text areas in session state
                st.session_state['structured_text'] = json.dumps(structured, indent=2) if structured else None
                st.session_state['original_text'] = json.dumps(original_contact or {}, indent=2)

                # The extraction call consumed a model prompt — refresh authoritative session info, set toast, and rerun
                try:
                    info = fetch_session_info()
                    if info:
                        st.session_state['session_info'] = info
                        st.session_state['toast_msg'] = f"Session used: {info.get('uses')}/{info.get('max_uses')} — {info.get('remaining')} remaining"
                        st.experimental_rerun()
                except Exception:
                    pass
            else:
                st.error(f"Extraction failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")


## Step 2: Review and edit
st.markdown("---")
st.header("Step 2 — Review & Edit")
st.info("Review the parsed fields. If something is wrong, edit the contact or the structured JSON. Use the 'Validate JSON' buttons to check your edits before continuing.")

col1, col2 = st.columns([1,1])
with col1:
    st.subheader("Structured data (model)")
    if st.session_state.get('structured_text'):
        st.json(json.loads(st.session_state['structured_text']))
        if st.checkbox("Edit structured JSON", key="edit_structured_toggle"):
            st.session_state['structured_text'] = st.text_area("structured_json", st.session_state['structured_text'], height=300)
            if st.button("Validate structured JSON"):
                try:
                    _ = json.loads(st.session_state['structured_text'])
                    st.success("Structured JSON is valid")
                except Exception as e:
                    st.error(f"Invalid JSON: {e}")
    else:
        st.info("No structured data yet — upload a PDF in Step 1.")

with col2:
    st.subheader("Original contact (editable)")
    if st.session_state.get('original_text'):
        st.json(json.loads(st.session_state['original_text']))
        st.session_state['original_text'] = st.text_area("original_contact_json", st.session_state['original_text'], height=300)
        if st.button("Validate contact JSON"):
            try:
                _ = json.loads(st.session_state['original_text'])
                st.success("Contact JSON is valid")
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
    else:
        st.info("No contact data yet — upload a PDF in Step 1.")


## Step 3: Optional — Tailor to a job description
st.markdown("---")
st.header("Step 3 — Tailor to a job description (optional)")
st.info("Paste the job description and choose a rewrite style. The model will return tailored summary/skills/experience sections. You can edit the tailored output before generating the final CV.")

with st.form(key='tailor_form'):
    job_description = st.text_area("Job description (paste here)", height=200)
    rewrite_style = st.selectbox("Rewrite style", ["keywords", "minimal", "full"], index=0)
    tailor_submit = st.form_submit_button("Tailor JSON to ATS")

if tailor_submit:
    if not st.session_state.get('structured_text'):
        st.error("No structured data available — please upload and validate a CV first.")
    else:
        try:
            cv_json = json.loads(st.session_state['structured_text'])
        except Exception as e:
            st.error(f"Structured JSON is invalid: {e}")
            cv_json = None
        try:
            orig_contact_obj = json.loads(st.session_state['original_text']) if st.session_state.get('original_text') else None
        except Exception:
            orig_contact_obj = None
        if cv_json is not None:
            payload = {
                "cv_json": json.dumps(cv_json),
                "job_description": job_description or "",
                "rewrite_style": rewrite_style,
                "original_contact": json.dumps(orig_contact_obj) if orig_contact_obj else None
            }
            try:
                with st.spinner("Calling tailoring model — this may take a bit..."):
                    resp = requests.post(f"{backend_url}/tailor-json-to-ats/", data=payload, headers=_headers(), timeout=180)
                if resp.status_code == 200:
                    result = resp.json()
                    tailored = result.get('tailored_data') or result.get('tailored') or {}
                    st.success("Tailoring complete — review below")
                    st.session_state['tailored_text'] = json.dumps(tailored, indent=2)
                    st.subheader("Tailored output (preview)")
                    st.json(tailored)
                    # refresh session info so uses/max_uses reflect this call; show toast and rerun to update banner
                    try:
                        info = fetch_session_info()
                        if info:
                            st.session_state['session_info'] = info
                            st.session_state['toast_msg'] = f"Session used: {info.get('uses')}/{info.get('max_uses')} — {info.get('remaining')} remaining"
                            st.experimental_rerun()
                    except Exception:
                        pass
                else:
                    st.error(f"Tailoring failed: {resp.status_code} {resp.text}")
            except Exception as e:
                st.error(f"Error calling backend: {e}")

    
if st.session_state.get('tailored_text'):
    st.subheader("Editable Tailored JSON")
    st.session_state['tailored_text'] = st.text_area("tailored_json", st.session_state['tailored_text'], height=300)
    if st.button("Validate tailored JSON"):
        try:
            _ = json.loads(st.session_state['tailored_text'])
            st.success("Tailored JSON is valid")
        except Exception as e:
            st.error(f"Invalid JSON: {e}")


## Step 4: Generate final CV
st.markdown("---")
st.header("Step 4 — Generate final CV (PDF)")
st.info("Choose which data to use for final generation and click Generate. The server will produce a downloadable PDF.")

with st.form(key='generate_form'):
    choice = st.radio("Use data from:", ("Edited tailored JSON", "Tailored JSON", "Structured JSON"))
    gen_submit = st.form_submit_button("Generate Final PDF")

if gen_submit:
    # pick data source
    use_obj = None
    if choice == "Edited tailored JSON" and st.session_state.get('tailored_text'):
        try:
            use_obj = json.loads(st.session_state['tailored_text'])
        except Exception as e:
            st.error(f"Edited tailored JSON is invalid: {e}")
    elif choice == "Tailored JSON" and st.session_state.get('tailored_text'):
        try:
            use_obj = json.loads(st.session_state['tailored_text'])
        except:
            use_obj = None
    elif choice == "Structured JSON" and st.session_state.get('structured_text'):
        try:
            use_obj = json.loads(st.session_state['structured_text'])
        except Exception as e:
            st.error(f"Structured JSON is invalid: {e}")

    if use_obj is None:
        st.error("No valid data available for generation. Please validate your JSON first.")
    else:
        try:
            orig_contact_obj = json.loads(st.session_state['original_text']) if st.session_state.get('original_text') else None
        except Exception:
            orig_contact_obj = None
        payload = {
            "tailored_json": json.dumps({"tailored_data": use_obj, "original_contact": orig_contact_obj})
        }
        if orig_contact_obj:
            payload['original_contact'] = json.dumps(orig_contact_obj)
        try:
            with st.spinner("Generating PDF on server — this may take a moment..."):
                resp = requests.post(f"{backend_url}/generate-final-cv/", data=payload, headers=_headers(), timeout=180)

            if resp.status_code == 200:
                result = resp.json()
                download_link = result.get('download_link')
                if download_link:
                    full_url = backend_url.rstrip('/') + download_link
                    st.success("CV generated")
                    st.markdown(f"[Download final PDF]({full_url})")
                    try:
                        r = requests.get(full_url, timeout=60)
                        if r.status_code == 200:
                            st.download_button("Download PDF", data=r.content, file_name="Final_ATS_CV.pdf", mime="application/pdf")
                        else:
                            st.info("Could not fetch PDF for inline download; use the download link above")
                    except Exception:
                        st.info("Could not fetch PDF for inline download; use the download link above")
                    # refresh session info after generation
                    try:
                        info = fetch_session_info()
                        if info:
                            st.session_state['session_info'] = info
                            st.session_state['toast_msg'] = f"Session used: {info.get('uses')}/{info.get('max_uses')} — {info.get('remaining')} remaining"
                            st.experimental_rerun()
                    except Exception:
                        pass
                else:
                    st.error(f"No download link returned: {result}")
            else:
                st.error(f"Generation failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")


st.markdown("---")
#st.info("Tips: make sure your FastAPI server is running locally on http://localhost:8000. Install dependencies: streamlit, requests.")

# Session controls
st.sidebar.markdown("---")
st.sidebar.subheader("Session")
# Admin helper: paste an admin token and activate it for this session
admin_token_input = st.sidebar.text_input("Admin token (paste here)", type="password")
if st.sidebar.button("Use admin token"):
    if admin_token_input:
        st.session_state['session_token'] = admin_token_input
        st.experimental_set_query_params(token=st.session_state['session_token'])
        # refresh session info into session_state
        info = fetch_session_info()
        if info and info.get('is_admin'):
            st.sidebar.success("Admin session active — quota bypass enabled")
        else:
            st.sidebar.warning("Token set but not recognized as admin or session-info unavailable")
    else:
        st.sidebar.info("Paste an admin token first")



# Helpful notes
#st.info("Tips: run your FastAPI server locally on http://localhost:8000 and then use this Streamlit app to interact with it. Install dependencies: streamlit, requests.")
