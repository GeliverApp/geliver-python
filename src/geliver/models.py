# Auto-generated from openapi.yaml
from __future__ import annotations
from typing import Optional, List, Dict
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field
class Address(BaseModel):
    """Address model"""
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[City] = None
    cityCode: Optional[str] = None
    cityName: Optional[str] = None
    countryCode: Optional[str] = None
    countryName: Optional[str] = None
    createdAt: Optional[str] = None
    district: Optional[District] = None
    districtID: Optional[int] = None
    districtName: Optional[str] = None
    email: Optional[str] = None
    id: Optional[str] = None
    isActive: Optional[bool] = None
    isDefaultReturnAddress: Optional[bool] = None
    isDefaultSenderAddress: Optional[bool] = None
    isInvoiceAddress: Optional[bool] = None
    isRecipientAddress: Optional[bool] = None
    metadata: Optional[JSONContent] = None
    name: Optional[str] = None
    owner: Optional[str] = None
    phone: Optional[str] = None
    shortName: Optional[str] = None
    source: Optional[str] = None
    state: Optional[str] = None
    streetID: Optional[str] = None
    streetName: Optional[str] = None
    test: Optional[bool] = None
    updatedAt: Optional[str] = None
    zip: Optional[str] = None

class City(BaseModel):
    """City model"""
    areaCode: Optional[str] = None
    cityCode: Optional[str] = None
    countryCode: Optional[str] = None
    name: Optional[str] = Field(default=None, description="Model")

class DbStringArray(BaseModel):
    """DbStringArray model"""
    pass

class District(BaseModel):
    """District model"""
    cityCode: Optional[str] = None
    countryCode: Optional[str] = None
    districtID: Optional[int] = None
    name: Optional[str] = Field(default=None, description="Model")
    regionCode: Optional[str] = None

# Duration was a model placeholder; API returns integer timestamp for duration values.

class Item(BaseModel):
    """Item model"""
    countryOfOrigin: Optional[str] = None
    createdAt: Optional[str] = None
    currency: Optional[str] = None
    currencyLocal: Optional[str] = None
    id: Optional[str] = None
    massUnit: Optional[str] = None
    maxDeliveryTime: Optional[str] = None
    maxShipTime: Optional[str] = None
    owner: Optional[str] = None
    quantity: Optional[int] = None
    sku: Optional[str] = None
    test: Optional[bool] = None
    title: Optional[str] = None
    totalPrice: Optional[str] = None
    totalPriceLocal: Optional[str] = None
    unitPrice: Optional[str] = None
    unitPriceLocal: Optional[str] = None
    unitWeight: Optional[str] = None
    updatedAt: Optional[str] = None
    variantTitle: Optional[str] = None

class JSONContent(BaseModel):
    """JSONContent model"""
    pass

class Offer(BaseModel):
    """Offer model"""
    amount: Optional[str] = None
    amountLocal: Optional[str] = None
    amountLocalOld: Optional[str] = None
    amountLocalTax: Optional[str] = None
    amountLocalVat: Optional[str] = None
    amountOld: Optional[str] = None
    amountTax: Optional[str] = None
    amountVat: Optional[str] = None
    averageEstimatedTime: Optional[int] = None
    averageEstimatedTimeHumanReadible: Optional[str] = None
    bonusBalance: Optional[str] = None
    createdAt: Optional[str] = None
    currency: Optional[str] = None
    currencyLocal: Optional[str] = None
    discountRate: Optional[str] = None
    durationTerms: Optional[str] = None
    estimatedArrivalTime: Optional[str] = None
    id: Optional[str] = None
    integrationType: Optional[str] = None
    isAccepted: Optional[bool] = None
    isC2C: Optional[bool] = None
    isGlobal: Optional[bool] = None
    isMainOffer: Optional[bool] = None
    isProviderAccountOffer: Optional[bool] = None
    maxEstimatedTime: Optional[int] = None
    minEstimatedTime: Optional[int] = None
    owner: Optional[str] = None
    predictedDeliveryTime: Optional[Decimal] = None
    providerAccountID: Optional[str] = None
    providerAccountName: Optional[str] = None
    providerAccountOwnerType: Optional[str] = None
    providerCode: Optional[str] = None
    providerServiceCode: Optional[str] = None
    providerTotalAmount: Optional[str] = None
    rating: Optional[Decimal] = None
    scheduleDate: Optional[str] = None
    shipmentTime: Optional[str] = None
    test: Optional[bool] = None
    totalAmount: Optional[str] = None
    totalAmountLocal: Optional[str] = None
    updatedAt: Optional[str] = None

