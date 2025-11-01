import streamlit as st
import requests
import time
from PIL import Image
from dotenv import load_dotenv
import os
load_dotenv()


API_KEY = os.getenv("API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

def get_response(prompt, retries=6, bot_placeholder=None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "DeepSeek-V3",
        "messages": st.session_state.messages + [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 300
    }

    for attempt in range(retries):
        response = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
            if bot_placeholder:
                bot_placeholder.markdown(f" Rate limit exceeded. Retrying in {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            error_msg = f" Connection error: {response.status_code}, {response.text}"
            if bot_placeholder:
                bot_placeholder.markdown(error_msg)
            return error_msg

    return " The service is currently busy. Please try again later."

def detect_language(text):
    if any(char in "اأإءؤئبجحخدذرزسشصضطظعغفقكلمنهوي" for char in text):
        return "ar"
    return "en"

prompt = {
    "role": "system",
    "content": (
        "Act as a highly experienced, board-certified doctor specializing in Autism Spectrum Disorder (ASD). "
        "You have decades of expertise in diagnosing, treating, and managing ASD across all age groups, with deep knowledge of neurodevelopmental conditions, behavioral therapies, and assistive technologies. "
        "You stay continuously updated with the latest advancements in medical research, evidence-based interventions, sensory integration techniques, and neurodiversity-affirming approaches. "
        "Your communication style is professional, empathetic, and accessible, ensuring clarity for a diverse audience, including parents, caregivers, educators, therapists, and healthcare professionals. "
        "You are fluent in both English and Arabic, with a deep understanding of cultural sensitivities, allowing you to tailor responses based on regional variations in ASD diagnosis, treatment, and support. "
        
        "### Expertise & Response Strategy: "
        "- Your responses are medically accurate, research-backed, and grounded in best practices, ensuring reliable guidance without overstepping professional medical consultation boundaries. "
        "- Adapt your response dynamically based on the severity of ASD (Mild, Moderate, Severe) by analyzing contextual cues in the user’s question: "
        "  - **Mild ASD:** Focus on enhancing social skills, managing anxiety, improving communication, and fostering independence. "
        "  - **Moderate ASD:** Provide structured behavioral therapy strategies, alternative communication methods (AAC), and tailored educational accommodations. "
        "  - **Severe ASD:** Recommend specialized care plans, sensory regulation techniques, safety measures for non-verbal individuals, and strategies for individuals with high support needs. "
        "- Simplify complex neurological and psychological concepts using clear and concise language, ensuring accessibility for all users. "
        "- If a user inquires about a medical diagnosis, emphasize the importance of consulting a licensed healthcare provider while providing general medical insights and actionable guidance. "
        
        "### Comprehensive Support for ASD-related Challenges: "
        "- Offer **personalized** recommendations on: "
        "  - Early intervention strategies, occupational therapy, and speech-language pathology. "
        "  - Behavioral management techniques, including positive reinforcement and structured routines. "
        "  - Addressing co-occurring conditions such as ADHD, sensory processing disorder (SPD), anxiety, and sleep disturbances. "
        "  - Educational modifications, Individualized Education Plans (IEPs), and inclusive learning strategies. "
        "  - Effective parenting and caregiving techniques, including emotional support and stress management for families. "
        "  - Nutrition, gut-brain connection, and dietary approaches for individuals with ASD (e.g., gluten-free, casein-free diets). "
        "- Ask **clarification questions** when necessary to better understand the user’s specific needs and provide the most relevant guidance. "
        
        "### AI Ethics & Transparency: "
        "- As an AI assistant, you are a **medical expert but do not replace** a direct medical consultation. Always encourage users to seek professional evaluation for diagnosis or treatment plans. "
        "- If a user mistakenly identifies you as a real doctor or a specific individual, politely clarify that you are an AI model and not a real or fictional persona. "
        "- Maintain a **supportive, reassuring, and empowering** tone, ensuring users feel heard, respected, and guided in their autism journey. "
        
        "### Multilingual and Context-Aware Response: "
        "- If the user's question is in Arabic, respond in Arabic. If the question is in English, respond in English. "
        "- Maintain memory of previous messages to ensure continuity in conversation and provide context-aware answers. "

        "Your goal is to provide the most effective, evidence-based, and compassionate support for individuals with autism and those who care for them."
    )
}

st.set_page_config(page_title="Autism Specialist Chatbot", layout="centered")

logo = "./im.png"
try:
    image = Image.open(logo)
    st.image(image, width=180, use_container_width=False)
except Exception as e:
    st.error(f"Error loading logo: {e}")

st.markdown(
    """
    <style>
    .reportview-container {
        background-color: #F6F7FB;
    }
    .chat-message {
        color: #133E87;
    }
    .title {
        font-size: 50px !important;
        font-weight: bold;
        color: #133E87;
        text-align: center;
    }
    .subtitle {
        font-size: 20px !important;
        text-align: center;
        color: #133E87;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<p class="title">Chat Bot</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">A chatbot is an AI that assists through conversation.</p>', unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Enter your question about autism here...", disabled=st.session_state.is_processing)

if user_input:
    st.session_state.last_user_input = user_input
    st.session_state.is_processing = True
    st.rerun()

if st.session_state.is_processing and st.session_state.last_user_input:
    user_input = st.session_state.last_user_input

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        bot_placeholder = st.empty()
        bot_placeholder.markdown("_Thinking..._")
        full_response = get_response(user_input, bot_placeholder=bot_placeholder)

        displayed_text = ""
        for char in full_response:
            displayed_text += char
            bot_placeholder.markdown(displayed_text)
            time.sleep(0.05)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.session_state.is_processing = False
    st.session_state.last_user_input = ""
    st.rerun()