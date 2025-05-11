import logging
import time
from datetime import datetime, timedelta
from statistics import median
from typing import Optional, Dict, List, Union

import requests
from sentry_sdk import add_breadcrumb

CONFIG = dict(
    user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
    host="https://shop.oebbtickets.at",
)

API_PATHS = {
    "access_token": "/api/domain/v1/anonymousToken",
    "stations": "/api/hafas/v1/stations",
    "travel_actions": "/api/offer/v2/travelActions",
    "timetable": "/api/hafas/v4/timetable",
    "prices": "/api/offer/v1/prices",
}

logger = logging.getLogger(__name__)


def get_access_token(
    host: str = CONFIG["host"], user_agent: str = CONFIG["user_agent"]
) -> Optional[str]:
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Channel": "inet",
        "Lang": "de",
        "ClientId": "1",
    }

    r = requests.get(host + API_PATHS["access_token"], headers=headers)
    if not r:
        logger.error("Could not get access token.")
        return None

    access_token = r.json().get("access_token")
    return access_token


def get_request_headers(
    access_token: Optional[str] = None, user_agent: str = CONFIG["user_agent"]
) -> Optional[Dict[str, str]]:
    if not access_token:
        access_token = get_access_token()
        if not access_token:
            logger.warning("Could not get access token.")
            return None

    headers = {
        "AccessToken": access_token,
        "User-Agent": user_agent,
    }
    return headers


