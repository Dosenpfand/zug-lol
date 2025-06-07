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
    "init_user_data": "/api/domain/v1/initUserData",
}

logger = logging.getLogger(__name__)


def init_user_data(
    access_token: str,
    host: str = CONFIG["host"],
    user_agent: str = CONFIG["user_agent"],
) -> bool:
    """Initializes user data after obtaining an access token."""

    # TODO: Check what is needed and put in get_request_headers()
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,de;q=0.5",
        "Referer": host + "/de/ticket",
        "Channel": "inet",
        "Lang": "de",
        "x-ts-supportid": "WEB_z2qm6uuf_ynubh42i",  # TODO: Randomize?
        "ClientId": "27",  # TODO: Randomize?
        "AccessToken": access_token,
        "clientversion": "2.4.10975-7967",  # TODO: Randomize?
        "Content-Type": "application/json",
        "Origin": host,
        "DNT": "1",
        "Sec-GPC": "1",
    }
    url = host + API_PATHS["init_user_data"]
    try:
        r = requests.post(url, headers=headers, json={})
        r.raise_for_status()
        logger.info("User data initialized successfully.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not init user data: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(
                f"Response status: {e.response.status_code}, Response text: {e.response.text}"
            )
        return False


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

    response_data = r.json()
    access_token = response_data.get("access_token")

    if not access_token:
        logger.error("Access token not found in response.")
        return None

    if not init_user_data(access_token, host=host, user_agent=user_agent):
        logger.error("Failed to initialize user data after obtaining token.")
        return None

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


