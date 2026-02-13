import streamlit as st
import base64
import os
import json
import io
import pandas as pd
import re
from datetime import datetime
from groq import Groq
from PIL import Image
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
load_dotenv()

st.set_page_config(
    page_title="Industrial Gauge Digitizer Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []
if 'staging_data' not in st.session_state:
    st.session_state.staging_data = None

# API Setup
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ API Key missing! Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# --- 2. STYLING (Fixed Footer & Industrial Look) ---
st.markdown("""
    <style>
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #F8F9FA; color: #666; text-align: center;
        padding: 10px; z-index: 1000; border-top: 1px solid #E0E0E0;
    }
    .block-container { padding-bottom: 5rem; } /* Pad for footer */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; border: 1px solid #E0E0E0;
        border-radius: 8px; padding: 15px;
    }
    </style>
    <div class="footer">👨‍💻 Created by: <b>Durga Prasad</b> | Powered by Groq LPU & Llama Vision</div>
    """, unsafe_allow_html=True)


# --- 3. HELPER FUNCTIONS (The missing part!) ---
def encode_image_to_base64(image):
    """Convert PIL Image to Base64 string, resizing to optimize token usage."""
    max_size = (800, 800)
    image.thumbnail(max_size)
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def extract_json(text):
    """Robust JSON extraction using Regex."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {"error": "Failed to parse JSON", "raw": text}


def analyze_gauge(image_base64):
    """Tries Llama 4 Scout first, falls back to Llama 3.2 if unavailable."""
    prompt = """
    Analyze this industrial gauge. Return strictly JSON:
    {
        "reading": <number>,
        "unit": "<string>",
        "condition": "<Good/Warning/Critical>",
        "reasoning": "<short explanation>"
    }
    """

    # Priority list: Try Scout (Best) -> Try 90b (Good) -> Try 11b (Fast)
    models = [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.2-90b-vision-preview",
        "llama-3.2-11b-vision-preview"
    ]

    last_error = ""

    for model_id in models:
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            return extract_json(completion.choices[0].message.content)
        except Exception as e:
            last_error = str(e)
            continue  # Try next model

    return {"error": f"All models failed. Last error: {last_error}"}


# --- 4. MAIN UI LAYOUT ---
st.title("🏭 Industrial Gauge Digitizer Pro")
st.markdown("### Computer Vision Telemetry & Historian")

col_left, col_right = st.columns([1, 1.2], gap="large")

# --- LEFT COLUMN: INPUT & ANALYSIS ---
with col_left:
    st.subheader("1. Field Capture")

    input_method = st.radio("Select Input:", ["Upload Photo", "Live Camera"], horizontal=True)

    img_file = None
    if input_method == "Upload Photo":
        img_file = st.file_uploader("Upload Image", type=['jpg', 'png', 'jpeg'])
    else:
        img_file = st.camera_input("Capture Gauge")

    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Current View", use_container_width=True)

        if st.button("🚀 Analyze Telemetry", type="primary", use_container_width=True):
            with st.spinner("Processing Signal..."):
                base64_img = encode_image_to_base64(image)
                ai_data = analyze_gauge(base64_img)

                if "error" in ai_data:
                    st.error(f"Error: {ai_data['error']}")
                else:
                    # Save to staging for review
                    st.session_state['staging_data'] = ai_data
                    st.rerun()

# --- RIGHT COLUMN: VERIFICATION & LOGS ---
with col_right:
    st.subheader("2. Human Verification")

    # STAGING AREA (Review Data)
    if st.session_state.get('staging_data'):
        st.info("📝 **Review AI Output:** Please verify data before saving.")

        with st.form("verification_form"):
            stage = st.session_state['staging_data']

            # Editable Fields
            c1, c2 = st.columns(2)
            # Handle reading if it comes as None/Null
            default_reading = float(stage.get('reading') or 0.0)

            new_reading = c1.number_input("Pressure Reading", value=default_reading)
            new_unit = c2.text_input("Unit", value=stage.get('unit', 'PSI'))

            # Condition Dropdown
            cond_options = ["Good", "Warning", "Critical", "Damaged"]
            ai_cond = stage.get('condition', 'Good')
            # Find best match index
            default_idx = 0
            for i, opt in enumerate(cond_options):
                if opt in ai_cond: default_idx = i

            new_condition = st.selectbox("Condition", cond_options, index=default_idx)
            new_notes = st.text_area("Operator Notes", value=stage.get('reasoning', ''), height=70)

            # COMMIT
            if st.form_submit_button("✅ Verify & Save to Database", type="primary", use_container_width=True):
                # Save to History
                timestamp = datetime.now().strftime("%H:%M:%S")
                record = {
                    "Time": timestamp,
                    "Reading": new_reading,
                    "Unit": new_unit,
                    "Condition": new_condition,
                    "Notes": new_notes,
                    "Verified": True
                }
                st.session_state.history.insert(0, record)

                # Clear Staging
                st.session_state['staging_data'] = None
                st.success("Record Saved!")
                st.rerun()

    # HISTORY TABLE
    st.divider()
    st.markdown("#### 📜 Shift Logs")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Verified": st.column_config.CheckboxColumn(default=True, disabled=True),
                "Condition": st.column_config.TextColumn(validate="^(Good|Warning|Critical)$")
            }
        )

        # CSV Download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Shift Report",
            csv,
            "shift_report.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.caption("No records yet. Analyze an image to begin.")