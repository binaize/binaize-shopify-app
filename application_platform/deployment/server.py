import json
import uuid

import requests
from flask import Flask, redirect, request, render_template

from application_platform.src import helpers
from application_platform.src.shopify_client import ShopifyStoreClient
from config import TOKEN_URL, SIGN_UP
from config import WEBHOOK_APP_UNINSTALL_URL, BASE_URL, SHOP_URL
from utils.logger.pylogger import get_logger

logger = get_logger("server", "INFO")
app = Flask(__name__)

ACCESS_TOKEN = None
NONCE = None
ACCESS_MODE = []  # Defaults to offline access mode if left blank or omitted.
# https://shopify.dev/concepts/about-apis/authentication#api-access-modes
SCOPES = ['read_products', "read_orders", "read_themes", "write_themes",
          "read_customers"]  # https://shopify.dev/docs/admin-api/access-scopes


@app.route('/app_launched', methods=['GET'])
@helpers.verify_web_call
def app_launched():
    logger.info(json.dumps(request.args))
    shop = request.args.get('shop')
    code = request.args.get('code')

    global ACCESS_TOKEN, NONCE

    # ACCESS_TOKEN = ShopifyStoreClient.authenticate(shop=shop, code=code)
    logger.info(ACCESS_TOKEN)
    if ACCESS_TOKEN:
        shop_request = requests.get(f"https://{shop}" + SHOP_URL, headers={
            "X-Shopify-Access-Token": ACCESS_TOKEN
        })

        logger.info("SHOP NAME --> ")
        logger.info(shop_request.json())

        x = requests.post('https://dev.api.binaize.com' + TOKEN_URL,
                          data={
                              "username": shop_request.json()["shop"]["id"],
                              "password": shop_request.json()["shop"]["name"]
                          })

        logger.info("------------------------")
        logger.info(x.json()["access_token"])

        return render_template('welcome.html', shop=shop, accessToken=x.json()["access_token"])

    # The NONCE is a single-use random value we send to Shopify so we know the next call from Shopify is valid (see
    # app_installed) https://en.wikipedia.org/wiki/Cryptographic_nonce
    nonce = uuid.uuid4().hex
    redirect_url = helpers.generate_install_redirect_url(shop=shop, scopes=SCOPES, nonce=nonce, access_mode=ACCESS_MODE)
    return redirect(redirect_url, code=302)


@app.route('/app_installed', methods=['GET'])
@helpers.verify_web_call
def app_installed():
    logger.info(json.dumps(request.args))
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app installation started.")

    # Ok, NONCE matches, we can get rid of it now (a nonce, by definition, should only be used once)
    # Using the `code` received from Shopify we can now generate an access token that is specific to the specified `shop` with the
    #   ACCESS_MODE and SCOPES we asked for in #app_installed
    global NONCE, ACCESS_TOKEN

    # Shopify passes our NONCE, created in #app_launched, as the `state` parameter, we need to ensure it matches!
    state = request.args.get('state')

    if state != NONCE:
        return "Invalid `state` received", 400
    NONCE = None

    shop = request.args.get('shop')
    code = request.args.get('code')
    ACCESS_TOKEN = ShopifyStoreClient.authenticate(shop=shop, code=code)

    # We have an access token! Now let's register a webhook so Shopify will notify us if/when the app gets uninstalled
    # NOTE This webhook will call the #app_uninstalled function defined below
    shopify_client = ShopifyStoreClient(shop=shop, access_token=ACCESS_TOKEN)

    shop_details = requests.get(f"https://{shop}" + SHOP_URL, headers={
        "X-Shopify-Access-Token": ACCESS_TOKEN
    })

    shop_name = shop_details.json()["shop"]["name"]
    shop_email = shop_details.json()["shop"]["email"]
    shop_id = shop_details.json()["shop"]["id"]

    logger.info("shop id : {shop_id}".format(shop_id=shop_id))
    logger.info("shop name : {shop_name}".format(shop_name=shop_name))
    logger.info("shop email : {shop_email}".format(shop_email=shop_email))
    logger.info("shopify access token : {shopify_access_token}".format(shopify_access_token=ACCESS_TOKEN))

    shopify_client.create_webook(address=WEBHOOK_APP_UNINSTALL_URL, topic="app/uninstalled")

    sign_up_response = requests.post(BASE_URL + SIGN_UP,
                                     json={
                                         "client_id": shop_id,
                                         "shopify_store": shop_name,
                                         "shopify_access_token": ACCESS_TOKEN
                                     })

    sign_up_message = sign_up_response.json()["message"]
    logger.info(sign_up_message)

    token_response = requests.post(BASE_URL + TOKEN_URL,
                                   data={
                                       "username": shop_id,
                                       "password": shop_name
                                   })

    binaize_access_token = token_response.json()["access_token"]
    logger.info("binaize access token : {binaize_access_token}".format(binaize_access_token=binaize_access_token))

    redirect_url = helpers.generate_post_install_redirect_url(shop=shop, access_token=binaize_access_token)

    logger.info("app installation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return redirect(redirect_url, code=302)


@app.route('/app_uninstalled', methods=['POST'])
@helpers.verify_webhook_call
def app_uninstalled():
    logger.info(json.dumps(request.args))
    # https://shopify.dev/docs/admin-api/rest/reference/events/webhook?api[version]=2020-04
    # Someone uninstalled your app, clean up anything you need to
    # NOTE the shop ACCESS_TOKEN is now void!
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app uninstallation started.")

    global ACCESS_TOKEN
    ACCESS_TOKEN = None

    webhook_topic = request.headers.get('X-Shopify-Topic')
    shop_details = request.get_json()
    logger.info("webhook call received {webhook_topic}:{shop_details}".format(webhook_topic=webhook_topic,
                                                                              shop_details=json.dumps(
                                                                                  shop_details)))

    shop_name = shop_details["name"]
    shop_email = shop_details["email"]
    shop_id = shop_details["id"]

    logger.info("shop id : {shop_id}".format(shop_id=shop_id))
    logger.info("shop name : {shop_name}".format(shop_name=shop_name))
    logger.info("shop email : {shop_email}".format(shop_email=shop_email))

    DELETE_URL = "/api/v1/schemas/client/delete"
    delete_response = requests.post(BASE_URL + DELETE_URL,
                                    json={
                                        "client_id": shop_id,
                                        "shopify_store": shop_name,
                                        "shopify_access_token": "invalid"
                                    })

    delete_message = delete_response.json()["message"]
    logger.info(delete_message)

    logger.info("app uninstallation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return "OK"


@app.route('/data_removal_request', methods=['POST'])
@helpers.verify_webhook_call
def data_removal_request():
    # https://shopify.dev/tutorials/add-gdpr-webhooks-to-your-app
    # Clear all personal information you may have stored about the specified shop
    return "OK"
