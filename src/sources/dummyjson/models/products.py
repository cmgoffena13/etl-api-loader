from typing import Optional

from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import Field, SQLModel


class DummyJSONReviews(SQLModel, table=True):
    product_id: int = Field(primary_key=True, alias="root.reviews[*].productId")
    reviewer_name: str = Field(primary_key=True, alias="root.reviews[*].reviewerName")
    rating: int = Field(alias="root.reviews[*].rating")
    comment: str = Field(alias="root.reviews[*].comment")
    date: DateTime = Field(alias="root.reviews[*].date")
    reviewer_email: str = Field(alias="root.reviews[*].reviewerEmail")


class DummyJSONProducts(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    title: str = Field(alias="root.title")
    description: str = Field(alias="root.description")
    category: str = Field(alias="root.category")
    price: float = Field(alias="root.price")
    discount_percentage: float = Field(alias="root.discountPercentage")
    rating: float = Field(alias="root.rating")
    stock: int = Field(alias="root.stock")
    tags: str = Field(alias="root.tags[*]")
    brand: Optional[str] = Field(default=None, alias="root.brand")
    sku: str = Field(alias="root.sku")
    weight: int = Field(alias="root.weight")
    dimensions_width: float = Field(alias="root.dimensions.width")
    dimensions_height: float = Field(alias="root.dimensions.height")
    dimensions_depth: float = Field(alias="root.dimensions.depth")
    warranty_information: str = Field(alias="root.warrantyInformation")
    shipping_information: str = Field(alias="root.shippingInformation")
    availability_status: str = Field(alias="root.availabilityStatus")
    return_policy: str = Field(alias="root.returnPolicy")
    minimum_order_quantity: int = Field(alias="root.minimumOrderQuantity")
    created_at: DateTime = Field(alias="root.meta.createdAt")
    updated_at: DateTime = Field(alias="root.meta.updatedAt")
    barcode: str = Field(alias="root.meta.barcode")
    qr_code: str = Field(alias="root.meta.qrCode")
    images: str = Field(alias="root.images[*]")
    thumbnail: str = Field(alias="root.thumbnail")
