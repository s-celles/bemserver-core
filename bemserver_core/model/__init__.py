"""Model"""
from bemserver_core.authorization import init_authorization

from .users import User, UserGroup, UserByUserGroup
from .campaigns import (
    Campaign,
    CampaignScope,
    UserGroupByCampaign,
    UserGroupByCampaignScope,
)
from .sites import (
    StructuralElementProperty,
    SiteProperty,
    BuildingProperty,
    StoreyProperty,
    SpaceProperty,
    ZoneProperty,
    Site,
    Building,
    Storey,
    Space,
    Zone,
    SitePropertyData,
    BuildingPropertyData,
    StoreyPropertyData,
    SpacePropertyData,
    ZonePropertyData,
)
from .timeseries import (
    TimeseriesDataState,
    TimeseriesProperty,
    Timeseries,
    TimeseriesPropertyData,
    TimeseriesByDataState,
    TimeseriesBySite,
    TimeseriesByBuilding,
    TimeseriesByStorey,
    TimeseriesBySpace,
    TimeseriesByZone,
)
from .timeseries_data import TimeseriesData  # noqa
from .events import (  # noqa
    EventCategory,
    EventState,
    EventLevel,
    Event,
)


__all__ = [
    "User",
    "UserGroup",
    "UserByUserGroup",
    "Campaign",
    "CampaignScope",
    "UserGroupByCampaign",
    "UserGroupByCampaignScope",
    "StructuralElementProperty",
    "SiteProperty",
    "BuildingProperty",
    "StoreyProperty",
    "SpaceProperty",
    "ZoneProperty",
    "Site",
    "Building",
    "Storey",
    "Space",
    "Zone",
    "SitePropertyData",
    "BuildingPropertyData",
    "StoreyPropertyData",
    "SpacePropertyData",
    "ZonePropertyData",
    "TimeseriesDataState",
    "TimeseriesProperty",
    "Timeseries",
    "TimeseriesPropertyData",
    "TimeseriesByDataState",
    "TimeseriesData",
    "TimeseriesBySite",
    "TimeseriesByBuilding",
    "TimeseriesByStorey",
    "TimeseriesBySpace",
    "TimeseriesByZone",
    "EventCategory",
    "EventState",
    "EventLevel",
    "Event",
]


# Register classes for authorization
auth_model_classes = [
    User,
    UserGroup,
    UserByUserGroup,
    Campaign,
    CampaignScope,
    UserGroupByCampaign,
    UserGroupByCampaignScope,
    StructuralElementProperty,
    SiteProperty,
    BuildingProperty,
    StoreyProperty,
    SpaceProperty,
    ZoneProperty,
    Site,
    Building,
    Storey,
    Space,
    Zone,
    SitePropertyData,
    BuildingPropertyData,
    StoreyPropertyData,
    SpacePropertyData,
    ZonePropertyData,
    TimeseriesDataState,
    TimeseriesProperty,
    Timeseries,
    TimeseriesPropertyData,
    TimeseriesByDataState,
    TimeseriesBySite,
    TimeseriesByBuilding,
    TimeseriesByStorey,
    TimeseriesBySpace,
    TimeseriesByZone,
    EventCategory,
    EventState,
    EventLevel,
    Event,
]

init_authorization(auth_model_classes)