class OfferList(BaseModel):
    """OfferList model"""
    allowOfferFallback: Optional[bool] = None
    cheapest: Optional[Offer] = None
    createdAt: Optional[str] = None
    fastest: Optional[Offer] = None
    height: Optional[str] = None
    itemIDs: Optional[List[str]] = None
    length: Optional[str] = None
    list: Optional[List[Offer]] = None
    owner: Optional[str] = None
    parcelIDs: Optional[List[str]] = None
    parcelTemplateID: Optional[str] = None
    percentageCompleted: Optional[Decimal] = None
    providerAccountIDs: Optional[List[str]] = None
    providerCodes: Optional[List[str]] = None
    providerServiceCodes: Optional[List[str]] = None
    test: Optional[bool] = None
    totalOffersCompleted: Optional[int] = None
    totalOffersRequested: Optional[int] = None
    updatedAt: Optional[str] = None
    weight: Optional[str] = None
    width: Optional[str] = None

class Order(BaseModel):
    """Order model"""
    buyerShipmentMethod: Optional[str] = None
    buyerShippingCost: Optional[str] = None
    buyerShippingCostCurrency: Optional[str] = None
    createdAt: Optional[str] = None
    id: Optional[str] = None
    itemIDs: Optional[DbStringArray] = None
    merchantCode: Optional[str] = None
    notes: Optional[str] = None
    orderCode: Optional[str] = None
    orderNumber: Optional[str] = None
    orderStatus: Optional[str] = None
    organizationID: Optional[str] = None
    owner: Optional[str] = None
    shipment: Optional[Shipment] = None
    sourceCode: Optional[str] = None
    sourceIdentifier: Optional[str] = None
    test: Optional[bool] = None
    totalAmount: Optional[str] = None
    totalAmountCurrency: Optional[str] = None
    totalTax: Optional[str] = None
    updatedAt: Optional[str] = None

class Parcel(BaseModel):
    """Parcel model"""
    amount: Optional[str] = None
    amountLocal: Optional[str] = None
    amountLocalOld: Optional[str] = None
    amountLocalTax: Optional[str] = None
    amountLocalVat: Optional[str] = None
    amountOld: Optional[str] = None
    amountTax: Optional[str] = None
    amountVat: Optional[str] = None
    barcode: Optional[str] = None
    bonusBalance: Optional[str] = None
    commercialInvoiceUrl: Optional[str] = None
    createdAt: Optional[str] = None
    currency: Optional[str] = None
    currencyLocal: Optional[str] = None
    customsDeclaration: Optional[str] = None
    desi: Optional[str] = Field(default=None, description="Desi of parcel")
    discountRate: Optional[str] = None
    distanceUnit: Optional[str] = Field(default=None, description="Distance unit of parcel")
    eta: Optional[str] = None
    extra: Optional[JSONContent] = None
    height: Optional[str] = Field(default=None, description="Height of parcel")
    hidePackageContentOnTag: Optional[bool] = None
    id: Optional[str] = None
    invoiceGenerated: Optional[bool] = None
    invoiceID: Optional[str] = None
    isMainParcel: Optional[bool] = None
    itemIDs: Optional[List[str]] = None
    labelFileType: Optional[str] = None
    labelURL: Optional[str] = None
    length: Optional[str] = Field(default=None, description="Length of parcel")
    massUnit: Optional[str] = Field(default=None, description="Weight unit of parcel")
    metadata: Optional[JSONContent] = None
    metadataText: Optional[str] = Field(default=None, description="Meta string to add additional info on your shipment/parcel")
    oldDesi: Optional[str] = None
    oldWeight: Optional[str] = None
    owner: Optional[str] = None
    parcelReferenceCode: Optional[str] = None
    parcelTemplateID: Optional[str] = Field(default=None, description="Instead of setting parcel size manually, you can set this to a predefined Parcel Template")
    productPaymentOnDelivery: Optional[bool] = None
    providerTotalAmount: Optional[str] = None
    qrCodeUrl: Optional[str] = None
    refundInvoiceID: Optional[str] = None
    responsiveLabelURL: Optional[str] = None
    shipmentDate: Optional[str] = None
    shipmentID: Optional[str] = None
    stateCode: Optional[str] = None
    template: Optional[str] = None
    test: Optional[bool] = None
    totalAmount: Optional[str] = None
    totalAmountLocal: Optional[str] = None
    trackingNumber: Optional[str] = Field(default=None, description="Tracking number")
    trackingStatus: Optional[Tracking] = None
    trackingUrl: Optional[str] = None
    updatedAt: Optional[str] = None
    useDimensionsOfItems: Optional[bool] = Field(default=None, description="If true, auto calculates total parcel size using the size of items")
    useWeightOfItems: Optional[bool] = Field(default=None, description="If true, auto calculates total parcel weight using the weight of items")
    weight: Optional[str] = Field(default=None, description="Weight of parcel")
    width: Optional[str] = Field(default=None, description="Width of parcel")

