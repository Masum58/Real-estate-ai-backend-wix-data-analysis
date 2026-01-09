from typing import List, Dict
from app.models.subject_property import SubjectProperty
import math


class ComparableSelector:
    """
    Selects relevant MLS comparable properties
    based on the subject property.
    
    🔥 UPDATED: 1 mile radius, weight system, NC/SC cross-state support
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
        
        🔥 UPDATED: 1 mile radius MAX, NC/SC cross-state support
        """

        # ============================================
        # 🔥 LOCATION FILTERS
        # ============================================
        
        # Filter 1: City match (REQUIRED)
        comp_city = comp.get("city", "").strip().lower()
        subject_city = self.subject.city.strip().lower()
        
        if comp_city != subject_city:
            return False
        
        # Filter 2: State match (FLEXIBLE for border properties)
        comp_state = comp.get("state", "").strip().upper()
        subject_state = self.subject.state.strip().upper()
        
        # Allow NC/SC cross-border comparables (client requirement: neighborhoods span state lines)
        ALLOWED_STATE_PAIRS = [
            {"NC", "SC"},  # North Carolina / South Carolina border
        ]
        
        # Only enforce state matching if BOTH states are provided
        if comp_state and subject_state:
            # Exact match is always OK
            if comp_state == subject_state:
                pass  # Continue
            # Check if states are in allowed cross-border pairs
            elif any({comp_state, subject_state} == pair for pair in ALLOWED_STATE_PAIRS):
                pass  # Allow cross-state comparables
            else:
                return False  # Different states not in allowed pairs
        # If either state is missing, allow it (MLS data might not have state field)
        # This allows Fort Mill and other properties to work even if state field is empty
        
        # Filter 3: Zip code proximity (within same zip or adjacent)
        comp_zip = str(comp.get("zip", "")).strip()
        subject_zip = str(self.subject.zip_code).strip()
        
        # If zip codes are very different (>100 apart), likely too far
        if comp_zip and subject_zip:
            try:
                zip_diff = abs(int(comp_zip) - int(subject_zip))
                if zip_diff > 100:  # More than 100 zip codes apart
                    return False
            except (ValueError, TypeError):
                pass  # If zip codes aren't numeric, skip this check
        
        # Filter 4: Distance check - 1 MILE RADIUS MAX (client requirement)
        if self.subject.latitude and self.subject.longitude:
            comp_lat = comp.get("latitude")
            comp_lon = comp.get("longitude")
            
            if comp_lat and comp_lon:
                distance = self.calculate_distance(
                    self.subject.latitude,
                    self.subject.longitude,
                    comp_lat,
                    comp_lon
                )
                
                # Reject if more than 1 mile away (client requirement: 1 mile radius MAX)
                if distance > 1:
                    return False

        # ============================================
        # PROPERTY FILTERS
        # ============================================

        # Bedrooms filter (+/- 1)
        if abs(comp.get("bedrooms", 0) - self.subject.bedrooms) > 1:
            return False

        # Bathrooms filter (+/- 1)
        comp_baths = comp.get("bathrooms", 0)
        if abs(comp_baths - self.subject.bathrooms) > 1:
            return False

        # Square footage filter (+/- 25%)
        sqft = comp.get("areaSqft", 0)
        if sqft <= 0:
            return False

        lower_sqft = self.subject.square_footage * 0.75
        upper_sqft = self.subject.square_footage * 1.25

        if not (lower_sqft <= sqft <= upper_sqft):
            return False

        # Year built filter (+/- 20 years)
        year_built = comp.get("yearBuilt")
        if year_built:
            if abs(year_built - self.subject.year_built) > 20:
                return False

        # Status filter (only closed sales)
        status = comp.get("status")
        if status != "Closed":
            return False

        return True

    def select(self, mls_records: List[Dict], limit: int = 25) -> List[Dict]:
        """
        Return top relevant comparable properties.
        
        🔥 UPDATED: Distance-based weighting system - closer properties prioritized!
        Client requirement: 1 mile radius max, weight system for proximity
        """

        selected = []

        for record in mls_records:
            if self.is_comparable(record):
                # Calculate distance and add weight to record
                if self.subject.latitude and self.subject.longitude:
                    comp_lat = record.get("latitude", 0)
                    comp_lon = record.get("longitude", 0)
                    if comp_lat and comp_lon:
                        distance = self.calculate_distance(
                            self.subject.latitude,
                            self.subject.longitude,
                            comp_lat,
                            comp_lon
                        )
                        record['_distance'] = distance
                        
                        # Weight system: closer = better (client requirement)
                        # Properties within 0.1 miles get highest weight
                        if distance < 0.1:
                            record['_weight'] = 10.0  # Very close - immediate neighbors
                        elif distance < 0.25:
                            record['_weight'] = 8.0   # Close - same block
                        elif distance < 0.5:
                            record['_weight'] = 6.0   # Nearby - walking distance
                        elif distance < 0.75:
                            record['_weight'] = 4.0   # Moderate - short drive
                        else:
                            record['_weight'] = 2.0   # Far - edge of 1 mile radius
                    else:
                        record['_distance'] = float('inf')
                        record['_weight'] = 1.0
                else:
                    record['_distance'] = float('inf')
                    record['_weight'] = 1.0
                    
                selected.append(record)

        # 🔥 Sort by distance (closest first) - implements weight system
        if self.subject.latitude and self.subject.longitude:
            selected.sort(key=lambda x: x.get('_distance', float('inf')))
        else:
            # Fallback: Sort by closest square footage
            selected.sort(
                key=lambda x: abs(
                    x.get("areaSqft", 0) - self.subject.square_footage
                )
            )

        return selected[:limit]