from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
import pytesseract
from PIL import Image
import io
from googletrans import Translator
from gtts import gTTS
import os
import uuid

app = FastAPI()
translator = Translator()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/process-prescription/")
async def process_prescription(file: UploadFile = File(...), target_lang: str = "hi"):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # OCR: extract English text
    text = pytesseract.image_to_string(image)

    # Translate text
    translated = translator.translate(text, dest=target_lang).text

    # Generate TTS audio
    tts = gTTS(text=translated, lang=target_lang)
    audio_filename = f"audio_{uuid.uuid4()}.mp3"
    tts.save(audio_filename)

    return JSONResponse({
        "original_text": text,
        "translated_text": translated,
        "audio_file": f"/audio/{audio_filename}"
    })

@app.get("/audio/{filename}")
def get_audio(filename: str):
    file_path = f"./{filename}"
    if os.path.exists(file_path):
        return FileResponse(path=file_path, media_type="audio/mpeg", filename=filename)
    return JSONResponse({"error": "File not found"}, status_code=404)
