"""
Mobile Fraud Check - Take Photos of Claims Documents
AI-powered fraud detection from document images using Claude Vision
"""

import streamlit as st
import os
import json
import time
from databricks.sdk import WorkspaceClient
import base64
from PIL import Image
import io

# Page configuration optimized for mobile
st.set_page_config(
    page_title="📸 Mobile Fraud Check",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"  # Better for mobile
)

# Mobile-optimized CSS
st.markdown("""
<style>
    /* Mobile-first responsive design */
    .mobile-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .camera-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .result-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        animation: slideUp 0.5s ease-out;
    }
    
    .fraud-detected {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
    }
    
    .legitimate-claim {
        background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
        color: white;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Large touch-friendly buttons */
    .stButton>button {
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
    }
    
    /* Better mobile spacing */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        
        .mobile-header h1 {
            font-size: 1.75rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='mobile-header'>
    <h1 style='margin: 0; color: white; -webkit-text-fill-color: white; font-size: 2rem;'>📸 Mobile Fraud Check</h1>
    <p style='margin-top: 0.5rem; font-size: 1rem; opacity: 0.95;'>Take a photo to detect fraud instantly</p>
</div>
""", unsafe_allow_html=True)

# Configuration
CATALOG = os.getenv("CATALOG_NAME", "fraud_detection_dev")
SCHEMA = os.getenv("SCHEMA_NAME", "claims_analysis")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "159828d8fa91cd28")
VECTOR_INDEX = f"{CATALOG}.{SCHEMA}.fraud_cases_index"

# Initialize Databricks client
@st.cache_resource
def get_workspace_client():
    """Initialize Databricks WorkspaceClient"""
    try:
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

w = get_workspace_client()

def encode_image_to_base64(image_bytes):
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_bytes).decode('utf-8')

def analyze_image_with_claude(image_bytes, image_type="jpeg"):
    """Analyze claim document image using Claude Vision"""
    try:
        from databricks_langchain import ChatDatabricks
        
        # Use Claude Sonnet 4.5 with vision capabilities
        llm = ChatDatabricks(
            endpoint="databricks-claude-sonnet-4-5",
            temperature=0.1,
            max_tokens=2000
        )
        
        # Encode image
        base64_image = encode_image_to_base64(image_bytes)
        
        # Create vision prompt
        prompt = f"""You are an expert insurance fraud investigator. Analyze this claim document image and extract all relevant information.

Look for:
1. Claim ID
2. Member/Patient ID
3. Provider name and details
4. Date of service
5. Billed amount
6. Services/procedures described
7. Any suspicious patterns or red flags

Extract the text from the image and structure it as a claim description. Then analyze for potential fraud indicators:
- Upcoding (inflated charges)
- Phantom billing (services not rendered)
- Unbundling (separate billing for bundled services)
- Dates inconsistencies
- Provider patterns
- Amount anomalies

Provide:
1. Extracted claim text
2. Fraud risk assessment (High/Medium/Low)
3. Specific red flags found
4. Brief explanation

Format your response as JSON with these fields:
{{
    "claim_text": "extracted claim information...",
    "risk_level": "High/Medium/Low",
    "red_flags": ["flag1", "flag2"],
    "explanation": "brief explanation...",
    "extracted_data": {{
        "claim_id": "...",
        "amount": "...",
        "provider": "...",
        "date": "..."
    }}
}}"""
        
        # For now, since we need to call the API with image support
        # We'll use the statement execution API with the image
        st.info("🔍 Analyzing document with Claude Vision AI...")
        
        # Call UC function for classification (we'll extract text first)
        # For MVP, let's use OCR or text extraction approach
        st.warning("⚠️ Image analysis requires Claude Vision API integration. For now, showing demo flow.")
        
        return {
            "claim_text": "Demo: Medical claim detected from image",
            "risk_level": "Medium",
            "red_flags": ["Amount verification needed", "Provider check required"],
            "explanation": "Document uploaded successfully. Full vision analysis coming soon.",
            "extracted_data": {
                "claim_id": "Detected from image",
                "amount": "To be extracted",
                "provider": "To be extracted",
                "date": "To be extracted"
            }
        }
        
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return None

def call_uc_function(function_name, *args):
    """Call UC fraud detection functions"""
    try:
        escaped_args = []
        for arg in args:
            if isinstance(arg, str):
                escaped_arg = arg.replace("'", "''")
                escaped_args.append(f"'{escaped_arg}'")
            else:
                escaped_args.append(str(arg))
        
        args_str = ', '.join(escaped_args)
        query = f"SELECT {CATALOG}.{SCHEMA}.{function_name}({args_str}) as result"
        
        result = w.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=query,
            wait_timeout="50s"
        )
        
        if result.status.state.value == "SUCCEEDED":
            if result.result and result.result.data_array:
                data = result.result.data_array[0][0]
                if isinstance(data, str):
                    try:
                        return json.loads(data)
                    except:
                        return data
                return data
        return None
    except Exception as e:
        st.error(f"Error calling function: {e}")
        return None

# Main UI
st.markdown("## 📷 Capture or Upload Document")

# Camera input (works on mobile browsers)
tab1, tab2 = st.tabs(["📸 Take Photo", "📁 Upload Image"])

