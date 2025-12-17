"""
Fraud Insights Dashboard
Displays analytics and trends from batch fraud analysis results
Enhanced with Advanced Visualizations and Interactive Charts
"""

import streamlit as st
import os
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Fraud Insights | Fraud Detection",
    page_icon="📈",
    layout="wide"
)

# Custom CSS - Futuristic dashboard
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0A1929 0%, #071318 100%);
        color: #E0F7FA;
    }
    
    .insight-card {
        background: rgba(19, 47, 63, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.3);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.1);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(19, 47, 63, 0.8) 100%);
        border: 1px solid rgba(0, 217, 255, 0.4);
        padding: 1.5rem;
        border-radius: 16px;
        color: #00D9FF;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2);
    }
    
    .chart-container {
        background: rgba(19, 47, 63, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.2);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 217, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(0, 184, 212, 0.1) 100%);
        border: 2px solid #00D9FF;
        color: #00D9FF !important;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header - Futuristic design
st.markdown("""
<div style='text-align: center; padding: 3rem 2rem; 
     background: linear-gradient(135deg, rgba(0, 184, 212, 0.1) 0%, rgba(19, 47, 63, 0.8) 100%);
     border: 1px solid rgba(0, 184, 212, 0.3); border-radius: 20px; margin-bottom: 2rem;
     box-shadow: 0 8px 32px rgba(0, 184, 212, 0.2), inset 0 0 60px rgba(0, 184, 212, 0.05);
     backdrop-filter: blur(10px);'>
    <div style='font-size: 0.9rem; color: #00B8D4; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 0.5rem; opacity: 0.8;'>
        ◆ ANALYTICS DASHBOARD ◆
    </div>
    <h1 style='font-size: 3rem; margin: 0; color: #00B8D4; text-shadow: 0 0 30px rgba(0, 184, 212, 0.6);'>
        Fraud Insights
    </h1>
    <p style='font-size: 1.125rem; margin-top: 1rem; color: #80DEEA;'>
        Analytics and trends from fraud detection analysis
    </p>
    <p style='font-size: 0.875rem; margin-top: 0.5rem; color: #00B8D4; opacity: 0.8;'>
        ⚡ Real-time dashboard  •  📊 Interactive charts  •  🤖 Genie-powered queries
    </p>
</div>
""", unsafe_allow_html=True)

# Configuration
CATALOG = os.getenv("CATALOG_NAME", "fraud_detection_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "claims_analysis")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "159828d8fa91cd28")  # From app.yaml

# Initialize clients
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

# Initialize clients
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

def get_sql_connection():
    """Create Databricks SQL connection - called lazily when needed"""
    try:
        # Check if WAREHOUSE_ID is set
        if not WAREHOUSE_ID:
            st.error("❌ **SQL Connection Error**: WAREHOUSE_ID not configured")
            st.info("""
            **To fix this:**
            1. Set `DATABRICKS_WAREHOUSE_ID` in your `app.yaml`
            2. Or set it as environment variable
            3. Get warehouse ID from: SQL Warehouses → Copy ID
            """)
            return None
        
        cfg = Config()
        
        # Check if we have valid config
        if not cfg.host:
            st.error("❌ **SQL Connection Error**: Databricks host not configured")
            st.info("""
            **To fix this:**
            - Ensure you're running in Databricks Apps environment
            - Or configure authentication in `~/.databrickscfg`
            """)
            return None
        
        return sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            credentials_provider=lambda: cfg.authenticate,
        )
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ **SQL Connection Error**: {error_msg}")
        
        # Provide specific troubleshooting based on error type
        if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.warning("""
            **🔐 Authentication Issue:**
            - Ensure the app's service principal has permissions
            - Run: `./grant_permissions.sh dev`
            - Check SQL Warehouse permissions
            """)
        elif "not found" in error_msg.lower():
            st.warning(f"""
            **📍 Warehouse Not Found:**
            - Warehouse ID: `{WAREHOUSE_ID}`
            - Verify warehouse exists and is running
            - Check warehouse ID in `app.yaml`
            """)
        elif "timeout" in error_msg.lower():
            st.warning("""
            **⏱️ Connection Timeout:**
            - Check if SQL Warehouse is running
            - Try starting the warehouse manually
            - Check network connectivity
            """)
        else:
            st.info("""
            **💡 General Troubleshooting:**
            - Check SQL Warehouse is running
            - Verify permissions are granted
            - Check `app.yaml` configuration
            - Review app logs in Databricks
            """)
        
        return None

