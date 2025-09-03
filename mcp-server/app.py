import streamlit as st
import httpx

st.set_page_config(page_title="Driver Assistant Chat", layout="centered")
st.title("Driver Assistant Chat")

st.markdown("Upload an audio file and get a smart response from the assistant.")

# Audio uploader
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "webm", "mp4", "mpga"])

if audio_file is not None:
    with st.spinner("Sending to assistant..."):
        try:
            files = {"audio": (audio_file.name, audio_file, audio_file.type)}
            response = httpx.post("http://api:8000/transcribe-audio", files=files)  #'api' is the FastAPI container name in Docker
            if response.status_code == 200:
                st.success("Assistant says:")
                st.markdown(f"> {response.text}")
            else:
                st.error(f"Server returned an error: {response.text}")
        except Exception as e:
            st.error(f"Failed to contact server: {e}")
