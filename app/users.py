from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Numeric, TIMESTAMP, ForeignKey
from datetime import datetime
from .db import Base


class UserRegistered(Base):
    __tablename__ = "registered_freelance_data_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="user")
