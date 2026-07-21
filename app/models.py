# qui inserire le classi per inferire le Response API
from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, TypeVar, Generic 

class Address(BaseModel):
    country: str
    city: str
    street: str
    civicNum: str

class ReqUser(BaseModel):
    name: str
    lastName: str
    address: Address
    prePhone: str
    phone: str
    email: str
    pw: str

class ResUser(BaseModel):
    name: str
    lastName: str
    address: Address
    prePhone: str
    phone: str
    email: str
    pw: str
    tk: str

# tipo generico per ottenere l'oggetto del db
T = TypeVar("T")

class ResponseUserAPI(GenericModel, Generic[T]):
    id: int
    data_user: Optional[T]

class ResponseAPI(GenericModel, Generic[T]):
    success: bool
    message: str
    data: T
    status: int