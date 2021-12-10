from enum import Enum


def human_readable(value):
    value = value.replace('__1__', '_/_')
    value = value.replace('__2__', '_-_')
    value = value.replace('__3__', ',_')
    value = value.split('_')
    value = [word[0:1].upper() + word[1:].lower() for word in value]
    value = ' '.join(value).strip()
    return value


def to_choices(e):
    e_dict = dict(e.__members__)
    return [(e_dict[k].value, human_readable(k)) for k in e_dict]


class Frequency(Enum):
    DAILY = 1
    MONTHLY = 2
    QUARTERLY = 3
    SEMI_ANNUALLY = 4
    ANNUALLY = 5
    ONE_TIME = 6


class Currency(Enum):
    USD = 23
    INR = 24


class UserRole(Enum):
    CUSTOMER = 1
    VENDOR = True


class Gender(Enum):
    MALE = 1
    FEMALE = 2
    OTHER = 3


class WarrantyService(Enum):
    VIDEO_TECHNICAL_SUPPORT = 1
    ONLINE_SUPPORT = 2
    SPARE_PARTS = 3


class ProductCondition(Enum):
    NEW = "New"
    OLD = "Old"


class SalesService(Enum):
    VIDEO_TECHNICAL_SUPPORT = 1
    ONLINE_SUPPORT = 2
    FREE_SPARE_PARTS = 3


class PackageType(Enum):
    PACKED_IN_ONE_CARTON_BOX_OR_WOODEN_BOX = 1
    SECTION_IN_SEPARATE_PACKAGE = 2


class DiscountType(Enum):
    PERCENTAGE = 1
    FIXED_AMOUNT = 2


class MinimumRequirements(Enum):
    NONE = 0
    MINIMAL_ORDER_VALUE = 1
    MINIMUM_QUANTITY_OF_ITEMS = 2

