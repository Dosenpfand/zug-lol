from statistics import median

import requests
from datetime import datetime
import time


def get_access_token():
    r = requests.get('https://tickets-mobile.oebb.at/api/domain/v4/init')
    access_token = r.json().get('accessToken')
    return access_token


def get_request_headers(access_token=None):
    if not access_token:
        access_token = get_access_token()

        if not access_token:
            return None

    headers = {'AccessToken': access_token,
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    return headers


def get_station_id(name, access_token=None):
    headers = get_request_headers(access_token)
    params = {'name': name, 'count': 1}
    r = requests.get('https://shop.oebbtickets.at/api/hafas/v1/stations', params, headers=headers)
    if not type(r.json()) is list or not len(r.json()):
        return None
    return r.json()[0]['number']


def get_station_names(name, access_token=None):
    headers = get_request_headers(access_token)
    # TODO: Add more?
    # add_headers = {
    #     'Host': 'shop.oebbtickets.at',
    #     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0',
    #     'Accept': 'application/json, text/plain, */*',
    #     'Accept-Language': 'en-US,en;q=0.7,de;q=0.3',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Referer': 'https://shop.oebbtickets.at/de/ticket',
    #     'Channel': 'inet',
    #     'Lang': 'de',
    #     'Cache-Control': 'no-cache',
    #     'Pragma': 'no-cache',
    #     'x-ts-supportid': 'WEB_kp0jm46z',
    #     'ClientId': '4',
    #     'clientversion': '2.4.8148 - TSPNEU - 102662 - b1 - cd83796',
    #     'DNT': '1',
    #     'Connection': 'keep-alive',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin'}
    params = {'name': name, 'count': 10}
    r = requests.get('https://shop.oebbtickets.at/api/hafas/v1/stations', params, headers=headers)
    if not type(r.json()) is list or not len(r.json()):
        return []
    return [station['name'] if station['name'] != '' else station['meta'] for station in r.json()]


def get_travel_action_id(origin_id, destination_id, date=None, access_token=None):
    if not date:
        date = datetime.utcnow()
    headers = get_request_headers(access_token)

    url = 'https://shop.oebbtickets.at/api/offer/v2/travelActions'
    # TODO: lat,long not needed, name not relevant
    data = \
        {
            'from':
                {
                    'latitude': 48208548, 'longitude': 16372132,
                    'name': 'Wien',
                    'number': origin_id
                },
            'to':
                {
                    'latitude': 47263774, 'longitude': 11400973,
                    'name': 'Innsbruck',
                    'number': destination_id},
            'datetime': date.isoformat(), 'customerVias': [], 'ignoreHistory': True,
            'filter':
                {'productTypes': [], 'history': True, 'maxEntries': 5, 'channel': 'inet'}
        }

    r = requests.post(url, json=data, headers=headers)
    # TODO: here and for all requests handle responses != OK

    travel_actions = r.json().get('travelActions')
    if not travel_actions:
        return None

    travel_action = next(action for action in travel_actions if action['entrypoint']['id'] == 'timetable')
    if not travel_action:
        return None

    travel_action_id = travel_action['id']
    return travel_action_id


def get_connection_id(travel_action_id, date=None, has_vc66=False, get_only_first=True, access_token=None):
    url = 'https://shop.oebbtickets.at/api/hafas/v4/timetable'
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
                "motorailTrainRelevance": "PERSON_ONLY"
            }
        )
    data = {'travelActionId': travel_action_id, 'datetimeDeparture': date.isoformat(),
            'filter':
                {'regionaltrains': False, 'direct': False, 'wheelchair': False, 'bikes': False, 'trains': False,
                 'motorail': False, 'connections': []},
            'passengers':
                [{'me': False, 'remembered': False, 'markedForDeath': False,
                  'challengedFlags': {'hasHandicappedPass': False, 'hasAssistanceDog': False, 'hasWheelchair': False,
                                      'hasAttendant': False},
                  'cards': cards,
                  'relations': [],
                  'isBirthdateChangeable': True,
                  'isBirthdateDeletable': True, 'isNameChangeable': True, 'isDeletable': True, 'isSelected': True,
                  'id': int(time.time()), 'type': 'ADULT', 'birthdateChangeable': True, 'birthdateDeletable': True,
                  'nameChangeable': True, 'passengerDeletable': True}],
            'entryPointId': 'timetable', 'count': 5,
            'debugFilter':
                {'noAggregationFilter': False, 'noEqclassFilter': False, 'noNrtpathFilter': False,
                 'noPaymentFilter': False, 'useTripartFilter': False, 'noVbxFilter': False,
                 'noCategoriesFilter': False},
            'sortType': 'DEPARTURE', }
    # TODO: not necessary?
    # 'from': {'latitude': 48208548, 'longitude': 16372132, 'name': 'Wien', 'number': 1190100},
    # 'to': {'latitude': 47263774, 'longitude': 11400973, 'name': 'Innsbruck', 'number': 1170101}}
    headers = get_request_headers(access_token)
    r = requests.post(url, json=data, headers=headers)
    if not r.json().get('connections') or not type(r.json()['connections']) is list or not len(r.json()['connections']):
        return None

    if get_only_first:
        connection_id = r.json()['connections'][0]['id']
        return connection_id

    connection_ids = [connection['id'] for connection in r.json()['connections']]
    return connection_ids


def get_price_for_connection(connection_id, access_token=None):
    # TODO: Here and for all URIs, put them (or parts) separately
    url = 'https://shop.oebbtickets.at/api/offer/v1/prices'
    if type(connection_id) is not list:
        connection_id = [connection_id]

    connection_id_params = [('connectionIds[]', current_id) for current_id in connection_id]
    params = connection_id_params + [('sortType', 'DEPARTURE'), ('bestPriceId', 'undefined')]
    headers = get_request_headers(access_token)
    r = requests.get(url, params=params, headers=headers)

    prices = [offer.get('price') if not offer.get('reducedScope') else None for offer in r.json()['offers']]
    prices_cleaned = list(filter(None, prices))

    if prices_cleaned:
        price = median(prices_cleaned)
    else:
        price = None

    return price


def get_price(origin, destination, date=None, has_vc66=False, access_token=None):
    if not access_token:
        access_token = get_access_token()
    if not access_token:
        return None

    origin_id = get_station_id(origin, access_token=access_token)
    destination_id = get_station_id(destination, access_token=access_token)
    if not origin_id or not destination_id:
        return None

    travel_action_id = get_travel_action_id(origin_id, destination_id, date=date, access_token=access_token)
    connection_id = get_connection_id(travel_action_id, date=date, has_vc66=has_vc66, access_token=access_token)
    if not connection_id:
        return None

    price = get_price_for_connection(connection_id, access_token=access_token)
    return price
