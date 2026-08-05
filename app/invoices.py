from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, TIMESTAMP, ForeignKey
from datetime import datetime
from decimal import Decimal
from .db import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True) # int8
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False) # timestamptz
    num_invoice: Mapped[Decimal] = mapped_column(Numeric, unique=True, nullable=False) # numeric su DB
    taxable: Mapped[str] = mapped_column(String, nullable=False) # text su DB (es. "1000,50")
    vat: Mapped[str] = mapped_column(String(10), nullable=False) # text su DB (es. "22%")
    total: Mapped[str] = mapped_column(String, nullable=False) # text su DB! (es. "1221,61")
    creation_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False) # timestamptz
    protocol_numb: Mapped[Decimal] = mapped_column(Numeric, nullable=False) # numeric su DB
    invoice_token: Mapped[str] = mapped_column(String(255), nullable=False) # text/varchar
    tax_id_code: Mapped[str] = mapped_column(String(20), nullable=False) # text/varchar

    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # user: Mapped["User"] = relationship(back_populates="invoices")