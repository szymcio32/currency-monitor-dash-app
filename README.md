# Currency monitoring - Dash application
Application is responsible for monitoring currency rates from 2019.

It has a graph, which dynamically change according to user inputs(base currency, currencies, start date, end date)
The graph shows all picked currencies and compare them to base currency.
It has also a dynamic table, which shows last five rates for all picked currencies.

The rate data is taken  from foreign exchange rates API:
http://exchangeratesapi.io/

The purpose of the project was to learn how to build and deploy Dash application

## Setup
Clone the repository, install packages from requirements.txt and run the app
```buildoutcfg
git clone https://github.com/szymcio32/currency-monitor-dash-app.git
cd dash-app
pip install -r requirements.txt
python index.py
```

## Example of app

Main app:

![example-1](https://user-images.githubusercontent.com/32844693/63227756-28a63500-c1ea-11e9-8e9d-1885da2c17dd.PNG)

After selecting four currencies

![example-2](https://user-images.githubusercontent.com/32844693/63227761-36f45100-c1ea-11e9-8236-268f2b358166.PNG)

## Technologies

- Python 3.7.0
- Dash 1.0.1
- HTML / CSS