"""
SearchRequest DTO for price search requests.

This module defines the data transfer object for incoming search requests.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Data transfer object for price search requests.

    This DTO validates and carries the information needed to perform
    a price search operation.

    Attributes:
        query: The raw search query string (e.g., "FedEx 2Day, Zone 5, 3 lb").
        source_pdf: Optional specific PDF file to search in.
        use_cache: Whether to use cached results (default: True).
    """

    query: str = Field(
        ...,
        min_length=1,
        description="The search query string",
        examples=["FedEx 2Day, Zone 5, 3 lb"]
    )

    source_pdf: Optional[str] = Field(
        None,
        description="Optional specific PDF file to search in"
    )

    use_cache: bool = Field(
        True,
        description="Whether to use cached results"
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """
        Validate the query string.

        Args:
            v: The query value to validate.

        Returns:
            The validated and stripped query.

        Raises:
            ValueError: If query is empty after stripping.
        """
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or whitespace only")
        return v

    @field_validator("source_pdf")
    @classmethod
    def validate_source_pdf(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate the source_pdf field.

        Args:
            v: The source_pdf value to validate.

        Returns:
            The validated source_pdf or None.

        Raises:
            ValueError: If source_pdf is an empty string.
        """
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "FedEx 2Day, Zone 5, 3 lb",
                    "use_cache": True
                },
                {
                    "query": "Standard Overnight, z2, 10 lbs",
                    "source_pdf": "FedEx_Standard_List_Rates_2025.pdf",
                    "use_cache": False
                }
            ]
        }
    }
