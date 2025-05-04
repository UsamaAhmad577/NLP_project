from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import asyncio
import shutil
import os
from typing import Optional

from model import story_to_audio, extract_text_from_pdf

# Initialize with compatible FastAPI version
app = FastAPI(title="Story2Audio API", version="1.0.0")

# Pydantic model with explicit config
class StoryInput(BaseModel):
    story: str
    
    class Config:
        extra = "forbid"  # Strict validation
        json_schema_extra = {
            "example": {
                "story": "Once upon a time..."
            }
        }

@app.post("/generate")
async def generate_from_text(story_input: StoryInput):
    """Convert text to audio"""
    if not story_input.story.strip():
        raise HTTPException(
            status_code=400,
            detail="Story text cannot be empty"
        )

    try:
        loop = asyncio.get_event_loop()
        audio_path = await loop.run_in_executor(
            None, 
            story_to_audio, 
            story_input.story
        )

        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(
                status_code=500,
                detail="Audio file generation failed"
            )

        return {
            "status": "success",
            "audio_url": f"/audio/{os.path.basename(audio_path)}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Convert PDF to audio"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    temp_path = None
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        text = extract_text_from_pdf(temp_path)
        if not text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        loop = asyncio.get_event_loop()
        audio_path = await loop.run_in_executor(None, story_to_audio, text)
        
        if not audio_path:
            raise HTTPException(
                status_code=500,
                detail="Audio generation failed"
            )

        return {
            "status": "success",
            "audio_url": f"/audio/{os.path.basename(audio_path)}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing error: {str(e)}"
        )
    
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Retrieve generated audio file"""
    file_path = os.path.join("outputs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Audio file not found"
        )
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename
    )