w = get_workspace_client()

# Get Genie Space ID - Try multiple sources in order
def get_genie_space_id():
    """
    Get Genie Space ID from multiple sources (in priority order):
    1. Environment variable (if set in app.yaml)
    2. config_genie table (automatic lookup)
    
    This allows automatic discovery without manual config updates.
    """
    # Try environment variable first
    env_genie_id = os.getenv("GENIE_SPACE_ID")
    if env_genie_id:
        return env_genie_id
    
    # Fall back to querying config_genie table
    try:
        sql_conn = get_sql_connection()
        if sql_conn:
            with sql_conn.cursor() as cursor:
                cursor.execute(f"""
                    SELECT config_value 
                    FROM {CATALOG}.{SCHEMA}.config_genie 
                    WHERE config_key = 'genie_space_id'
                """)
                result = cursor.fetchone()
                if result and result[0]:
                    return result[0]
    except Exception as e:
        # Silently fail - will show warning in UI
        pass
    
    return None

GENIE_SPACE_ID = get_genie_space_id()

# SQL Query Functions
@st.cache_data(ttl=300)
def get_fraud_statistics():
    """Get overall fraud statistics"""
    sql_conn = get_sql_connection()
    if not sql_conn:
        st.warning("⚠️ Cannot fetch statistics: SQL connection unavailable")
        return None
    
    try:
        with sql_conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    COUNT(*) as total_claims,
                    SUM(CASE WHEN is_fraudulent THEN 1 ELSE 0 END) as fraud_cases,
                    ROUND(AVG(CASE WHEN is_fraudulent THEN 1.0 ELSE 0.0 END) * 100, 2) as fraud_rate,
                    ROUND(AVG(risk_score), 2) as avg_risk_score
                FROM {CATALOG}.{SCHEMA}.fraud_analysis
            """)
            result = cursor.fetchone()
            if result:
                return {
                    "total_claims": result[0] or 0,
                    "fraud_cases": result[1] or 0,
                    "fraud_rate": result[2] or 0.0,
                    "avg_risk_score": result[3] or 0.0
                }
    except Exception as e:
        st.error(f"❌ Error fetching statistics: {e}")
        if "not found" in str(e).lower() or "does not exist" in str(e).lower():
            st.info("""
            **📊 Table Not Found:**
            The fraud_analysis table may not exist yet.
            - Run batch processing first to populate data
            - Or run setup notebooks to create tables
            """)
    return None

@st.cache_data(ttl=300)
def get_fraud_by_type():
    """Get fraud breakdown by type"""
    sql_conn = get_sql_connection()
    if not sql_conn:
        return None  # Error already shown by get_sql_connection
    
    try:
        with sql_conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    fraud_type,
                    COUNT(*) as count
                FROM {CATALOG}.{SCHEMA}.fraud_analysis
                WHERE is_fraudulent = TRUE
                GROUP BY fraud_type
                ORDER BY count DESC
            """)
            results = cursor.fetchall()
            if results:
                return pd.DataFrame(results, columns=["Fraud Type", "Count"])
    except Exception as e:
        st.warning(f"⚠️ Cannot fetch fraud types: {e}")
    return None

