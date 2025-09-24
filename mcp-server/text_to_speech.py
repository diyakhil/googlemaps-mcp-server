from bs4 import BeautifulSoup
from gtts import gTTS
import tempfile
import os
import streamlit as st
import re 

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

def clean_text_formatting(text):
    """
    Cleans up markdown, special characters, and formatting issues from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned and formatted text.
    """
    # Remove markdown-style bold and italics (e.g., **bold**, *italic*)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)

    # Remove markdown headers and horizontal rules
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # removes headers like # Title
    text = re.sub(r'-{3,}', '', text)  # removes '---' or '----'

    # Replace \n and \r with space
    text = text.replace('\\n', ' ').replace('\\r', ' ')

    # Remove stray hash symbols
    text = re.sub(r'#', '', text)

    # Collapse multiple spaces into one
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def speak_text(text):
    """
    Takes a text response, cleans HTML, converts to speech, and plays it.
    
    Args:
        text (str): The text to be cleaned and converted to speech.
    """
    html_cleaned_response = clean_html(text)
    clean_response = clean_text_formatting(html_cleaned_response)
    
    tts = gTTS(clean_response)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        tts.save(temp_audio.name)
        temp_audio.close()
        
        st.audio(temp_audio.name, format='audio/mp3')
        os.remove(temp_audio.name)
