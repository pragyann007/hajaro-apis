# app/hajaro/models/__init__.py

# First, import your SQLAlchemy Base so it's shared
from app.core.database import Base  

# Import all of your models so they register with the Base metadata
from app.hajaro.models.users import UsersModel
from app.hajaro.models.business import BusinessModel
from app.hajaro.models.business_categories import BusinessCategories
from app.hajaro.models.business_claims import BusinessClaims
from app.hajaro.models.business_hours import BusinessHours
from app.hajaro.models.business_media import BusinessMedia
from app.hajaro.models.business_submissions import BusinessSubmissions
from app.hajaro.models.business_verifications import BusinessVerifications
from app.hajaro.models.catalog_items import CatalogItems
from app.hajaro.models.categories import CategoryModel
from app.hajaro.models.locations import Locations
from app.hajaro.models.offers import Offers
from app.hajaro.models.reviews import Reviews
from app.hajaro.models.verification_events import VerificationEvents
from app.hajaro.models.verification_requests import VerificationRequests

# Explicitly expose Base and all models to clean up imports elsewhere
__all__ = [
    "Base",
    "UsersModel",
    "BusinessModel",
    "BusinessCategories",
    "BusinessClaims",
    "BusinessHours",
    "BusinessMedia",
    "BusinessSubmissions",
    "BusinessVerifications",
    "CatalogItems",
    "CategoryModel",
    "Locations",
    "Offers",
    "Reviews",
    "VerificationEvents",
    "VerificationRequests",
]