@st.cache_data(ttl=300)
def get_top_indicators():
    """Get top fraud indicators"""
    sql_conn = get_sql_connection()
    if not sql_conn:
        return None  # Error already shown by get_sql_connection
    
    try:
        with sql_conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    explode(red_flags) as indicator
                FROM {CATALOG}.{SCHEMA}.fraud_analysis
                WHERE is_fraudulent = TRUE AND red_flags IS NOT NULL
            """)
            results = cursor.fetchall()
            if results:
                indicators = [r[0] for r in results]
                indicator_counts = pd.Series(indicators).value_counts().head(10)
                return pd.DataFrame({
                    "Indicator": indicator_counts.index,
                    "Count": indicator_counts.values
                })
    except Exception as e:
        st.warning(f"⚠️ Cannot fetch indicators: {e}")
    return None

@st.cache_data(ttl=300)
def get_fraud_trends():
    """Get fraud detection trends over time"""
    sql_conn = get_sql_connection()
    if not sql_conn:
        return None  # Error already shown by get_sql_connection
    
    try:
        with sql_conn.cursor() as cursor:
            cursor.execute(f"""
                SELECT 
                    DATE(analysis_timestamp) as date,
                    COUNT(*) as total_claims,
                    SUM(CASE WHEN is_fraudulent THEN 1 ELSE 0 END) as fraud_cases
                FROM {CATALOG}.{SCHEMA}.fraud_analysis
                GROUP BY DATE(analysis_timestamp)
                ORDER BY date
            """)
            results = cursor.fetchall()
            if results:
                return pd.DataFrame(results, columns=["Date", "Total Claims", "Fraud Cases"])
    except Exception as e:
        st.warning(f"⚠️ Cannot fetch trends: {e}")
    return None

# Main Dashboard
st.markdown("---")

# Key Metrics with enhanced styling
st.markdown("### 📊 Key Performance Indicators")

stats = get_fraud_statistics()
if stats:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(102,126,234,0.3);'>
            <div style='font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Total Claims</div>
            <div style='font-size: 2.5rem; font-weight: 700;'>{:,}</div>
            <div style='font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>Analyzed to date</div>
        </div>
        """.format(stats['total_claims']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(255,107,107,0.3);'>
            <div style='font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Fraud Detected</div>
            <div style='font-size: 2.5rem; font-weight: 700;'>{:,}</div>
            <div style='font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>Suspicious claims</div>
        </div>
        """.format(stats['fraud_cases']), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(240,147,251,0.3);'>
            <div style='font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Detection Rate</div>
            <div style='font-size: 2.5rem; font-weight: 700;'>{}%</div>
            <div style='font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>Fraud percentage</div>
        </div>
        """.format(stats['fraud_rate']), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); padding: 1.5rem; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 12px rgba(67,233,123,0.3);'>
            <div style='font-size: 0.875rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem;'>Avg Risk Score</div>
            <div style='font-size: 2.5rem; font-weight: 700;'>{}/10</div>
            <div style='font-size: 0.75rem; opacity: 0.8; margin-top: 0.5rem;'>Mean risk level</div>
        </div>
        """.format(stats['avg_risk_score']), unsafe_allow_html=True)
else:
    st.info("📊 No data available yet. Process some claims in Batch Processing to see insights!")

st.markdown("---")

# Charts Section
st.markdown("---")
st.markdown("## 📊 Fraud Analytics Dashboard")

col1, col2 = st.columns(2)

with col1:
    # Fraud Type Breakdown with enhanced styling
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🎯 Fraud Type Distribution")
    fraud_types = get_fraud_by_type()
    if fraud_types is not None and not fraud_types.empty:
        fig = go.Figure(data=[go.Pie(
            labels=fraud_types["Fraud Type"],
            values=fraud_types["Count"],
            hole=0.5,
            marker=dict(
                colors=['#667eea', '#f093fb', '#4facfe', '#43e97b', '#feca57', '#ff6b6b'],
                line=dict(color='white', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=12, color='white'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Distribution of Fraud Types",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333'}
            },
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No fraud type data available yet. Process claims to see distribution.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Top Fraud Indicators with enhanced styling
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown("### 🚩 Top Fraud Red Flags")
    indicators = get_top_indicators()
    if indicators is not None and not indicators.empty:
        fig = px.bar(
            indicators,
            x="Count",
            y="Indicator",
            orientation='h',
            labels={"Count": "Occurrences", "Indicator": "Red Flag"},
            color="Count",
            color_continuous_scale=["#4facfe", "#f093fb", "#ff6b6b"]
        )
        
        fig.update_layout(
            title={
                'text': "Most Common Fraud Indicators",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#333'}
            },
            yaxis={'categoryorder':'total ascending'},
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=False,
            xaxis_title="Number of Occurrences",
            yaxis_title="",
            hovertemplate='<b>%{y}</b><br>Count: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No indicator data available yet. Process claims to see red flags.")
    st.markdown('</div>', unsafe_allow_html=True)

# Fraud Trends Over Time with enhanced visualization
st.markdown("---")
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown("### 📈 Fraud Detection Trends Over Time")
trends = get_fraud_trends()
if trends is not None and not trends.empty:
    # Create dual-axis chart with area fills
    fig = go.Figure()
    
    # Add total claims as area
    fig.add_trace(go.Scatter(
        x=trends["Date"],
        y=trends["Total Claims"],
        name="Total Claims",
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='<b>Total Claims</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add fraud cases as area
    fig.add_trace(go.Scatter(
        x=trends["Date"],
        y=trends["Fraud Cases"],
        name="Fraud Cases",
        line=dict(color='#ff6b6b', width=3),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.2)',
        hovertemplate='<b>Fraud Cases</b><br>Date: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Calculate fraud rate line
    fraud_rate = (trends["Fraud Cases"] / trends["Total Claims"] * 100).round(1)
    
    fig.add_trace(go.Scatter(
        x=trends["Date"],
        y=fraud_rate,
        name="Fraud Rate (%)",
        line=dict(color='#f093fb', width=2, dash='dash'),
        yaxis='y2',
        hovertemplate='<b>Fraud Rate</b><br>Date: %{x}<br>Rate: %{y}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': "Claims Analysis and Fraud Rate Over Time",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#333'}
        },
        xaxis_title="Date",
        yaxis_title="Number of Claims",
        yaxis2=dict(
            title="Fraud Rate (%)",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        hovermode='x unified',
        height=450,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#E0E0E0',
            borderwidth=1
        ),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📊 No trend data available yet. Process more claims to see trends over time.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Genie Natural Language Interface
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 12px; margin: 2rem 0; color: white;'>
    <h2 style='margin: 0; color: white; -webkit-text-fill-color: white;'>💬 Ask Genie - Natural Language Queries</h2>
    <p style='margin-top: 0.5rem; opacity: 0.95;'>Query your fraud data using plain English powered by AI</p>
</div>
""", unsafe_allow_html=True)