# TODO: Maybe not even needed?
def get_station_details(
    name: str,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[Dict[str, Union[str, int, None]]]:
    """Fetches station details including ID, name, latitude, and longitude."""
    headers = get_request_headers(access_token)
    params = {"name": name, "count": "1"}
    try:
        r = requests.get(host + API_PATHS["stations"], params=params, headers=headers)
        r.raise_for_status()
        response_data = r.json()
        if not isinstance(response_data, list) or not len(response_data):
            logger.error(
                f"No station details found for '{name}'. Response: {response_data}"
            )
            return None

        station_data = response_data[0]
        latitude = station_data.get("latitude")
        longitude = station_data.get("longitude")

        return {
            "number": station_data.get("number"),
            "name": station_data.get("name") or station_data.get("meta"),
            "latitude": int(latitude * 1_000_000) if latitude is not None else None,
            "longitude": int(longitude * 1_000_000) if longitude is not None else None,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not get station details for '{name}': {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(
                f"Response status: {e.response.status_code}, Response text: {e.response.text}"
            )
        return None
    except (ValueError, TypeError, KeyError) as e:
        logger.error(
            f"Error processing station data for '{name}': {e}. Data: {station_data if 'station_data' in locals() else 'N/A'}"
        )
        return None


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

    # TODO: Check what is needed and put in get_request_headers()
    base_headers = get_request_headers(access_token)
    if not base_headers:
        logger.error("Failed to get base request headers for get_travel_action_id.")
        return None

    # TODO: Check what is needed and put in get_request_headers()
    specific_headers = {
        # "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,de;q=0.5",
        # "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://shop.oebbtickets.at/de/ticket",
        "Channel": "inet",
        "Lang": "de",
        "x-ts-supportid": "WEB_z2qm6uuf_ynubh42i",
        "ClientId": "26",
        # "AccessToken": "N/A",
        "clientversion": "2.4.10940-TSPNEU-1",
        "Content-Type": "application/json",
        "Origin": "https://shop.oebbtickets.at",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    headers = {**base_headers, **specific_headers}

    url = host + API_PATHS["travel_actions"]
    # TODO: lat,long not needed, name not relevant
    data = {
        "from": {
            "meta": "Wien",
            "latitude": 48208548,
            "longitude": 16372132,
            "name": "",
            "number": origin_id,
        },
        "to": {
            "meta": "Innsbruck",
            "latitude": 47263774,
            "longitude": 11400973,
            "name": "",
            "number": destination_id,
        },
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
        "customerVias": [],
        "ignoreHistory": True,
        "travelActionTypes": ["timetable"],
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
    origin_station_details: Dict[str, Union[str, int, None]],
    destination_station_details: Dict[str, Union[str, int, None]],
    date: Optional[datetime] = None,
    get_only_first: bool = True,
    access_token: Optional[str] = None,
    host: str = CONFIG["host"],
) -> Optional[Union[str, List[str]]]:
    url = host + API_PATHS["timetable"]
    if not date:
        date = datetime.utcnow()

    data = {
        "travelActionId": travel_action_id,
        "datetimeDeparture": date.strftime("%Y-%m-%dT%H:%M:%S.000"),
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
        "from": {
            "latitude": origin_station_details.get("latitude"),
            "longitude": origin_station_details.get("longitude"),
            "name": origin_station_details.get("name"),
            "number": origin_station_details.get("number"),
        },
        "to": {
            "latitude": destination_station_details.get("latitude"),
            "longitude": destination_station_details.get("longitude"),
            "name": destination_station_details.get("name"),
            "number": destination_station_details.get("number"),
        },
    }

    base_headers = get_request_headers(access_token, user_agent=CONFIG["user_agent"])
    if not base_headers:
        logger.error("Failed to get base request headers for get_connection_ids.")
        return None

    # TODO: Check what is needed and put in get_request_headers()
    specific_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,de;q=0.5",
        "Referer": host + "/de/ticket/timetable",
        "Channel": "inet",
        "Lang": "de",
        "x-ts-supportid": "WEB_z2qm6uuf_ynubh42i",
        "ClientId": "27",
        "clientversion": "2.4.10975-7967",
        "Content-Type": "application/json",
        "Origin": host,
    }
    headers = {**base_headers, **specific_headers}

    try:
        r = requests.post(url, json=data, headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not get connection IDs: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(
                f"Response status: {e.response.status_code}, Response text: {e.response.text}"
            )
        return None

    try:
        response_json = r.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(
            f"Failed to decode JSON response from timetable. Text: {r.text[:500]}"
        )  # Log snippet of text
        return None

    connections = response_json.get("connections")
    if not isinstance(connections, list) or not connections:
        logger.error(
            f"No connections found or invalid format. Response: {response_json}"
        )
        return None

    if get_only_first:
        connection_id = connections[0].get("id")
        if not connection_id:
            logger.error(
                f"First connection is missing an ID. Connection data: {connections[0]}"
            )
            return None
        return connection_id

    connection_ids = [
        connection.get("id") for connection in connections if connection.get("id")
    ]
    if not connection_ids:  # If all connections were missing IDs
        logger.error(
            f"All connections were missing IDs. Connections data: {connections}"
        )
        return None
    return connection_ids


def get_price_for_connection(
    connection_id: Union[str, List[str]],
    access_token: Optional[str] = None,
    has_vc66: bool = False,
    host: str = CONFIG["host"],
) -> Optional[float]:
    url = host + API_PATHS["prices"]
    if isinstance(connection_id, str):
        connection_id = [connection_id]

    connection_id_params = [
        ("connectionIds[]", current_id) for current_id in connection_id
    ]
    params = connection_id_params + [
        ("sortType", "DEPARTURE"),
        ("bestPriceId", "undefined"),
    ]

    base_headers = get_request_headers(access_token, user_agent=CONFIG["user_agent"])
    if not base_headers:
        logger.error("Failed to get base request headers for get_price_for_connection.")
        return None

    # TODO: Check what is needed and put in get_request_headers()
    specific_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en,de;q=0.5",
        "Referer": host + "/de/ticket/timetable",
        "Channel": "inet",
        "Lang": "de",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "x-ts-supportid": "WEB_z2qm6uuf_ynubh42i",
        "ClientId": "27",
        "clientversion": "2.4.10975-7967",
    }
    headers = {**base_headers, **specific_headers}

    try:
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not retrieve price for connection: {e}")
        if hasattr(e, "response") and e.response is not None:
            logger.error(
                f"Response status: {e.response.status_code}, Response text: {e.response.text}"
            )
        return None

    try:
        response_json = r.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(
            f"Failed to decode JSON response from prices. Text: {r.text[:500]}"
        )
        return None

    offers = response_json.get("offers")
    if not isinstance(offers, list):
        logger.error(
            f"Offers not found or invalid format in price response. Response: {response_json}"
        )
        return None

    prices = [
        offer.get("price") if not offer.get("reducedScope") else None
        for offer in offers
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

    origin_details = get_station_details(origin, access_token=access_token)
    destination_details = get_station_details(destination, access_token=access_token)

    if not origin_details or not destination_details:
        logger.warning("Could not get origin/destination details.")
        return None

    if not origin_details.get("number") or not destination_details.get("number"):
        logger.warning("Origin/destination station number missing in details.")
        return None

    travel_action_id = get_travel_action_id(
        str(origin_details["number"]),
        str(destination_details["number"]),
        date=date,
        access_token=access_token,
    )
    if not travel_action_id:
        logger.warning("Could not get travel action ID.")
        return None

    connection_ids = get_connection_ids(
        travel_action_id,
        origin_details,
        destination_details,
        date=date,
        get_only_first=(not take_median),
        access_token=access_token,
        host=CONFIG["host"],
    )
    if not connection_ids:
        logger.warning("Could not get connection ID.")
        return None

    price = get_price_for_connection(
        connection_ids, access_token=access_token, has_vc66=has_vc66
    )
    return price
