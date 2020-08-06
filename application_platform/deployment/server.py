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

shop_to_access_token_nonce_dict = dict()
ACCESS_MODE = []  # Defaults to offline access mode if left blank or omitted
# https://shopify.dev/concepts/about-apis/authentication#api-access-modes
SCOPES = ['read_products', "read_orders", "read_themes", "write_themes",
          "read_customers"]  # https://shopify.dev/docs/admin-api/access-scopes


@app.route('/app_launched', methods=['GET'])
@helpers.verify_web_call
def app_launched():
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app launch started.")
    logger.info("request args : {request_args}".format(request_args=json.dumps(request.args)))
    logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
        shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))

    shopify_domain = request.args.get('shop')
    shopify_access_token = shop_to_access_token_nonce_dict[shopify_domain][
        0] if shopify_domain in shop_to_access_token_nonce_dict else None
    nonce = shop_to_access_token_nonce_dict[shopify_domain][
        1] if shopify_domain in shop_to_access_token_nonce_dict else None

    logger.info("shopify_domain : {shopify_domain}".format(shopify_domain=shopify_domain))
    logger.info("shopify_access_token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))
    logger.info("nonce : {nonce}".format(nonce=nonce))

    if shopify_access_token:
        shop_details_url = "https://{shopify_domain}{shop_url}".format(shopify_domain=shopify_domain, shop_url=SHOP_URL)
        logger.info("shop_details_url : {shop_details_url}".format(shop_details_url=shop_details_url))

        shop_details_response = requests.get(shop_details_url, headers={
            "X-Shopify-Access-Token": shopify_access_token
        })

        logger.info("shop details : {shop_details}".format(shop_details=shop_details_response.json()))

        shop_id = shop_details_response.json()["shop"]["id"]

        logger.info("shop_id : {shop_id}".format(shop_id=shop_id))
        logger.info("shopify_domain : {shopify_domain}".format(shopify_domain=shopify_domain))

        shop_details_url = "https://{shopify_domain}{shop_url}".format(shopify_domain=shopify_domain, shop_url=SHOP_URL)
        logger.info("shop_details_url : {shop_details_url}".format(shop_details_url=shop_details_url))

        binaize_token_response = requests.post('https://dev.api.binaize.com' + TOKEN_URL,
                                               data={
                                                   "username": shop_id,
                                                   "password": shopify_domain
                                               })

        logger.info("binaize_token_response : {binaize_token_response}".format(
            binaize_token_response=binaize_token_response.json()))

        binaize_access_token = binaize_token_response.json()["access_token"]

        logger.info("binaize access token : {binaize_access_token}".format(binaize_access_token=binaize_access_token))
        logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
            shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))
        logger.info("app launched for already installed app.")
        logger.info("app launch ended.")
        logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

        return render_template('welcome.html', shop=shopify_domain, accessToken=binaize_access_token)

    else:
        # The NONCE is a single-use random value we send to Shopify so we know the next call from Shopify is valid (see
        # #app_installed) https://en.wikipedia.org/wiki/Cryptographic_nonce
        nonce = uuid.uuid4().hex
        redirect_url = helpers.generate_install_redirect_url(shop=shopify_domain, scopes=SCOPES, nonce=nonce,
                                                             access_mode=ACCESS_MODE)

        shop_to_access_token_nonce_dict[shopify_domain] = (shopify_access_token, nonce)

        logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
            shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))
        logger.info("redirecting to app installation url.")
        logger.info("app launch ended.")
        logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

        return redirect(redirect_url, code=302)


