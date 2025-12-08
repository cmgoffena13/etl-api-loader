from typing import Optional

from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime


class Review(BaseModel):
    rating: int
    comment: str
    date: DateTime
    reviewerName: str
    reviewerEmail: str


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
    # Flattened fields
    dimensions_width: float
    dimensions_height: float
    dimensions_depth: float

    warrantyInformation: str
    shippingInformation: str
    availabilityStatus: str
    returnPolicy: str
    minimumOrderQuantity: int
    # Flattened fields
    meta_createdAt: DateTime
    meta_updatedAt: DateTime
    meta_barcode: str
    meta_qrCode: str

    images: list[str]
    thumbnail: str
