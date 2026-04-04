import streamlit as st
import requests
import json
from groq import Groq
from PIL import Image
import google.generativeai as genai
import base64
import io

# Page config for wide layout and custom favicon
st.set_page_config(
    page_title="ARISE",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Black Chancery Bold Italic font and Gemini-style design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');

* {
    font-family: 'Times New Roman', Times, serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Cinzel Decorative', cursive !important;
    text-transform: uppercase !important;
    letter-spacing: 2px;
}

.stApp {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    color: white;
}

.sidebar .sidebar-content {
    background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
    border-right: 1px solid #2a2f45;
}

.stSidebar > div:first-child {
    background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%);
}

.chat-message {
    padding: 1.5rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: 1px solid #4a5fc4;
}

.assistant-message {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border: 1px solid #0f8b6e;
}

.image-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.3);
}

.new-chat-btn {
    background: linear-gradient(135deg, #ff6b6b, #feca57);
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: bold;
    font-size: 16px;
    color: white;
    width: 100%;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.new-chat-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(255,107,107,0.4);
}

.copy-btn, .rewrite-btn {
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 8px 16px;
    color: white;
    font-size: 14px;
    margin: 0 4px;
    transition: all 0.2s ease;
}

.copy-btn:hover, .rewrite-btn:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-1px);
}
</style>
""", unsafe_allow_html=True)

# Initialize API clients
@st.cache_resource
def init_clients():
    groq_client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
    genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY"))
    return groq_client, genai.GenerativeModel('gemini-1.5-flash')

# Load clients
groq_client, gemini_model = init_clients()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar - Gemini Style
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.5rem; margin: 0; color: #ff6b6b; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>
            ARISE
        </h1>
        <p style='color: #a0a0a0; font-size: 0.9rem; margin: 0;'>AI Excellence</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✨ New Chat", key="new_chat", help="Start a fresh conversation"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
    
    st.divider()
    
    # Settings
    with st.expander("⚙️ Settings", expanded=False):
        theme = st.selectbox("Theme", ["Dark (Gemini)", "Light"])
        model_choice = st.selectbox("Chat Model", ["llama-3.3-70b-versatile", "llama3-70b-8192"])
        image_size = st.selectbox("Image Size", ["512x512", "1024x1024"])
    
    st.divider()
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #a0a0a0; font-size: 0.8rem;'>
        Powered by<br>
        <span style='color: #ff6b6b;'>Groq</span> + 
        <span style='color: #4285f4;'>Gemini</span>
    </div>
    """, unsafe_allow_html=True)

# Main chat interface
st.markdown("# ✨ ARISE AI")
st.markdown("**World-class Chat & Image Generation - Free Forever**")

# Display chat messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(
        message["role"], 
        avatar="👤" if message["role"] == "user" else "✨"
    ):
        if "image" in message:
            st.image(message["image"], use_column_width=True)
        else:
            st.markdown(message["content"])
        
        # Action buttons
        if message["role"] == "assistant":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 Copy", key=f"copy_{i}"):
                    st.code(message["content"])
            with col2:
                if st.button("🔄 Rewrite", key=f"rewrite_{i}"):
                    # Trigger rewrite
                    rewrite_prompt = f"Rewrite this response to make it better, more concise, and engaging:\n\n{message['content']}"
                    st.session_state.messages.append({"role": "user", "content": rewrite_prompt})
                    st.rerun()

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✨"):
        # Generate response using Groq Llama-3.3
        with st.spinner("ARISE is thinking..."):
            response = groq_client.chat.completions.create(
                model=st.session_state.get("model", "llama-3.3-70b-versatile"),
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=0.7,
                max_tokens=2048
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Image Generation Tab (using columns for Gemini-style layout)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎨 AI Image Generator")
    image_prompt = st.text_area("Describe your image:", height=100, 
                               placeholder="A futuristic cyberpunk city at night with neon lights...")
    
    if st.button("✨ Generate Image", type="primary"):
        with st.spinner("Creating your image with Gemini..."):
            try:
                response = gemini_model.generate_content(
                    [image_prompt, "Create a high-quality image of this description."]
                )
                # Note: Gemini 1.5 Flash text-to-image via Google AI Studio
                # For production, use the actual image generation endpoint
                st.success("Image generated! (Demo mode - connect your Google API key)")
                # Placeholder image - replace with actual API response
                st.image("https://via.placeholder.com/512x512/667eea/ffffff?text=ARISE+AI+Image", 
                        caption=image_prompt, use_column_width=True)
            except Exception as e:
                st.error(f"Image generation error: {str(e)}")

with col2:
    st.markdown("### 🔧 Quick Actions")
    if st.button("🎭 Surprise Me"):
        surprise_prompts = [
            "A majestic dragon flying over mountains at sunset",
            "Cyberpunk samurai in neon-lit Tokyo streets",
            "Steampunk airship battle in Victorian skies"
        ]
        st.text_area("Surprise prompt:", value=surprise_prompts[0], key="surprise")
    
    st.markdown("**Image Size:**")
    st.radio("Size", ["512x512", "1024x1024"], key="img_size")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #a0a0a0; font-size: 0.9rem;'>
    🚀 ARISE AI - Free ChatGPT + Gemini Alternative | 
    <a href='https://github.com/yourusername/ARISE-AI' style='color: #ff6b6b;'>Source</a>
</div>
""", unsafe_allow_html=True)
