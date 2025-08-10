from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai


load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            pdf_parts = []
            for page in images:
                img_byte_arr = io.BytesIO()
                page.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                pdf_parts.append({
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                })
            return pdf_parts
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
            return None
    else:
        st.warning("No file uploaded.")
        return None


def get_gemini_response(system_prompt, pdf_content, job_description):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            system_prompt,
            *pdf_content,  
            job_description
        ])
        return response.text
    except Exception as e:
        st.error(f"Error from Gemini API: {e}")
        return None


st.set_page_config(page_title="ATS Resume Expert", layout="wide")
st.title("📄 ATS Resume Expert")
st.markdown("AI-powered resume evaluation using **Google Gemini AI**")


input_text = st.text_area("📌 Paste the Job Description here:", key="input", height=200)
uploaded_file = st.file_uploader("📤 Upload your Resume (PDF)", type=["pdf"])


input_prompt1 = """
You are an experienced Technical Human Resource Manager. 
Review the provided resume against the job description. 
Provide a professional evaluation highlighting strengths and weaknesses 
in relation to the specified job requirements.
"""

input_prompt3 = """
You are an ATS (Applicant Tracking System) scanner with expertise in Data Science and ATS algorithms. 
Evaluate the resume against the job description. 
Provide:
1. Match percentage
2. Missing keywords
3. Final thoughts
"""


col1, col2 = st.columns(2)

with col1:
    submit1 = st.button("💼 Tell Me About the Resume")

with col2:
    submit3 = st.button("📊 Percentage Match")


if submit1 or submit3:
    if not uploaded_file:
        st.error("⚠ Please upload a resume PDF.")
    elif not input_text.strip():
        st.error("⚠ Please paste the job description.")
    else:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            with st.spinner("Processing with Gemini AI... ⏳"):
                if submit1:
                    response = get_gemini_response(input_prompt1, pdf_content, input_text)
                elif submit3:
                    response = get_gemini_response(input_prompt3, pdf_content, input_text)

            if response:
                st.subheader("✅ AI Response")
                st.markdown(response)
