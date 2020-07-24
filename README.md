# binaize-shopify-app

## To deploy in EC2 DEV cluster

```bash
ssh -i "binaize-optimize.pem" ubuntu@dev.shopify.binaize.com
sudo apt update
sudo apt -y install docker.io
sudo apt -y install docker-compose
git clone https://github.com/binaize/binaize-shopify-app.git
cd binaize-shopify-app
scp -i "binaize-optimize.pem" ./hermes-dev.env ubuntu@dev.shopify.binaize.com:~/binaize-shopify-app/
git checkout development
cp hermes-dev.env hermes.env
```

## To deploy in EC2 STAGING cluster

```bash
ssh -i "binaize-optimize.pem" ubuntu@staging.shopify.binaize.com
sudo apt update
sudo apt -y install docker.io
sudo apt -y install docker-compose
git clone https://github.com/binaize/binaize-shopify-app.git
scp -i "binaize-optimize.pem" ./hermes-staging.env ubuntu@staging.shopify.binaize.com:~/binaize-shopify-app/
cd binaize-shopify-app
git checkout staging
cp hermes-staging.env hermes.env
```

## To deploy in EC2 PROD cluster

```bash
ssh -i "binaize-optimize.pem" ubuntu@shopify.binaize.com
sudo apt update
sudo apt -y install docker.io
sudo apt -y install docker-compose
git clone https://github.com/binaize/binaize-shopify-app.git
scp -i "binaize-optimize.pem" ./hermes-prod.env ubuntu@shopify.binaize.com:~/binaize-shopify-app/
cd binaize-shopify-app
git checkout master
cp hermes-prod.env hermes.env
```

# For first time deployment

```bash
nohup sudo docker-compose -f docker-compose-hermes.yaml up --build --remove-orphans >> ~/theia.out&
```

# For re-deployment
```bash
nohup sudo docker-compose -f docker-compose-hermes.yaml up --build --remove-orphans >> ~/theia.out&
```
