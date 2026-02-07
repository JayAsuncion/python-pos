from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from app.database import Base

class ProductTemplate(Base):
    __tablename__ = "product_template"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    image = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    is_deleted_by = Column(Integer, nullable=True)