if GENIE_SPACE_ID:
    st.markdown("""
    Ask questions about your fraud data in plain English. Genie will automatically generate SQL and return results.
    """)
    
    # Expanded example questions
    example_questions = [
        "Show me all fraudulent claims",
        "What are the top 10 highest risk claims?",
        "Show claims with amount greater than $40,000",
        "Which providers have the most fraud cases?",
        "Show fraud trends by month",
        "What is the average claim amount for fraudulent vs legitimate claims?",
        "Which claim types have the highest fraud rate?",
        "Show me claims with risk score above 8",
        "What are the most common fraud red flags?",
        "Compare fraud rates across different claim types"
    ]
    
    # User input
    user_question = st.text_input(
        "Your question:",
        placeholder="e.g., Show me all high-risk fraudulent claims",
        help="Ask any question about your fraud detection data"
    )
    
    # Quick question buttons in a grid
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    for i, question in enumerate(example_questions):
        col_idx = i % 3
        with [col1, col2, col3][col_idx]:
            if st.button(question, key=f"q_{i}", use_container_width=True):
                user_question = question
    
    if user_question:
        with st.spinner("🤔 Genie is thinking..."):
            try:
                # Start conversation using official Genie API pattern
                start_response = w.api_client.do(
                    'POST',
                    f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation',
                    body={'content': user_question}
                )
                
                conversation_id = start_response.get('conversation_id')
                message_id = start_response.get('message_id')
                
                if not conversation_id or not message_id:
                    st.error("Failed to start Genie conversation")
                else:
                    # Poll for result
                    max_attempts = 30  # 30 * 2 = 60 seconds max
                    attempt = 0
                    
                    while attempt < max_attempts:
                        time.sleep(2)  # Wait 2 seconds between polls
                        attempt += 1
                        
                        # Get message status
                        message_response = w.api_client.do(
                            'GET',
                            f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}'
                        )
                        
                        status = message_response.get('status')
                        
                        if status == 'COMPLETED':
                            # Extract results
                            attachments = message_response.get('attachments', [])
                            
                            if attachments:
                                attachment = attachments[0]
                                text_response = attachment.get('text', {}).get('content', '')
                                query = attachment.get('query', {}).get('query', '')
                                
                                # Display text response
                                if text_response:
                                    st.success("**Genie's Response:**")
                                    st.markdown(text_response)
                                
                                # Display generated SQL
                                if query:
                                    with st.expander("🔍 View Generated SQL"):
                                        st.code(query, language="sql")
                                    
                                    # Get query results
                                    try:
                                        attachment_id = attachment.get('query', {}).get('attachment_id') or attachment.get('attachment_id')
                                        if attachment_id:
                                            result_response = w.api_client.do(
                                                'GET',
                                                f'/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}'
                                            )
                                            
                                            # Extract data from statement_response (correct path from notebook)
                                            stmt_response = result_response.get('statement_response', {})
                                            
                                            if stmt_response:
                                                # Get schema from manifest
                                                manifest = stmt_response.get('manifest', {})
                                                schema = manifest.get('schema', {})
                                                columns = schema.get('columns', [])
                                                column_names = [col.get('name') for col in columns]
                                                
                                                # Get data rows from result
                                                result_obj = stmt_response.get('result', {})
                                                data_array = result_obj.get('data_array', [])
                                                
                                                if data_array and column_names:
                                                    # Create DataFrame
                                                    df = pd.DataFrame(data_array, columns=column_names)
                                                    
                                                    st.success(f"✅ Found {len(df)} results")
                                                    st.dataframe(df, use_container_width=True)
                                                    
                                                    # Auto-generate chart if applicable
                                                    if len(df.columns) == 2 and len(df) > 1 and len(df) < 50:
                                                        st.markdown("**📊 Visualization:**")
                                                        fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                                                        st.plotly_chart(fig, use_container_width=True)
                                                else:
                                                    st.info("Query executed successfully but returned no results.")
                                            else:
                                                st.warning("No statement_response in query result")
                                    except Exception as e:
                                        st.warning(f"Could not fetch query results: {e}")
                            else:
                                st.info("Query completed but no results available.")
                            break
                            
                        elif status == 'FAILED':
                            error = message_response.get('error', {})
                            st.error(f"Query failed: {error}")
                            break
                        elif status == 'CANCELLED':
                            st.warning("Query was cancelled")
                            break
                    
                    if attempt >= max_attempts:
                        st.warning("Query timed out. Please try a simpler question.")
                    
            except Exception as e:
                st.error(f"Error executing Genie query: {e}")
                st.info("💡 Make sure you've granted **Can Run** permissions to the app's service principal on the Genie Space.")
