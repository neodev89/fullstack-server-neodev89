from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, TIMESTAMP, ForeignKey
from .db import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    num_invoice: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    taxable: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    vat: Mapped[str] = mapped_column(String(10), nullable=False)
    total: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    creation_date: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    protocol_numb: Mapped[int] = mapped_column(Integer, nullable=False)
    invoice_token: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id_code: Mapped[str] = mapped_column(String(20), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="invoices")
