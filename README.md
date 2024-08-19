NOTE: https://nyc-taxi-trip.herokuapp.com/ is no longer in service.

## How long will my taxi trip take in NYC?
This repo contains the source code for the flask app [NYC Taxi Trip Duration](https://nyc-taxi-trip.herokuapp.com/)
that predicts taxi trip durations with an ML model deployed in a simple and quick interface without having to calculate routes.
Its development is based on [this research](https://www.kaggle.com/qshick/nyc-taxi-trips) using NYC Open Data containing over 1.4 millions of taxi trips.

## Simply click two points on the map
Users just need to click pickup/dropoff points on the web page. The model then makes an inference with hundreds of inputs like locations and timestamps. It also makes an API request to [OpenWeather](https://openweathermap.org/api) to prepare weather inputs.
![nyc_taxi_duration_example](https://github.com/user-attachments/assets/f341b6cb-1cec-4b38-a2c3-709de807b64c)
