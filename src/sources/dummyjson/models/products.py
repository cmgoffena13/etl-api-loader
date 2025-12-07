from typing import Optional

from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class Dimensions(BaseModel):
    width: float
    height: float
    depth: float


class Review(BaseModel):
    rating: int
    comment: str
    date: DateTime
    reviewerName: str
    reviewerEmail: str


class Meta(BaseModel):
    createdAt: DateTime
    updatedAt: DateTime
    barcode: str
    qrCode: str


class DummyJSONProduct(BaseModel):
    id: int
    title: str
    description: str
    category: str
    price: float
    discountPercentage: float
    rating: float
    stock: int
    tags: list[str]
    brand: Optional[str] = None
    sku: str
    weight: int
    dimensions: Dimensions
    warrantyInformation: str
    shippingInformation: str
    availabilityStatus: str
    reviews: list[Review]
    returnPolicy: str
    minimumOrderQuantity: int
    meta: Meta
    images: list[str]
    thumbnail: str
