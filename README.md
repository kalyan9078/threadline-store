# Threadline

A modern clothing e-commerce storefront built with Python, Flask, SQLite, JavaScript, HTML, and CSS.

## Features

- Responsive fashion storefront with product categories
- Dynamic product catalogue served by a Flask API
- Shopping bag persisted in browser storage
- Checkout flow with server-side price validation
- SQLite database for products and orders

## Run locally

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Open `http://127.0.0.1:5001` in your browser.

## Project structure

```text
app.py             Flask server and API endpoints
schema.sql         SQLite database schema
static/            Responsive HTML, CSS, and JavaScript storefront
```
