# CMS DASH BPA App

A Dockerized Python Dash App for visualizing XXX.

## Run the app locally (without docker)
```bash
cd dash-test/cms_dash
export LOCAL_DEV_MODE='True' # to save bandwidth
python index.py
```
open your browser and navigate to http://0.0.0.0:5050/

##   Run the app using docker
```bash
cd dash-test
docker build . -t dash-test:latest
docker run -p 8050:8050 dash-test:latest
```
open your browser and navigate to on http://0.0.0.0:8050
