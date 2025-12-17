"""
Claim Analysis Page - AI-Powered Fraud Detection with LangGraph Agent
Enhanced UI/UX with Modern Visualizations
Based on databricks-ai-ticket-vectorsearch pattern
"""

import streamlit as st
import os
import json
import time
from databricks.sdk import WorkspaceClient
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Claim Analysis | AI Fraud Detection",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for modern look
st.markdown("""
<style>
    /* Enhanced styling */
    .claim-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .fraud-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(255,107,107,0.3);
    }
    
    .legitimate-alert {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(81,207,102,0.3);
    }
    
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .classify-badge { background: #e3f2fd; color: #1565c0; }
    .extract-badge { background: #f3e5f5; color: #6a1b9a; }
    .search-badge { background: #fff3e0; color: #ef6c00; }
    .explain-badge { background: #e8f5e9; color: #2e7d32; }
    
    /* Animation for results */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .result-card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Progress indicator */
    .thinking-animation {
        display: inline-block;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; margin-bottom: 2rem; color: white;'>
    <h1 style='font-size: 2.5rem; margin: 0; color: white; -webkit-text-fill-color: white;'>📊 AI Claim Analysis</h1>
    <p style='font-size: 1.125rem; margin-top: 0.5rem; opacity: 0.95;'>Intelligent fraud detection powered by LangGraph agents</p>
</div>
""", unsafe_allow_html=True)

# Read configuration from environment (set in app.yaml)
CATALOG = os.getenv("CATALOG_NAME", "fraud_detection_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "claims_analysis")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "148ccb90800933a1")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
VECTOR_INDEX = f"{CATALOG}.{SCHEMA}.fraud_cases_index"

# Initialize Databricks client
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient (automatically authenticated in Databricks Apps)"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

w = get_workspace_client()

def call_uc_function(function_name, *args, timeout=50, show_debug=False):
    """Call a Unity Catalog function using Statement Execution API"""
    try:
        # Escape single quotes in string arguments
        escaped_args = []
        for arg in args:
            if isinstance(arg, str):
                escaped_arg = arg.replace("'", "''")
                escaped_args.append(f"'{escaped_arg}'")
            else:
                escaped_args.append(str(arg))
        
        args_str = ', '.join(escaped_args)
        query = f"SELECT {CATALOG}.{SCHEMA}.{function_name}({args_str}) as result"
        
        if show_debug:
            st.info(f"🔍 Executing: {function_name}(...) on warehouse {WAREHOUSE_ID}")
        
        result = w.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=query,
            wait_timeout="50s"
        )
        
        if result.status.state.value == "SUCCEEDED":
            if result.result and result.result.data_array:
                data = result.result.data_array[0][0]
                
                if isinstance(data, str):
                    import json
                    try:
                        parsed = json.loads(data)
                        return parsed
                    except:
                        return data
                elif isinstance(data, dict):
                    return data
                elif isinstance(data, (list, tuple)):
                    # For STRUCT types returned as arrays
                    if function_name == "fraud_generate_explanation" and len(data) >= 3:
                        return {
                            'summary': data[0],
                            'key_findings': data[1] if data[1] else [],
                            'recommendations': data[2] if data[2] else []
                        }
                    return data
                else:
                    return data
            return None
        else:
            if show_debug:
                st.error(f"Query failed: {result.status.state.value}")
                if result.status.error:
                    st.error(f"Error: {result.status.error.message}")
            return None
    
    except Exception as e:
        if show_debug:
            st.error(f"Error calling UC function {function_name}: {e}")
        return None

