from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import delete, select

from app.api.deps import SessionDep, get_current_user, require_admin
from app.core.security import get_password_hash
from app.models import Board, RefreshSession, User, UserCreate, UserRead, UserSelfUpdate, UserUpdate

router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
	session: SessionDep, current_user: User = Depends(require_admin)
) -> list[UserRead]:
	users = session.exec(select(User)).all()
	return [UserRead.model_validate(user) for user in users]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
	session: SessionDep,
	payload: UserCreate,
	current_user: User = Depends(require_admin),
) -> UserRead:
	existing = session.exec(select(User).where(User.username == payload.username)).first()
	if existing is not None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
		)
	user = User(
		username=payload.username,
		role=payload.role,
		password_hash=get_password_hash(payload.password),
	)
	session.add(user)
	session.commit()
	session.refresh(user)
	return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
	return UserRead.model_validate(current_user)


@router.patch("/me", response_model=UserRead)
def update_me(
	session: SessionDep,
	payload: UserSelfUpdate,
	current_user: User = Depends(get_current_user),
) -> UserRead:
	updates = payload.model_dump(exclude_unset=True)
	if "password" in updates:
		current_user.password_hash = get_password_hash(updates.pop("password"))
	for key, value in updates.items():
		setattr(current_user, key, value)

	session.add(current_user)
	session.commit()
	session.refresh(current_user)
	return UserRead.model_validate(current_user)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
	session: SessionDep,
	user_id: int,
	payload: UserUpdate,
	current_user: User = Depends(require_admin),
) -> UserRead:
	user = session.get(User, user_id)
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

	updates = payload.model_dump(exclude_unset=True)
	if "password" in updates:
		user.password_hash = get_password_hash(updates.pop("password"))
	for key, value in updates.items():
		setattr(user, key, value)

	session.add(user)
	session.commit()
	session.refresh(user)
	return UserRead.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
	session: SessionDep, user_id: int, current_user: User = Depends(require_admin)
) -> None:
	user = session.get(User, user_id)
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	owned = session.exec(select(Board).where(Board.owner_id == user.id)).first()
	if owned is not None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Cannot delete user who owns boards",
		)
	session.exec(delete(RefreshSession).where(RefreshSession.user_id == user.id))

	session.delete(user)
	session.commit()
