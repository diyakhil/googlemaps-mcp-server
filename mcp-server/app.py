import streamlit as st
import httpx
try:
    from streamlit_audiorecorder import audiorecorder
except ImportError:
    from audiorecorder import audiorecorder
import io
from text_to_speech import speak_text
from streamlit_geolocation import streamlit_geolocation
import re 
from html import unescape


def clean_chat_output(text):
    """
    Cleans and formats chat agent output for Streamlit-safe Markdown rendering.

    Handles:
    - Escape characters like \\n, \n, \t
    - Markdown (**bold**, *italic*, > quote)
    - Simple HTML tags like <b>, <br>
    - Unescaped HTML entities (&amp;, &nbsp;, etc.)
    """

    # Unescape HTML entities like &amp;, &nbsp;, etc.
    text = unescape(text)

    # Replace backslash-escaped newlines (\n, \\n) with Markdown line breaks
    text = text.replace('\\n', '\n')  # double-escaped
    text = text.replace('\n', '  \n')  # Markdown line break

    # Convert simple HTML tags to Markdown
    text = re.sub(r'<\s*(b|strong)\s*>', '**', text)
    text = re.sub(r'<\s*/\s*(b|strong)\s*>', '**', text)
    text = re.sub(r'<\s*(i|em)\s*>', '*', text)
    text = re.sub(r'<\s*/\s*(i|em)\s*>', '*', text)
    text = re.sub(r'<\s*br\s*/?>', '  \n', text)

    return text 


# -----------------------------------------------------
# Streamlit App UI
# -----------------------------------------------------
st.set_page_config(page_title="Driver Assistant Chat", layout="centered")
st.title("Driver Assistant Chat")

# Location info
location = streamlit_geolocation()
headers = {
    "X-User-Lat": str(location["latitude"]),
    "X-User-Lon": str(location["longitude"]),
}

# Create tabs for Audio and Text chat
tab_audio, tab_text = st.tabs(["🎤 Audio Chat", "💬 Text Chat"])

# -----------------------------------------------------
# 🎤 AUDIO CHAT TAB
# -----------------------------------------------------
with tab_audio:
    st.markdown("### Record your message")
    st.markdown("Record audio directly or upload an audio file to get a smart response from the assistant.")

    audio = audiorecorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        pause_prompt="",
        start_style={},
        pause_style={},
        stop_style={},
        show_visualizer=True,
        key=None
    )

    if len(audio) > 0:
        audio_bytes = audio.export().read()
        st.audio(audio_bytes)
        
        if st.button("Send Recording", key="send_recording"):
            with st.spinner("Sending to assistant..."):
                try:
                    audio_file = io.BytesIO(audio_bytes)
                    files = {"audio": ("recording.wav", audio_file, "audio/wav")}

                    response = httpx.post(
                        "http://app:8000/transcribe-audio", 
                        files=files, 
                        headers=headers, 
                        timeout=300.0
                    )
        
                    if response.status_code == 200:
                        st.success("Assistant says:")
                        st.markdown(f"> {clean_chat_output(response.text)}")

                        speak_text(response.text)
                    else:
                        st.error(f"Server returned an error: {response.text}")
                except Exception as e:
                    st.error(f"Failed to contact server: {e}")
                    st.write("DEBUG - Exception details:", str(e))


# -----------------------------------------------------
# 💬 TEXT CHAT TAB
# -----------------------------------------------------
with tab_text:
    st.markdown("### Type your message to chat with the assistant")

    user_input = st.text_area("Enter your message:", placeholder="Hey assistant, how’s the weather today?")
    # session_id = st.text_input("Session ID (optional)", value="default_session")
    session_id = "session_id"

    if st.button("Send Text", key="send_text"):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            with st.spinner("Contacting assistant..."):
                try:
                    payload = {
                        "text": user_input,
                        "session_id": session_id
                    }

                    response = httpx.post(
                        "http://app:8000/chat",
                        json=payload,
                        headers=headers,
                        timeout=300.0
                    )

                    if response.status_code == 200:
                        response_json = response.json()
                        message = response_json.get("response", "")
                        st.success("Assistant says:")
                        st.markdown(f"> {clean_chat_output(message)}")

                        speak_text(message)

                    else:
                        st.error(f"Server returned error {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"Failed to contact server: {e}")
                    st.write("DEBUG - Exception details:", str(e))
