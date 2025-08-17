from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class GameBase(BaseModel):
    difficulty_level: str


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    current_state: List[List[int]]


class Game(GameBase):
    id: int
    user_id: int
    puzzle_data: List[List[int]]
    solution: List[List[int]]
    current_state: List[List[int]]
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GameResponse(BaseModel):
    id: int
    puzzle_data: List[List[int]]
    current_state: List[List[int]]
    difficulty_level: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NextGameResponse(BaseModel):
    has_next: bool
    next_game_id: Optional[int] = None
    suggested_difficulty: str
