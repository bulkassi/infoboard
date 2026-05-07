from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import delete, select

from app.api.deps import SessionDep, get_current_user, get_optional_user
from app.models import (
	Board,
	BoardType,
	CardCommon,
	CardCreate,
	CardEmployee,
	CardPositionUpdate,
	CardRead,
	CardService,
	CardUpdate,
	ShareLink,
	Tag,
	TagToCard,
	TagRead,
	User,
)

router = APIRouter()

PUBLIC_TYPES = {
	BoardType.MAIN,
	BoardType.ABOUT,
	BoardType.EMPLOYEES,
	BoardType.SERVICES,
}


def _get_board_or_404(session: SessionDep, board_id: int) -> Board:
	board = session.get(Board, board_id)
	if board is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
	return board


def _is_share_token_valid(
	session: SessionDep, board_id: int, token: str | None
) -> bool:
	if not token:
		return False
	share = session.exec(
		select(ShareLink).where(ShareLink.token == token, ShareLink.board_id == board_id)
	).first()
	if share is None:
		return False
	return share.expires_at >= datetime.now(timezone.utc)


def _ensure_can_view_board(
	session: SessionDep, board: Board, user: User | None, share_token: str | None
) -> None:
	if board.type in PUBLIC_TYPES:
		return
	if user is not None:
		return
	if _is_share_token_valid(session, board.id, share_token):
		return
	raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _ensure_can_edit_board(session: SessionDep, board: Board, user: User) -> None:
	if board.type in {BoardType.MAIN, BoardType.EMPLOYEES, BoardType.SERVICES}:
		return
	if board.type == BoardType.COMMON and board.owner_id == user.id:
		return
	raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Edit access denied")


def _card_to_read(card: Any, card_type: str, tag_ids: list[int]) -> CardRead:
	data = card.model_dump()
	return CardRead(type=card_type, tag_ids=tag_ids, **data)


def _get_tags_for_card(session: SessionDep, card_id: int) -> list[int]:
	rows = session.exec(
		select(TagToCard.tag_id).where(TagToCard.card_id == card_id)
	).all()
	return list(rows)


def _get_card_and_type_or_404(session: SessionDep, card_id: int) -> tuple[Any, str]:
	card = session.get(CardCommon, card_id)
	card_type = "common"
	if card is None:
		card = session.get(CardEmployee, card_id)
		card_type = "employee"
	if card is None:
		card = session.get(CardService, card_id)
		card_type = "service"
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	return card, card_type


def _set_tags_for_card(
	session: SessionDep, user: User, card_id: int, tag_ids: list[int]
) -> None:
	if not tag_ids:
		session.exec(
			delete(TagToCard).where(TagToCard.card_id == card_id)
		)
		return

	tags = session.exec(select(Tag).where(Tag.id.in_(tag_ids))).all()
	if len(tags) != len(set(tag_ids)):
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tags")
	for tag in tags:
		if not tag.global_ and tag.owner_id != user.id:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied"
			)

	session.exec(
		delete(TagToCard).where(TagToCard.card_id == card_id)
	)
	for tag_id in set(tag_ids):
		session.add(TagToCard(card_id=card_id, tag_id=tag_id))


def _ensure_can_edit_card_tags(session: SessionDep, card_id: int, user: User) -> CardCommon:
	card = session.get(CardCommon, card_id)
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	board = _get_board_or_404(session, card.board_id)
	_ensure_can_edit_board(session, board, user)
	return card


def _get_tags_for_card_read(session: SessionDep, card_id: int) -> list[TagRead]:
	return [
		TagRead.model_validate(tag)
		for tag in session.exec(
			select(Tag)
			.join(TagToCard, Tag.id == TagToCard.tag_id)
			.where(TagToCard.card_id == card_id)
		).all()
	]


@router.get("/boards/{board_id}/cards", response_model=list[CardRead])
def get_cards(
	session: SessionDep,
	board_id: int,
	user: User | None = Depends(get_optional_user),
	share_token: str | None = Query(default=None),
) -> list[CardRead]:
	board = _get_board_or_404(session, board_id)
	_ensure_can_view_board(session, board, user, share_token)

	cards: list[CardRead] = []
	for card in session.exec(select(CardCommon).where(CardCommon.board_id == board.id)).all():
		tags = _get_tags_for_card(session, card.id)
		cards.append(_card_to_read(card, "common", tags))
	for card in session.exec(select(CardEmployee).where(CardEmployee.board_id == board.id)).all():
		cards.append(_card_to_read(card, "employee", []))
	for card in session.exec(select(CardService).where(CardService.board_id == board.id)).all():
		cards.append(_card_to_read(card, "service", []))

	return cards


