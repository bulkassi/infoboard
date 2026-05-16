from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import delete, select

from app.api.deps import SessionDep, get_current_user, get_optional_user
from app.models import (
	Board,
	BoardType,
	CardBase,
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
	expires_at = share.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	return expires_at >= datetime.now(timezone.utc)


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


def _merge_card_read(
	base: CardBase,
	card: Any,
	card_type: str,
	tag_ids: list[int],
) -> CardRead:
	card_data = card.model_dump(exclude={"card_id"})
	return CardRead(
		id=base.id,
		board_id=base.board_id,
		file_id=base.file_id,
		type=card_type,
		tag_ids=tag_ids,
		**card_data,
	)


def _get_tags_for_card(session: SessionDep, card_id: int) -> list[int]:
	rows = session.exec(
		select(TagToCard.tag_id).where(TagToCard.card_id == card_id)
	).all()
	return list(rows)


def _get_card_with_base_or_404(
	session: SessionDep, card_id: int
) -> tuple[CardBase, Any, str]:
	base = session.get(CardBase, card_id)
	if base is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

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

	return base, card, card_type


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
	base = session.get(CardBase, card_id)
	if base is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	board = _get_board_or_404(session, base.board_id)
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
	for base, card in session.exec(
		select(CardBase, CardCommon)
		.where(CardBase.board_id == board.id)
		.where(CardCommon.card_id == CardBase.id)
	).all():
		tags = _get_tags_for_card(session, base.id)
		cards.append(_merge_card_read(base, card, "common", tags))
	for base, card in session.exec(
		select(CardBase, CardEmployee)
		.where(CardBase.board_id == board.id)
		.where(CardEmployee.card_id == CardBase.id)
	).all():
		cards.append(_merge_card_read(base, card, "employee", []))
	for base, card in session.exec(
		select(CardBase, CardService)
		.where(CardBase.board_id == board.id)
		.where(CardService.card_id == CardBase.id)
	).all():
		cards.append(_merge_card_read(base, card, "service", []))

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

	base = CardBase(
		board_id=board.id,
		file_id=payload.file_id,
	)
	session.add(base)
	session.commit()
	session.refresh(base)

	if payload.type == "common":
		card = CardCommon(
			card_id=base.id,
			title=payload.title,
			content=payload.content,
			col=payload.col,
			row=payload.row,
			col_span=payload.col_span,
			row_span=payload.row_span,
		)
	elif payload.type == "employee":
		card = CardEmployee(
			card_id=base.id,
			surname=payload.surname,
			name=payload.name,
			patronymic=payload.patronymic,
			position=payload.position,
		)
	elif payload.type == "service":
		card = CardService(
			card_id=base.id,
			name=payload.name,
			description=payload.description,
			link=payload.link,
		)
	else:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown card type")

	session.add(card)
	session.commit()
	if payload.type == "common":
		card = session.get(CardCommon, base.id)
	elif payload.type == "employee":
		card = session.get(CardEmployee, base.id)
	else:
		card = session.get(CardService, base.id)

	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	session.refresh(base)
	session.refresh(card)

	if payload.type == "common":
		_set_tags_for_card(session, user, base.id, payload.tag_ids)
		session.commit()
		tags = _get_tags_for_card(session, base.id)
		session.refresh(base)
		session.refresh(card)
	else:
		tags = []
	return _merge_card_read(base, card, payload.type, tags)


@router.get("/cards/{card_id}/tags", response_model=list[TagRead])
def get_card_tags(
	session: SessionDep,
	card_id: int,
	user: User | None = Depends(get_optional_user),
	share_token: str | None = Query(default=None),
) -> list[TagRead]:
	base = session.get(CardBase, card_id)
	if base is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	card = session.get(CardCommon, card_id)
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	session.refresh(base)
	session.refresh(card)
	board = _get_board_or_404(session, base.board_id)
	_ensure_can_view_board(session, board, user, share_token)
	return _get_tags_for_card_read(session, base.id)


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
			TagToCard.card_id == card.card_id,
			TagToCard.tag_id == tag.id,
		)
	).first() is None:
		session.add(TagToCard(card_id=card.card_id, tag_id=tag.id))
		session.commit()
	return _get_tags_for_card_read(session, card.card_id)


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
			TagToCard.card_id == card.card_id,
			TagToCard.tag_id == tag_id,
		)
	).first()
	if card_tag is not None:
		session.delete(card_tag)
		session.commit()
	return _get_tags_for_card_read(session, card.card_id)


@router.patch("/cards/{card_id}", response_model=CardRead)
def update_card(
	session: SessionDep,
	card_id: int,
	payload: CardUpdate,
	user: User = Depends(get_current_user),
) -> CardRead:
	base, card, card_type = _get_card_with_base_or_404(session, card_id)

	board = _get_board_or_404(session, base.board_id)
	_ensure_can_edit_board(session, board, user)

	updates = payload.model_dump(exclude_unset=True)
	tag_ids = updates.pop("tag_ids", None)
	position_fields = {"col", "row", "col_span", "row_span"}
	if "file_id" in updates:
		base.file_id = updates.pop("file_id")
	for key, value in updates.items():
		if card_type != "common" and key in position_fields:
			continue
		if hasattr(card, key):
			setattr(card, key, value)

	session.add(base)
	session.add(card)
	session.commit()
	base = session.get(CardBase, base.id)
	if base is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	if card_type == "common":
		card = session.get(CardCommon, base.id)
	elif card_type == "employee":
		card = session.get(CardEmployee, base.id)
	else:
		card = session.get(CardService, base.id)
	if card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

	if tag_ids is not None and card_type == "common":
		_set_tags_for_card(session, user, base.id, tag_ids)
		session.commit()
		session.refresh(base)
		session.refresh(card)

	if card_type == "common":
		tags = _get_tags_for_card(session, base.id)
	else:
		tags = []
	return _merge_card_read(base, card, card_type, tags)


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
	base = session.get(CardBase, card_id)
	if base is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")

	board = _get_board_or_404(session, base.board_id)
	_ensure_can_edit_board(session, board, user)

	card.col = payload.col
	card.row = payload.row
	card.col_span = payload.col_span
	card.row_span = payload.row_span
	session.add(card)
	session.commit()
	base = session.get(CardBase, base.id)
	card = session.get(CardCommon, card_id)
	if base is None or card is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
	session.refresh(base)
	session.refresh(card)
	tags = _get_tags_for_card(session, base.id)
	return _merge_card_read(base, card, "common", tags)


@router.delete("/cards/{card_id}", status_code=status.HTTP_200_OK)
def delete_card(
	session: SessionDep, card_id: int, user: User = Depends(get_current_user)
) -> None:
	base, card, card_type = _get_card_with_base_or_404(session, card_id)

	board = _get_board_or_404(session, base.board_id)
	_ensure_can_edit_board(session, board, user)

	session.exec(
		delete(TagToCard).where(TagToCard.card_id == base.id)
	)

	if card_type == "common":
		session.exec(delete(CardCommon).where(CardCommon.card_id == base.id))
	elif card_type == "employee":
		session.exec(delete(CardEmployee).where(CardEmployee.card_id == base.id))
	else:
		session.exec(delete(CardService).where(CardService.card_id == base.id))

	session.exec(delete(CardBase).where(CardBase.id == base.id))
	session.commit()
