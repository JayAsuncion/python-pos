from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    product_template_id = Column(Integer, ForeignKey("product_template.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    image = Column(String, nullable=True)
    starting_stock = Column(Numeric(15, 6), nullable=False, default=0)
    running_stock = Column(Numeric(15, 6), nullable=False, default=0)
    cost_price = Column(Numeric(15, 6), nullable=False)
    selling_price = Column(Numeric(15, 6), nullable=False)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Relationship to ProductTemplate
    product_template = relationship("ProductTemplate", backref="products")
