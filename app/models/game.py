from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    puzzle_data = Column(Text, nullable=False)  # JSON string of initial puzzle
    solution = Column(Text, nullable=False)  # JSON string of solution
    current_state = Column(Text, nullable=False)  # JSON string of current state
    difficulty_level = Column(String, nullable=False)  # easy, medium, hard, expert
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="games")
