from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Annotated as An, ClassVar, Union
from typing import List, Optional, Literal

from beanie import Document, Indexed, Link, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.country import CountryAlpha3
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from pydantic_geojson import PointModel

from config import settings
from schemas.promotion import BasePromotion, PromotionUnion
from schemas.relationship import Relationship
from utilities.image_mixin import ImageMixin
from utilities.schema_variations import Filter, schema_models, INPUT, OUTPUT, UPDATE
from schema_common import ImagePair
from utilities.openapi_msgid_inject import MsgIdTag


class OpeningHours(BaseModel):
    open_time: timedelta  # date time from start of week, includes day and hour of opening
    close_time: timedelta


class ServiceCategory(str, Enum):
    CART = "cart"
    SHOP = "shop"
    GYM = "gym"
    RESTAURANT = "restaurant"


class Session(Document):
    user_id: str
    user_token: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sessions"
        indexes = [
            [("user_token", 1)],
            [("user_id", 1)],
        ]


class contactInfo(BaseModel):
    phone: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None
    address: An[Optional[str], Field(max_length=1000)] = None


# Main Documents using schema_models decorator with variation objects
@schema_models(INPUT, OUTPUT, UPDATE)
class User(Document):
    phone: An[
        PhoneNumber,
        PhoneNumberValidator(number_format="E164"),
        Indexed(unique=True),
        Filter("in"),
    ]
    first_name: An[Optional[str], Field(max_length=50), MsgIdTag()] = None
    last_name: An[Optional[str], Field(max_length=50), MsgIdTag()] = None
    email: Optional[EmailStr] = None
    fav_srvs: An[List[Link["Service"]], Filter("in")] = []
    my_srvs: An[List[Link["Service"]], Filter("in")] = []
    # relationships: An[List[Link["Relationship"]], Filter("in")] = []
    created_at: An[datetime, Filter("in"), Field(default_factory=datetime.utcnow, exclude=True)]

    class Settings:
        name = "users"
        use_state_management = True


@schema_models(INPUT, OUTPUT, UPDATE)
class Product(Document, ImageMixin):
    price: Decimal
    images: An[List[ImagePair], Filter("in"), Field(max_length=5)] = []
    _MAX_IMAGES: ClassVar[int] = 5
    active: bool = True
    name: str = Field(max_length=100)
    description: An[Optional[str], Field(max_length=1000)] = None

    class Settings:
        name = "products"
        use_state_management = True


@schema_models(INPUT, OUTPUT, UPDATE)
class Service(Document, ImageMixin):
    owner: An[Link[User], Filter("in")]
    service_cat: ServiceCategory
    alt_contact_info: Optional[contactInfo] = None
    name: str = Field(max_length=100)
    description: Optional[str] = None
    products: An[List[Link[Product]], Filter("in")] = []
    images: An[List[ImagePair], Filter("in"), Field(max_length=5)] = []
    _MAX_IMAGES: ClassVar[int] = 5
    map_icon_url: Optional[str] = None
    active: bool = True
    country: CountryAlpha3  # ISO country code
    promotions: List[PromotionUnion] = []
    created_at: An[datetime, Filter("in"), Field(default_factory=datetime.utcnow)]

    class Settings:
        name = "services"
        is_root = True
        use_state_management = True


@schema_models(INPUT, OUTPUT, UPDATE)
class FixedService(Service):
    service_type: Literal["fixed"]
    opening_hours: Optional[List[OpeningHours]] = None
    fixed_location: PointModel

    class Settings:
        indexes = [[("fixed_location", "2dsphere")]]


@schema_models(INPUT, OUTPUT, UPDATE)
class MobileService(Service):
    service_type: Literal["mobile"]
    live_location_timestamp: Optional[datetime] = None


@schema_models(INPUT, OUTPUT, UPDATE)
class OccasionalService(Service):
    service_type: Literal["occasional"]
    must_contact: bool = True
    fixed_location: PointModel

    class Settings:
        indexes = [[("fixed_location", "2dsphere")]]


@schema_models(INPUT, OUTPUT)
class Transaction(Document):
    text: str
    points_given: int  # always positive
    created_at: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[PointModel] = None

    class Settings:
        name = "transactions"


async def beanie_init():
    # Create Motor client
    client = AsyncIOMotorClient(settings.DB_URI)
    # Initialize beanie with the Sample document class and a database
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            Product,
            Service,
            FixedService,
            MobileService,
            OccasionalService,
            Transaction,
            Relationship,
            Session,
        ],
    )


# Rebuild models with forward references
User.rebuild_models()  # type: ignore

Relationship.model_rebuild()

# Service union types - defined globally
ServiceClassesInputs = An[
    Union[FixedService.Input, MobileService.Input, OccasionalService.Input],  # type: ignore
    Field(discriminator="service_type"),
]

ServiceClassesUpdates = An[
    Union[FixedService.Update, MobileService.Update, OccasionalService.Update],  # type: ignore
    Field(discriminator="service_type"),
]

ServiceClassesOutputs = Union[FixedService.Output, MobileService.Output, OccasionalService.Output]  # type: ignore
