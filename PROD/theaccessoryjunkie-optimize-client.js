
var URL = 'https://api.binaize.com';
var visitors_url = "/api/v1/schemas/visitor/register";
var client_id = "theaccessoryjunkie"

// jQuery
$.getScript('https://cdnjs.cloudflare.com/ajax/libs/ClientJS/0.1.11/client.min.js', function () {


    let client = new ClientJS();

    console.log(client.getBrowser());

    // IP info data
    $.get("https://ipinfo.io", function (ip_response) {

        console.log(ip_response);

        var decodedCookie = document.cookie;
        var ca = decodedCookie.split(';');
        console.log(ca)

        for (var i = 0; i < ca.length; i++) {
            name = ca[i].split('=')[0];
            value = ca[i].split('=')[1];

            if (name == " _shopify_y") {
                var session_id = value;
                console.log("Initialized session_id from cookie. - " + session_id);

                if (session_id !== "") {

                    // Execute only if shopify session id exists.
                    fetch(URL + visitors_url, {
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
                            "ip": ip_response.ip,
                            "city": ip_response.city,
                            "region": ip_response.region,
                            "country": ip_response.country,
                            "lat": ip_response.loc.split(",")[0],
                            "long": ip_response.loc.split(",")[1],
                            "timezone": ip_response.timezone,
                            "browser": client.getBrowser(),
                            "os": client.getOS(),
                            "device": client.getDeviceType() || "Desktop",
                            "fingerprint": client.getFingerprint()
                        })
                    }).then(res => res.json()).then(data => {
                        console.log(data);
                    }).catch(e => {
                        console.log("Message error", e);
                    })


                }



                break;
            }
        }



    }, "json")

});


