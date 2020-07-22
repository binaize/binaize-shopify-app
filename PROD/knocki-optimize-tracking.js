var client_id = "knocki"
var main_url = 'https://api.binaize.com';

var visit_register = '/api/v1/schemas/visit/register';
var cookie_register = '/api/v1/schemas/cookie/register';
var visitors_url = "/api/v1/schemas/visitor/register";

var sub_str_url = window.location.pathname

console.log(sub_str_url)

if (sub_str_url.search("products") !== -1) {

    console.log("Collection: " + sub_str_url.search("products"));
    getCookiesVisitRegister(reg_visit, "product", sub_str_url.substr(sub_str_url.search("/products")));
    btn_cookie_generate();

} else if (sub_str_url.search("collections") !== -1) {

    console.log("Collection: " + sub_str_url.search("collection"));
    getCookiesVisitRegister(reg_visit, "collection", sub_str_url.substr(sub_str_url.search("/collection")));
    btn_cookie_generate();

} else if (sub_str_url.search("cart") !== -1) {

    console.log("Cart: " + sub_str_url.search("cart"));
    getCookiesVisitRegister(reg_visit, "cart", sub_str_url.substr(sub_str_url.search("/cart")));
    btn_cookie_generate();

} else if (sub_str_url.search("account") !== -1) {

    console.log("Account: " + sub_str_url.search("account"));

} else if (sub_str_url.search("challange") !== -1) {

    console.log("Challange Page before login: " + sub_str_url.search("challange"));

} else if (sub_str_url.search("checkouts") !== -1) {

    console.log("Checkout: " + sub_str_url.search("checkouts"));
    getCookiesVisitRegister(reg_visit, "checkout", sub_str_url.substr(sub_str_url.search("/checkout")));
    btn_cookie_generate();

} else {

    console.log("Homepage");
    getCookiesVisitRegister(reg_visit, "home", sub_str_url);
    btn_cookie_generate();

}


function reg_visit(event, url, session_id) {

    console.log("POST : Initiated to register conversion event.");
    fetch(main_url + visit_register, {
        method: 'POST',
        mode: 'cors',
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            "client_id": client_id,
            "session_id": session_id,
            "event_name": event,
            "url": url
        })
    }).then(res => res.json()).then(data => {
        console.log("POST : Successful to register visit event -- " + data.message);
    }).catch(e => {
        console.log("message error", e);
    });

}

function getCookiesVisitRegister(callback, event, url) {

    var decodedCookie = document.cookie;
    var ca = decodedCookie.split(';');

    for (var i = 0; i < ca.length; i++) {
        name = ca[i].split('=')[0];
        value = ca[i].split('=')[1];

        if (name == " _shopify_y") {
            var session_id = value;
            // console.log(session_id);
            // break;
        }

    }
    console.log("Successfully set session_id from cookie - " + session_id);
    callback(event, url, session_id);
}

function btn_cookie_generate() {

    var decodedCookie = document.cookie;
    var ca = decodedCookie.split(';');

    var cookies = {}
    for (var i = 0; i < ca.length; i++) {
        var name = ca[i].split('=')[0];
        var value = ca[i].split('=')[1];

        if (name == " cart") {
            cookies[name.trim()] = value;
        } else if (name == " _shopify_y") {
            cookies[name.trim()] = value;
        }
    }

    console.log("Cookies: ");
    console.log(cookies);

    if ("cart" in cookies && "_shopify_y" in cookies) {

        if (cookies["_shopify_y"] !== "") {

            fetch(main_url + cookie_register, {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    "client_id": client_id,
                    "session_id": cookies["_shopify_y"],
                    "cart_token": cookies["cart"]
                })
            }).then(res => res.json()).then(data => {
                console.log("POST : Successful to register COOKIE event -- " + data.message);
            }).catch(e => {
                console.log("message error", e);
            })

        }else {
            console.log("No shopify Session ID Found!")
        }

        return
    } else {
        console.log("No cart key in cookies");
    }
}