def get_station_id(
    name: str,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[str]:
    headers = get_request_headers(access_token)
    params = {"name": name, "count": "1"}
    r = requests.get(host + API_PATHS["stations"], params, headers=headers)
    if not r or not type(r.json()) is list or not len(r.json()):
        logger.error("Could not get station ID.")
        return None

    return r.json()[0]["number"]


def get_station_names(
    name: str,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> List[str]:
    headers = get_request_headers(access_token)
    params = {"name": name, "count": "10"}
    r = requests.get(host + API_PATHS["stations"], params, headers=headers)
    if not r or not type(r.json()) is list or not len(r.json()):
        logger.error("Could not get station names.")
        return []

    return [
        station["name"] if station["name"] != "" else station["meta"]
        for station in r.json()
    ]


def get_travel_action_id(
    origin_id: str,
    destination_id: str,
    date: Optional[datetime] = None,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[str]:
    if not date:
        date = datetime.utcnow()
    headers = get_request_headers(access_token)

    url = host + API_PATHS["travel_actions"]
    # TODO: lat,long not needed, name not relevant
    data = {
        "from": {
            "latitude": 48208548,
            "longitude": 16372132,
            "name": "Wien",
            "number": origin_id,
        },
        "to": {
            "latitude": 47263774,
            "longitude": 11400973,
            "name": "Innsbruck",
            "number": destination_id,
        },
        "datetime": date.isoformat(),
        "customerVias": [],
        "ignoreHistory": True,
        "filter": {
            "productTypes": [],
            "history": True,
            "maxEntries": 5,
            "channel": "inet",
        },
    }

    r = requests.post(url, json=data, headers=headers)
    if not r:
        logger.error("Could not get travel actions.")
        return None

    travel_actions = r.json().get("travelActions")
    if not travel_actions:
        logger.error("Could not parse travel actions.")
        return None

    travel_action = next(
        action for action in travel_actions if action["entrypoint"]["id"] == "timetable"
    )
    if not travel_action:
        logger.error("Could not find time table in travel actions.")
        return None

    travel_action_id = travel_action.get("id")

    if not travel_action_id:
        logger.error("Could not find ID in travel action.")

    return travel_action_id


def get_connection_ids(
    travel_action_id: str,
    date: Optional[datetime] = None,
    get_only_first: bool = True,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[List[str]]:
    url = host + API_PATHS["timetable"]
    if not date:
        date = datetime.utcnow()

    data = {
        "travelActionId": travel_action_id,
        "datetimeDeparture": date.isoformat(),
        "filter": {
            "regionaltrains": False,
            "direct": False,
            "wheelchair": False,
            "bikes": False,
            "trains": False,
            "motorail": False,
            "connections": [],
        },
        "passengers": [
            {
                "me": False,
                "remembered": False,
                "markedForDeath": False,
                "challengedFlags": {
                    "hasHandicappedPass": False,
                    "hasAssistanceDog": False,
                    "hasWheelchair": False,
                    "hasAttendant": False,
                },
                "cards": [],
                "relations": [],
                "isBirthdateChangeable": True,
                "isBirthdateDeletable": True,
                "isNameChangeable": True,
                "isDeletable": True,
                "isSelected": True,
                "id": int(time.time()),
                "type": "ADULT",
                "birthdateChangeable": True,
                "birthdateDeletable": True,
                "nameChangeable": True,
                "passengerDeletable": True,
            }
        ],
        "entryPointId": "timetable",
        "count": 5,
        "debugFilter": {
            "noAggregationFilter": False,
            "noEqclassFilter": False,
            "noNrtpathFilter": False,
            "noPaymentFilter": False,
            "useTripartFilter": False,
            "noVbxFilter": False,
            "noCategoriesFilter": False,
        },
        "sortType": "DEPARTURE",
    }
    # TODO: not necessary?
    # 'from': {'latitude': 48208548, 'longitude': 16372132, 'name': 'Wien', 'number': 1190100},
    # 'to': {'latitude': 47263774, 'longitude': 11400973, 'name': 'Innsbruck', 'number': 1170101}}
    headers = get_request_headers(access_token)
    r = requests.post(url, json=data, headers=headers)
    if (
        not r
        or not r.json().get("connections")
        or not type(r.json()["connections"]) is list
        or not len(r.json()["connections"])
    ):
        logger.error("Could not get connection IDs.")
        return None

    if get_only_first:
        connection_id = r.json()["connections"][0]["id"]
        return connection_id

    connection_ids = [connection["id"] for connection in r.json()["connections"]]
    return connection_ids


def get_price_for_connection(
    connection_id: Union[str, List[str]],
    access_token: Optional[str] = None,
    has_vc66: bool = False,
    host: str = CONFIG["host"],
) -> Optional[float]:
    url = host + API_PATHS["prices"]
    if type(connection_id) is str:
        connection_id = [connection_id]

    connection_id_params = [
        ("connectionIds[]", current_id) for current_id in connection_id
    ]
    params = connection_id_params + [
        ("sortType", "DEPARTURE"),
        ("bestPriceId", "undefined"),
    ]
    headers = get_request_headers(access_token)
    r = requests.get(url, params=params, headers=headers)

    if not r.ok:
        logger.error("Could not retrieve price for connection.")
        return None

    prices = [
        offer.get("price") if not offer.get("reducedScope") else None
        for offer in r.json()["offers"]
    ]
    prices_cleaned: List[float] = list(filter(None, prices))

    if prices_cleaned:
        price = median(prices_cleaned)
        if has_vc66:
            price = round(price / 2, 2)
    else:
        add_breadcrumb(type="info", category="response.json", data=r.json())
        logger.error("Could not determine price for connection.")
        price = None

    return price


def get_price(
    origin: str,
    destination: str,
    date: Optional[datetime] = None,
    has_vc66: bool = False,
    take_median: bool = False,
    access_token: Optional[str] = None,
) -> Optional[float]:
    if not date:
        date = (datetime.utcnow() + timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )

    if not access_token:
        access_token = get_access_token()
    if not access_token:
        logger.warning("Could not get access token.")
        return None

    origin_id = get_station_id(origin, access_token=access_token)
    destination_id = get_station_id(destination, access_token=access_token)
    if not origin_id or not destination_id:
        logger.warning("Could not get origin/destination ID.")
        return None

    travel_action_id = get_travel_action_id(
        origin_id, destination_id, date=date, access_token=access_token
    )
    if not travel_action_id:
        logger.warning("Could not get travel action ID.")
        return None

    connection_ids = get_connection_ids(
        travel_action_id,
        date=date,
        get_only_first=(not take_median),
        access_token=access_token,
    )
    if not connection_ids:
        logger.warning("Could not get connection ID.")
        return None

    price = get_price_for_connection(
        connection_ids, access_token=access_token, has_vc66=has_vc66
    )
    return price