# ===== LANGCHAIN TOOLS FOR LANGRAPH AGENT =====
try:
    from langchain_core.tools import Tool, StructuredTool
    from pydantic import BaseModel, Field
    from langgraph.prebuilt import create_react_agent
    from langchain_core.messages import SystemMessage
    from databricks_langchain import ChatDatabricks
    
    LANGCHAIN_AVAILABLE = True
    
    # Tool input schemas
    class ClassifyClaimInput(BaseModel):
        claim_text: str = Field(description="The insurance claim text to classify for fraud")
    
    class ExtractIndicatorsInput(BaseModel):
        claim_text: str = Field(description="The claim text to extract fraud indicators from")
    
    class SearchFraudPatternsInput(BaseModel):
        query: str = Field(description="The search query to find relevant fraud patterns")
    
    class GenerateExplanationInput(BaseModel):
        claim_text: str = Field(description="The claim text to explain")
        is_fraudulent: bool = Field(description="Whether the claim is fraudulent (from classification)")
        fraud_type: str = Field(description="Type of fraud detected (from classification)", default="none")
    
    # Tool wrapper functions
    def classify_claim_wrapper(claim_text: str) -> str:
        """Classifies a claim as fraudulent or legitimate"""
        result = call_uc_function("fraud_classify", claim_text, show_debug=False)
        import json
        return json.dumps(result, indent=2) if result else json.dumps({"error": "Classification failed"})
    
    def extract_indicators_wrapper(claim_text: str) -> str:
        """Extracts fraud indicators from a claim"""
        result = call_uc_function("fraud_extract_indicators", claim_text, show_debug=False)
        import json
        return json.dumps(result, indent=2) if result else json.dumps({"error": "Extraction failed"})
    
    def search_fraud_patterns_wrapper(query: str) -> str:
        """Searches the fraud knowledge base for relevant patterns"""
        import json
        try:
            if not w:
                return json.dumps({"error": "WorkspaceClient not initialized"})
            
            body = {
                "columns": ["doc_id", "doc_type", "title", "content"],
                "num_results": 3,
                "query_text": query
            }
            
            response = w.api_client.do(
                'POST',
                f'/api/2.0/vector-search/indexes/{VECTOR_INDEX}/query',
                body=body
            )
            
            if isinstance(response, dict) and 'error_code' in response:
                error_msg = response.get('message', 'Unknown error')
                return json.dumps({"error": f"Vector Search error: {error_msg}"})
            
            data_array = response.get('result', {}).get('data_array', [])
            
            if data_array:
                formatted = []
                for row in data_array:
                    formatted.append({
                        "doc_id": row[0],
                        "doc_type": row[1],
                        "title": row[2],
                        "content": row[3][:500]  # Truncate for agent
                    })
                return json.dumps(formatted, indent=2)
            return json.dumps([])
        except Exception as e:
            return json.dumps({"error": f"Search failed: {str(e)}"})
    
    def generate_explanation_wrapper(claim_text: str, is_fraudulent: bool, fraud_type: str = "none") -> str:
        """Generates comprehensive fraud explanation with risk factors and recommendations"""
        result = call_uc_function("fraud_generate_explanation", claim_text, is_fraudulent, fraud_type, show_debug=False)
        import json
        return json.dumps(result, indent=2) if result else json.dumps({"error": "Explanation generation failed"})
    
    # Create LangChain Tools
    classify_tool = Tool(
        name="classify_claim",
        description="Classifies a healthcare claim as fraudulent or legitimate. Use this FIRST to understand fraud risk. Returns JSON with is_fraudulent, fraud_probability, fraud_type, confidence.",
        func=classify_claim_wrapper,
        args_schema=ClassifyClaimInput
    )
    
    extract_tool = Tool(
        name="extract_indicators",
        description="Extracts fraud indicators from claim including risk score, red flags, anomaly indicators, urgency level, and financial impact. Use after classification to get detailed analysis. Returns JSON with structured indicators.",
        func=extract_indicators_wrapper,
        args_schema=ExtractIndicatorsInput
    )
    
    search_tool = Tool(
        name="search_fraud_patterns",
        description="Searches the fraud knowledge base for relevant patterns, schemes, and documentation using semantic search. Use to find similar fraud cases or detection techniques. Returns JSON array with title, content, fraud_type for top matches.",
        func=search_fraud_patterns_wrapper,
        args_schema=SearchFraudPatternsInput
    )
    
    explain_tool = StructuredTool.from_function(
        func=generate_explanation_wrapper,
        name="generate_explanation",
        description="Generates comprehensive fraud explanation with summary, risk factors, recommendations. REQUIRES results from classify_claim first. Pass claim_text, is_fraudulent (true/false), and fraud_type from classification. Returns JSON with detailed explanation.",
        args_schema=GenerateExplanationInput
    )
    
    # LangGraph Agent creation
    @st.cache_resource
    def create_langraph_agent():
        """Create the LangGraph ReAct agent with all tools"""
        try:
            # Use Claude Sonnet 4.5 for EXCELLENT function calling support
            agent_endpoint = os.getenv("LLM_ENDPOINT", "databricks-claude-sonnet-4-5")
            
            # Initialize LLM
            llm = ChatDatabricks(
                endpoint=agent_endpoint,
                temperature=0.1,  # Low temp for reliable tool calls
                max_tokens=2000
            )
            
            # Create agent with all tools
            tools_list = [classify_tool, extract_tool, search_tool, explain_tool]
            
            # CRITICAL: Bind tools to LLM for consistent JSON format
            llm_with_tools = llm.bind_tools(tools_list)
            
            agent = create_react_agent(
                model=llm_with_tools,
                tools=tools_list
            )
            
            return agent
        except Exception as e:
            st.error(f"Error creating agent: {e}")
            import traceback
            st.error(traceback.format_exc())
            return None
    
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    st.warning(f"LangChain/LangGraph not available: {e}")

