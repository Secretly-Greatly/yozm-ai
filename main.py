import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from process import processing
import uvicorn

app = FastAPI()

@app.post("/photo_upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = f"uploaded/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    photo_id = processing(save_path)
    
    if photo_id == None:
        return JSONResponse(content={"content": "일치하는 사진이 없습니다."})
    
    return JSONResponse(content={"id": photo_id})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)