from bs4 import BeautifulSoup
from gtts import gTTS
import tempfile
import os
import streamlit as st

def clean_html(text):
    """
    Cleans HTML tags from the given text using BeautifulSoup.
    
    Args:
        text (str): The input text that may contain HTML tags.
    
    Returns:
        str: The cleaned text without HTML tags.
    """
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=' ', strip=True)
    return clean_text

def speak_text(text):
    """
    Takes a text response, cleans HTML, converts to speech, and plays it.
    
    Args:
        text (str): The text to be cleaned and converted to speech.
    """
    clean_response = clean_html(text)
    
    tts = gTTS(clean_response)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        tts.save(temp_audio.name)
        temp_audio.close()
        
        st.audio(temp_audio.name, format='audio/mp3')
        os.remove(temp_audio.name)
