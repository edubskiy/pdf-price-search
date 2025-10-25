"""
ServiceInfo DTO for shipping service information.

This module defines the data transfer object for service metadata.
"""

from typing import List, Tuple
from pydantic import BaseModel, Field


class ServiceInfo(BaseModel):
    """
    Data transfer object for shipping service information.

    This DTO carries metadata about available shipping services.

    Attributes:
        name: The service name.
        available_zones: List of available zone numbers.
        weight_range: Tuple of (min_weight, max_weight) in pounds.
        source_pdf: The PDF file where this service is defined.
    """

    name: str = Field(
        ...,
        description="The service name"
    )

    available_zones: List[int] = Field(
        ...,
        description="List of available zone numbers"
    )

    weight_range: Tuple[float, float] = Field(
        ...,
        description="Tuple of (min_weight, max_weight) in pounds"
    )

    source_pdf: str = Field(
        ...,
        description="The PDF file where this service is defined"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "FedEx 2Day",
                    "available_zones": [2, 3, 4, 5, 6, 7, 8],
                    "weight_range": [1.0, 150.0],
                    "source_pdf": "FedEx_Standard_List_Rates_2025.pdf"
                }
            ]
        }
    }

    @property
    def min_weight(self) -> float:
        """Get the minimum weight."""
        return self.weight_range[0]

    @property
    def max_weight(self) -> float:
        """Get the maximum weight."""
        return self.weight_range[1]
