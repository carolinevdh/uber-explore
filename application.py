import json
import random
import urllib
import urllib2

from flask import Flask, render_template, request


app = Flask(__name__)

WECODE_LATITUDE = 42.3799673
WECODE_LONGITUDE = -71.1156968

DEFAULT_PRODUCT_ID = '55c66225-fbe7-4fd5-9072-eab1ece5e23e'

MUBER_URL = 'http://m.uber.com/sign-up?'
PRODUCTS_URL = 'https://api.uber.com/v1/products?'
TIME_URL = 'https://api.uber.com/v1/estimates/time?'
PRICE_URL = 'https://api.uber.com/v1/estimates/price?'
CONFIG_FILE = 'config.json'  # secrets should be kept in gitignored file of this name
LOCATIONS_FILE = 'locations.json'


@app.route('/')
def index():
    """Render the start page."""
    return render_template('index.html')


@app.route('/explore', methods=['GET'])
def explore():
    """Render a random location and Uber button."""

    # Load json holding list of locations
    with open(LOCATIONS_FILE, 'r') as f:
        locations = json.load(f)

    # Pick a random location
    location = random.choice(locations)

    # Parse variables for page
    destination = str(location['label'])
    dropoff_latitude = float(location['lat'])
    dropoff_longitude = float(location['lng'])

    # Load secrets
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    client_id = config['client_id']
    token = config['token']

    request_url = construct_request(
        client_id=client_id,
        destination=destination,
        dropoff_latitude=dropoff_latitude,
        dropoff_longitude=dropoff_longitude
    )

    # Get string price range with currency.
    price_estimate = get_price_estimate(
        token=token,
        start_latitude=WECODE_LATITUDE,
        start_longitude=WECODE_LONGITUDE,
        end_latitude=dropoff_latitude,
        end_longitude=dropoff_longitude
    )

    # Get time estimate in rounded minutes.
    time_estimate = get_time_estimate(
        token=token,
        start_latitude=WECODE_LATITUDE,
        start_longitude=WECODE_LONGITUDE,
        product_id=DEFAULT_PRODUCT_ID
    )
    time_estimate = int(round(time_estimate / 60.))

    # Render the page
    return render_template(
        'explore.html',
        destination=destination,
        time_estimate=time_estimate,
        price_estimate=price_estimate,
        request_url=request_url
    )


def construct_request(client_id, destination, dropoff_latitude, dropoff_longitude, product_id=DEFAULT_PRODUCT_ID):
    """Helper function to construct the request url"""

    #  Construct deeplinkurl to request a ride
    request_params = {
        'client_id': client_id,
        'product_id': product_id,
        'pickup_latitude': WECODE_LATITUDE,
        'pickup_longitude': WECODE_LONGITUDE,
        'dropoff_latitude': dropoff_latitude,
        'dropoff_longitude': dropoff_longitude,
    }

    return MUBER_URL + urllib.urlencode(request_params)


def get_price_estimate(token, start_latitude, start_longitude, end_latitude, end_longitude, product_id=DEFAULT_PRODUCT_ID):
    """Returns price estimate range as a string for given product_id and trip start and end points."""

    request_params = {
        'start_latitude': start_latitude,
        'start_longitude': start_longitude,
        'end_latitude': end_latitude,
        'end_longitude': end_longitude,
    }

    url = PRICE_URL + urllib.urlencode(request_params)
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Token {}'.format(token))
    response = urllib2.urlopen(req)

    data = json.loads(response.read())
    product_prices = data['prices']
    price_estimate = [i['estimate'] for i in product_prices if i['product_id'] == product_id]
    price_estimate = price_estimate[0]

    return price_estimate


def get_time_estimate(token, start_latitude, start_longitude, product_id=DEFAULT_PRODUCT_ID):
    """Returns ETA in seconds for given product_id and (lat, lng)."""

    request_params = {
        'token': token,
        'start_latitude': start_latitude,
        'start_longitude': start_longitude,
        'product_id': product_id,
    }

    url = TIME_URL + urllib.urlencode(request_params)
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Token {}'.format(token))
    response = urllib2.urlopen(req)

    data = json.loads(response.read())
    product_times = data['times']
    time_estimate = [i['estimate'] for i in product_times if i['product_id'] == product_id]
    time_estimate = time_estimate[0]

    return time_estimate
    

def get_products(token, latitude, longitude):
    """Returns list of dictionaries for products available at given lat lng."""

    request_params = {
        'token': token,
        'latitude': latitude,
        'longitude': longitude,
    }

    url = PRODUCTS_URL + urllib.urlencode(request_params)
    req = urllib2.Request(url)
    req.add_header('Authorization', 'Token {}'.format(token))
    response = urllib2.urlopen(req)

    data = json.loads(response.read())
    products = data['products']

    return products


if __name__ == '__main__':

    app.run(debug=True)
