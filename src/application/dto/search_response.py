"""
SearchResponse DTO for price search responses.

This module defines the data transfer object for search results.
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    """
    Data transfer object for price search responses.

    This DTO carries the results of a price search operation,
    including both successful results and error information.

    Attributes:
        success: Whether the search was successful.
        price: The found price (if successful).
        currency: The currency code (default: "USD").
        service: The matched service name.
        zone: The zone number.
        weight: The weight in pounds.
        source_document: The PDF file where the price was found.
        error_message: Error message (if unsuccessful).
        search_time_ms: Time taken for the search in milliseconds.
    """

    success: bool = Field(
        ...,
        description="Whether the search was successful"
    )

    price: Optional[Decimal] = Field(
        None,
        description="The found price"
    )

    currency: str = Field(
        "USD",
        description="The currency code"
    )

    service: Optional[str] = Field(
        None,
        description="The matched service name"
    )

    zone: Optional[int] = Field(
        None,
        description="The zone number"
    )

    weight: Optional[float] = Field(
        None,
        description="The weight in pounds"
    )

    source_document: Optional[str] = Field(
        None,
        description="The PDF file where the price was found"
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message if unsuccessful"
    )

    search_time_ms: float = Field(
        ...,
        ge=0,
        description="Time taken for the search in milliseconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "price": "29.50",
                    "currency": "USD",
                    "service": "FedEx 2Day",
                    "zone": 5,
                    "weight": 3.0,
                    "source_document": "FedEx_Standard_List_Rates_2025.pdf",
                    "error_message": None,
                    "search_time_ms": 45.2
                },
                {
                    "success": False,
                    "price": None,
                    "currency": "USD",
                    "service": None,
                    "zone": None,
                    "weight": None,
                    "source_document": None,
                    "error_message": "Service not found: Unknown Service",
                    "search_time_ms": 12.5
                }
            ]
        }
    }

    @classmethod
    def success_response(
        cls,
        price: Decimal,
        service: str,
        zone: int,
        weight: float,
        source_document: str,
        search_time_ms: float
    ) -> "SearchResponse":
        """
        Create a successful search response.

        Args:
            price: The found price.
            service: The matched service name.
            zone: The zone number.
            weight: The weight in pounds.
            source_document: The PDF file where the price was found.
            search_time_ms: Time taken for the search in milliseconds.

        Returns:
            A SearchResponse indicating success.
        """
        return cls(
            success=True,
            price=price,
            currency="USD",
            service=service,
            zone=zone,
            weight=weight,
            source_document=source_document,
            error_message=None,
            search_time_ms=search_time_ms
        )

    @classmethod
    def error_response(
        cls,
        error_message: str,
        search_time_ms: float
    ) -> "SearchResponse":
        """
        Create an error search response.

        Args:
            error_message: The error message.
            search_time_ms: Time taken for the search in milliseconds.

        Returns:
            A SearchResponse indicating failure.
        """
        return cls(
            success=False,
            price=None,
            currency="USD",
            service=None,
            zone=None,
            weight=None,
            source_document=None,
            error_message=error_message,
            search_time_ms=search_time_ms
        )
