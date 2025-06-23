import streamlit as st
from fpdf import FPDF
import base64
import google.generativeai as genai
import time
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY) 
model = genai.GenerativeModel('gemini-pro')


def generate_ai_summary(experience, tone="professional"):
    prompt = f"""
    Create a {tone} 3-sentence professional summary for a resume based on:
    {experience}
    """
    response = model.generate_content(prompt)
    return response.text

def improve_with_ai(text, purpose="resume"):
    prompt = f"""
    Improve this {purpose} content to be more impactful and ATS-friendly:
    {text}
    """
    response = model.generate_content(prompt)
    return response.text

def suggest_skills(job_description=""):
    prompt = f"""
    Suggest 10 relevant hard and soft skills for a resume based on:
    {job_description}
    Return as a comma-separated list.
    """
    response = model.generate_content(prompt)
    return response.text


def generate_pdf(data, template):
    pdf = FPDF()
    pdf.add_page()
    
    # Template Designs
    if template == "Modern Blue":
        primary_color = (70, 130, 180)  # SteelBlue
    elif template == "Elegant Purple":
        primary_color = (147, 112, 219)  # MediumPurple
    else:
        primary_color = (46, 139, 87)  # SeaGreen
    

    pdf.set_fill_color(*primary_color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, data["name"], ln=1, fill=True)
    
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"📧 {data['email']} | 📞 {data['phone']}", ln=1)
    
    
    sections = [
        ("PROFESSIONAL SUMMARY", data["summary"]),
        ("WORK EXPERIENCE", "\n".join(
            f"🏢 {job['role']} at {job['company']}\n- {job['description']}" 
             for job in data["jobs"]
        )),
        ("EDUCATION", f"🎓 {data['education']}"),
        ("SKILLS", f"🛠️ {data['skills']}")
    ]
    
    pdf.set_font("Arial", "B", 14)
    for title, content in sections:
        pdf.cell(0, 10, title, ln=1)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, content)
        pdf.ln(2)
    
    return pdf.output(dest="S").encode("latin1")


st.set_page_config(
    page_title="AI Resume Builder Pro",
    page_icon="🤖",
    layout="wide",
)


st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .css-1aumxhk {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        padding: 25px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #6a5acd, #9370db);
        color: white !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(106, 90, 205, 0.4);
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border: 2px solid #6a5acd !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar (AI Features) ---
with st.sidebar:
    st.title("🤖 AI Assistant")
    
    # AI Chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])
    
    if prompt := st.chat_input("Ask career advice..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            response = model.generate_content(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.rerun()
    
    # AI Tools
    st.markdown("---")
    st.subheader("🛠 AI Tools")
    if st.button("✨ Generate Summary"):
        if "jobs" in st.session_state and st.session_state.jobs:
            experience = "\n".join([job["description"] for job in st.session_state.jobs])
            ai_summary = generate_ai_summary(experience)
            st.session_state.summary = ai_summary
            st.rerun()

# --- Main Form ---
col1, col2 = st.columns(2)

with col1:
    st.title("AI Resume Builder Pro")
    st.markdown("Build **ATS-optimized resumes** with AI assistance")
    
    with st.form("resume_form"):
        # Personal Info
        st.subheader("👤 Personal Information")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        
        # AI-Enhanced Summary
        st.subheader("📌 Professional Summary")
        summary = st.text_area(
            "Describe your professional background",
            help="Click 'Generate Summary' in sidebar for AI help"
        )
        
        # Work Experience
        st.subheader("💼 Work Experience")
        jobs = []
        num_jobs = st.number_input("Number of positions", 1, 5, 1)
        for i in range(num_jobs):
            st.write(f"**Position {i+1}**")
            company = st.text_input(f"Company {i+1}", key=f"company{i}")
            role = st.text_input(f"Role {i+1}", key=f"role{i}")
            description = st.text_area(
                f"Description {i+1}", 
                key=f"desc{i}",
                help="Describe achievements with metrics if possible"
            )
            jobs.append({"company": company, "role": role, "description": description})
        
        # Education & Skills
        st.subheader("🎓 Education")
        education = st.text_input("Degree & Institution")
        
        st.subheader("🛠 Skills")
        skills = st.text_input(
            "List your skills", 
            help="Click 'Suggest Skills' below for AI recommendations"
        )
        
        # Template Selection
        st.subheader("🎨 Choose Design")
        template = st.radio(
            "Select template:",
            ["Modern Blue", "Elegant Purple", "Clean Green"],
            horizontal=True
        )
        
        submitted = st.form_submit_button("Generate Resume")

# --- Real-Time Preview ---
with col2:
    st.title("👀 Live Preview")
    if submitted or name:
        with st.expander("📄 Resume Preview", expanded=True):
            preview_html = f"""
            <div style="
                border: 2px solid #6a5acd;
                border-radius: 15px;
                padding: 25px;
                background: white;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
            ">
                <h2 style="color: #6a5acd; margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px;">
                    {name}
                </h2>
                <p style="color: #555;">📧 {email} | 📞 {phone}</p>
                
                <h3 style="color: #6a5acd; border-bottom: 1px solid #eee; padding-bottom: 5px;">SUMMARY</h3>
                <p>{summary}</p>
                
                <h3 style="color: #6a5acd; border-bottom: 1px solid #eee; padding-bottom: 5px;">EXPERIENCE</h3>
                {"".join([
                    f'<p style="margin-bottom: 15px;"><b style="color: #333;">🏢 {job["role"]} at {job["company"]}</b><br>'
                    f'<span style="color: #555;">- {job["description"]}</span></p>' 
                    for job in jobs
                ])}
                
                <h3 style="color: #6a5acd; border-bottom: 1px solid #eee; padding-bottom: 5px;">EDUCATION</h3>
                <p>🎓 {education}</p>
                
                <h3 style="color: #6a5acd; border-bottom: 1px solid #eee; padding-bottom: 5px;">SKILLS</h3>
                <p>🛠️ {skills}</p>
            </div>
            """
            st.markdown(preview_html, unsafe_allow_html=True)
            
            # Download PDF
            if submitted:
                with st.spinner("Creating your PDF..."):
                    pdf_data = generate_pdf(
                        {
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "summary": summary,
                            "jobs": jobs,
                            "education": education,
                            "skills": skills
                        },
                        template
                    )
                    
                    st.download_button(
                        label="📥 Download PDF Resume",
                        data=pdf_data,
                        file_name=f"{name}_Resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.success("Your AI-enhanced resume is ready!")

# --- AI Skill Suggester ---
if st.sidebar.button("🔍 Suggest Skills"):
    with st.sidebar:
        with st.spinner("Analyzing your profile..."):
            job_desc = "\n".join([job["description"] for job in jobs]) if jobs else ""
            suggested_skills = suggest_skills(job_desc)
            st.session_state.skills = suggested_skills
            st.rerun()

# --- Session State Management ---
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "skills" not in st.session_state:
    st.session_state.skills = ""
