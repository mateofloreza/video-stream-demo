# main.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Video, Base
from schemas import VideoRead
from s3client import generate_s3_key, upload_fileobj, get_presigned_url, stream_s3_object

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Video upload demo")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload", response_model=VideoRead)
def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Basic validation: allow common video mime types (optional)
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video/* content types allowed")

    s3_key = generate_s3_key(file.filename)

    # Upload file to S3
    try:
        # file.file is a SpooledTemporaryFile; pass directly to boto3 upload_fileobj
        upload_fileobj(file.file, s3_key, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {e}")

    # Store metadata in DB
    video = Video(filename=file.filename, mime_type=file.content_type, s3_key=s3_key)
    db.add(video)
    db.commit()
    db.refresh(video)

    return video

@app.get("/videos/{video_id}", response_model=VideoRead)
def get_video_metadata(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@app.get("/videos/{video_id}/stream-url")
def get_stream_url(video_id: int, db: Session = Depends(get_db)):
    """
    Return a presigned URL for direct client-to-S3 streaming/download.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    try:
        url = get_presigned_url(video.s3_key, expires_in=3600)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create presigned URL: {e}")
    return {"url": url, "expires_in": 3600}

@app.get("/videos/{video_id}/stream")
def stream_video_proxy(video_id: int, db: Session = Depends(get_db)):
    """
    Proxy streaming: server reads from S3 and streams bytes to client. Useful if you
    want to hide S3 keys or support content-range handling (not implemented here).
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    try:
        generator = stream_s3_object(video.s3_key)
        return StreamingResponse(generator, media_type=video.mime_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 stream failed: {e}")

