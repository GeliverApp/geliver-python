from __future__ import annotations
from typing import Optional, Union
from pydantic import BaseModel
from .models import Address


class CreateAddressRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    countryCode: str
    cityName: str
    cityCode: str
    districtName: str
    districtID: Optional[int] = None
    zip: str
    shortName: Optional[str] = None
    isRecipientAddress: Optional[bool] = None


class CreateShipmentRequestBase(BaseModel):
    sourceCode: str
    senderAddressID: str
    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    distanceUnit: Optional[str] = None
    weight: Optional[str] = None
    massUnit: Optional[str] = None
    providerServiceCode: Optional[str] = None
    test: Optional[bool] = None


class CreateShipmentWithRecipientID(CreateShipmentRequestBase):
    recipientAddressID: str


class CreateShipmentWithRecipientAddress(CreateShipmentRequestBase):
    recipientAddress: Address


CreateShipmentRequest = Union[CreateShipmentWithRecipientID, CreateShipmentWithRecipientAddress]


class UpdatePackageRequest(BaseModel):
    height: Optional[str] = None
    width: Optional[str] = None
    length: Optional[str] = None
    distanceUnit: Optional[str] = None
    weight: Optional[str] = None
    massUnit: Optional[str] = None


class ReturnShipmentRequest(BaseModel):
    isReturn: Optional[bool] = True
    willAccept: bool
    providerServiceCode: str
    count: int
    senderAddress: dict
