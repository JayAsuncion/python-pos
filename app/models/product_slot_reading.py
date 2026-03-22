from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP as PG_TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.database import Base

class ProductSlotReading(Base):
    __tablename__ = "product_slot_reading"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shift.id"), nullable=False)
    product_slot_id = Column(Integer, ForeignKey("product_slot.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)  # Snapshot at shift start
    start_reading = Column(Numeric(15, 6), nullable=False)
    end_reading = Column(Numeric(15, 6), nullable=True)  # Null until shift ends
    start_reading_image_url = Column(String, nullable=False)  # Required image URL
    end_reading_image_url = Column(String, nullable=True)  # Required when shift ends
    cost_price_snapshot = Column(Numeric(15, 6), nullable=False)  # Price at shift start
    selling_price_snapshot = Column(Numeric(15, 6), nullable=False)  # Price at shift start
    
    # Void tracking fields
    voided_at = Column(PG_TIMESTAMP(timezone=True), nullable=True)
    voided_by = Column(Integer, nullable=True)
    void_reason = Column(String, nullable=True)
    
    # Standard audit fields
    created_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(PG_TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, nullable=True)

    # Unique constraint: one reading record per product slot per shift
    __table_args__ = (UniqueConstraint('shift_id', 'product_slot_id', name='_shift_product_slot_uc'),)

    # Relationships
    shift = relationship("Shift", backref="product_slot_readings")
    product_slot = relationship("ProductSlot", backref="product_slot_readings")
    product = relationship("Product", backref="product_slot_readings")

    # Computed properties
    @hybrid_property
    def quantity_sold(self):
        if self.end_reading is not None and self.start_reading is not None:
            return self.end_reading - self.start_reading
        return None

    @hybrid_property
    def revenue_amount(self):
        if self.quantity_sold is not None and self.selling_price_snapshot is not None:
            return self.quantity_sold * self.selling_price_snapshot
        return None

    @hybrid_property
    def cost_amount(self):
        if self.quantity_sold is not None and self.cost_price_snapshot is not None:
            return self.quantity_sold * self.cost_price_snapshot
        return None
