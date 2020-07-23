require('isomorphic-fetch');

const conf = require("./config");
const FormData = require('form-data');

const dotenv = require('dotenv');
const Koa = require('koa');
const next = require('next');
const {default: createShopifyAuth} = require('@shopify/koa-shopify-auth');
const {verifyRequest} = require('@shopify/koa-shopify-auth');
const session = require('koa-session');

dotenv.config();

const port = parseInt(process.env.PORT, 10) || 3000;
const dev = process.env.NODE_ENV !== 'production';
const app = next({dev});
const handle = app.getRequestHandler();

const {SHOPIFY_API_SECRET_KEY, SHOPIFY_API_KEY} = process.env;

app.prepare().then(() => {
    const server = new Koa();
    server.use(session({secure: true, sameSite: 'none'}, server));
    server.keys = [SHOPIFY_API_SECRET_KEY];

    function fetchCall(shop, token) {

        let binaize_access_token = '';

        const formData = new FormData();
        formData.append("username", "bivav");
        formData.append("password", "bivav12!@");


        return fetch(process.env.REACT_APP_BASE_URL + process.env.REACT_APP_TOKEN, {
            method: "post",
            body: formData
        }).then((response) => response.json())
            .then((respData) => {
                console.log(respData)
                return respData
            }).catch(err => {
                console.log(err);
                return "error"
            });

    }


    server.use(
        createShopifyAuth({
            apiKey: SHOPIFY_API_KEY,
            secret: SHOPIFY_API_SECRET_KEY,
            accessMode: 'offline',
            scopes: ['read_products', "read_orders"],
            async afterAuth(ctx) {
                const {shop, accessToken} = ctx.session;

                console.log("accessCode")
                console.log(accessToken)


                // let shopify_access_token = await fetch("https://{shop}.myshopify.com/admin/oauth/access_token",
                //     {
                //         method: "POST",
                //         body: {
                //             "client_id": SHOPIFY_API_KEY,
                //             "client_secret": SHOPIFY_API_SECRET_KEY,
                //             "code": accessToken
                //         }
                //     }).then((response) => {
                //     console.log(response.json())
                //     return response.json()
                // })


                let binaize_token = await fetchCall(shop, accessToken)
                    .then(res => {
                        console.log("first")
                        console.log(res["access_token"])
                        return res["access_token"]
                    })

                console.log("second")
                console.log(binaize_token)

                try {
                    ctx.redirect('/?at=' + binaize_token);
                } catch (e) {
                    console.error("Error!", e);
                }


            },
        }),
    );

    server.use(verifyRequest());

    server.use(async (ctx) => {
        await handle(ctx.req, ctx.res);
        ctx.respond = false;
        ctx.res.statusCode = 200;

        console.log(ctx.res.statusCode)
        return

    });

    server.listen(port, () => {
        console.log(`> Ready on http://localhost:${port}`);
    });

});