with tab1:
    st.markdown("""
    <div class='camera-container'>
        <p style='text-align: center; color: #666; margin-bottom: 1rem;'>
            Use your device camera to capture a claim document
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Camera input - works on mobile devices
    camera_photo = st.camera_input("Take a picture of the claim document")
    
    if camera_photo is not None:
        # Display captured image
        image = Image.open(camera_photo)
        st.image(image, caption="Captured Document", use_container_width=True)
        
        # Process button
        if st.button("🔍 Analyze This Document", type="primary", key="analyze_camera"):
            with st.spinner("🤖 AI is analyzing your document..."):
                # Get image bytes
                image_bytes = camera_photo.getvalue()
                
                # Analyze with Claude Vision
                vision_result = analyze_image_with_claude(image_bytes)
                
                if vision_result:
                    # Extract claim text
                    claim_text = vision_result.get("claim_text", "")
                    
                    if claim_text and claim_text != "Demo: Medical claim detected from image":
                        # Run fraud classification
                        fraud_result = call_uc_function("fraud_classify", claim_text)
                        
                        if fraud_result:
                            is_fraud = fraud_result.get('is_fraudulent', False)
                            fraud_prob = fraud_result.get('fraud_probability', 0)
                            fraud_type = fraud_result.get('fraud_type', 'Unknown')
                            
                            # Display result
                            st.markdown("---")
                            
                            if is_fraud:
                                st.markdown(f"""
                                <div class='result-card fraud-detected'>
                                    <h2 style='margin: 0; color: white; -webkit-text-fill-color: white;'>⚠️ FRAUD ALERT</h2>
                                    <div style='font-size: 2rem; margin: 1rem 0; font-weight: 700;'>{fraud_prob*100:.1f}% Risk</div>
                                    <div style='font-size: 1.125rem;'>Type: {fraud_type}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class='result-card legitimate-claim'>
                                    <h2 style='margin: 0; color: white; -webkit-text-fill-color: white;'>✅ LEGITIMATE</h2>
                                    <div style='font-size: 2rem; margin: 1rem 0; font-weight: 700;'>{(1-fraud_prob)*100:.1f}% Confidence</div>
                                    <div style='font-size: 1.125rem;'>No fraud indicators detected</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Show extracted information
                            with st.expander("📋 Extracted Information"):
                                st.write("**Claim Text:**")
                                st.text(claim_text)
                                
                                st.write("**Extracted Data:**")
                                st.json(vision_result.get("extracted_data", {}))
                            
                            # Show red flags
                            red_flags = vision_result.get("red_flags", [])
                            if red_flags:
                                st.warning("**🚩 Red Flags Detected:**")
                                for flag in red_flags:
                                    st.write(f"- {flag}")
                    else:
                        # Demo mode - show vision analysis result
                        st.info("📸 **Document Captured Successfully**")
                        st.json(vision_result)
                        st.info("""
                        **💡 Next Steps:**
                        - Full Claude Vision integration will extract text from images
                        - Text will be automatically analyzed for fraud
                        - Real-time results on mobile devices
                        """)

with tab2:
    st.markdown("""
    <div class='camera-container'>
        <p style='text-align: center; color: #666; margin-bottom: 1rem;'>
            Upload an existing photo or PDF of the claim document
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Upload a photo of the claim document"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        if uploaded_file.type.startswith('image/'):
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Document", use_container_width=True)
        else:
            st.info(f"📄 PDF uploaded: {uploaded_file.name}")
        
        # Process button
        if st.button("🔍 Analyze This Document", type="primary", key="analyze_upload"):
            with st.spinner("🤖 AI is analyzing your document..."):
                # Get file bytes
                file_bytes = uploaded_file.getvalue()
                
                # Analyze with Claude Vision
                vision_result = analyze_image_with_claude(file_bytes)
                
                if vision_result:
                    # Show result (same as camera tab)
                    st.info("📸 **Document Uploaded Successfully**")
                    st.json(vision_result)
                    st.info("""
                    **💡 Next Steps:**
                    - Full Claude Vision integration will extract text from images
                    - Text will be automatically analyzed for fraud
                    - Results available on any device
                    """)

# Sample documents section
st.markdown("---")
st.markdown("## 📱 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: #f8f9fa; border-radius: 12px;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📸</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>1. Capture</div>
        <div style='font-size: 0.875rem; color: #666;'>Take a photo of the claim document</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: #f8f9fa; border-radius: 12px;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🤖</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>2. Analyze</div>
        <div style='font-size: 0.875rem; color: #666;'>AI extracts and analyzes the claim</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: #f8f9fa; border-radius: 12px;'>
        <div style='font-size: 3rem; margin-bottom: 0.5rem;'>⚡</div>
        <div style='font-weight: 600; margin-bottom: 0.5rem;'>3. Results</div>
        <div style='font-size: 0.875rem; color: #666;'>Instant fraud detection results</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tips section
with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    ### 📸 Photography Tips:
    - **Good Lighting**: Ensure the document is well-lit
    - **Flat Surface**: Place document on a flat surface
    - **Full Frame**: Capture the entire document
    - **Clear Focus**: Make sure text is readable
    - **Avoid Glare**: No reflections or shadows
    
    ### 📋 Supported Documents:
    - Medical claim forms
    - Pharmacy receipts
    - Provider invoices
    - Explanation of Benefits (EOB)
    - Prior authorization forms
    - Any claim-related paperwork
    
    ### 🤖 AI Analysis:
    - Extracts text using Claude Vision
    - Identifies claim details automatically
    - Runs fraud detection algorithms
    - Provides instant risk assessment
    - Highlights suspicious patterns
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; color: white; text-align: center;'>
    <h3 style='margin: 0; color: white; -webkit-text-fill-color: white;'>🚀 Mobile-First Fraud Detection</h3>
    <p style='margin-top: 0.5rem; opacity: 0.95;'>Powered by Claude Vision • Unity Catalog • LangGraph</p>
    <p style='font-size: 0.875rem; opacity: 0.85; margin-top: 0.5rem;'>Works on smartphones, tablets, and desktop</p>
</div>
""", unsafe_allow_html=True)

st.caption("📸 Mobile Fraud Check | Built with Claude Vision + Databricks | Best viewed on mobile devices")

