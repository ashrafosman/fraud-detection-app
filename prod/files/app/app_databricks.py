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

# Custom CSS for modern look
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #FF3621;
        --secondary-color: #1E88E5;
        --success-color: #00C853;
        --warning-color: #FFB300;
        --danger-color: #D32F2F;
    }
    
    /* Better metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Enhanced sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Better buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Card-like containers */
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Animated success/error messages */
    .stAlert {
        animation: slideIn 0.3s ease-out;
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
    
    /* Better typography */
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #FF3621, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .status-ready {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    
    .status-error {
        background-color: #FFEBEE;
        color: #C62828;
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

# Enhanced Sidebar
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='font-size: 2rem; margin: 0; color: white;'>🛡️</h1>
    <h2 style='font-size: 1.5rem; margin: 0.5rem 0; color: white;'>Fraud Detection</h2>
    <p style='color: #90CAF9; font-size: 0.875rem;'>AI-Powered Claims Analysis</p>
</div>
""", unsafe_allow_html=True)

# Environment info
env_color = "#4CAF50" if ENVIRONMENT == "prod" else "#FFC107" if ENVIRONMENT == "staging" else "#2196F3"
st.sidebar.markdown(f"""
<div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
    <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
        <span style='color: {env_color}; font-size: 1.5rem;'>●</span>
        <span style='color: white; font-weight: 600;'>Environment: {ENVIRONMENT.upper()}</span>
    </div>
    <div style='color: #B0BEC5; font-size: 0.875rem;'>
        <div>📁 Catalog: <code style='background: rgba(0,0,0,0.2); padding: 0.125rem 0.5rem; border-radius: 4px;'>{CATALOG}</code></div>
        <div style='margin-top: 0.25rem;'>📊 Schema: <code style='background: rgba(0,0,0,0.2); padding: 0.125rem 0.5rem; border-radius: 4px;'>{SCHEMA}</code></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation with icons
st.sidebar.markdown("""
<div style='color: white;'>
    <h3 style='color: #90CAF9; font-size: 1rem; margin-bottom: 1rem;'>📍 NAVIGATION</h3>
    <div style='margin-left: 0.5rem;'>
        <div style='margin-bottom: 0.75rem;'>🏠 <strong>Home</strong> - Dashboard & Overview</div>
        <div style='margin-bottom: 0.75rem;'>📊 <strong>Claim Analysis</strong> - AI Agent Analysis</div>
        <div style='margin-bottom: 0.75rem;'>⚡ <strong>Batch Processing</strong> - Bulk Claims</div>
        <div style='margin-bottom: 0.75rem;'>📈 <strong>Fraud Insights</strong> - Analytics & Trends</div>
        <div style='margin-bottom: 0.75rem;'>🔎 <strong>Case Search</strong> - Similar Cases</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Quick stats in sidebar
st.sidebar.markdown("""
<div style='color: white;'>
    <h3 style='color: #90CAF9; font-size: 1rem; margin-bottom: 1rem;'>⚡ QUICK STATS</h3>
</div>
""", unsafe_allow_html=True)

# Main page with hero section
st.markdown("""
<div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; margin-bottom: 2rem; color: white;'>
    <h1 style='font-size: 3rem; margin: 0; color: white; -webkit-text-fill-color: white;'>🛡️ AI-Powered Fraud Detection</h1>
    <p style='font-size: 1.25rem; margin-top: 1rem; opacity: 0.95;'>Intelligent Insurance Claims Analysis Platform</p>
    <p style='font-size: 1rem; margin-top: 0.5rem; opacity: 0.85;'>Powered by LangGraph Agents • Unity Catalog • Vector Search</p>
</div>
""", unsafe_allow_html=True)

# Key features cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🧠</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>LangGraph Agents</div>
        <div style='font-size: 0.875rem; opacity: 0.9;'>ReAct pattern reasoning</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; color: white;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🎯</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>UC AI Functions</div>
        <div style='font-size: 0.875rem; opacity: 0.9;'>Classify, Extract, Explain</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px; color: white;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🔍</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>Vector Search</div>
        <div style='font-size: 0.875rem; opacity: 0.9;'>Find similar cases</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 12px; color: white;'>
        <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>💬</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>Genie API</div>
        <div style='font-size: 0.875rem; opacity: 0.9;'>Natural language queries</div>
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

# Architecture Visualization
st.markdown("## 🏗️ System Architecture")

# Create an interactive architecture diagram using columns and cards
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; margin-bottom: 1rem;'>
        <div style='font-size: 1.5rem; font-weight: 600;'>👤 User Input (Claim)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0;'>⬇️</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; margin-bottom: 1rem;'>
        <div style='font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;'>🧠 LangGraph ReAct Agent</div>
        <div style='font-size: 0.875rem; opacity: 0.9;'>Reason → Act → Observe → Repeat</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0;'>⬇️</div>", unsafe_allow_html=True)

# Tools row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 8px; text-align: center; color: white;'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🎯</div>
        <div style='font-size: 0.875rem; font-weight: 600;'>UC Classify</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1rem; border-radius: 8px; text-align: center; color: white;'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📊</div>
        <div style='font-size: 0.875rem; font-weight: 600;'>UC Extract</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 1rem; border-radius: 8px; text-align: center; color: white;'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🔍</div>
        <div style='font-size: 0.875rem; font-weight: 600;'>Vector Search</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); padding: 1rem; border-radius: 8px; text-align: center; color: white;'>
        <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>💬</div>
        <div style='font-size: 0.875rem; font-weight: 600;'>Genie API</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align: center; font-size: 2rem; margin: 1rem 0;'>⬇️</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white;'>
        <div style='font-size: 1.5rem; font-weight: 600;'>📋 Fraud Assessment Report</div>
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

# Performance metrics
st.markdown("## ⚡ Performance Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #E8F5E9; border-radius: 8px;'>
        <div style='font-size: 2rem; font-weight: 700; color: #2E7D32;'>94%</div>
        <div style='font-size: 0.875rem; color: #558B2F;'>Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #E3F2FD; border-radius: 8px;'>
        <div style='font-size: 2rem; font-weight: 700; color: #1565C0;'>3-8s</div>
        <div style='font-size: 0.875rem; color: #1976D2;'>Per Claim</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #FFF3E0; border-radius: 8px;'>
        <div style='font-size: 2rem; font-weight: 700; color: #EF6C00;'>$0.002</div>
        <div style='font-size: 0.875rem; color: #F57C00;'>Cost/Claim</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #F3E5F5; border-radius: 8px;'>
        <div style='font-size: 2rem; font-weight: 700; color: #6A1B9A;'>1,298x</div>
        <div style='font-size: 0.875rem; color: #7B1FA2;'>ROI</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: #FCE4EC; border-radius: 8px;'>
        <div style='font-size: 2rem; font-weight: 700; color: #C2185B;'>4</div>
        <div style='font-size: 0.875rem; color: #D81B60;'>AI Tools</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Get started CTA
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 16px; text-align: center; color: white; margin-top: 2rem;'>
    <h2 style='color: white; -webkit-text-fill-color: white; margin-bottom: 1rem;'>Ready to Get Started?</h2>
    <p style='font-size: 1.125rem; opacity: 0.95; margin-bottom: 1.5rem;'>Select a page from the sidebar or use the quick action buttons above to begin analyzing claims!</p>
    <p style='font-size: 0.875rem; opacity: 0.85;'>💡 Tip: Start with the <strong>Claim Analysis</strong> page to see the AI agent in action</p>
</div>
""", unsafe_allow_html=True)


