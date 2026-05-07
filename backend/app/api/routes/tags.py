from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep, get_current_user
from app.models import Tag, TagCreate, TagRead, TagUpdate, User, UserRole

router = APIRouter()


@router.get("/tags", response_model=list[TagRead])
def list_tags(session: SessionDep, user: User = Depends(get_current_user)) -> list[TagRead]:
	tags = session.exec(
		select(Tag).where((Tag.global_.is_(True)) | (Tag.owner_id == user.id))
	).all()
	return [TagRead.model_validate(tag) for tag in tags]


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(
	session: SessionDep, payload: TagCreate, user: User = Depends(get_current_user)
) -> TagRead:
	tag = Tag(
		text=payload.text,
		text_color=payload.text_color,
		background_color=payload.background_color,
		global_=payload.global_ if user.role == UserRole.ADMIN else False,
		owner_id=None if (payload.global_ and user.role == UserRole.ADMIN) else user.id,
	)
	session.add(tag)
	session.commit()
	session.refresh(tag)
	return TagRead.model_validate(tag)


@router.patch("/tags/{tag_id}", response_model=TagRead)
def update_tag(
	session: SessionDep,
	tag_id: int,
	payload: TagUpdate,
	user: User = Depends(get_current_user),
) -> TagRead:
	tag = session.get(Tag, tag_id)
	if tag is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
	if not tag.global_ and tag.owner_id != user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied")
	if tag.global_ and user.role != UserRole.ADMIN:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied")

	updates = payload.model_dump(exclude_unset=True)
	for key, value in updates.items():
		if key == "global_" and user.role != UserRole.ADMIN:
			continue
		setattr(tag, key, value)
	session.add(tag)
	session.commit()
	session.refresh(tag)
	return TagRead.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_200_OK)
def delete_tag(
	session: SessionDep, tag_id: int, user: User = Depends(get_current_user)
) -> None:
	tag = session.get(Tag, tag_id)
	if tag is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
	if tag.global_ and user.role != UserRole.ADMIN:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied")
	if not tag.global_ and tag.owner_id != user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied")
	session.delete(tag)
	session.commit()
