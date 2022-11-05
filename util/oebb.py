from statistics import median
from typing import Optional, Dict, List, Union

import requests
from datetime import datetime
import time

CONFIG = dict(
    user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    host="https://shop.oebbtickets.at",
)

API_PATHS = {
    "access_token": "/api/domain/v4/init",
    "stations": "/api/hafas/v1/stations",
    "travel_actions": "/api/offer/v2/travelActions",
    "timetable": "/api/hafas/v4/timetable",
    "prices": "/api/offer/v1/prices",
}


def get_access_token(
    host: str = CONFIG["host"], user_agent: str = CONFIG["user_agent"]
) -> Optional[str]:
    headers = {"User-Agent": user_agent}
    r = requests.get(host + API_PATHS["access_token"], headers=headers)
    if not r:
        return None

    access_token = r.json().get("accessToken")
    return access_token


def get_request_headers(
    access_token: Optional[str] = None, user_agent: str = CONFIG["user_agent"]
) -> Optional[Dict[str, str]]:
    if not access_token:
        access_token = get_access_token()
        if not access_token:
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
        return None

    travel_actions = r.json().get("travelActions")
    if not travel_actions:
        return None

    travel_action = next(
        action for action in travel_actions if action["entrypoint"]["id"] == "timetable"
    )
    if not travel_action:
        return None

    travel_action_id = travel_action["id"]
    return travel_action_id


def get_connection_ids(
    travel_action_id: str,
    date: Optional[datetime] = None,
    has_vc66: bool = False,
    get_only_first: bool = True,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[List[str]]:
    url = host + API_PATHS["timetable"]
    if not date:
        date = datetime.utcnow()

    cards = []
    if has_vc66:
        cards.append(
            {
                "name": "Vorteilscard 66",
                "cardId": 9097862,
                "numberRequired": False,
                "isChallenged": False,
                "isFamily": False,
                "isSelectable": True,
                "image": "discountCard",
                "isMergeableIntoCustomerAccount": True,
                "motorailTrainRelevance": "PERSON_ONLY",
            }
        )
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
                "cards": cards,
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
        not r.json().get("connections")
        or not type(r.json()["connections"]) is list
        or not len(r.json()["connections"])
    ):
        return None

    if get_only_first:
        connection_id = r.json()["connections"][0]["id"]
        return connection_id

    connection_ids = [connection["id"] for connection in r.json()["connections"]]
    return connection_ids


def get_price_for_connection(
    connection_id: Union[str, List[str]],
    access_token: Optional[str] = None,
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

    prices = [
        offer.get("price") if not offer.get("reducedScope") else None
        for offer in r.json()["offers"]
    ]
    prices_cleaned: List[float] = list(filter(None, prices))

    if prices_cleaned:
        price = median(prices_cleaned)
    else:
        price = None

    return price


def get_price(
    origin: str,
    destination: str,
    date: Optional[datetime] = None,
    has_vc66: bool = False,
    access_token: Optional[str] = None,
) -> Optional[float]:
    if not access_token:
        access_token = get_access_token()
    if not access_token:
        return None

    origin_id = get_station_id(origin, access_token=access_token)
    destination_id = get_station_id(destination, access_token=access_token)
    if not origin_id or not destination_id:
        return None

    travel_action_id = get_travel_action_id(
        origin_id, destination_id, date=date, access_token=access_token
    )
    if not travel_action_id:
        return None

    connection_ids = get_connection_ids(
        travel_action_id, date=date, has_vc66=has_vc66, access_token=access_token
    )
    if not connection_ids:
        return None

    price = get_price_for_connection(connection_ids, access_token=access_token)
    return price
