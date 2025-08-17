from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Game
from ..schemas import GameCreate, GameUpdate, GameResponse, NextGameResponse
from ..core.security import get_current_user
from ..core.sudoku import sudoku_generator, board_to_json, json_to_board

router = APIRouter(prefix="/games", tags=["games"])


@router.get("/", response_model=List[GameResponse])
def get_user_games(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    games = db.query(Game).filter(Game.user_id == current_user.id).all()

    game_responses = []
    for game in games:
        game_responses.append(
            GameResponse(
                id=game.id,
                puzzle_data=json_to_board(game.puzzle_data),
                current_state=json_to_board(game.current_state),
                difficulty_level=game.difficulty_level,
                completed=game.completed,
                created_at=game.created_at,
                updated_at=game.updated_at,
                completed_at=game.completed_at,
            )
        )

    return game_responses


@router.post("/new", response_model=GameResponse)
def create_new_game(
    game_create: GameCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    puzzle, solution = sudoku_generator.generate_puzzle(game_create.difficulty_level)

    db_game = Game(
        user_id=current_user.id,
        puzzle_data=board_to_json(puzzle),
        solution=board_to_json(solution),
        current_state=board_to_json(puzzle),
        difficulty_level=game_create.difficulty_level,
    )

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return GameResponse(
        id=db_game.id,
        puzzle_data=puzzle,
        current_state=puzzle,
        difficulty_level=db_game.difficulty_level,
        completed=db_game.completed,
        created_at=db_game.created_at,
        updated_at=db_game.updated_at,
        completed_at=db_game.completed_at,
    )


@router.get("/next-available", response_model=NextGameResponse)
def get_next_available_game(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    next_game = (
        db.query(Game)
        .filter(Game.user_id == current_user.id, Game.completed.is_(False))
        .first()
    )

    difficulty_progression = ["easy", "medium", "hard", "expert"]
    completed_games = (
        db.query(Game)
        .filter(Game.user_id == current_user.id, Game.completed.is_(True))
        .count()
    )

    suggested_difficulty = difficulty_progression[min(completed_games // 5, 3)]

    return NextGameResponse(
        has_next=next_game is not None,
        next_game_id=next_game.id if next_game else None,
        suggested_difficulty=suggested_difficulty,
    )


@router.get("/{game_id}", response_model=GameResponse)
def get_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = (
        db.query(Game)
        .filter(Game.id == game_id, Game.user_id == current_user.id)
        .first()
    )

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    return GameResponse(
        id=game.id,
        puzzle_data=json_to_board(game.puzzle_data),
        current_state=json_to_board(game.current_state),
        difficulty_level=game.difficulty_level,
        completed=game.completed,
        created_at=game.created_at,
        updated_at=game.updated_at,
        completed_at=game.completed_at,
    )


@router.put("/{game_id}", response_model=GameResponse)
def update_game(
    game_id: int,
    game_update: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    game = (
        db.query(Game)
        .filter(Game.id == game_id, Game.user_id == current_user.id)
        .first()
    )

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    if game.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update completed game",
        )

    game.current_state = board_to_json(game_update.current_state)

    if sudoku_generator.is_complete(game_update.current_state):
        game.completed = True
        game.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(game)

    return GameResponse(
        id=game.id,
        puzzle_data=json_to_board(game.puzzle_data),
        current_state=json_to_board(game.current_state),
        difficulty_level=game.difficulty_level,
        completed=game.completed,
        created_at=game.created_at,
        updated_at=game.updated_at,
        completed_at=game.completed_at,
    )