# Sample claims for testing (Healthcare Payer scenarios)
SAMPLE_CLAIMS = {
    "Legitimate Office Visit": """Medical claim #CLM-2024-001
Member ID: MEM-456789
Provider: Dr. Sarah Chen, Internal Medicine
Date of Service: 2024-12-10
Billed Amount: $185
Description: Annual wellness visit for established patient. Preventive care exam with routine blood work. Member has consistent visit history with this in-network provider. Diagnosis codes and procedure codes align correctly. Standard reimbursement request.""",

    "Upcoding Scheme": """Medical claim #CLM-2024-045
Member ID: MEM-123456
Provider: QuickCare Medical Center (Out-of-Network)
Date of Service: 2024-12-12
Billed Amount: $47,500
Description: Provider billing for complex surgical procedures but documentation shows only routine office visit. Four similar high-complexity claims for same patient in 6 months. Diagnosis codes (routine checkup) don't match procedure codes (major surgery). Provider has pattern of upcoding across multiple patients. Medical necessity not established.""",

    "Phantom Billing": """Medical claim #CLM-2024-089
Member ID: MEM-789012
Provider: Metro Health Services
Date of Service: 2024-12-08
Billed Amount: $12,000
Description: Provider billing for services member never received. Member confirmed they were out of state on date of service. Provider submitting claims for same patient on multiple dates when patient was traveling. Pattern of billing for non-existent appointments. Provider address flagged as residential location.""",

    "Prescription Drug Diversion": """Pharmacy claim #CLM-2024-112
Member ID: MEM-345678
Provider: Valley Pharmacy (Out-of-Network)
Date of Service: 2024-12-05
Billed Amount: $8,500
Description: Multiple high-cost controlled substance prescriptions filled at out-of-network pharmacy far from member's home. Same medications refilled early repeatedly. Prescriber has no prior relationship with patient. Pharmacy has pattern of early refills and doctor shopping indicators. Member has 8 different prescribers in 3 months.""",
}

# Main UI
st.markdown("---")

if not LANGCHAIN_AVAILABLE:
    st.error("❌ LangChain/LangGraph not available. Please install required packages.")
    st.code("pip install langgraph>=1.0.0 langchain>=0.3.0 langchain-core>=0.3.0 databricks-langchain")
