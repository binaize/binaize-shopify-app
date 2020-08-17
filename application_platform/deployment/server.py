import json
import uuid

import requests
from flask import Flask, redirect, request, render_template

from application_platform.src import helpers
from application_platform.src.shopify_client import ShopifyStoreClient
from config import TOKEN_URL, SIGN_UP
from config import WEBHOOK_APP_UNINSTALL_URL, BINAIZE_API_URL
from utils.logger.pylogger import get_logger

logger = get_logger("server", "INFO")
app = Flask(__name__)

SCOPES = ['read_products', "read_orders", "read_themes", "write_themes",
          "read_customers"]  # https://shopify.dev/docs/admin-api/access-scopes


@app.route('/app_launched', methods=['GET'])
@helpers.verify_web_call
def app_launched():
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app launch started.")
    logger.info("request args : {request_args}".format(request_args=json.dumps(request.args)))

    shop_id = request.args.get('shop')

    binaize_shop_details_response = requests.get(
        "https://dev.api.binaize.com/api/v1/schemas/shop/shopify_details?shop_id=" + shop_id)
    binaize_shop_details = binaize_shop_details_response.json()
    logger.info(
        "binaize_shop_details : {binaize_shop_details}".format(binaize_shop_details=json.dumps(binaize_shop_details)))

    if binaize_shop_details is not None:
        shopify_access_token = binaize_shop_details["shopify_access_token"]
        shopify_nonce = binaize_shop_details["shopify_nonce"]
    else:
        shopify_access_token = None
        shopify_nonce = None

    logger.info("shopify domain : {shopify_domain}".format(shopify_domain=shop_id))
    logger.info("shopify access token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))
    logger.info("shopify nonce : {shopify_nonce}".format(shopify_nonce=shopify_nonce))

    if shopify_access_token:
        logger.info("shop_id : {shop_id}".format(shop_id=shop_id))

        binaize_token_response = requests.post(BINAIZE_API_URL + TOKEN_URL,
                                               data={
                                                   "username": shop_id,
                                                   "password": shop_id
                                               })

        logger.info("binaize_token_response : {binaize_token_response}".format(
            binaize_token_response=binaize_token_response.json()))

        binaize_access_token = binaize_token_response.json()["access_token"]

        logger.info("binaize access token : {binaize_access_token}".format(binaize_access_token=binaize_access_token))
        logger.info("app launched for already installed app.")
        logger.info("app launch ended.")
        logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

        return render_template('welcome.html', shop=shop_id, accessToken=binaize_access_token)

    else:
        shopify_nonce = uuid.uuid4().hex
        redirect_url = helpers.generate_install_redirect_url(shop=shop_id, scopes=SCOPES, nonce=shopify_nonce,
                                                             access_mode=[])

        binaize_nonce_response = requests.post(
            BINAIZE_API_URL + "/api/v1/schemas/shop/nonce/update",
            json={
                "shop_id": shop_id,
                "shopify_nonce": shopify_nonce
            })

        logger.info("binaize nonce response : {binaize_nonce_response}".format(
            binaize_nonce_response=binaize_nonce_response.json()))
        binaize_nonce_message = binaize_nonce_response.json()["message"]
        logger.info(
            "binaize_nonce_message : {binaize_nonce_message}".format(binaize_nonce_message=binaize_nonce_message))

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

    state = request.args.get('state')
    shop_id = request.args.get('shop')
    code = request.args.get('code')

    binaize_shop_details_response = requests.get(
        "https://dev.api.binaize.com/api/v1/schemas/shop/shopify_details?shop_id=" + shop_id)
    binaize_shop_details = binaize_shop_details_response.json()
    logger.info(
        "binaize_shop_details : {binaize_shop_details}".format(binaize_shop_details=json.dumps(binaize_shop_details)))

    if binaize_shop_details is not None:
        shopify_access_token = binaize_shop_details["shopify_access_token"]
        shopify_nonce = binaize_shop_details["shopify_nonce"]
    else:
        shopify_access_token = None
        shopify_nonce = None

    logger.info("shop_id : {shop_id}".format(shop_id=shop_id))
    logger.info("shopify_access_token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))
    logger.info("shopify_nonce : {shopify_nonce}".format(shopify_nonce=shopify_nonce))
    logger.info("state : {state}".format(state=state))
    logger.info("code : {code}".format(code=code))

    if state != shopify_nonce:
        return "App is already installed", 400

    shopify_access_token = ShopifyStoreClient.authenticate(shop=shop_id, code=code)
    logger.info("shopify access token : {shopify_access_token}".format(shopify_access_token=shopify_access_token))

    shopify_client = ShopifyStoreClient(shop=shop_id, access_token=shopify_access_token)
    shopify_client.create_webook(address=WEBHOOK_APP_UNINSTALL_URL, topic="app/uninstalled")

    sign_up_response = requests.post(BINAIZE_API_URL + SIGN_UP,
                                     json={
                                         "shop_id": shop_id,
                                         "shopify_access_token": shopify_access_token
                                     })

    logger.info("sign_up_response : {sign_up_response}".format(sign_up_response=sign_up_response.json()))
    sign_up_message = sign_up_response.json()["message"]
    logger.info("sign_up_message : {sign_up_message}".format(sign_up_message=sign_up_message))

    binaize_token_response = requests.post(BINAIZE_API_URL + TOKEN_URL,
                                           data={
                                               "username": shop_id,
                                               "password": shop_id
                                           })

    logger.info("binaize_token_response : {binaize_token_response}".format(
        binaize_token_response=binaize_token_response.json()))

    binaize_access_token = binaize_token_response.json()["access_token"]
    logger.info("binaize access token : {binaize_access_token}".format(binaize_access_token=binaize_access_token))

    redirect_url = helpers.generate_post_install_redirect_url(shop=shop_id, access_token=binaize_access_token)

    logger.info("app installation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return redirect(redirect_url, code=302)


@app.route('/app_uninstalled', methods=['POST'])
@helpers.verify_webhook_call
def app_uninstalled():
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))
    logger.info("app uninstallation started.")
    logger.info("request args : {request_args}".format(request_args=json.dumps(request.args)))

    webhook_topic = request.headers.get('X-Shopify-Topic')
    shop_details = request.get_json()
    logger.info("webhook call received {webhook_topic}:{shop_details}".format(webhook_topic=webhook_topic,
                                                                              shop_details=json.dumps(
                                                                                  shop_details)))

    shop_id = shop_details["myshopify_domain"]

    logger.info("shop id : {shop_id}".format(shop_id=shop_id))

    DELETE_URL = "/api/v1/schemas/shop/delete"
    delete_response = requests.post(BINAIZE_API_URL + DELETE_URL,
                                    json={
                                        "shop_id": shop_id,
                                        "shopify_access_token": "invalid"
                                    })

    delete_message = delete_response.json()["message"]
    logger.info("deletion message : {delete_message}".format(delete_message=delete_message))

    logger.info("app uninstallation ended.")
    logger.info("{hash}".format(hash="".join(["#" for i in range(60)])))

    return "OK"


@app.route('/data_removal_request', methods=['POST'])
@helpers.verify_webhook_call
def data_removal_request():
    # https://shopify.dev/tutorials/add-gdpr-webhooks-to-your-app
    # Clear all personal information you may have stored about the specified shop
    return "OK"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