@router.post("/boards/{board_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(
	session: SessionDep,
	board_id: int,
	payload: CardCreate,
	user: User = Depends(get_current_user),
) -> CardRead:
	board = _get_board_or_404(session, board_id)
	_ensure_can_edit_board(session, board, user)

	if payload.type == "common":
		card = CardCommon(
			board_id=board.id,
			title=payload.title,
			content=payload.content,
			col=payload.col,
			row=payload.row,
			col_span=payload.col_span,
			row_span=payload.row_span,
			file_id=payload.file_id,
		)
	elif payload.type == "employee":
		card = CardEmployee(
			board_id=board.id,
			surname=payload.surname,
			name=payload.name,
			patronymic=payload.patronymic,
			position=payload.position,
			file_id=payload.file_id,
		)
	elif payload.type == "service":
		card = CardService(
			board_id=board.id,
			name=payload.name,
			description=payload.description,
			link=payload.link,
			file_id=payload.file_id,
		)
	else:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown card type")

	session.add(card)
	session.commit()
	session.refresh(card)

	if payload.type == "common":
		_set_tags_for_card(session, user, card.id, payload.tag_ids)
		session.commit()
		tags = _get_tags_for_card(session, card.id)
	else:
		tags = []
	return _card_to_read(card, payload.type, tags)


@router.get("/cards/{card_id}/tags", response_model=list[TagRead])
def get_card_tags(
	session: SessionDep,
	card_id: int,
	user: User | None = Depends(get_optional_user),
	share_token: str | None = Query(default=None),
) -> list[TagRead]:
	card = session.get(CardCommon, card_id)
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	board = _get_board_or_404(session, card.board_id)
	_ensure_can_view_board(session, board, user, share_token)
	return _get_tags_for_card_read(session, card.id)


@router.post("/cards/{card_id}/tags/{tag_id}", response_model=list[TagRead])
def attach_tag_to_card(
	session: SessionDep,
	card_id: int,
	tag_id: int,
	user: User = Depends(get_current_user),
) -> list[TagRead]:
	card = _ensure_can_edit_card_tags(session, card_id, user)
	tag = session.get(Tag, tag_id)
	if tag is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
	if not tag.global_ and tag.owner_id != user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tag access denied")
	if session.exec(
		select(TagToCard).where(
			TagToCard.card_id == card.id,
			TagToCard.tag_id == tag.id,
		)
	).first() is None:
		session.add(TagToCard(card_id=card.id, tag_id=tag.id))
		session.commit()
	return _get_tags_for_card_read(session, card.id)


@router.delete("/cards/{card_id}/tags/{tag_id}", response_model=list[TagRead])
def detach_tag_from_card(
	session: SessionDep,
	card_id: int,
	tag_id: int,
	user: User = Depends(get_current_user),
) -> list[TagRead]:
	card = _ensure_can_edit_card_tags(session, card_id, user)
	card_tag = session.exec(
		select(TagToCard).where(
			TagToCard.card_id == card.id,
			TagToCard.tag_id == tag_id,
		)
	).first()
	if card_tag is not None:
		session.delete(card_tag)
		session.commit()
	return _get_tags_for_card_read(session, card.id)


@router.patch("/cards/{card_id}", response_model=CardRead)
def update_card(
	session: SessionDep,
	card_id: int,
	payload: CardUpdate,
	user: User = Depends(get_current_user),
) -> CardRead:
	card = session.get(CardCommon, card_id)
	card_type = "common"
	if card is None:
		card = session.get(CardEmployee, card_id)
		card_type = "employee"
	if card is None:
		card = session.get(CardService, card_id)
		card_type = "service"
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

	board = _get_board_or_404(session, card.board_id)
	_ensure_can_edit_board(session, board, user)

	updates = payload.model_dump(exclude_unset=True)
	tag_ids = updates.pop("tag_ids", None)
	position_fields = {"col", "row", "col_span", "row_span"}
	for key, value in updates.items():
		if card_type != "common" and key in position_fields:
			continue
		if hasattr(card, key):
			setattr(card, key, value)

	session.add(card)
	session.commit()
	session.refresh(card)

	if tag_ids is not None and card_type == "common":
		_set_tags_for_card(session, user, card.id, tag_ids)
		session.commit()

	if card_type == "common":
		tags = _get_tags_for_card(session, card.id)
	else:
		tags = []
	return _card_to_read(card, card_type, tags)


@router.patch("/cards/{card_id}/position", response_model=CardRead)
def update_card_position(
	session: SessionDep,
	card_id: int,
	payload: CardPositionUpdate,
	user: User = Depends(get_current_user),
) -> CardRead:
	card = session.get(CardCommon, card_id)
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

	board = _get_board_or_404(session, card.board_id)
	_ensure_can_edit_board(session, board, user)

	card.col = payload.col
	card.row = payload.row
	card.col_span = payload.col_span
	card.row_span = payload.row_span
	session.add(card)
	session.commit()
	session.refresh(card)
	tags = _get_tags_for_card(session, card.id)
	return _card_to_read(card, "common", tags)


@router.delete("/cards/{card_id}", status_code=status.HTTP_200_OK)
def delete_card(
	session: SessionDep, card_id: int, user: User = Depends(get_current_user)
) -> None:
	card = session.get(CardCommon, card_id)
	card_type = "common"
	if card is None:
		card = session.get(CardEmployee, card_id)
		card_type = "employee"
	if card is None:
		card = session.get(CardService, card_id)
		card_type = "service"
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

	board = _get_board_or_404(session, card.board_id)
	_ensure_can_edit_board(session, board, user)

	session.exec(
		delete(TagToCard).where(TagToCard.card_id == card.id)
	)
	session.delete(card)
	session.commit()
