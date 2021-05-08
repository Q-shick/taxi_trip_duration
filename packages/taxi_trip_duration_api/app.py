import numpy as np
import pandas as pd
import json
import pickle
import os
import datetime as dt

from flask import Flask, request, jsonify, render_template
import plotly
import plotly.graph_objs as go
import plotly.express as px

import config, pipeline as pp

#----------------------------------------------------------------------------------

model = pickle.load(open("data/model.pickle", 'rb'))

df_map = pd.read_csv("data/taxi_trip_samples_2.csv")
# px.set_mapbox_access_token(config.API_KEYS["mapbox"])
px.set_mapbox_access_token(os.environ["MAPBOX"])

fig = px.scatter_mapbox(df_map,
                        lat="latitude", lon="longitude",
                        color="type", opacity=0.7,
                        size="dist_mile", size_max=12, zoom=10,
                        color_continuous_scale=px.colors.cyclical.IceFire,
                        animation_frame="pickup_hour")

fig.update_layout(width=900, height=500, font_family="Verdana")
graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

#----------------------------------------------------------------------------------

# Flask instance
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html',
                           graphJSON=graphJSON,
                           prediction_text="0 Mintues",
                           # mapbox_access_token=config.API_KEYS["mapbox"])
                           mapbox_access_token=os.environ["MAPBOX"])

@app.route('/predict', methods=['POST'])
def predict():
    df = pd.DataFrame([[float(x) for x in request.form.values()]], columns=config.INPUT_VARS.keys())
    df = df.astype(config.INPUT_VARS)
    df['pickup_datetime'] = dt.datetime.now()
    df['vendor_id'] = 1
    df['store_and_fwd_flag'] = 'N'

    df_scaled = pp.data_processing(df)
    pred = model.predict(df_scaled)[0]
    pred_print = str(int(pred // 60)) + " Minutes " + str(int(round(pred % 60, 0))) + " Seconds"

    return pred_print

if __name__ == "__main__":
    app.run(debug=True)