@app.route('/app_installed', methods=['GET'])
@helpers.verify_web_call
def app_installed():
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app installation started.")
    logger.info("request args : {request_args}".format(request_args=json.dumps(request.args)))
    logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
        shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))

    state = request.args.get('state')
    shopify_domain = request.args.get('shop')
    code = request.args.get('code')

    shopify_access_token = shop_to_access_token_nonce_dict[shopify_domain][
        0] if shopify_domain in shop_to_access_token_nonce_dict else None
    nonce = shop_to_access_token_nonce_dict[shopify_domain][
        1] if shopify_domain in shop_to_access_token_nonce_dict else None

    logger.info("shopify_domain : {shopify_domain}".format(shopify_domain=shopify_domain))
    logger.info("shopify_access_token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))
    logger.info("nonce : {nonce}".format(nonce=nonce))
    logger.info("state : {state}".format(state=state))
    logger.info("code : {code}".format(code=code))

    # Shopify passes our NONCE, created in #app_launched, as the `state` parameter, we need to ensure it matches!
    if state != nonce:
        return "App is already installed", 400
    nonce = None

    # Ok, NONCE matches, we can get rid of it now (a nonce, by definition, should only be used once)
    # Using the `code` received from Shopify we can now generate an access token that is specific to the specified `shop` with the
    #   ACCESS_MODE and SCOPES we asked for in #app_installed

    shopify_access_token = ShopifyStoreClient.authenticate(shop=shopify_domain, code=code)
    logger.info("shopify access token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))

    shop_to_access_token_nonce_dict[shopify_domain] = (shopify_access_token, nonce)

    # We have an access token! Now let's register a webhook so Shopify will notify us if/when the app gets uninstalled
    # NOTE This webhook will call the #app_uninstalled function defined below
    shopify_client = ShopifyStoreClient(shop=shopify_domain, access_token=shopify_access_token)

    shop_details_url = "https://{shopify_domain}{shop_url}".format(shopify_domain=shopify_domain, shop_url=SHOP_URL)
    logger.info("shop_details_url : {shop_details_url}".format(shop_details_url=shop_details_url))

    shop_details_response = requests.get(shop_details_url, headers={
        "X-Shopify-Access-Token": shopify_access_token
    })

    logger.info("shop details : {shop_details}".format(shop_details=shop_details_response.json()))

    shop_id = shop_details_response.json()["shop"]["id"]

    logger.info("shop id : {shop_id}".format(shop_id=shop_id))
    logger.info("shop domain : {shopify_domain}".format(shopify_domain=shopify_domain))

    shopify_client.create_webook(address=WEBHOOK_APP_UNINSTALL_URL, topic="app/uninstalled")

    sign_up_response = requests.post(BASE_URL + SIGN_UP,
                                     json={
                                         "client_id": shop_id,
                                         "shopify_store": shopify_domain,
                                         "shopify_access_token": shopify_access_token
                                     })

    logger.info("sign_up_response : {sign_up_response}".format(sign_up_response=sign_up_response.json()))
    sign_up_message = sign_up_response.json()["message"]
    logger.info("sign_up_message : {sign_up_message}".format(sign_up_message=sign_up_message))

    binaize_token_response = requests.post(BASE_URL + TOKEN_URL,
                                           data={
                                               "username": shop_id,
                                               "password": shopify_domain
                                           })

    logger.info("binaize_token_response : {binaize_token_response}".format(
        binaize_token_response=binaize_token_response.json()))

    binaize_access_token = binaize_token_response.json()["access_token"]
    logger.info("binaize access token : {binaize_access_token}".format(binaize_access_token=binaize_access_token))

    redirect_url = helpers.generate_post_install_redirect_url(shop=shopify_domain, access_token=binaize_access_token)

    logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
        shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))
    logger.info("app installation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return redirect(redirect_url, code=302)


@app.route('/app_uninstalled', methods=['POST'])
@helpers.verify_webhook_call
def app_uninstalled():
    # https://shopify.dev/docs/admin-api/rest/reference/events/webhook?api[version]=2020-04
    # Someone uninstalled your app, clean up anything you need to
    # NOTE the shop ACCESS_TOKEN is now void!
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app uninstallation started.")
    logger.info("request args : {request_args}".format(request_args=json.dumps(request.args)))
    logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
        shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))

    webhook_topic = request.headers.get('X-Shopify-Topic')
    shop_details = request.get_json()
    logger.info("webhook call received {webhook_topic}:{shop_details}".format(webhook_topic=webhook_topic,
                                                                              shop_details=json.dumps(
                                                                                  shop_details)))

    shop_id = shop_details["id"]
    shopify_domain = shop_details["myshopify_domain"]

    shop_to_access_token_nonce_dict.pop(shopify_domain, None)

    logger.info("shop id : {shop_id}".format(shop_id=shop_id))
    logger.info("shop domain : {shopify_domain}".format(shopify_domain=shopify_domain))

    DELETE_URL = "/api/v1/schemas/client/delete"
    delete_response = requests.post(BASE_URL + DELETE_URL,
                                    json={
                                        "client_id": shop_id,
                                        "shopify_store": shopify_domain,
                                        "shopify_access_token": "invalid"
                                    })

    delete_message = delete_response.json()["message"]
    logger.info("deletion message : {delete_message}".format(delete_message=delete_message))

    logger.info("shop_to_access_token_nonce_dict : {shop_to_access_token_nonce_dict}".format(
        shop_to_access_token_nonce_dict=json.dumps(shop_to_access_token_nonce_dict)))
    logger.info("app uninstallation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return "OK"


@app.route('/data_removal_request', methods=['POST'])
@helpers.verify_webhook_call
def data_removal_request():
    # https://shopify.dev/tutorials/add-gdpr-webhooks-to-your-app
    # Clear all personal information you may have stored about the specified shop
    return "OK"

