from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Shift(Base):
    __tablename__ = "shift"

    id = Column(Integer, primary_key=True, index=True)
    shift_template_id = Column(Integer, ForeignKey("shift_template.id"), nullable=False)
    shift_date = Column(Date, nullable=False)  # The calendar date this shift belongs to
    actual_start_datetime = Column(PG_TIMESTAMP(timezone=True), nullable=False)  # When "Start Shift" was clicked
    actual_end_datetime = Column(PG_TIMESTAMP(timezone=True), nullable=True)  # When "End Shift" was clicked
    started_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Who clicked "Start Shift"
    ended_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who clicked "End Shift"
    status = Column(String, nullable=False, default="active")  # "active" or "completed"
    
    # Standard audit fields
    is_active = Column(Boolean, default=True)
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    shift_template = relationship("ShiftTemplate", backref="shifts")
    started_by_user = relationship("User", foreign_keys=[started_by], backref="shifts_started")
    ended_by_user = relationship("User", foreign_keys=[ended_by], backref="shifts_ended")
