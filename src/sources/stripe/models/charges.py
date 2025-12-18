from typing import Optional

from sqlmodel import Field, SQLModel


class StripeCharges(SQLModel, table=True):
    id: str = Field(primary_key=True, alias="root.id")
    object_type: str = Field(alias="root.object")
    amount: int = Field(alias="root.amount")
    amount_captured: int = Field(alias="root.amount_captured")
    amount_refunded: int = Field(alias="root.amount_refunded")
    balance_transaction: Optional[str] = Field(alias="root.balance_transaction")
    billing_details_city: Optional[str] = Field(
        alias="root.billing_details.address.city"
    )
    billing_details_country: Optional[str] = Field(
        alias="root.billing_details.address.country"
    )
    billing_details_line1: Optional[str] = Field(
        alias="root.billing_details.address.line1"
    )
    billing_details_line2: Optional[str] = Field(
        alias="root.billing_details.address.line2"
    )
    billing_details_postal_code: Optional[str] = Field(
        alias="root.billing_details.address.postal_code"
    )
    billing_details_state: Optional[str] = Field(
        alias="root.billing_details.address.state"
    )
    billing_details_email: Optional[str] = Field(alias="root.billing_details.email")
    billing_details_name: Optional[str] = Field(alias="root.billing_details.name")
    billing_details_phone: Optional[str] = Field(alias="root.billing_details.phone")
    billing_details_tax_id: Optional[str] = Field(alias="root.billing_details.tax_id")
    calculated_statement_descriptor: Optional[str] = Field(
        alias="root.calculated_statement_descriptor"
    )
    captured: bool = Field(alias="root.captured")
    created: int = Field(alias="root.created")
    currency: str = Field(alias="root.currency")
    customer: Optional[str] = Field(alias="root.customer")
    description: Optional[str] = Field(alias="root.description")
    disputed: bool = Field(alias="root.disputed")
    livemode: bool = Field(alias="root.livemode")
    paid: bool = Field(alias="root.paid")
    payment_method: Optional[str] = Field(alias="root.payment_method")
    receipt_email: Optional[str] = Field(alias="root.receipt_email")
    receipt_url: Optional[str] = Field(alias="root.receipt_url")
    refunded: bool = Field(alias="root.refunded")
    status: str = Field(alias="root.status")
    outcome_network_status: Optional[str] = Field(alias="root.outcome.network_status")
    outcome_risk_level: Optional[str] = Field(alias="root.outcome.risk_level")
    outcome_risk_score: Optional[int] = Field(alias="root.outcome.risk_score")
    outcome_seller_message: Optional[str] = Field(alias="root.outcome.seller_message")
    outcome_type: Optional[str] = Field(alias="root.outcome.type")
    payment_method_details_card_brand: Optional[str] = Field(
        alias="root.payment_method_details.card.brand"
    )
    payment_method_details_card_last4: Optional[str] = Field(
        alias="root.payment_method_details.card.last4"
    )
    payment_method_details_card_network: Optional[str] = Field(
        alias="root.payment_method_details.card.network"
    )
    payment_method_details_card_country: Optional[str] = Field(
        alias="root.payment_method_details.card.country"
    )
    payment_method_details_card_exp_month: Optional[int] = Field(
        alias="root.payment_method_details.card.exp_month"
    )
    payment_method_details_card_exp_year: Optional[int] = Field(
        alias="root.payment_method_details.card.exp_year"
    )
    payment_method_details_card_funding: Optional[str] = Field(
        alias="root.payment_method_details.card.funding"
    )
    payment_method_details_type: Optional[str] = Field(
        alias="root.payment_method_details.type"
    )
    source_id: Optional[str] = Field(alias="root.source.id")
    source_brand: Optional[str] = Field(alias="root.source.brand")
    source_last4: Optional[str] = Field(alias="root.source.last4")
    source_country: Optional[str] = Field(alias="root.source.country")
    source_exp_month: Optional[int] = Field(alias="root.source.exp_month")
    source_exp_year: Optional[int] = Field(alias="root.source.exp_year")
    source_funding: Optional[str] = Field(alias="root.source.funding")
