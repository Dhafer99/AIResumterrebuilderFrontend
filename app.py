import streamlit as st
import requests
import json
import io
import time

# Professional page configuration
st.set_page_config(
    page_title="AI Resume Rebuilder | Professional ATS Optimization",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling with mobile-only optimizations
st.markdown("""
<style>
    /* Hide Streamlit's top menu and footer */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #stDecoration {display:none;}
    header {visibility: hidden;}
    
    /* Desktop styles remain unchanged */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .step-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        margin: 1rem 0;
    }
    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 1rem 0;
    }
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .feature-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
    }
    .success-message {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* MOBILE-ONLY STYLES - These only apply to mobile devices */
    @media (max-width: 768px) {
        /* Black background for mobile */
        .stApp {
            background-color: #000000 !important;
        }
        .main .block-container {
            background-color: #000000 !important;
        }
        
        /* White text for mobile readability */
        .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
        .stApp div, .stApp span, .stApp label, .stMarkdown {
            color: #ffffff !important;
        }
        
        /* File uploader mobile styling */
        .stFileUploader label, .stFileUploader div, .stFileUploader span {
            color: #ffffff !important;
        }
        .stFileUploader [data-testid="stFileUploaderDropzone"] {
            background-color: #333333 !important;
            border: 2px dashed #cccccc !important;
            color: #ffffff !important;
        }
        
        /* Info/Warning/Success messages for mobile */
        .stInfo, .stInfo div, .stInfo p {
            background-color: rgba(102, 126, 234, 0.3) !important;
            color: #ffffff !important;
        }
        .stWarning, .stWarning div, .stWarning p {
            background-color: rgba(255, 193, 7, 0.3) !important;
            color: #ffffff !important;
        }
        .stSuccess, .stSuccess div, .stSuccess p {
            background-color: rgba(40, 167, 69, 0.3) !important;
            color: #ffffff !important;
        }
        
        /* Input fields for mobile */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #333333 !important;
            color: #ffffff !important;
            border: 1px solid #666666 !important;
        }
        .stTextInput label, .stTextArea label {
            color: #ffffff !important;
        }
        
        /* Buttons for mobile */
        .stButton > button {
            background-color: #667eea !important;
            color: #ffffff !important;
            border: none !important;
        }
        
        /* Sidebar for mobile */
        .css-1d391kg {
            background-color: #222222 !important;
        }
        
        /* Make header text more mobile-friendly */
        .main-header {
            padding: 1.5rem 1rem !important;
            font-size: 0.9em !important;
        }
        
        /* Smaller padding for cards on mobile */
        .stats-card, .feature-highlight {
            padding: 0.75rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* FIX FOR EXTRACTED TEXT AND JSON DISPLAY ON MOBILE */
        /* JSON viewer styling for mobile - dark background with light text */
        .stJson, .stJson div, .stJson pre, .stJson code {
            background-color: #1e1e1e !important;
            color: #d4d4d4 !important;
            border: 1px solid #444444 !important;
        }
        
        /* Expander content on mobile */
        .streamlit-expanderContent {
            background-color: #1a1a1a !important;
            color: #ffffff !important;
        }
        
        /* Code blocks and preformatted text */
        pre, code {
            background-color: #1e1e1e !important;
            color: #d4d4d4 !important;
            padding: 0.5rem !important;
            border-radius: 4px !important;
        }
        
        /* Text areas with JSON or extracted content */
        .stTextArea textarea {
            background-color: #1e1e1e !important;
            color: #d4d4d4 !important;
            border: 1px solid #444444 !important;
        }
        
        /* Ensure all content containers have proper background */
        [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {
            background-color: transparent !important;
        }
        
        /* Fix for any remaining white backgrounds in content areas */
        .element-container, .stMarkdown, .stText {
            background-color: transparent !important;
        }
    }
    
    /* FIX FOR BUTTON VISIBILITY ISSUES - DESKTOP AND MOBILE */
    
    /* Credit usage information - ensure text is always visible with highest specificity */
    .credit-usage-info, .credit-usage-info *, 
    .credit-usage-info strong, .credit-usage-info em, 
    .credit-usage-info br + text, .credit-usage-info text {
        color: #333333 !important;
    }
    
    /* Desktop AND Mobile override for credit usage - very specific and forceful */
    .stApp .credit-usage-info,
    .stApp .credit-usage-info *,
    .stApp .credit-usage-info strong,
    .stApp .credit-usage-info em,
    .stApp .credit-usage-info div,
    .stApp .credit-usage-info span {
        color: #333333 !important;
    }
    
    /* Mobile override for credit usage - very specific */
    @media (max-width: 768px) {
        .stApp .credit-usage-info,
        .stApp .credit-usage-info *,
        .stApp .credit-usage-info strong,
        .stApp .credit-usage-info em,
        .stApp .credit-usage-info div,
        .stApp .credit-usage-info span {
            color: #333333 !important;
        }
    }
    
    /* Desktop button fixes */
    @media (min-width: 769px) {
        /* File uploader button */
        .stFileUploader button {
            background-color: #667eea !important;
            color: white !important;
            border: 1px solid #667eea !important;
        }
        
        /* Selectbox (dropdown) styling */
        .stSelectbox > div > div {
            background-color: white !important;
            color: #333333 !important;
            border: 1px solid #cccccc !important;
        }
        
        /* All buttons general styling */
        .stButton > button {
            background-color: #667eea !important;
            color: white !important;
            border: 1px solid #667eea !important;
        }
        
        /* Ensure selectbox text is visible */
        .stSelectbox label {
            color: #333333 !important;
        }
    }
    
    /* Mobile button fixes */
    @media (max-width: 768px) {
        /* File uploader button */
        .stFileUploader button {
            background-color: #667eea !important;
            color: white !important;
            border: 1px solid #667eea !important;
        }
        
        /* Selectbox (dropdown) styling for mobile */
        .stSelectbox > div > div {
            background-color: #333333 !important;
            color: white !important;
            border: 1px solid #666666 !important;
        }
        
        /* All buttons for mobile */
        .stButton > button {
            background-color: #667eea !important;
            color: white !important;
            border: 1px solid #667eea !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# LocalStorage session management functions
def init_session_from_storage():
    """Initialize session from localStorage using JavaScript"""
    st.components.v1.html("""
    <script>
    // Function to get session data from localStorage
    function getSessionFromStorage() {
        const sessionData = localStorage.getItem('ai_resume_session');
        if (sessionData) {
            try {
                return JSON.parse(sessionData);
            } catch (e) {
                console.error('Error parsing session data:', e);
                localStorage.removeItem('ai_resume_session');
            }
        }
        return null;
    }
    
    // Function to save session data to localStorage
    function saveSessionToStorage(sessionData) {
        try {
            localStorage.setItem('ai_resume_session', JSON.stringify(sessionData));
        } catch (e) {
            console.error('Error saving session data:', e);
        }
    }
    
    // Function to clear session data
    function clearSessionStorage() {
        localStorage.removeItem('ai_resume_session');
    }
    
    // Function to check if session is expired
    function isSessionExpired(sessionData) {
        if (!sessionData.expires_at) return false;
        return new Date() > new Date(sessionData.expires_at);
    }
    
    // Function to send session data to Streamlit
    function sendSessionToStreamlit() {
        const sessionData = getSessionFromStorage();
        if (sessionData && !isSessionExpired(sessionData)) {
            // Send to Streamlit via query params
            const urlParams = new URLSearchParams(window.location.search);
            if (!urlParams.get('token')) {
                urlParams.set('token', sessionData.token);
                const newUrl = window.location.pathname + '?' + urlParams.toString();
                window.history.replaceState({}, '', newUrl);
            }
            
            // Trigger a custom event that Streamlit can listen to
            window.dispatchEvent(new CustomEvent('sessionRestored', {
                detail: sessionData
            }));
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        sendSessionToStreamlit();
    });
    
    // Run immediately if DOM is already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', sendSessionToStreamlit);
    } else {
        sendSessionToStreamlit();
    }
    </script>
    """, height=0)

def save_session_to_storage(session_token, session_info=None):
    """Save session data to localStorage using JavaScript"""
    session_data = {
        'token': session_token,
        'timestamp': time.time(),
        'expires_at': None
    }
    
    if session_info:
        session_data.update({
            'uses': session_info.get('uses', 0),
            'max_uses': session_info.get('max_uses', 0),
            'remaining': session_info.get('remaining', 0),
            'is_admin': session_info.get('is_admin', False),
            'expires_at': session_info.get('expires_at')
        })
    
    st.components.v1.html(f"""
    <script>
    function saveSession() {{
        const sessionData = {json.dumps(session_data)};
        try {{
            localStorage.setItem('ai_resume_session', JSON.stringify(sessionData));
            console.log('Session saved to localStorage:', sessionData);
        }} catch (e) {{
            console.error('Error saving session:', e);
        }}
    }}
    saveSession();
    </script>
    """, height=0)

def clear_session_storage():
    """Clear session data from localStorage"""
    st.components.v1.html("""
    <script>
    localStorage.removeItem('ai_resume_session');
    console.log('Session cleared from localStorage');
    </script>
    """, height=0)

def get_session_from_storage():
    """Get session data from localStorage via query params"""
    # First check query params (set by JavaScript)
    query_params = st.query_params
    if "token" in query_params:
        return query_params["token"]
    return None

# Professional header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Resume Rebuilder</h1>
    <h3>Professional ATS-Optimized Resume Generation</h3>
    <p>Transform your resume with AI-powered analysis and optimization</p>
</div>
""", unsafe_allow_html=True)

