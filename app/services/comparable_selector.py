from typing import List, Dict
from app.models.subject_property import SubjectProperty
import math


class ComparableSelector:
    """
    Selects relevant MLS comparable properties
    based on the subject property.
    
    🔥 NEW: Now includes location-based filtering!
    """

    def __init__(self, subject: SubjectProperty):
        self.subject = subject

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in miles using Haversine formula.
        """
        if not all([lat1, lon1, lat2, lon2]):
            return float('inf')  # Return infinite distance if coordinates missing

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of Earth in miles
        radius_miles = 3958.8
        
        distance = radius_miles * c
        return distance

    def is_comparable(self, comp: Dict) -> bool:
        """
        Decide whether a MLS record is a valid comparable.
        
        🔥 NEW: Added location filtering!
        """

        # ============================================
        # 🔥 LOCATION FILTERS (NEW!)
        # ============================================
        
        # Filter 1: City match (REQUIRED)
        comp_city = comp.get("City", "").strip().lower()
        subject_city = self.subject.city.strip().lower()
        
        if comp_city != subject_city:
            return False
        
        # Filter 2: State match (REQUIRED if provided)
        comp_state = comp.get("StateOrProvince", "").strip().upper()
        subject_state = self.subject.state.strip().upper()
        
        # Note: MLS data might not have State field, so we're lenient here
        if comp_state and subject_state:
            if comp_state != subject_state:
                return False
        
        # Filter 3: Zip code proximity (within same zip or adjacent)
        comp_zip = str(comp.get("PostalCode", "")).strip()
        subject_zip = str(self.subject.zip_code).strip()
        
        # If zip codes are very different (>100 apart), likely too far
        if comp_zip and subject_zip:
            try:
                zip_diff = abs(int(comp_zip) - int(subject_zip))
                if zip_diff > 100:  # More than 100 zip codes apart
                    return False
            except (ValueError, TypeError):
                pass  # If zip codes aren't numeric, skip this check
        
        # Filter 4: Distance check (if coordinates available)
        if self.subject.latitude and self.subject.longitude:
            comp_lat = comp.get("Latitude")
            comp_lon = comp.get("Longitude")
            
            if comp_lat and comp_lon:
                distance = self.calculate_distance(
                    self.subject.latitude,
                    self.subject.longitude,
                    comp_lat,
                    comp_lon
                )
                
                # Reject if more than 15 miles away
                if distance > 15:
                    return False

        # ============================================
        # EXISTING FILTERS (Kept as is)
        # ============================================

        # Bedrooms filter (+/- 1)
        if abs(comp.get("BedroomsTotal", 0) - self.subject.bedrooms) > 1:
            return False

        # Bathrooms filter (+/- 1)
        comp_baths = comp.get("BathroomsFull", 0) + (comp.get("BathroomsHalf", 0) * 0.5)
        if abs(comp_baths - self.subject.bathrooms) > 1:
            return False

        # Square footage filter (+/- 25%)
        sqft = comp.get("LivingArea", 0) or comp.get("BuildingAreaTotal", 0)
        if sqft <= 0:
            return False

        lower_sqft = self.subject.square_footage * 0.75
        upper_sqft = self.subject.square_footage * 1.25

        if not (lower_sqft <= sqft <= upper_sqft):
            return False

        # Year built filter (+/- 20 years)
        year_built = comp.get("YearBuilt")
        if year_built:
            if abs(year_built - self.subject.year_built) > 20:
                return False

        # Status filter (only closed sales)
        status = comp.get("MlsStatus") or comp.get("StandardStatus") or comp.get("status")
        if status != "Closed":
            return False

        return True

    def select(self, mls_records: List[Dict], limit: int = 25) -> List[Dict]:
        """
        Return top relevant comparable properties.
        
        🔥 NEW: Now sorts by distance if coordinates available!
        """

        selected = []

        for record in mls_records:
            if self.is_comparable(record):
                selected.append(record)

        # 🔥 NEW: Sort by distance if coordinates available, otherwise by sqft
        if self.subject.latitude and self.subject.longitude:
            selected.sort(
                key=lambda x: self.calculate_distance(
                    self.subject.latitude,
                    self.subject.longitude,
                    x.get("Latitude", 0),
                    x.get("Longitude", 0)
                )
            )
        else:
            # Fallback: Sort by closest square footage
            selected.sort(
                key=lambda x: abs(
                    (x.get("LivingArea", 0) or x.get("BuildingAreaTotal", 0)) 
                    - self.subject.square_footage
                )
            )

        return selected[:limit]