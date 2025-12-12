from pydantic_extra_types.pendulum_dt import DateTime
from sqlmodel import Field, SQLModel


class TestProduct(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    name: str = Field(alias="root.name")
    price: float = Field(alias="root.price")
    category: str = Field(alias="root.category")


class TestProductWithNested(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    name: str = Field(alias="root.name")
    price: float = Field(alias="root.price")
    dimensions_width: float = Field(alias="root.dimensions.width")
    dimensions_height: float = Field(alias="root.dimensions.height")
    meta_created_at: DateTime = Field(alias="root.meta.createdAt")


class TestProductWithList(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    name: str = Field(alias="root.name")
    tags: str = Field(alias="root.tags[*]")
    images: str = Field(alias="root.images[*]")


class TestReview(SQLModel, table=True):
    product_id: int = Field(primary_key=True, alias="root.reviews[*].productId")
    reviewer_name: str = Field(primary_key=True, alias="root.reviews[*].reviewerName")
    rating: int = Field(alias="root.reviews[*].rating")
    comment: str = Field(alias="root.reviews[*].comment")


class TestListItem(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    title: str = Field(alias="root.title")
    body: str = Field(alias="root.body")


class TestInvoice(SQLModel, table=True):
    invoice_id: int = Field(primary_key=True, alias="root.invoice_id")
    invoice_date: str = Field(alias="root.invoice_date")
    customer_name: str = Field(alias="root.customer_name")
    total_amount: float = Field(alias="root.total_amount")


class TestInvoiceLineItem(SQLModel, table=True):
    invoice_id: int = Field(primary_key=True, alias="root.invoice_id")
    line_item_id: int = Field(
        primary_key=True, alias="root.invoice_line_items[*].line_item_id"
    )
    product_name: str = Field(alias="root.invoice_line_items[*].product_name")
    quantity: int = Field(alias="root.invoice_line_items[*].quantity")
    unit_price: float = Field(alias="root.invoice_line_items[*].unit_price")


class TestTransaction(SQLModel, table=True):
    invoice_id: int = Field(primary_key=True, alias="root.invoice_id")
    line_item_id: int = Field(
        primary_key=True, alias="root.invoice_line_items[*].line_item_id"
    )
    txn_id: int = Field(
        primary_key=True, alias="root.invoice_line_items[*].transactions[*].txn_id"
    )
    txn_date: str = Field(alias="root.invoice_line_items[*].transactions[*].txn_date")
    txn_amount: float = Field(
        alias="root.invoice_line_items[*].transactions[*].txn_amount"
    )
    payment_method: str = Field(
        alias="root.invoice_line_items[*].transactions[*].payment_method"
    )


class TestProductWithMaxLength(SQLModel, table=True):
    id: int = Field(primary_key=True, alias="root.id")
    name: str = Field(alias="root.name")
    code: str = Field(max_length=3, alias="root.code")