class Shipment(BaseModel):
    """Shipment model"""
    acceptedOffer: Optional[Offer] = None
    acceptedOfferID: Optional[str] = None
    amount: Optional[str] = None
    amountLocal: Optional[str] = None
    amountLocalOld: Optional[str] = None
    amountLocalTax: Optional[str] = None
    amountLocalVat: Optional[str] = None
    amountOld: Optional[str] = None
    amountTax: Optional[str] = None
    amountVat: Optional[str] = None
    barcode: Optional[str] = None
    bonusBalance: Optional[str] = None
    buyerNote: Optional[str] = None
    cancelDate: Optional[str] = None
    categoryCode: Optional[str] = None
    commercialInvoiceUrl: Optional[str] = None
    createReturnLabel: Optional[bool] = None
    createdAt: Optional[str] = None
    currency: Optional[str] = None
    currencyLocal: Optional[str] = None
    customsDeclaration: Optional[str] = None
    desi: Optional[str] = Field(default=None, description="Desi of parcel")
    discountRate: Optional[str] = None
    distanceUnit: Optional[str] = Field(default=None, description="Distance unit of parcel")
    enableAutomation: Optional[bool] = None
    eta: Optional[str] = None
    extraParcels: Optional[List[Parcel]] = None
    hasError: Optional[bool] = None
    height: Optional[str] = Field(default=None, description="Height of parcel")
    hidePackageContentOnTag: Optional[bool] = None
    id: Optional[str] = None
    invoiceGenerated: Optional[bool] = None
    invoiceID: Optional[str] = None
    isRecipientSmsActivated: Optional[bool] = None
    isReturn: Optional[bool] = None
    isReturned: Optional[bool] = None
    isTrackingOnly: Optional[bool] = None
    items: Optional[List[Item]] = None
    labelFileType: Optional[str] = None
    labelURL: Optional[str] = None
    lastErrorCode: Optional[str] = None
    lastErrorMessage: Optional[str] = None
    length: Optional[str] = Field(default=None, description="Length of parcel")
    massUnit: Optional[str] = Field(default=None, description="Weight unit of parcel")
    metadata: Optional[JSONContent] = None
    metadataText: Optional[str] = Field(default=None, description="Meta string to add additional info on your shipment/parcel")
    offers: Optional[OfferList] = None
    oldDesi: Optional[str] = None
    oldWeight: Optional[str] = None
    order: Optional[Order] = None
    orderID: Optional[str] = None
    organizationShipmentID: Optional[int] = None
    owner: Optional[str] = None
    packageAcceptedAt: Optional[str] = None
    parcelTemplateID: Optional[str] = Field(default=None, description="Instead of setting parcel size manually, you can set this to a predefined Parcel Template")
    productPaymentOnDelivery: Optional[bool] = None
    providerAccountID: Optional[str] = None
    providerAccountIDs: Optional[List[str]] = None
    providerBranchName: Optional[str] = None
    providerCode: Optional[str] = None
    providerCodes: Optional[List[str]] = None
    providerInvoiceNo: Optional[str] = None
    providerReceiptNo: Optional[str] = None
    providerSerialNo: Optional[str] = None
    providerServiceCode: Optional[str] = None
    providerServiceCodes: Optional[List[str]] = None
    providerTotalAmount: Optional[str] = None
    qrCodeUrl: Optional[str] = None
    recipientAddress: Optional[Address] = None
    recipientAddressID: Optional[str] = None
    refundInvoiceID: Optional[str] = None
    responsiveLabelURL: Optional[str] = None
    returnAddressID: Optional[str] = None
    sellerNote: Optional[str] = None
    senderAddress: Optional[Address] = None
    senderAddressID: Optional[str] = None
    shipmentDate: Optional[str] = None
    statusCode: Optional[str] = None
    tags: Optional[List[str]] = None
    tenantId: Optional[str] = None
    test: Optional[bool] = None
    totalAmount: Optional[str] = None
    totalAmountLocal: Optional[str] = None
    trackingNumber: Optional[str] = Field(default=None, description="Tracking number")
    trackingStatus: Optional[Tracking] = None
    trackingUrl: Optional[str] = None
    updatedAt: Optional[str] = None
    useDimensionsOfItems: Optional[bool] = Field(default=None, description="If true, auto calculates total parcel size using the size of items")
    useWeightOfItems: Optional[bool] = Field(default=None, description="If true, auto calculates total parcel weight using the weight of items")
    weight: Optional[str] = Field(default=None, description="Weight of parcel")
    width: Optional[str] = Field(default=None, description="Width of parcel")

class ShipmentResponse(BaseModel):
    """ShipmentResponse model"""
    additionalMessage: Optional[str] = None
    code: Optional[str] = None
    data: Optional[Shipment] = None
    message: Optional[str] = None
    result: Optional[bool] = None

class Tracking(BaseModel):
    """Tracking model"""
    createdAt: Optional[str] = None
    hash: Optional[str] = None
    id: Optional[str] = None
    locationLat: Optional[Decimal] = None
    locationLng: Optional[Decimal] = None
    locationName: Optional[str] = None
    owner: Optional[str] = None
    statusDate: Optional[str] = None
    statusDetails: Optional[str] = None
    test: Optional[bool] = None
    trackingStatusCode: Optional[str] = None
    trackingSubStatusCode: Optional[str] = None
    updatedAt: Optional[str] = None

class WebhookUpdateTrackingRequest(BaseModel):
    """Webhook payload for tracking status updates"""
    event: str
    metadata: Optional[str] = None
    data: Shipment
