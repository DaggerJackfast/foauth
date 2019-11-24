# Foauth
foauth is a library for testing social (google, facebook, twitter) authorization methods.

## Setup
Clone repository to local
```bash
git clone git@github.com:DaggerJackfast/foauth.git
```
Before installing it need to setup env files
```bash
touch foauth/.env
touch pages/.env.local
```
Add the next content to foauth/.env file
```
GOOGLE_CLIENT_ID=<your google application id>
GOOGLE_CLIENT_SECRET=<your google application client secret>
FACEBOOK_CLIENT_ID=<your facebook application client id>
FACEBOOK_CLIENT_SECRET=<your facebook application client secret>
TWITTER_CLIENT_SECRET=<your facebook application client secret>
TWITTER_CLIENT_SECRET=<your facebook application client secret>
```
Add the same content to pages/.env.local but add REACT_APP_ prefix before environment variable key(like REACT_APP_GOOGLE_CLIENT_ID)

Next you should setup https certs to localhost

Install mkcert utility (https://github.com/FiloSottile/mkcert).

Create .pem key and cert
```bash
mkdir certs
cd certs
mkcert localhost
```
Install and run CA to local
```bash
mkcert -install
```
Install requrements for back and run application
```bash
cd foauth
pip install -r requirements.txt
python app.py
```

Install requirements for front and run application
```bash
cd pages
yarn
yarn start
```

