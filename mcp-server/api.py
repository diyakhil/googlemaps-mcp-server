from fastapi import FastAPI, UploadFile, File, HTTPException, Header
import httpx
import os
from pathlib import Path
from chat_agent import process_chat_message
from typing import Optional

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

SUPPORTED_FORMATS = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
OPENAI_TRANSCRIPTION_URL = "https://api.openai.com/v1/audio/transcriptions"

@app.post("/transcribe-audio")
async def transcribe_audio(audio: UploadFile = File(...), latitude: Optional[str] = Header(None, alias="X-User-Lat"),
    longitude: Optional[str] = Header(None, alias="X-User-Lon")):

    print("=== DEBUG INFO ===")
    print("Received latitude:", latitude)
    print("Received longitude:", longitude)
    print("Audio filename:", audio.filename)
    print("Audio content type:", audio.content_type)
    print("==================")

    if latitude and longitude:
        location_info = f" (Current location: lat={latitude}, lon={longitude})"
    else:
        location_info = " (Location not available)"
        print("Warning: Location data not provided")

    print(location_info)

    if not audio.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(audio.filename).suffix.lower()
    if file_extension not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    try:
        audio_content = await audio.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    if len(audio_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is 25MB"
        )
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    files = {
        "file": (audio.filename, audio_content, audio.content_type)
    }

    data = {
        "model": "whisper-1",
        "response_format": "json",
        "temperature": 0
    }

    try:
        # Make request to OpenAI API
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            response = await client.post(
                OPENAI_TRANSCRIPTION_URL,
                headers=headers,
                files=files,
                data=data
            )
        
        # Check if request was successful
        if response.status_code != 200:
            error_detail = response.text
            raise HTTPException(
                status_code=response.status_code,
                detail=f"OpenAI API error: {error_detail}"
            )
        
        transcription_data = response.json()
        transcribed_text = transcription_data.get("text", "")

        #transcribed_text += f" (Current location: lat={latitude}, lon={longitude})"

        print("Transcribed text:", transcribed_text)

        agent_response = await process_chat_message(transcribed_text, "session_id")

        print("Agent response:", agent_response['response'])

        return agent_response["response"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


#test with curl using this command curl 
# -X POST "http://localhost:8000/transcribe-audio" \
  #-H "Content-Type: multipart/form-data" \
  #-F "audio=@/Users/diyakhilnani/Documents/googlemaps-mcp-server/driver_assistant_test.m4a"