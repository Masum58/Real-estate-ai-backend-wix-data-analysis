from typing import Optional
from pydantic import BaseModel, Field, model_validator
import requests

class SubjectProperty(BaseModel):
    """
    Represents the user's property input from Wix form.
    Automatically geocodes address using MLSGrid API (1 call) or free Nominatim.
    """

    address: str = Field(..., description="Full property address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State (e.g., NC, SC)")
    zip_code: str = Field(..., description="Postal/ZIP code")
    bedrooms: int = Field(..., gt=0, description="Number of bedrooms")
    bathrooms: float = Field(..., gt=0, description="Number of bathrooms")
    square_footage: int = Field(..., gt=100, description="Total living area in sqft")
    year_built: int = Field(..., ge=1800, le=2100, description="Year the property was built")
    condition_score: int = Field(..., ge=1, le=10, description="User provided condition rating (1–10)")
    user_notes: Optional[str] = Field(None, description="Optional notes provided by the user")
    email: Optional[str] = Field(None, description="User email")
    latitude: Optional[float] = Field(None, description="Latitude for precise location matching")
    longitude: Optional[float] = Field(None, description="Longitude for precise location matching")

    @model_validator(mode='after')
    def geocode_if_needed(self):
        """
        Automatically geocode address to get lat/lon if not provided.
        Priority: MLSGrid API (1 call) > Nominatim (free) > None
        """
        if self.latitude is None or self.longitude is None:
            print(f"🔵 Geocoding: {self.address}, {self.city}, {self.state}")
            
            # Try MLSGrid first (most accurate, 1 API call)
            try:
                from app.services.mlsgrid_geocode import geocode_from_mlsgrid
                
                coords = geocode_from_mlsgrid(
                    self.address, 
                    self.city, 
                    self.state, 
                    self.zip_code
                )
                
                if coords:
                    self.latitude = coords["latitude"]
                    self.longitude = coords["longitude"]
                    print(f"✅ Geocoded via MLSGrid")
                    return self
            except Exception as e:
                print(f"⚠️ MLSGrid geocoding failed: {e}")
            
            # Fallback to free Nominatim
            try:
                full_address = f"{self.address}, {self.city}, {self.state} {self.zip_code}, USA"
                
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    "q": full_address,
                    "format": "json",
                    "limit": 1
                }
                headers = {
                    "User-Agent": "RealEstateValuationAPI/1.0"
                }
                
                print(f"⚠️ Trying free Nominatim geocoding...")
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    if results and len(results) > 0:
                        self.latitude = float(results[0]["lat"])
                        self.longitude = float(results[0]["lon"])
                        print(f"✅ Geocoded via Nominatim: {self.latitude}, {self.longitude}")
                        return self
                
                print(f"⚠️ Nominatim: No results")
                    
            except Exception as e:
                print(f"⚠️ Nominatim error: {e}")
            
            # No geocoding worked
            print(f"⚠️ Could not geocode address")
            print(f"⚠️ Will fall back to city-wide search (no 1-mile radius)")
        else:
            print(f"✅ Using provided coordinates: {self.latitude}, {self.longitude}")
        
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "address": "510 Martha Ave",
                "city": "Charlotte",
                "state": "NC",
                "zip_code": "28202",
                "bedrooms": 3,
                "bathrooms": 2,
                "square_footage": 1169,
                "year_built": 1981,
                "condition_score": 5,
                "user_notes": "Test property",
                "email": "test@test.com"
            }
        }