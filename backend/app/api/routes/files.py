from __future__ import annotations

from fastapi import APIRouter, Depends, File as UploadFileDep, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.api.deps import SessionDep, get_current_user
from app.models import File as FileModel, FileRead, User

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


@router.post("/files", response_model=FileRead, status_code=status.HTTP_201_CREATED)
async def upload_file(
    session: SessionDep,
    file: UploadFile = UploadFileDep(...),
    user: User = Depends(get_current_user),
) -> FileRead:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    content = await file.read()
    record = FileModel(
        filename=file.filename or "upload",
        mime_type=file.content_type or "application/octet-stream",
        size=len(content),
        content=content,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return FileRead.model_validate(record)


@router.get("/files/{file_id}")
def download_file(session: SessionDep, file_id: int) -> Response:
    record = session.get(FileModel, file_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return Response(content=record.content, media_type=record.mime_type)


@router.delete("/files/{file_id}", status_code=status.HTTP_200_OK)
def delete_file(
    session: SessionDep, file_id: int, user: User = Depends(get_current_user)
) -> None:
    record = session.get(FileModel, file_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    session.delete(record)
    session.commit()