else:
    st.warning("⚠️ Genie Space not configured. The Genie natural language interface is currently unavailable.")
    st.markdown("""
    **To enable Genie:**
    1. Genie Space is automatically created during setup
    2. Grant **Can Run** permission to your app's service principal on the Genie Space
    3. See README for detailed instructions
    """)

st.markdown("---")

# Tips and insights
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 12px; color: white; margin-top: 2rem;'>
    <h3 style='margin: 0 0 1rem 0; color: white; -webkit-text-fill-color: white;'>💡 Pro Tips for Better Insights</h3>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;'>
        <div>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📊</div>
            <strong>Process More Claims</strong><br>
            <span style='opacity: 0.9; font-size: 0.875rem;'>Run batch processing to populate these dashboards with richer data and trends</span>
        </div>
        <div>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>💬</div>
            <strong>Use Genie</strong><br>
            <span style='opacity: 0.9; font-size: 0.875rem;'>Ask natural language questions to explore your data in ways not covered by these charts</span>
        </div>
        <div>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🔍</div>
            <strong>Identify Patterns</strong><br>
            <span style='opacity: 0.9; font-size: 0.875rem;'>Look for recurring fraud types and red flags to improve your detection strategies</span>
        </div>
        <div>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>📈</div>
            <strong>Monitor Trends</strong><br>
            <span style='opacity: 0.9; font-size: 0.875rem;'>Track fraud rates over time to measure the effectiveness of your prevention efforts</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.caption("💡 **Dashboard refreshes every 5 minutes** | Built with Unity Catalog + Plotly + Genie API")
