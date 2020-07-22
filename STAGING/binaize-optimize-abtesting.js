var client_id = 'binaize';
var URL = 'https://staging.api.binaize.com';

var experiment_id = 'c9ce1dffea814bf19927c6083ee42b38';

var variation_1 = '18c5521e5530470e968c7f5f1bbf5967';
// var variation_2 = '1600cf81176e42b6a752dedb5f3a6e64';
var variation_original = 'ee4e261aad60495ea90c377d532f8c2d';

var subStr = window.location.pathname
// var subStr = str.substr(str.search("com/") + 4)

var var_redirect = '/api/v1/schemas/variation/redirection';
var event_register = '/api/v1/schemas/event/register';

console.log(subStr)

if (subStr === "/") {
    console.log("Homepage");
    getCookieVariationID(getVariationID);

} else if (subStr.search("collections") !== -1) {
    console.log("Collection: " + subStr.search("collections"));
    getCookiesConvClick(conversionClick);
}

function getCookieVariationID(callback) {
    console.log("getCookie called.");
    var decodedCookie = document.cookie;
    var ca = decodedCookie.split(';');
    console.log(ca)

    for (var i = 0; i < ca.length; i++) {
        name = ca[i].split('=')[0];
        value = ca[i].split('=')[1];

        if (name == " _shopify_y") {
            var session_id = value;
            console.log("Initialized session_id from cookie. - " + session_id);
            break;
        }
    }
    callback(session_id)
}

function getCookiesConvClick(callback, str) {

    var decodedCookie = document.cookie;
    var ca = decodedCookie.split(';');

    for (var i = 0; i < ca.length; i++) {
        name = ca[i].split('=')[0];
        value = ca[i].split('=')[1];

        if (name == " _shopify_y") {
            var session_id = value;
            //           console.log(session_id);
            break;
        }
    }
    console.log("Successfully set session_id from cookie - " + session_id);
    callback(str, session_id);
}

function getVariationID(session_id) {

    console.log("GET : Initiated to get variation ID to redirect.");
    console.log("session id - " + session_id)

    fetch(URL + var_redirect + '?client_id=' + client_id + '&experiment_id=' + experiment_id + '&session_id=' + session_id,
        {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            }
        })
        .then((res) => {
            console.log(res.status);
            if (res.status === 200) {
                res.json().then(data => {

                    console.log("POST : Successful to get variation ID to redirect." + data.variation_id);
                    console.log(data);

                    if ("variation_id" in data) {

                        var var_id = data.variation_id;
                        console.log("Var ID : " + var_id)
                        localStorage.setItem("variation_id", var_id);

                        if (var_id === variation_1) {
                            console.log("Redirecting to : " + var_id);
                            document.getElementById("edited_title_1").style.display = "block";
                            document.getElementById("edited_title_1_subtext").style.display = "block";

                        } else {
                            console.log("Redirecting to : " + var_id);
                            document.getElementById("edited_title_original").style.display = "block";
                            document.getElementById("edited_title_original_subtext").style.display = "block";
                        }

                    } else {
                        console.log("No Variation ID");
                        var var_id = variation_original
                        document.getElementById("edited_title_normal").style.display = "block";
                    }

                }).catch(err => {
                    console.log(err);
                    document.getElementById("edited_title_normal").style.display = "block";
                })
            }
            else {
                console.log("Problem with server..");
                document.getElementById("edited_title_normal").style.display = "block";
            }
        }).catch(err => {
            console.log(err);
            document.getElementById("edited_title_normal").style.display = "block";
        })
}


function conversionClick(var_id, session_id) {

    console.log("POST : Initiated to Converstion click.");
    fetch(URL + event_register,
        {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(
                {
                    "client_id": client_id,
                    "experiment_id": experiment_id,
                    "session_id": session_id,
                    "variation_id": localStorage.getItem("variation_id"),
                    "event_name": "clicked",
                    "timestamp": "no"
                })
        }).then(res => res.json()).then(data => {
            console.log("POST : Successful to register Conversion Click " + "-" + localStorage.getItem("variation_id") + "-" + data.message);
            console.log(data.message);
        }).catch(e => {
            console.log("message error", { e });
        });

}