# Fixed backend URL (not editable in UI for normal users)
backend_url = "https://9bc1aeec0fb7.ngrok-free.app/"

# Restore session token from URL query parameters on app load
query_params = st.query_params
if "token" in query_params:
    st.session_state.token = query_params["token"]

# If a token exists in session_state, persist it to the URL
if st.session_state.get("token"):
    st.query_params["token"] = st.session_state.token

def _init_state():
    """Initialize session state with professional progress tracking"""
    for key, val in {
        'structured_text': None,
        'original_text': None,
        'tailored_text': None,
        'extracted_preview': None,
        'step_completed': {1: False, 2: False, 3: False, 4: False},
        'progress_percentage': 0,
        'session_from_storage': False
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val
    # session token storage
    if 'session_token' not in st.session_state:
        st.session_state['session_token'] = None
    # ensure we only attempt auto-create once per user entrance
    if 'session_initialized' not in st.session_state:
        st.session_state['session_initialized'] = False

def update_progress():
    """Update progress based on completed steps"""
    completed_steps = sum(1 for completed in st.session_state['step_completed'].values() if completed)
    st.session_state['progress_percentage'] = (completed_steps / 4) * 100

def show_progress_bar():
    """Display professional progress bar"""
    progress = st.session_state.get('progress_percentage', 0)
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress}%"></div>
    </div>
    <p style="text-align: center; color: #666; font-size: 0.9em;">
        Progress: {progress:.0f}% Complete • Step {sum(1 for completed in st.session_state['step_completed'].values() if completed)} of 4
    </p>
    """, unsafe_allow_html=True)


_init_state()

# Persist session token into query params if available, so reloads keep the same token
if st.session_state.get('session_token'):
    st.query_params["token"] = st.session_state['session_token']

# Attempt to restore session token from query params on load
try:
    q = st.query_params
    qtoken = q.get('token')
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
    """Try to restore session from localStorage first, then create a demo session if needed."""
    
    # First, try to restore from localStorage via JavaScript
    if not st.session_state.get('session_from_storage'):
        init_session_from_storage()
        st.session_state['session_from_storage'] = True
    
    # Check if we got a token from localStorage (via query params)
    storage_token = get_session_from_storage()
    if storage_token and not st.session_state.get('session_token'):
        st.session_state['session_token'] = storage_token
        # Fetch session info for this token
        info = fetch_session_info()
        if info:
            st.session_state['session_info'] = info
            # Check if session is still valid (not expired and has remaining uses)
            if not info.get('is_admin', False) and info.get('remaining', 0) <= 0:
                st.warning("⚠️ **Stored Session Exhausted**: Your saved session has no remaining credits. Creating a new demo session...")
                # Clear the exhausted session
                clear_session_storage()
                st.session_state['session_token'] = None
                st.session_state['session_info'] = None
            else:
                st.session_state['session_initialized'] = True
                return
    
    # If we have a valid session token, don't create a new one
    if st.session_state.get('session_token'):
        st.session_state['session_initialized'] = True
        return
    
    # If initialization already attempted, don't try again
    if st.session_state.get('session_initialized'):
        return
    
    # Create a new demo session
    try:
        sresp = requests.post(f"{backend_url}/session", data={'ttl_minutes': 60, 'max_uses': 4}, timeout=4)
        if sresp.status_code == 200:
            token = sresp.json().get('token')
            st.session_state['session_token'] = token
            
            # Fetch session info and save to localStorage
            info = fetch_session_info()
            if info:
                st.session_state['session_info'] = info
                save_session_to_storage(token, info)
                st.success("✅ New demo session created and saved!")
    except Exception:
        pass
    finally:
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

# Professional sidebar with enhanced information
st.sidebar.markdown("""
<div style="background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
    <h2 style="color: white; text-align: center;">⚙️ Control Panel</h2>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 🎯 How it Works")
