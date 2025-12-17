"""
Fraud Detection Agent - Streamlit App
PRODUCTION VERSION - For Databricks Apps deployment
Enhanced with Modern UI/UX

Pattern based on databricks-ai-ticket-vectorsearch project
"""

import streamlit as st
import os
from databricks.sdk import WorkspaceClient
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Fraud Detection | Intelligent Claims Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Futuristic Databricks Theme (Dark Teal/Cyan)
st.markdown("""
<style>
    /* Main theme colors - Databricks Futuristic */
    :root {
        --primary-cyan: #00D9FF;
        --secondary-teal: #00B8D4;
        --dark-bg: #0A1929;
        --darker-bg: #071318;
        --card-bg: #132F3F;
        --border-glow: rgba(0, 217, 255, 0.3);
        --text-primary: #E0F7FA;
        --text-secondary: #80DEEA;
        --success-green: #00E676;
        --danger-red: #FF1744;
        --warning-amber: #FFC107;
    }
    
    /* Global background */
    .stApp {
        background: linear-gradient(135deg, #0A1929 0%, #071318 100%);
        color: var(--text-primary);
    }
    
    /* Main content area */
    .main {
        background: transparent;
    }
    
    /* Enhanced sidebar - Databricks dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071318 0%, #0A1929 100%);
        border-right: 1px solid rgba(0, 217, 255, 0.2);
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    /* Futuristic buttons with glow */
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 184, 212, 0.1) 100%);
        border: 2px solid var(--primary-cyan);
        border-radius: 12px;
        color: var(--primary-cyan) !important;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(0, 184, 212, 0.2) 100%);
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.4), 0 0 60px rgba(0, 217, 255, 0.2);
        transform: translateY(-2px);
        border-color: var(--success-green);
    }
    
    /* Primary button special styling */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--secondary-teal) 100%);
        color: var(--darker-bg) !important;
        border: none;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.5);
    }
    
    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 0 40px rgba(0, 217, 255, 0.7), 0 0 80px rgba(0, 217, 255, 0.3);
    }
    
    /* Card-like containers with glow */
    .main-card, .stExpander, div[data-testid="stExpander"] {
        background: rgba(19, 47, 63, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.1), inset 0 0 20px rgba(0, 217, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* Metrics with cyberpunk glow */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--success-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.875rem;
    }
    
    /* Headers with cyberpunk glow */
    h1, h2, h3 {
        color: var(--primary-cyan) !important;
        text-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        font-weight: 700;
    }
    
    h1 {
        font-size: 2.5rem;
        background: linear-gradient(135deg, var(--primary-cyan) 0%, var(--success-green) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(19, 47, 63, 0.8);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 8px;
        color: var(--text-primary);
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }
    
    /* Select boxes */
    .stSelectbox>div>div {
        background: rgba(19, 47, 63, 0.8);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Progress bars */
    .stProgress>div>div>div {
        background: linear-gradient(90deg, var(--primary-cyan) 0%, var(--success-green) 100%);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
    }
    
    /* Alerts with glow */
    .stAlert {
        background: rgba(19, 47, 63, 0.8);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        animation: slideIn 0.3s ease-out;
        backdrop-filter: blur(10px);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Success alerts */
    .stSuccess {
        background: rgba(0, 230, 118, 0.1);
        border-color: var(--success-green);
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.2);
    }
    
    /* Error alerts */
    .stError {
        background: rgba(255, 23, 68, 0.1);
        border-color: var(--danger-red);
        box-shadow: 0 0 20px rgba(255, 23, 68, 0.2);
    }
    
    /* Warning alerts */
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border-color: var(--warning-amber);
        box-shadow: 0 0 20px rgba(255, 193, 7, 0.2);
    }
    
    /* Info alerts */
    .stInfo {
        background: rgba(0, 217, 255, 0.1);
        border-color: var(--primary-cyan);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Tables */
    table {
        background: rgba(19, 47, 63, 0.6);
        color: var(--text-primary);
    }
    
    thead tr th {
        background: rgba(0, 217, 255, 0.2) !important;
        color: var(--primary-cyan) !important;
        border-bottom: 2px solid var(--primary-cyan);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    tbody tr {
        border-bottom: 1px solid rgba(0, 217, 255, 0.1);
    }
    
    tbody tr:hover {
        background: rgba(0, 217, 255, 0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(19, 47, 63, 0.4);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 217, 255, 0.1);
        border-color: var(--primary-cyan);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(0, 184, 212, 0.2) 100%);
        border-color: var(--primary-cyan);
        color: var(--primary-cyan) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(19, 47, 63, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        color: var(--primary-cyan) !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }
    
    /* Spinner */
    .stSpinner>div {
        border-color: var(--primary-cyan);
        border-right-color: transparent;
    }
    
    /* Links */
    a {
        color: var(--primary-cyan) !important;
        text-decoration: none;
    }
    
    a:hover {
        color: var(--success-green) !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    /* Code blocks */
    code {
        background: rgba(19, 47, 63, 0.8);
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 6px;
        color: var(--primary-cyan);
        padding: 0.2rem 0.4rem;
    }
    
    pre {
        background: rgba(19, 47, 63, 0.8);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--darker-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary-cyan) 0%, var(--secondary-teal) 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-cyan);
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    /* Glowing border animation */
    @keyframes borderGlow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        }
        50% {
            box-shadow: 0 0 40px rgba(0, 217, 255, 0.6);
        }
    }
    
    /* Status indicators */
    .status-ready {
        background: linear-gradient(135deg, rgba(0, 230, 118, 0.2) 0%, rgba(0, 230, 118, 0.1) 100%);
        border: 1px solid var(--success-green);
        color: var(--success-green);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.3);
    }
    
    .status-error {
        background: linear-gradient(135deg, rgba(255, 23, 68, 0.2) 0%, rgba(255, 23, 68, 0.1) 100%);
        border: 1px solid var(--danger-red);
        color: var(--danger-red);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        box-shadow: 0 0 20px rgba(255, 23, 68, 0.3);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(19, 47, 63, 0.6);
        border: 2px dashed rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        padding: 2rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-cyan);
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Configuration (read from environment variables)
CATALOG = os.getenv("CATALOG_NAME", "fraud_detection_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "claims_analysis")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "159828d8fa91cd28")  # From app.yaml
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

# Initialize Databricks client (uses Databricks Apps authentication)
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient (automatically authenticated in Databricks Apps)"""
    try:
        # Check if we have OAuth credentials configured
        client_id = os.getenv("DATABRICKS_CLIENT_ID")
        client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")
        host = os.getenv("DATABRICKS_HOST")
        
        if client_id and client_secret and host:
            # OAuth authentication with service principal
            from databricks.sdk.oauth import ClientCredentials
            
            return WorkspaceClient(
                host=f"https://{host}" if not host.startswith("http") else host,
                client_id=client_id,
                client_secret=client_secret
            )
        elif host:
            # Try with host only (will use other auth methods)
            return WorkspaceClient(host=f"https://{host}" if not host.startswith("http") else host)
        else:
            # Default initialization (works in Databricks Apps)
            return WorkspaceClient()
            
    except Exception as e:
        error_msg = str(e)
        
        if "default auth: cannot configure default credentials" in error_msg:
            st.error("❌ **Authentication Configuration Missing**")
            st.warning("""
            **For Databricks Apps deployment:**
            - This error occurs during local development
            - The app will authenticate automatically when deployed to Databricks Apps
            - To test locally, configure authentication in `~/.databrickscfg`
            
            **To fix:**
            1. **Deploy to Databricks** (recommended):
               ```bash
               databricks apps deploy frauddetection-prod --source-code-path prod/files/app
               ```
            
            2. **Or configure local auth**:
               - Go to: https://docs.databricks.com/en/dev-tools/auth.html
               - Set up authentication profile
               - Or set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables
            """)
        else:
            st.error(f"Failed to initialize Databricks client: {error_msg}")
            
        return None

w = get_workspace_client()

# Show authentication status in sidebar
if w is None:
    st.sidebar.error("⚠️ Not connected to Databricks")
    st.sidebar.info("Deploy to Databricks Apps to enable full functionality")

# Enhanced Sidebar - Futuristic design
st.sidebar.markdown("""
<div style='text-align: center; padding: 1.5rem 0; border-bottom: 1px solid rgba(0, 217, 255, 0.2);'>
    <h1 style='font-size: 2.5rem; margin: 0; filter: drop-shadow(0 0 20px rgba(0, 217, 255, 0.8));'>🛡️</h1>
    <h2 style='font-size: 1.5rem; margin: 0.5rem 0; color: #00D9FF; text-shadow: 0 0 15px rgba(0, 217, 255, 0.5);'>
        Fraud Detection
    </h2>
    <p style='color: #80DEEA; font-size: 0.875rem; letter-spacing: 1px;'>AI-POWERED CLAIMS ANALYSIS</p>
</div>
""", unsafe_allow_html=True)

# Environment info - Futuristic design
env_color = "#00E676" if ENVIRONMENT == "prod" else "#FFC107" if ENVIRONMENT == "staging" else "#00D9FF"
env_glow = "rgba(0, 230, 118, 0.3)" if ENVIRONMENT == "prod" else "rgba(255, 193, 7, 0.3)" if ENVIRONMENT == "staging" else "rgba(0, 217, 255, 0.3)"
st.sidebar.markdown(f"""
<div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 217, 255, 0.3); 
     padding: 1rem; border-radius: 12px; margin: 1rem 0;
     box-shadow: 0 4px 20px {env_glow};'>
    <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
        <span style='color: {env_color}; font-size: 1.5rem; filter: drop-shadow(0 0 10px {env_color});'>●</span>
        <span style='color: #00D9FF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;'>
            {ENVIRONMENT}
        </span>
    </div>
    <div style='color: #80DEEA; font-size: 0.75rem;'>
        <div style='margin-bottom: 0.5rem;'>
            📁 <span style='color: #00D9FF;'>Catalog:</span>
            <code style='background: rgba(0,0,0,0.4); padding: 0.125rem 0.5rem; border-radius: 4px; color: #00E676;'>{CATALOG}</code>
        </div>
        <div>
            📊 <span style='color: #00D9FF;'>Schema:</span>
            <code style='background: rgba(0,0,0,0.4); padding: 0.125rem 0.5rem; border-radius: 4px; color: #00E676;'>{SCHEMA}</code>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='border-top: 1px solid rgba(0, 217, 255, 0.2); margin: 1rem 0;'></div>", unsafe_allow_html=True)

# Navigation with icons - Futuristic design
st.sidebar.markdown("""
<div style='color: #80DEEA;'>
    <h3 style='color: #00D9FF; font-size: 0.9rem; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 2px;'>
        📍 Navigation
    </h3>
    <div style='margin-left: 0rem;'>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; background: rgba(0, 217, 255, 0.05); border-left: 3px solid #00D9FF; border-radius: 4px;'>
            🏠 <strong style='color: #00D9FF;'>Home</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- Dashboard</span>
        </div>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid rgba(0, 217, 255, 0.2); border-radius: 4px;'>
            📊 <strong style='color: #80DEEA;'>Claim Analysis</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- AI Agent</span>
        </div>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid rgba(0, 217, 255, 0.2); border-radius: 4px;'>
            ⚡ <strong style='color: #80DEEA;'>Batch Processing</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- Bulk</span>
        </div>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid rgba(0, 217, 255, 0.2); border-radius: 4px;'>
            📈 <strong style='color: #80DEEA;'>Fraud Insights</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- Analytics</span>
        </div>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid rgba(0, 217, 255, 0.2); border-radius: 4px;'>
            🔎 <strong style='color: #80DEEA;'>Case Search</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- Similar</span>
        </div>
        <div style='padding: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid rgba(0, 217, 255, 0.2); border-radius: 4px;'>
            📱 <strong style='color: #80DEEA;'>Mobile Check</strong> <span style='font-size: 0.75rem; opacity: 0.7;'>- Photo AI</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div style='border-top: 1px solid rgba(0, 217, 255, 0.2); margin: 1rem 0;'></div>", unsafe_allow_html=True)

# Quick stats in sidebar - Futuristic design
st.sidebar.markdown("""
<div style='color: #80DEEA;'>
    <h3 style='color: #00D9FF; font-size: 0.9rem; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 2px;'>
        ⚡ Quick Stats
    </h3>
</div>
""", unsafe_allow_html=True)

# Main page with futuristic hero section
st.markdown("""
<div style='text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(19, 47, 63, 0.8) 100%); 
     border: 1px solid rgba(0, 217, 255, 0.3); border-radius: 20px; margin-bottom: 2rem; 
     box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2), inset 0 0 60px rgba(0, 217, 255, 0.05);
     backdrop-filter: blur(10px);'>
    <div style='font-size: 1rem; color: #00D9FF; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 1rem; opacity: 0.8;'>
        ◆ DATABRICKS ◆
    </div>
    <h1 style='font-size: 3.5rem; margin: 0; color: #00D9FF; text-shadow: 0 0 30px rgba(0, 217, 255, 0.6);'>
        AI-Powered Fraud Detection System
    </h1>
    <p style='font-size: 1.25rem; margin-top: 1.5rem; color: #80DEEA; letter-spacing: 1px;'>
        Intelligent Insurance Claims Analysis Platform
    </p>
    <div style='margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(0, 217, 255, 0.2);'>
        <span style='color: #00D9FF; font-size: 0.9rem; opacity: 0.8;'>
            ⚡ LangGraph Agents  •  🎯 Unity Catalog  •  🔍 Vector Search  •  💬 Genie AI
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Key features cards - Futuristic design
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 217, 255, 0.4); border-radius: 16px; 
         box-shadow: 0 8px 32px rgba(0, 217, 255, 0.15), inset 0 0 30px rgba(0, 217, 255, 0.05);
         transition: all 0.3s ease; backdrop-filter: blur(10px);'>
        <div style='font-size: 3rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(0, 217, 255, 0.6));'>🧠</div>
        <div style='font-weight: 700; margin-bottom: 0.5rem; color: #00D9FF; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;'>
            LangGraph Agents
        </div>
        <div style='font-size: 0.8rem; color: #80DEEA; opacity: 0.85;'>ReAct pattern reasoning</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 230, 118, 0.4); border-radius: 16px; 
         box-shadow: 0 8px 32px rgba(0, 230, 118, 0.15), inset 0 0 30px rgba(0, 230, 118, 0.05);
         transition: all 0.3s ease; backdrop-filter: blur(10px);'>
        <div style='font-size: 3rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(0, 230, 118, 0.6));'>🎯</div>
        <div style='font-weight: 700; margin-bottom: 0.5rem; color: #00E676; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;'>
            UC AI Functions
        </div>
        <div style='font-size: 0.8rem; color: #80DEEA; opacity: 0.85;'>Classify, Extract, Explain</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 184, 212, 0.4); border-radius: 16px; 
         box-shadow: 0 8px 32px rgba(0, 184, 212, 0.15), inset 0 0 30px rgba(0, 184, 212, 0.05);
         transition: all 0.3s ease; backdrop-filter: blur(10px);'>
        <div style='font-size: 3rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(0, 184, 212, 0.6));'>🔍</div>
        <div style='font-weight: 700; margin-bottom: 0.5rem; color: #00B8D4; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;'>
            Vector Search
        </div>
        <div style='font-size: 0.8rem; color: #80DEEA; opacity: 0.85;'>Find similar cases</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 2rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(255, 193, 7, 0.4); border-radius: 16px; 
         box-shadow: 0 8px 32px rgba(255, 193, 7, 0.15), inset 0 0 30px rgba(255, 193, 7, 0.05);
         transition: all 0.3s ease; backdrop-filter: blur(10px);'>
        <div style='font-size: 3rem; margin-bottom: 1rem; filter: drop-shadow(0 0 10px rgba(255, 193, 7, 0.6));'>💬</div>
        <div style='font-weight: 700; margin-bottom: 0.5rem; color: #FFC107; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;'>
            Genie API
        </div>
        <div style='font-size: 0.8rem; color: #80DEEA; opacity: 0.85;'>Natural language queries</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick start section
st.markdown("## 🚀 Quick Start")

# Quick action buttons
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("📊 Analyze", use_container_width=True, type="primary"):
        st.switch_page("pages/1_claim_analysis.py")

with col2:
    if st.button("⚡ Batch", use_container_width=True):
        st.switch_page("pages/2_batch_processing.py")

with col3:
    if st.button("📈 Insights", use_container_width=True):
        st.switch_page("pages/3_fraud_insights.py")

with col4:
    if st.button("🔎 Search", use_container_width=True):
        st.switch_page("pages/4_case_search.py")

with col5:
    if st.button("📸 Mobile", use_container_width=True, help="NEW! Take photos to check fraud"):
        st.switch_page("pages/5_mobile_fraud_check.py")

st.markdown("---")

# System Status Section
st.markdown("## 📊 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🌍 Environment", ENVIRONMENT.upper(), delta="Active" if w else "Error")
with col2:
    st.metric("🤖 LLM Model", "Claude Sonnet 4.5", delta="Latest")
with col3:
    st.metric("🔧 AI Tools", "4", delta="Classify, Extract, Search, Query")
with col4:
    # Check if workspace client is available
    status_icon = "✅" if w else "❌"
    status_text = "Ready" if w else "Error"
    status_delta = "Operational" if w else "Check Connection"
    st.metric(f"{status_icon} System", status_text, delta=status_delta)

st.markdown("---")

# Architecture Visualization - Futuristic design
st.markdown("""
<h2 style='color: #00D9FF; margin-top: 2rem; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 2px;'>
    🏗️ System Architecture
</h2>
""", unsafe_allow_html=True)

# Create an interactive architecture diagram using columns and cards
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 217, 255, 0.4); 
         padding: 1.5rem; border-radius: 16px; text-align: center; margin-bottom: 1rem;
         box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2);'>
        <div style='font-size: 1.5rem; font-weight: 600; color: #00D9FF; text-shadow: 0 0 15px rgba(0, 217, 255, 0.5);'>
            👤 User Input (Claim)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0; color: #00D9FF;'>⬇️</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.8); border: 2px solid rgba(0, 217, 255, 0.6); 
         padding: 1.5rem; border-radius: 16px; text-align: center; margin-bottom: 1rem;
         box-shadow: 0 8px 32px rgba(0, 217, 255, 0.3), inset 0 0 30px rgba(0, 217, 255, 0.1);'>
        <div style='font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; color: #00D9FF; text-shadow: 0 0 20px rgba(0, 217, 255, 0.6);'>
            🧠 LangGraph ReAct Agent
        </div>
        <div style='font-size: 0.875rem; color: #80DEEA;'>Reason → Act → Observe → Repeat</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0; color: #00D9FF;'>⬇️</div>", unsafe_allow_html=True)

# Tools row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 230, 118, 0.4); 
         padding: 1rem; border-radius: 12px; text-align: center;
         box-shadow: 0 4px 20px rgba(0, 230, 118, 0.2);'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(0, 230, 118, 0.5));'>🎯</div>
        <div style='font-size: 0.875rem; font-weight: 600; color: #00E676;'>UC Classify</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 217, 255, 0.4); 
         padding: 1rem; border-radius: 12px; text-align: center;
         box-shadow: 0 4px 20px rgba(0, 217, 255, 0.2);'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(0, 217, 255, 0.5));'>📊</div>
        <div style='font-size: 0.875rem; font-weight: 600; color: #00D9FF;'>UC Extract</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 184, 212, 0.4); 
         padding: 1rem; border-radius: 12px; text-align: center;
         box-shadow: 0 4px 20px rgba(0, 184, 212, 0.2);'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(0, 184, 212, 0.5));'>🔍</div>
        <div style='font-size: 0.875rem; font-weight: 600; color: #00B8D4;'>Vector Search</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(255, 193, 7, 0.4); 
         padding: 1rem; border-radius: 12px; text-align: center;
         box-shadow: 0 4px 20px rgba(255, 193, 7, 0.2);'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 0 10px rgba(255, 193, 7, 0.5));'>💬</div>
        <div style='font-size: 0.875rem; font-weight: 600; color: #FFC107;'>Genie API</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0; color: #00D9FF;'>⬇️</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='background: rgba(19, 47, 63, 0.6); border: 1px solid rgba(0, 230, 118, 0.4); 
         padding: 1.5rem; border-radius: 16px; text-align: center;
         box-shadow: 0 8px 32px rgba(0, 230, 118, 0.2);'>
        <div style='font-size: 1.5rem; font-weight: 600; color: #00E676; text-shadow: 0 0 15px rgba(0, 230, 118, 0.5);'>
            📋 Fraud Assessment Report
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Key Features
st.markdown("## ✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎯 Intelligent Analysis
    - **Adaptive Reasoning**: Agent selects optimal tools based on claim complexity
    - **Multi-Tool Integration**: Seamlessly combines classification, extraction, and search
    - **Explainable AI**: Full transparency in decision-making process
    - **Real-time Processing**: Results in 3-8 seconds per claim
    """)
    
    st.markdown("""
    ### 📊 Comprehensive Insights
    - **Risk Scoring**: 0-10 scale with detailed breakdown
    - **Red Flag Detection**: Automated identification of suspicious patterns
    - **Similar Case Matching**: Vector search across historical fraud cases
    - **Natural Language Queries**: Ask questions in plain English
    """)

with col2:
    st.markdown("""
    ### ⚡ Batch Processing
    - **Bulk Analysis**: Process hundreds of claims simultaneously
    - **Progress Tracking**: Real-time updates on batch status
    - **Export Options**: Download results as CSV or save to tables
    - **Flexible Depth**: Choose between quick, standard, or deep analysis
    """)
    
    st.markdown("""
    ### 📈 Analytics Dashboard
    - **Fraud Trends**: Visualize patterns over time
    - **Type Breakdown**: Understand distribution of fraud types
    - **Indicator Analysis**: Identify most common red flags
    - **Interactive Charts**: Plotly-powered visualizations
    """)

st.markdown("---")

# Performance metrics - Futuristic design
st.markdown("""
<h2 style='color: #00D9FF; margin-top: 2rem; margin-bottom: 1.5rem; text-transform: uppercase; letter-spacing: 2px;'>
    ⚡ Performance Metrics
</h2>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 230, 118, 0.4); border-radius: 12px;
         box-shadow: 0 4px 20px rgba(0, 230, 118, 0.2);'>
        <div style='font-size: 2.2rem; font-weight: 700; color: #00E676; text-shadow: 0 0 20px rgba(0, 230, 118, 0.6);'>94%</div>
        <div style='font-size: 0.75rem; color: #80DEEA; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;'>Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 217, 255, 0.4); border-radius: 12px;
         box-shadow: 0 4px 20px rgba(0, 217, 255, 0.2);'>
        <div style='font-size: 2.2rem; font-weight: 700; color: #00D9FF; text-shadow: 0 0 20px rgba(0, 217, 255, 0.6);'>3-8s</div>
        <div style='font-size: 0.75rem; color: #80DEEA; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;'>Per Claim</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(255, 193, 7, 0.4); border-radius: 12px;
         box-shadow: 0 4px 20px rgba(255, 193, 7, 0.2);'>
        <div style='font-size: 2.2rem; font-weight: 700; color: #FFC107; text-shadow: 0 0 20px rgba(255, 193, 7, 0.6);'>$0.002</div>
        <div style='font-size: 0.75rem; color: #80DEEA; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;'>Cost/Claim</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(0, 184, 212, 0.4); border-radius: 12px;
         box-shadow: 0 4px 20px rgba(0, 184, 212, 0.2);'>
        <div style='font-size: 2.2rem; font-weight: 700; color: #00B8D4; text-shadow: 0 0 20px rgba(0, 184, 212, 0.6);'>1,298x</div>
        <div style='font-size: 0.75rem; color: #80DEEA; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;'>ROI</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem 1rem; background: rgba(19, 47, 63, 0.6); 
         border: 1px solid rgba(156, 39, 176, 0.4); border-radius: 12px;
         box-shadow: 0 4px 20px rgba(156, 39, 176, 0.2);'>
        <div style='font-size: 2.2rem; font-weight: 700; color: #AB47BC; text-shadow: 0 0 20px rgba(156, 39, 176, 0.6);'>4</div>
        <div style='font-size: 0.75rem; color: #80DEEA; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;'>AI Tools</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Get started CTA - Futuristic design
st.markdown("""
<div style='background: rgba(19, 47, 63, 0.8); border: 2px solid rgba(0, 217, 255, 0.5); 
     padding: 3rem 2rem; border-radius: 20px; text-align: center; margin-top: 3rem;
     box-shadow: 0 8px 40px rgba(0, 217, 255, 0.3), inset 0 0 60px rgba(0, 217, 255, 0.05);
     backdrop-filter: blur(10px);'>
    <h2 style='color: #00D9FF; text-shadow: 0 0 30px rgba(0, 217, 255, 0.6); margin-bottom: 1rem; font-size: 2rem;'>
        ⚡ Ready to Get Started?
    </h2>
    <p style='font-size: 1.125rem; color: #80DEEA; margin-bottom: 1.5rem;'>
        Select a page from the sidebar or use the quick action buttons above to begin analyzing claims!
    </p>
    <div style='padding: 1rem; background: rgba(0, 217, 255, 0.1); border-radius: 12px; border: 1px solid rgba(0, 217, 255, 0.3); margin-top: 1rem;'>
        <p style='font-size: 0.875rem; color: #00D9FF; margin: 0;'>
            💡 <strong>Pro Tip:</strong> Start with the <strong>Claim Analysis</strong> page to see the AI agent in action
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


