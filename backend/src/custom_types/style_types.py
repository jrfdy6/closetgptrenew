from enum import Enum
from typing import List

class StyleType(str, Enum):
    DARK_ACADEMIA = "Dark Academia"
    OLD_MONEY = "Old Money"
    STREETWEAR = "Streetwear"
    Y2K = "Y2K"
    MINIMALIST = "Minimalist"
    BOHO = "Boho"
    PREPPY = "Preppy"
    GRUNGE = "Grunge"
    CLASSIC = "Classic"
    TECHWEAR = "Techwear"
    ANDROGYNOUS = "Androgynous"
    COASTAL_CHIC = "Coastal Chic"
    BUSINESS_CASUAL = "Business Casual"
    AVANT_GARDE = "Avant-Garde"
    COTTAGECORE = "Cottagecore"
    EDGY = "Edgy"
    ATHLEISURE = "Athleisure"
    CASUAL_COOL = "Casual Cool"
    ROMANTIC = "Romantic"
    ARTSY = "Artsy"

# Export types for use in other modules
__all__ = ['StyleType'] 