else:
    # Info boxes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; text-align: center;'>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🧠</div>
            <div style='font-weight: 600; font-size: 0.875rem;'>LANGGRAPH AGENT</div>
            <div style='font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;'>Intelligent ReAct Pattern</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 8px; color: white; text-align: center;'>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>🔧</div>
            <div style='font-weight: 600; font-size: 0.875rem;'>4 AI TOOLS</div>
            <div style='font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;'>Classify • Extract • Search • Explain</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1rem; border-radius: 8px; color: white; text-align: center;'>
            <div style='font-size: 1.5rem; margin-bottom: 0.5rem;'>⚡</div>
            <div style='font-weight: 600; font-size: 0.875rem;'>3-8 SECONDS</div>
            <div style='font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;'>Analysis Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Claim input section
    st.markdown("### 📝 Enter Claim Details")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sample_choice = st.selectbox(
            "Choose a sample claim or enter your own:", 
            ["Custom"] + list(SAMPLE_CLAIMS.keys()),
            help="Select a pre-configured example or choose 'Custom' to enter your own claim"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if sample_choice != "Custom":
            st.info(f"💡 **{sample_choice}** loaded")
    
    if sample_choice == "Custom":
        claim_text = st.text_area(
            "Claim Information:", 
            height=200, 
            value="",
            placeholder="Enter claim ID, member ID, provider, date, amount, and description...",
            help="Include as much detail as possible for accurate analysis"
        )
    else:
        claim_text = st.text_area(
            "Claim Information:", 
            height=200, 
            value=SAMPLE_CLAIMS[sample_choice]
        )
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_btn = st.button("🚀 Analyze Claim with AI Agent", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not claim_text.strip():
            st.warning("⚠️ Please enter claim details")
        else:
            st.markdown("---")
            
            # Create progress placeholder
            progress_container = st.container()
            results_container = st.container()
            
            with progress_container:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px; margin: 1rem 0;'>
                    <div class='thinking-animation' style='font-size: 3rem; margin-bottom: 1rem;'>🤖</div>
                    <h3 style='color: #495057; margin: 0;'>AI Agent is analyzing your claim...</h3>
                    <p style='color: #6c757d; margin-top: 0.5rem;'>Reason → Act → Observe → Repeat</p>
                </div>
                """, unsafe_allow_html=True)
            
            total_start = time.time()
            
            # Create agent
            agent = create_langraph_agent()
            
            if not agent:
                st.error("Failed to create LangGraph agent")
            else:
                # System prompt
                system_prompt = """You are an expert healthcare fraud detection analyst for insurance payers (Humana, UHG, Cigna, etc.). Your job is to analyze claims and detect fraud.

You have access to these tools:
1. classify_claim - Determines if claim is fraudulent (returns is_fraudulent, fraud_type, etc). Use this FIRST.
2. extract_indicators - Extracts detailed fraud indicators. Use after classification.
3. search_fraud_patterns - Searches fraud knowledge base. Use for most claims.
4. generate_explanation - Creates comprehensive explanation. MUST pass is_fraudulent and fraud_type from classify_claim results.

IMPORTANT: You MUST use the tools by calling them properly. After using tools, provide a final analysis.

Analysis strategy:
- Start with classify_claim (get is_fraudulent and fraud_type)
- Then use extract_indicators
- Use search_fraud_patterns to find similar fraud cases
- Use generate_explanation with the is_fraudulent and fraud_type from step 1
- After gathering information, provide your final fraud assessment

Be thorough but efficient."""
                
                try:
                    # Invoke agent with system message
                    result = agent.invoke({
                        "messages": [
                            SystemMessage(content=system_prompt),
                            ("user", f"Analyze this healthcare claim for fraud and provide a comprehensive assessment: {claim_text}")
                        ]
                    })
                    
                    elapsed_time = (time.time() - total_start) * 1000
                    
                    # Clear progress and show results
                    progress_container.empty()
                    
                    with results_container:
                        # Parse messages to show reasoning
                        messages = result.get('messages', [])
                        
                        # Show success message
                        st.success(f"✅ Analysis complete in {elapsed_time:.0f}ms")
                        
                        # Extract tool calls and results
                        tool_calls = []
                        agent_response = None
                        
                        for msg in messages:
                            msg_type = getattr(msg, 'type', None) or type(msg).__name__.lower()
                            
                            if 'ai' in msg_type:
                                content = getattr(msg, 'content', '')
                                tool_calls_in_msg = getattr(msg, 'tool_calls', [])
                                
                                if tool_calls_in_msg:
                                    for tc in tool_calls_in_msg:
                                        tool_name = tc.get('name', 'unknown')
                                        tool_args = tc.get('args', {})
                                        tool_calls.append({
                                            'name': tool_name,
                                            'args': tool_args
                                        })
                                elif content and not agent_response:
                                    agent_response = content
                            
                            elif 'tool' in msg_type:
                                tool_name = getattr(msg, 'name', 'unknown')
                                tool_content = getattr(msg, 'content', '')
                                
                                for tc in tool_calls:
                                    if tc['name'] == tool_name and 'result' not in tc:
                                        tc['result'] = tool_content
                                        break
                        
                        # Display tool usage visualization
                        if tool_calls:
                            st.markdown("---")
                            st.markdown("### 🔧 AI Agent Tool Usage")
                            
                            # Tool usage chart
                            tool_names = [tc['name'] for tc in tool_calls]
                            tool_counts = {}
                            for name in tool_names:
                                tool_counts[name] = tool_counts.get(name, 0) + 1
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Create horizontal bar chart
                                fig = go.Figure(go.Bar(
                                    y=list(tool_counts.keys()),
                                    x=list(tool_counts.values()),
                                    orientation='h',
                                    marker=dict(
                                        color=['#667eea', '#f093fb', '#4facfe', '#43e97b'],
                                        line=dict(color='white', width=2)
                                    ),
                                    text=list(tool_counts.values()),
                                    textposition='auto'
                                ))
                                
                                fig.update_layout(
                                    title="Tools Used by Agent",
                                    xaxis_title="Number of Calls",
                                    yaxis_title="",
                                    height=250,
                                    margin=dict(l=0, r=0, t=40, b=0),
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)'
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; margin-top: 1rem;'>
                                    <div style='font-size: 2rem; font-weight: 700; color: #667eea;'>{len(tool_calls)}</div>
                                    <div style='font-size: 0.875rem; color: #6c757d;'>Total Tool Calls</div>
                                </div>
                                <div style='text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; margin-top: 0.5rem;'>
                                    <div style='font-size: 2rem; font-weight: 700; color: #f093fb;'>{len(tool_counts)}</div>
                                    <div style='font-size: 0.875rem; color: #6c757d;'>Unique Tools</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Display detailed tool results
                            st.markdown("### 📋 Detailed Tool Outputs")
                            
                            for i, tc in enumerate(tool_calls, 1):
                                tool_name = tc['name']
                                tool_args = tc.get('args', {})
                                tool_result = tc.get('result', 'No result')
                                
                                # Badge color based on tool
                                badge_class = {
                                    'classify_claim': 'classify-badge',
                                    'extract_indicators': 'extract-badge',
                                    'search_fraud_patterns': 'search-badge',
                                    'generate_explanation': 'explain-badge'
                                }.get(tool_name, 'classify-badge')
                                
                                icon = {
                                    'classify_claim': '🎯',
                                    'extract_indicators': '📊',
                                    'search_fraud_patterns': '🔍',
                                    'generate_explanation': '💡'
                                }.get(tool_name, '🔧')
                                
                                with st.expander(f"{icon} **Tool {i}: {tool_name}**", expanded=(i == 1)):
                                    st.markdown(f'<span class="tool-badge {badge_class}">{tool_name}</span>', unsafe_allow_html=True)
                                    
                                    st.write("**Input:**")
                                    st.json(tool_args)
                                    
                                    st.write("**Output:**")
                                    try:
                                        result_json = json.loads(tool_result)
                                        
                                        # Special formatting for classification results
                                        if tool_name == 'classify_claim' and isinstance(result_json, dict):
                                            is_fraud = result_json.get('is_fraudulent', False)
                                            fraud_prob = result_json.get('fraud_probability', 0)
                                            
                                            if is_fraud:
                                                st.markdown(f"""
                                                <div class='fraud-alert'>
                                                    <h3 style='margin: 0; color: white;'>⚠️ FRAUD DETECTED</h3>
                                                    <div style='font-size: 1.25rem; margin-top: 0.5rem;'>Risk: {fraud_prob*100:.1f}%</div>
                                                    <div style='font-size: 0.875rem; margin-top: 0.5rem; opacity: 0.9;'>Type: {result_json.get('fraud_type', 'Unknown')}</div>
                                                </div>
                                                """, unsafe_allow_html=True)
                                            else:
                                                st.markdown(f"""
                                                <div class='legitimate-alert'>
                                                    <h3 style='margin: 0; color: white;'>✅ LEGITIMATE CLAIM</h3>
                                                    <div style='font-size: 1.25rem; margin-top: 0.5rem;'>Confidence: {result_json.get('confidence', 0)*100:.1f}%</div>
                                                </div>
                                                """, unsafe_allow_html=True)
                                        
                                        st.json(result_json)
                                    except:
                                        st.text(tool_result[:500] + "..." if len(tool_result) > 500 else tool_result)
                        
                        # Display final agent response
                        if agent_response:
                            st.markdown("---")
                            st.markdown("### 💡 Agent's Final Analysis")
                            
                            st.markdown(f"""
                            <div class='claim-card result-card'>
                                {agent_response}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Performance metrics
                        st.markdown("---")
                        st.markdown("### ⚡ Performance Metrics")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("⏱️ Response Time", f"{elapsed_time:.0f}ms")
                        with col2:
                            st.metric("🔧 Tools Used", f"{len(tool_calls)}/4")
                        with col3:
                            cost_per_tool = 0.0005
                            total_cost = len(tool_calls) * cost_per_tool
                            st.metric("💰 Est. Cost", f"${total_cost:.4f}")
                        with col4:
                            efficiency = (len(tool_calls) / 4) * 100
                            st.metric("📊 Efficiency", f"{efficiency:.0f}%")
                        
                except Exception as e:
                    progress_container.empty()
                    st.error(f"Error running agent: {e}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())

# Bottom tips
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;'>
    <h3 style='margin: 0; color: white; -webkit-text-fill-color: white;'>💡 Pro Tips</h3>
    <div style='margin-top: 1rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; text-align: left;'>
        <div>
            <strong>🎯 Be Specific:</strong><br>
            Include claim ID, member info, provider details, and amounts for best results
        </div>
        <div>
            <strong>⚡ Use Samples:</strong><br>
            Try the pre-configured examples to see different fraud patterns
        </div>
        <div>
            <strong>🔍 Review Tools:</strong><br>
            Check which tools the agent used to understand its reasoning
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("🏥 Healthcare Payer Fraud Detection | Built with LangGraph + Unity Catalog AI Functions | ☁️ Databricks Apps")
