"""
Pydantic models for deposition data validation.
"""

from datetime import date
from pydantic import BaseModel, Field

materials = []


class DepositionEntry(BaseModel):
    """Schema for a deposition entry with validation rules."""

    Date: date = Field(description="Date of the deposition")

    Material: str = Field(
        min_length=1, max_length=50, description="Material being deposited"
    )

    Threshold_Power: float = Field(
        ge=0.0,  # greater than or equal to 0
        le=100.0,  # reasonable upper limit - adjust as needed
        description="Threshold power in %",
    )

    Power_Deposition: float = Field(
        ge=0.0,
        le=100.0,  # reasonable upper limit - adjust as needed
        description="Power used for deposition in %",
    )

    Rate: float = Field(
        ge=0.0,
        le=200.0,  # reasonable upper limit - adjust as needed
        description="Deposition rate in A/s",
    )

    Thickness_nm: float = Field(
        ge=0.0,
        le=5000.0,  # reasonable upper limit for nanometers - adjust as needed
        description="Thickness in nanometers",
    )

    Crystal_Monitor: float = Field(
        ge=0.0,
        le=100.0,  # reasonable upper limit - adjust as needed
        description="Crystal monitor reading",
    )

    class Config:
        validate_assignment = True
        use_enum_values = True
