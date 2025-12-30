from typing import List, Dict
from app.models.subject_property import SubjectProperty


class ComparableSelector:
    """
    Selects relevant MLS comparable properties
    based on the subject property.
    """

    def __init__(self, subject: SubjectProperty):
        self.subject = subject

    def is_comparable(self, comp: Dict) -> bool:
        """
        Decide whether a MLS record is a valid comparable.
        """

        # Bedrooms filter (+/- 1)
        if abs(comp.get("bedrooms", 0) - self.subject.bedrooms) > 1:
            return False

        # Bathrooms filter (+/- 1)
        if abs(comp.get("bathrooms", 0) - self.subject.bathrooms) > 1:
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
        if comp.get("status") != "Closed":
            return False

        return True

    def select(self, mls_records: List[Dict], limit: int = 25) -> List[Dict]:
        """
        Return top relevant comparable properties.
        """

        selected = []

        for record in mls_records:
            if self.is_comparable(record):
                selected.append(record)

        # Sort by closest square footage
        selected.sort(
            key=lambda x: abs(x.get("areaSqft", 0) - self.subject.square_footage)
        )

        return selected[:limit]
