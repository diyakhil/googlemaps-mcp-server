import streamlit as st
import httpx
from audio_recorder_streamlit import audio_recorder
import io

st.set_page_config(page_title="Driver Assistant Chat", layout="centered")
st.title("Driver Assistant Chat")

st.markdown("Record audio directly or upload an audio file to get a smart response from the assistant.")

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
                    # Create a file-like object from the audio bytes
                    audio_file = io.BytesIO(audio_bytes)
                    files = {"audio": ("recording.wav", audio_file, "audio/wav")}
                    
                    response = httpx.post("http://app:8000/transcribe-audio", files=files, timeout=60.0)
                    if response.status_code == 200:
                        st.success("Assistant says:")
                        st.markdown(f"> {response.text}")
                    else:
                        st.error(f"Server returned an error: {response.text}")
                except Exception as e:
                    st.error(f"Failed to contact server: {e}")

with tab2:
    st.markdown("### Upload an audio file")
    audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "webm", "mp4", "mpga"])
    
    if audio_file is not None:
        with st.spinner("Sending to assistant..."):
            try:
                files = {"audio": (audio_file.name, audio_file, audio_file.type)}
                response = httpx.post("http://app:8000/transcribe-audio", files=files, timeout=60.0)
                if response.status_code == 200:
                    st.success("Assistant says:")
                    st.markdown(f"> {response.text}")
                else:
                    st.error(f"Server returned an error: {response.text}")
            except Exception as e:
                st.error(f"Failed to contact server: {e}")