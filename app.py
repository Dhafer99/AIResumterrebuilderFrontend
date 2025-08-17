import streamlit as st
import requests
import json
import io

st.set_page_config(page_title="AI Resume Rebuilder Frontend", layout="wide")

st.title("AI Resume Rebuilder — Streamlit Frontend")

BACKEND_DEFAULT = "http://localhost:8000"
backend_url = st.text_input("Backend URL", BACKEND_DEFAULT)

import streamlit as st
import requests
import json
import io

st.set_page_config(page_title="AI Resume Rebuilder", layout="wide")

def _init_state():
    for key, val in {
        'structured_text': None,
        'original_text': None,
        'tailored_text': None,
        'extracted_preview': None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

# Sidebar: settings for non-developers
st.sidebar.title("Settings")
st.sidebar.markdown("Enter the URL where the FastAPI backend is running and an optional API token.")
BACKEND_DEFAULT = "http://localhost:8000"
backend_url = st.sidebar.text_input("Backend URL", BACKEND_DEFAULT)
api_token = st.sidebar.text_input("API token (optional)", type="password")
st.sidebar.markdown("---")
st.sidebar.markdown("Steps: 1) Upload PDF → 2) Review/Edit → 3) Tailor (optional) → 4) Generate PDF")


def _headers():
    h = {}
    if api_token:
        h['Authorization'] = api_token
    return h


st.title("AI Resume Rebuilder — Easy Mode")
st.markdown("A simple, step-by-step interface to extract, review, tailor, and generate ATS-friendly resumes. Follow the steps below.")


## Step 1: Upload and extract
st.header("Step 1 — Upload CV (PDF)")
st.info("Upload a clean PDF of your resume. The app will extract text and try to parse contact and structured sections.")
uploaded_file = st.file_uploader("Choose a PDF file to upload", type=["pdf"]) 

if uploaded_file is not None:
    # size check
    try:
        size_mb = uploaded_file.size / (1024*1024)
    except Exception:
        size_mb = None
    if size_mb and size_mb > 10:
        st.warning("File is larger than 10 MB — extraction may take longer or fail.")
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
                else:
                    st.error(f"No download link returned: {result}")
            else:
                st.error(f"Generation failed: {resp.status_code} {resp.text}")
        except Exception as e:
            st.error(f"Error calling backend: {e}")


st.markdown("---")
st.write("Backend URL used:", backend_url)

st.info("Tips: make sure your FastAPI server is running and reachable at the Backend URL. Install dependencies: streamlit, requests.")
st.write("Backend URL used:", backend_url)



# Helpful notes
st.info("Tips: run your FastAPI server locally on http://localhost:8000 and then use this Streamlit app to interact with it. Install dependencies: streamlit, requests.")