st.sidebar.markdown("""
**Step 1:** Upload your PDF resume  
**Step 2:** Review extracted data  
**Step 3:** Tailor to job (optional)  
**Step 4:** Generate optimized PDF  
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Features")
st.sidebar.markdown("""
✅ AI-powered text extraction  
✅ ATS compatibility analysis  
✅ Job-specific tailoring  
✅ Professional PDF generation  
✅ Real-time editing  
""")

st.sidebar.markdown("---")


def _headers():
    h = {}
    # Use session token (Bearer) if available
    if st.session_state.get('session_token'):
        h['Authorization'] = f"Bearer {st.session_state['session_token']}"
    return h


# Professional helper functions
def fetch_session_info():
    """Fetch session info from backend and store in session_state and localStorage"""
    token = st.session_state.get('session_token')
    if not token:
        return None
    try:
        headers = {'Authorization': f"Bearer {token}"}
        resp = requests.get(f"{backend_url}/session-info", headers=headers, timeout=5)
        if resp.status_code == 200:
            info = resp.json()
            st.session_state['session_info'] = info
            # Save updated session info to localStorage
            save_session_to_storage(token, info)
            return info
    except Exception:
        return None
    return None

def _headers():
    """Get authorization headers for API requests"""
    h = {}
    # Use session token (Bearer) if available
    if st.session_state.get('session_token'):
        h['Authorization'] = f"Bearer {st.session_state['session_token']}"
    return h

def handle_api_error(response, operation_name="operation"):
    """Handle API errors with user-friendly messages"""
    if response.status_code == 401:
        st.error("🔐 **Authentication Required**: Please refresh your session or contact support for a premium token.")
    elif response.status_code == 429:
        st.error("⏰ **Usage Limit Reached**: You've exceeded your free usage quota. Contact the developer for a premium token to continue using the service unlimited.")
        st.info("💡 **Need more usage?** Scroll down to the 'About the Developer' section to get a premium token!")
    elif response.status_code == 413:
        st.error("📄 **File Too Large**: Please use a smaller PDF file (under 10MB).")
    elif response.status_code == 422:
        st.error("📋 **Invalid Data**: Please check your input and try again.")
    elif response.status_code >= 500:
        st.error(f"🔧 **Service Temporarily Unavailable**: Our AI service is currently experiencing issues. Please try again in a few moments.")
    else:
        try:
            error_detail = response.json().get('detail', 'Unknown error')
            st.error(f"❌ **{operation_name.title()} Failed**: {error_detail}")
        except:
            st.error(f"❌ **{operation_name.title()} Failed**: Status code {response.status_code}")

# Show professional progress tracking
show_progress_bar()

# Enhanced session info display
session_info = st.session_state.get('session_info') or fetch_session_info()

# Professional toast messages using st.toast (more reliable)
if st.session_state.get('toast_msg'):
    try:
        msg = st.session_state.pop('toast_msg')
        st.toast(msg, icon="✅")
    except Exception:
        st.session_state.pop('toast_msg', None)

# Professional session status display
if session_info:
    uses = session_info.get('uses', 0)
    max_uses = session_info.get('max_uses', 0)
    remaining = session_info.get('remaining', 0)
    is_admin = session_info.get('is_admin', False)
    
    if is_admin:
        st.markdown(f"""
        <div class="stats-card">
            <h4>🔑 Admin Session Active</h4>
            <p>Unlimited usage • Admin privileges enabled</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="stats-card">
            <h4>📊 Session Status</h4>
            <p>Used: {uses}/{max_uses} • Remaining: {remaining} credits</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Credit usage information
        st.markdown("""
        <div class="credit-usage-info" style="background: #f8f9fa; border: 2px solid #667eea; padding: 1rem; border-radius: 8px; color: #333; margin: 0.5rem 0; font-size: 1.1em;">
            <strong style="color: #667eea;">💡 Credit Usage:</strong> Each AI-powered step consumes 1 credit:<br>
            • <strong>Step 1:</strong> Resume extraction & parsing (1 credit)<br>
            • <strong>Step 3:</strong> Job-specific tailoring (1 credit)<br>
            • <strong>Step 4:</strong> PDF generation (1 credit)<br>
            <em style="color: #28a745;">Step 2 (editing) is free and doesn't consume credits.</em>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Session", key='refresh_session', use_container_width=True):
            new_info = fetch_session_info()
            if new_info:
                st.success("✅ Session refreshed")
                st.rerun()
            else:
                st.error("❌ Could not refresh session info")


## 📄 Step 1: Upload and Extract Resume
st.markdown("""
<div class="step-header">
    <h2>📄 Step 1: Upload Your Resume (PDF)</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-highlight">
    <strong>🎯 What happens next:</strong><br>
    • AI will extract text from your PDF<br>
    • Parse contact information automatically<br>
    • Structure your experience and skills<br>
    • Prepare data for ATS optimization
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📎 Choose your resume PDF file", 
    type=["pdf"],
    help="Upload a clean, well-formatted PDF of your current resume"
) 

if uploaded_file is not None:
    # Professional file info display
    try:
        size_mb = uploaded_file.size / (1024*1024)
    except Exception:
        size_mb = None
    
    # File info card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
        <h4>📋 File Ready for Processing</h4>
        <p><strong>Filename:</strong> {uploaded_file.name}</p>
        <p><strong>Size:</strong> {size_mb:.2f} MB</p>
        <p><strong>Status:</strong> {'⚠️ Large file - may take longer' if size_mb and size_mb > 10 else '✅ Optimal size'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Professional extract button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        extract_clicked = st.button(
            "🚀 Extract & Parse Resume", 
            key='extract_button',
            use_container_width=True,
            type="primary"
        )
    if extract_clicked:
        # Professional session creation
        if not st.session_state.get('session_token'):
            with st.spinner("🔧 Setting up your session..."):
                try:
                    sresp = requests.post(f"{backend_url}/session", data={'ttl_minutes': 60, 'max_uses': 100}, timeout=10)
                    if sresp.status_code == 200:
                        token = sresp.json().get('token')
                        st.session_state['session_token'] = token
                        st.query_params["token"] = token
                        
                        # Fetch session info and save to localStorage
                        try:
                            info = fetch_session_info()
                            if info:
                                st.session_state['session_info'] = info
                                save_session_to_storage(token, info)
                        except Exception:
                            pass
                        
                        st.success("✅ Demo session created and saved to browser!")
                    else:
                        # Silently handle session creation failure
                        pass
                except Exception:
                    # Silently handle session creation failure
                    pass

        # Professional file processing
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        try:
            with st.spinner("🤖 AI is analyzing your resume... This may take 30-60 seconds"):
                # Add progress simulation for better UX
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)  # Simulate progress
                    progress_bar.progress(i + 1)
                
                resp = requests.post(f"{backend_url}/extract-cv-json/", files=files, headers=_headers(), timeout=180)
                progress_bar.empty()
                
            if resp.status_code == 200:
                data = resp.json()
                structured = data.get("structured_data")
                original_contact = data.get("original_contact")
                extracted = data.get("extracted_text")
                
                # Mark step as completed
                st.session_state['step_completed'][1] = True
                update_progress()
                
                # Professional success message
                st.markdown("""
                <div class="success-message">
                    🎉 Extraction Complete! Your resume has been successfully processed.
                </div>
                """, unsafe_allow_html=True)
                
                # Store extracted data
                st.session_state['extracted_preview'] = extracted[:2000] if extracted else None
                st.session_state['structured_text'] = json.dumps(structured, indent=2) if structured else None
                st.session_state['original_text'] = json.dumps(original_contact or {}, indent=2)

                # Update session info and show usage notification
                try:
                    info = fetch_session_info()
                    if info:
                        st.session_state['session_info'] = info
                        uses = info.get('uses', 0)
                        max_uses = info.get('max_uses', 0)
                        remaining = info.get('remaining', 0)
                        is_admin = info.get('is_admin', False)
                        
                        if is_admin:
                            st.info("🔑 **Admin Account**: You have unlimited usage!")
                        else:
                            if remaining > 0:
                                st.info(f"📊 **Usage Update**: You have **{remaining} uses remaining** out of {max_uses} total.")
                            else:
                                st.warning("⚠️ **Usage Limit Reached**: You've used all your free attempts. Contact the developer below for premium access!")
                        
                        st.session_state['toast_msg'] = f"🎯 Step 1 Complete! Session: {info.get('uses')}/{info.get('max_uses')} used"
                        st.rerun()
                except Exception:
                    pass
            else:
                handle_api_error(resp, "resume extraction")
        except Exception as e:
            st.error(f"🌐 **Connection Error**: Unable to connect to the AI service. Please check your internet connection and try again.")


## 📝 Step 2: Review and Edit Extracted Data
st.markdown("---")
st.markdown("""
<div class="step-header">
    <h2>📝 Step 2: Review & Edit Extracted Data</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-highlight">
    <strong>🔍 Quality Check:</strong><br>
    • Review AI-extracted information for accuracy<br>
    • Edit contact details if needed<br>
    • Validate JSON structure before proceeding<br>
    • Ensure all important details are captured
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1,1])
with col1:
    st.markdown("### 🤖 AI-Extracted Structure")
    if st.session_state.get('structured_text'):
        st.json(json.loads(st.session_state['structured_text']))
        
        with st.expander("✏️ Edit Structured Data", expanded=False):
            st.markdown("**⚠️ Advanced:** Only edit if you need to correct AI extraction errors")
            st.session_state['structured_text'] = st.text_area(
                "Structured JSON Data", 
                st.session_state['structured_text'], 
                height=300,
                help="This contains your experience, skills, and education data"
            )
            
            col_validate1, col_validate2 = st.columns([1, 1])
            with col_validate1:
                if st.button("✅ Validate Structure", key="validate_structured"):
                    try:
                        json.loads(st.session_state['structured_text'])
                        st.success("✅ Valid JSON structure!")
                        st.session_state['step_completed'][2] = True
                        update_progress()
                    except Exception as e:
                        st.error(f"❌ Invalid JSON: {e}")
    else:
        st.info("🔄 No structured data yet — complete Step 1 first.")

with col2:
    st.markdown("### 📞 Contact Information")
    if st.session_state.get('original_text'):
        contact_data = json.loads(st.session_state['original_text'])
        st.json(contact_data)
        
        with st.expander("✏️ Edit Contact Details", expanded=True):
            st.markdown("**📝 Common edits:** Update phone, email, or LinkedIn URL")
            st.session_state['original_text'] = st.text_area(
                "Contact JSON Data", 
                st.session_state['original_text'], 
                height=300,
                help="Your contact information (name, email, phone, etc.)"
            )
            
            col_validate3, col_validate4 = st.columns([1, 1])
            with col_validate3:
                if st.button("✅ Validate Contact", key="validate_contact"):
                    try:
                        json.loads(st.session_state['original_text'])
                        st.success("✅ Valid contact JSON!")
                    except Exception as e:
                        st.error(f"❌ Invalid JSON: {e}")
    else:
        st.info("🔄 No contact data yet — complete Step 1 first.")


## 🎯 Step 3: Job-Specific Tailoring (Optional)
st.markdown("---")
st.markdown("""
<div class="step-header">
    <h2>🎯 Step 3: Tailor to Job Description (Optional)</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-highlight">
    <strong>🚀 ATS Optimization:</strong><br>
    • Paste target job description<br>
    • AI will optimize keywords and phrases<br>
    • Tailored content improves ATS scores<br>
    • Skip this step for general-purpose resume
</div>
""", unsafe_allow_html=True)

with st.form(key='tailor_form'):
    st.markdown("### 📋 Job Description")
    job_description = st.text_area(
        "Paste the job description here", 
        height=200,
        placeholder="Copy and paste the full job description from the company's posting...",
        help="The more detailed the job description, the better the AI can tailor your resume"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        rewrite_style = st.selectbox(
            "🎨 Tailoring Style", 
            ["keywords", "minimal", "full"], 
            index=0,
            help="Keywords: Focus on matching key terms | Minimal: Light adjustments | Full: Comprehensive rewrite"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        tailor_submit = st.form_submit_button(
            "🎯 Tailor Resume with AI", 
            use_container_width=True,
            type="primary"
        )

if tailor_submit:
    if not st.session_state.get('structured_text'):
        st.error("❌ No structured data available — please complete Step 1 first.")
    else:
        # Validate structured data
        try:
            cv_json = json.loads(st.session_state['structured_text'])
        except Exception as e:
            st.error(f"❌ Structured JSON is invalid: {e}")
            cv_json = None
        
        # Validate contact data    
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
                with st.spinner("🤖 AI is tailoring your resume... This may take 45-90 seconds"):
                    # Progress bar for better UX
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    
                    resp = requests.post(f"{backend_url}/tailor-json-to-ats/", data=payload, headers=_headers(), timeout=180)
                    progress_bar.empty()
                    
                if resp.status_code == 200:
                    result = resp.json()
                    tailored = result.get('tailored_data') or result.get('tailored') or {}
                    
                    # Mark step as completed
                    st.session_state['step_completed'][3] = True
                    update_progress()
                    
                    st.markdown("""
                    <div class="success-message">
                        🎉 Tailoring Complete! Your resume has been optimized for this specific job.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state['tailored_text'] = json.dumps(tailored, indent=2)
                    
                    with st.expander("📊 View Tailored Results", expanded=True):
                        st.json(tailored)
                    
                    # Update session info and show usage notification
                    try:
                        info = fetch_session_info()
                        if info:
                            st.session_state['session_info'] = info
                            uses = info.get('uses', 0)
                            max_uses = info.get('max_uses', 0)
                            remaining = info.get('remaining', 0)
                            is_admin = info.get('is_admin', False)
                            
                            if is_admin:
                                st.info("🔑 **Admin Account**: You have unlimited usage!")
                            else:
                                if remaining > 0:
                                    st.info(f"📊 **Usage Update**: You have **{remaining} uses remaining** out of {max_uses} total.")
                                else:
                                    st.warning("⚠️ **Usage Limit Reached**: You've used all your free attempts. Contact the developer below for premium access!")
                            
                            # Show immediate toast notification
                            st.toast(f"🎯 Step 3 Complete! {uses}/{max_uses} uses consumed", icon="✅")
                            st.session_state['toast_msg'] = f"🎯 Step 3 Complete! Session: {info.get('uses')}/{info.get('max_uses')} used"
                    except Exception:
                        pass
                else:
                    handle_api_error(resp, "resume tailoring")
            except Exception as e:
                st.error(f"🌐 **Connection Error**: Unable to connect to the AI service. Please check your internet connection and try again.")

# Tailored content editing section
if st.session_state.get('tailored_text'):
    st.markdown("### ✏️ Fine-tune Tailored Content")
    with st.expander("📝 Edit Tailored JSON (Optional)", expanded=False):
        st.markdown("**💡 Tip:** You can make final adjustments to the AI-tailored content")
        st.session_state['tailored_text'] = st.text_area(
            "Tailored JSON Data", 
            st.session_state['tailored_text'], 
            height=300,
            help="The AI-tailored version of your resume data"
        )
        if st.button("✅ Validate Tailored JSON", key="validate_tailored"):
            try:
                json.loads(st.session_state['tailored_text'])
                st.success("✅ Tailored JSON is valid!")
            except Exception as e:
                st.error(f"❌ Invalid JSON: {e}")

## 📄 Step 4: Generate Professional PDF
st.markdown("---")
st.markdown("""
<div class="step-header">
    <h2>📄 Step 4: Generate Professional PDF</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-highlight">
    <strong>🎨 Final Output:</strong><br>
    • Choose your preferred data source<br>
    • Generate ATS-optimized PDF format<br>
    • Download ready-to-submit resume<br>
    • Professional formatting applied automatically
</div>
""", unsafe_allow_html=True)

with st.form(key='generate_form'):
    st.markdown("### 📊 Choose Data Source")
    
    # Smart default selection based on available data
    default_choice = 0
    if st.session_state.get('tailored_text'):
        default_choice = 0  # Tailored
    elif st.session_state.get('structured_text'):
        default_choice = 2  # Structured
    
    choice = st.radio(
        "Select the data version to use for PDF generation:",
        ("🎯 Tailored Data (Recommended)", "📝 Edited Tailored Data", "📋 Original Structured Data"),
        index=default_choice,
        help="Tailored data is optimized for ATS systems and specific job requirements"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gen_submit = st.form_submit_button(
            "🚀 Generate Professional PDF", 
            use_container_width=True,
            type="primary"
        )

if gen_submit:
    # Determine data source based on choice
    use_obj = None
    data_source = ""
    
    if choice == "📝 Edited Tailored Data" and st.session_state.get('tailored_text'):
        try:
            use_obj = json.loads(st.session_state['tailored_text'])
            data_source = "edited tailored"
        except Exception as e:
            st.error(f"❌ Edited tailored JSON is invalid: {e}")
    elif choice == "🎯 Tailored Data (Recommended)" and st.session_state.get('tailored_text'):
        try:
            use_obj = json.loads(st.session_state['tailored_text'])
            data_source = "tailored"
        except:
            use_obj = None
    elif choice == "📋 Original Structured Data" and st.session_state.get('structured_text'):
        try:
            use_obj = json.loads(st.session_state['structured_text'])
            data_source = "structured"
        except Exception as e:
            st.error(f"❌ Structured JSON is invalid: {e}")

    if use_obj is None:
        st.error("❌ No valid data available for generation. Please validate your JSON first.")
    else:
        # Prepare contact data
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
            with st.spinner(f"🎨 Generating professional PDF from {data_source} data... This may take 30-45 seconds"):
                # Progress simulation
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                resp = requests.post(f"{backend_url}/generate-final-cv/", data=payload, headers=_headers(), timeout=180)
                progress_bar.empty()

            if resp.status_code == 200:
                result = resp.json()
                download_link = result.get('download_link')
                
                if download_link:
                    # Mark final step as completed
                    st.session_state['step_completed'][4] = True
                    update_progress()
                    
                    st.markdown("""
                    <div class="success-message">
                        🎉 PDF Generated Successfully! Your professional resume is ready for download.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    full_url = backend_url.rstrip('/') + download_link
                    
                    # Download options
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown(f"🔗 **[Download PDF from Server]({full_url})**")
                    
                    with col2:
                        try:
                            r = requests.get(full_url, timeout=60)
                            if r.status_code == 200:
                                st.download_button(
                                    "⬇️ Download PDF File", 
                                    data=r.content, 
                                    file_name="Professional_Resume_ATS.pdf", 
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            else:
                                st.info("💡 Use the download link above to get your PDF")
                        except Exception:
                            st.info("💡 Use the download link above to get your PDF")
                    
                    # Update session info and show final usage notification
                    try:
                        info = fetch_session_info()
                        if info:
                            st.session_state['session_info'] = info
                            uses = info.get('uses', 0)
                            max_uses = info.get('max_uses', 0)
                            remaining = info.get('remaining', 0)
                            is_admin = info.get('is_admin', False)
                            
                            if is_admin:
                                st.info("🔑 **Admin Account**: You have unlimited usage for future resumes!")
                            else:
                                if remaining > 0:
                                    st.info(f"🎉 **Success!** You have **{remaining} uses remaining** for creating more resumes.")
                                else:
                                    st.warning("⚠️ **All Uses Consumed**: You've used all your free attempts. Contact the developer below for premium access to create more resumes!")
                            
                            # Show immediate toast notification
                            st.toast(f"🎉 Resume Complete! {uses}/{max_uses} uses consumed", icon="🎉")
                            st.session_state['toast_msg'] = f"🎉 Resume Complete! Session: {info.get('uses')}/{info.get('max_uses')} used"
                    except Exception:
                        pass
                else:
                    st.error(f"❌ No download link returned from service")
            else:
                handle_api_error(resp, "PDF generation")
        except Exception as e:
            st.error(f"🌐 **Connection Error**: Unable to connect to the AI service. Please check your internet connection and try again.")


# Professional footer and session controls
st.markdown("---")

## 👨‍💻 About the Developer
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; color: white; margin: 2rem 0;">
    <div style="text-align: center;">
        <h2>👨‍💻 Meet the Developer</h2>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    try:
        st.image("me.jpg", width=250, caption="Dhafer Souid")
    except:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); padding: 2rem; border-radius: 10px; text-align: center; color: white;">
            <h3>👨‍💻 Dhafer Souid</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # 3D Avatar Model below the photo
    try:
        with open("model3.glb", "rb") as f:
            model_data = f.read()
        
        st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0;">
            <h3 style="color: #667eea; margin-bottom: 0.5rem;">👋 Hey, That's Me!</h3>
            <p style="color: #666; font-size: 1.1em; margin-bottom: 1rem;">🎯 Interactive 3D Avatar - Drag to move </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display 3D model using HTML with model-viewer (bigger size)
        st.components.v1.html(f"""
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <div style="display: flex; justify-content: center; align-items: center; height: 400px;">
            <model-viewer 
                src="data:model/gltf-binary;base64,{__import__('base64').b64encode(model_data).decode()}"
                alt="Dhafer Souid 3D Avatar"
                auto-rotate
                autoplay
                camera-controls
                style="width: 320px; height: 320px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);"
                exposure="1.2"
                shadow-intensity="1.5">
            </model-viewer>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <p style="color: #667eea; font-weight: bold; font-size: 1em;">📞 Ready to collaborate? Let's connect!</p>
            <small style="color: #666;">🖱️ Click and drag to rotate • Scroll to zoom</small>
        </div>
        """, height=450)
        
    except Exception as e:
        # If 3D model fails, just show a placeholder
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
            <p>🎯 3D Avatar Loading...</p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    ### 🎓 Dhafer Souid
    **Fresh Graduate | Software Developer**
    
    Hi! I'm Dhafer, a passionate fresh graduate who built this AI Resume Rebuilder to help job seekers create ATS-optimized resumes using cutting-edge AI technology.
    
    #### 🚀 What I Do:
    - **AI Development**: Building intelligent applications that solve real-world problems
    - **Software Development**: Creating end-to-end solutions with modern technologies
    - **Resume Optimization**: Helping professionals stand out in competitive job markets
    
    #### 💡 About This Project:
    This application demonstrates expertise in:
    - **AI Integration**: Seamless AI-powered text processing and optimization
    - **User Experience**: Modern, intuitive interface design
    - **Cloud Solutions**: Scalable deployment and session management
    
    ---
    
    ### 🌟 Want More Usage?
    
    **Need unlimited access or premium features?**
    
    If you find this tool valuable and want extended usage beyond the free tier, I'd be happy to provide you with a **premium user token** for unlimited resume processing.
    
    📧 **Contact me for premium access:**
    - **Email**: [dhafer.souid@esprit.tn](mailto:dhafer.souid@esprit.tn)
    - **LinkedIn**: [Connect with Dhafer Souid](https://www.linkedin.com/in/dhafer-souid-46b88b11b)
    - **GitHub**: Check out my other projects and contributions
    
    💼 *I'm also open to freelance projects and full-time opportunities!*
    """)

st.markdown("""
<div class="feature-highlight" style="text-align: center; margin: 2rem 0;">
    <h3>🎉 Thank You for Using AI Resume Rebuilder!</h3>
    <p>Your feedback and success stories motivate me to keep improving this tool.</p>
    <p><strong>💡 Pro Tip:</strong> Bookmark this page and share it with friends who need resume help!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin: 2rem 0;">
    <h3>🎉 Congratulations!</h3>
    <p>You've created a professional, ATS-optimized resume using AI technology.</p>
    <p><strong>💡 Pro Tips:</strong> Save this URL with your session token to return later | Share with friends | Use for multiple job applications</p>
</div>
""", unsafe_allow_html=True)

# Enhanced sidebar session controls
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
    <h4>🔑 Premium User Access(more usages)</h4>
</div>
""", unsafe_allow_html=True)

admin_token_input = st.sidebar.text_input(
    "🔐 Premium user Token", 
    type="password",
    placeholder="Paste admin token here...",
    help="Admin tokens provide unlimited usage"
)

if st.sidebar.button("🔑 Activate Premium Token", use_container_width=True):
    if admin_token_input:
        st.session_state['session_token'] = admin_token_input
        
        # Fetch session info to validate the token
        info = fetch_session_info()
        if info and info.get('is_admin'):
            st.session_state['session_info'] = info
            # Save admin session to localStorage
            save_session_to_storage(admin_token_input, info)
            st.query_params["token"] = admin_token_input
            st.sidebar.success("✅ Admin session activated and saved!")
            st.sidebar.balloons()
        else:
            st.sidebar.warning("⚠️ Token not recognized as admin")
            # Clear invalid token from storage
            clear_session_storage()
    else:
        st.sidebar.error("❌ Please enter a token first")

# Session Management Section
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
    <h4>💾 Session Management</h4>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🔄 Refresh", use_container_width=True):
        info = fetch_session_info()
        if info:
            st.success("✅ Session updated!")
            st.rerun()

with col2:
    if st.button("🗑️ Clear Session", use_container_width=True):
        clear_session_storage()
        st.session_state['session_token'] = None
        st.session_state['session_info'] = None
        st.query_params.clear()
        st.success("✅ Session cleared!")
        st.rerun()

# Show session storage status
if st.session_state.get('session_info'):
    info = st.session_state['session_info']
    storage_status = "💾 Saved in browser" if st.session_state.get('session_token') else "⚠️ Not saved"
    st.sidebar.markdown(f"""
    <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 4px; font-size: 0.8em; margin: 0.5rem 0;">
        <strong>Storage:</strong> {storage_status}<br>
        <strong>Type:</strong> {'Admin' if info.get('is_admin') else 'Demo'}<br>
        <strong>Credits:</strong> {info.get('remaining', 0)} remaining
    </div>
    """, unsafe_allow_html=True)

# Professional footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    <p>🤖 <strong>AI Resume Rebuilder</strong></p>
    <p>Powered by AI • Professional Results</p>
    <p>© 2025 | Built with ❤️ and Streamlit</p>
</div>
""", unsafe_allow_html=True)
