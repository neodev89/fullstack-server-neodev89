from app.models import (
    ResponseAPI,
    ResponseUserAPI,
    ResUser,
    PartialInvoiceSchema,
)
from datetime import datetime
from decimal import Decimal

def make_user_example(id: int = 0):
    return ResponseUserAPI[ResUser](
        id=id,
        data_user={
            "name": "Mario",
            "lastName": "Rossi",
            "address": "Via Roma 1",
            "prePhone": "+39",
            "phone": "3331234567",
            "email": "example@example.com",
            "pw": "******",
            "tk": f"iduserfittizio_{id}",
        },
    ).dict()


def make_partial_invoice_example():
    return PartialInvoiceSchema(
        id=1,
        created_at=datetime.now(),
        num_invoice=Decimal("1234"),
        taxable="100",
        vat="22",
        total="122",
        creation_date=datetime.now(),
        protocol_numb=55,
        tax_id_code="ABCDEF12G34H567I",
        name="Mario",
        lastName="Rossi",
        email="mario.rossi@example.com"
    ).dict()

