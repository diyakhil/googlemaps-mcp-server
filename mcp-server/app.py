import streamlit as st
import httpx
from audio_recorder_streamlit import audio_recorder
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

st.set_page_config(page_title="Driver Assistant Chat", layout="centered")
st.title("Driver Assistant Chat")

st.markdown("Record audio directly or upload an audio file to get a smart response from the assistant.")

location = streamlit_geolocation()

headers = {
    "X-User-Lat": str(location["latitude"]),
    "X-User-Lon": str(location["longitude"]),
}

tab1, tab2 = st.tabs(["Record Audio", "Upload File"])

with tab1:
    st.markdown("### Record your message")
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e87070",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x",
    )
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("Send Recording", key="send_recording"):
            with st.spinner("Sending to assistant..."):
                try:
                    audio_file = io.BytesIO(audio_bytes)
                    files = {"audio": ("recording.wav", audio_file, "audio/wav")}

                    response = httpx.post("http://app:8000/transcribe-audio", files=files, headers=headers, timeout=300.0)
     
                    if response.status_code == 200:
                        st.success("Assistant says:")
                        st.markdown(f"> {clean_chat_output(response.text)}")

                        speak_text(response.text)
                    else:
                        st.error(f"Server returned an error: {response.text}")
                except Exception as e:
                    st.error(f"Failed to contact server: {e}")
                    st.error(f"Failed to contact server: {e}")
                    st.write("DEBUG - Exception details:", str(e)) 

with tab2:
    st.markdown("### Upload an audio file")
    audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "webm", "mp4", "mpga"])
    
    if audio_file is not None:
        with st.spinner("Sending to assistant..."):
            try:
                files = {"audio": (audio_file.name, audio_file, audio_file.type)}
                response = httpx.post("http://app:8000/transcribe-audio", files=files, headers=headers)
                if response.status_code == 200:
                    st.success("Assistant says:")
                    st.markdown(f"> {clean_chat_output(response.text)}")
                    
                     # Convert response text to speech
                    speak_text(response.text)
                else:
                    st.error(f"Server returned an error: {response.text}")
            except Exception as e:
                st.error(f"Failed to contact server: {e}")