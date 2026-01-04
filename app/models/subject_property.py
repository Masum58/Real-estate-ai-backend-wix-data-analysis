from typing import Optional
from pydantic import BaseModel, Field


class SubjectProperty(BaseModel):
    """
    Represents the user's property input from Wix form.
    This is NOT MLS data.
    """

    address: str = Field(..., description="Full property address")

    # 🔥 NEW: Location fields for better comparable matching
    city: str = Field(..., description="City name")
    
    state: str = Field(..., description="State (e.g., NC, SC)")
    
    zip_code: str = Field(..., description="Postal/ZIP code")

    bedrooms: int = Field(..., gt=0, description="Number of bedrooms")

    bathrooms: float = Field(..., gt=0, description="Number of bathrooms")

    square_footage: int = Field(..., gt=100, description="Total living area in sqft")

    year_built: int = Field(..., ge=1800, le=2100, description="Year the property was built")

    condition_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="User provided condition rating (1–10)"
    )

    user_notes: Optional[str] = Field(
        None,
        description="Optional notes provided by the user"
    )

    email: Optional[str] = Field(
        None,
        description="User email (not used in AI analysis)"
    )

    # 🔥 NEW: Optional lat/long for distance-based matching
    latitude: Optional[float] = Field(
        None,
        description="Optional latitude for precise location matching"
    )
    
    longitude: Optional[float] = Field(
        None,
        description="Optional longitude for precise location matching"
    )