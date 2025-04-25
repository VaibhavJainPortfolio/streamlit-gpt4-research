import streamlit as st
from fpdf import FPDF
from io import BytesIO
import base64
import re

from openai import OpenAI

# Streamlit config
st.set_page_config(page_title="🧠 AI-Powered Deep Research", layout="centered")
st.title("🔍 Deep Research on Any Person")
st.markdown("Provide a name or social media link + your OpenAI key to generate a comprehensive AI-powered report.")

# Inputs
api_key = st.text_input("🔐 Your OpenAI API Key", type="password")
search_input = st.text_input("👤 Name or Social Media Link", placeholder="e.g., John Doe or https://linkedin.com/in/xyz")

if "history" not in st.session_state:
    st.session_state.history = []

# PDF generator
def generate_pdf(text, filename="Research_Report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Clean non-ASCII characters
    cleaned_text = text.encode("ascii", "replace").decode("ascii")

    for line in cleaned_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)

    pdf_output_str = pdf.output(dest='S')  # Returns as string
    pdf_binary = BytesIO(pdf_output_str.encode("latin-1"))  # Encode to bytes
    pdf_binary.seek(0)
    return pdf_binary

# Download button
def download_button(data, filename, label):
    b64 = base64.b64encode(data.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{label}</a>'
    return href

# Main logic
if st.button("🚀 Start Deep Research"):
    if not api_key or not search_input:
        st.warning("Please enter both API key and search input.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            with st.spinner("🔍 Researching with GPT-4..."):
                prompt = f"""
You are a skilled AI researcher. Do intensive research on the Person using Deep Research and give me a massive report on everything you find. Find the needle in the haystack about him or her, something unknown, so I can easily reach out to him with an unexpected fact.Provide an in-depth report on the following person:

Input: {search_input}

Structure your response into:
1. Professional Background and Academic Credentials
2. Areas of Expertise and Contributions to the Field
3. Public Speaking, Conferences and Research
4. Affilitions and Leadership Roles
5. Awards, Recognitions and Honours
6. Personal Interests, Hobbies and Initiatives
7. Unique and Unexpected Facts(Ice Breakers)
8. References

Keep it insightful and well-formatted.
"""

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )

                result = response.choices[0].message.content
                st.session_state.history.append((search_input, result))

                st.subheader("📋 AI Research Report")
                st.markdown(result)

                pdf_data = generate_pdf(result)
                st.markdown(download_button(pdf_data, "Research_Report.pdf", "📥 Download Report as PDF"), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Show history
if st.session_state.history:
    with st.expander("🕘 Session History"):
        for i, (q, r) in enumerate(reversed(st.session_state.history)):
            st.markdown(f"**{i+1}.** _{q}_")
            st.code(r[:500] + "..." if len(r) > 500 else r)
