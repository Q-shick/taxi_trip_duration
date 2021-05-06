import numpy as np
import pandas as pd

import pickle
import requests

import datetime as dt
import holidays as hd

import geopy.distance as gpy
from shapely.geometry import LineString, Point, Polygon, LinearRing, shape, asShape
import shapely.ops as so
import shapely.wkt as wkt
from rtree import index

from sklearn.preprocessing import StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

from taxi_trip_duration_api import config

#----------------------------------------------------------------------------------

congested_df = pd.read_csv('data/congested_areas.csv')
congested_areas = pickle.load(open("data/congested_areas.pickle", "rb" ))
scaler = pickle.load(open("data/scaler.pickle", "rb"))
zero_encoding = pd.read_csv("data/zero_encoding.csv")

congested_agg = pd.read_csv("data/congested_agg.csv")
speed_agg = pd.read_csv("data/speed_agg.csv")
nta_agg = pd.read_csv("data/nta_agg.csv")

hourly_weather = pd.read_csv("data/hourly_weather.csv")
weather_cols = pd.read_csv('data/weather_cols.csv')

slow_trip_pickup = pd.read_csv("data/slow_trip_pickup.csv")
slow_trip_dropoff = pd.read_csv("data/slow_trip_dropoff.csv")

neighbor_pop = pd.read_csv('data/neighbor_pop.csv')
neighbor_pop['geometry'] = neighbor_pop['geometry'].apply(lambda g : wkt.loads(g))
rtree_idx = index.Index()
for fid, feature in neighbor_pop['geometry'].items():
    rtree_idx.insert(fid, feature.bounds)

#----------------------------------------------------------------------------------

def datetime_processing(df):
    # if isinstance(df['pickup_datetime'], dt.datetime) == False:
    #     df['pickup_datetime'] = df['pickup_datetime'].apply(lambda d : dt.datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))
    df['pickup_month'] = df['pickup_datetime'].apply(lambda d : d.month)
    df['pickup_date'] = df['pickup_datetime'].apply(lambda d : d.day)
    df['pickup_hour'] = df['pickup_datetime'].apply(lambda d : d.hour)
    df['pickup_minute'] = df['pickup_datetime'].apply(lambda d : d.minute)//10
    df['pickup_day'] = df['pickup_datetime'].apply(lambda d : d.weekday())
    df['holiday_ind'] = int(df['pickup_datetime'].apply(lambda d : dt.datetime.strftime(d, "%Y-%m-%d") in hd.US()))

    return df

def dist_processing(df):
    df['dist_mile'] = df.apply(lambda d : \
        gpy.distance((d['pickup_latitude'], d['pickup_longitude']), \
                     (d['dropoff_latitude'], d['dropoff_longitude'])).miles, axis=1)

    return df

def lat_lon_movement_processing(df):
    df['horizontal_move'] = df['dropoff_longitude'] - df['pickup_longitude']
    df['vertical_move'] = df['dropoff_latitude'] - df['pickup_latitude']

    return df

def busy_location_processing(df):
    def dist_from_center(lat, long, centers, radius):
        for _, row in centers.iterrows():
            radius_measured = gpy.distance((lat, long), (row['latitude'], row['longitude'])).miles
            if radius_measured < radius:
                return int(row['cluster']), radius_measured
        return -1, 0

    df[['busy_pickup_spot','busy_pickup_dist']] = df.apply(lambda d : \
        dist_from_center(d['pickup_latitude'], d['pickup_longitude'], slow_trip_pickup, config.DIST_THRESHOLD), axis=1).tolist()
    df[['busy_dropoff_spot','busy_dropoff_dist']] = df.apply(lambda d : \
        dist_from_center(d['dropoff_latitude'], d['dropoff_longitude'], slow_trip_dropoff, config.DIST_THRESHOLD), axis=1).tolist()

    return df

def within_congested_area(area, pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):
    """ Return miles overlapping the given area
        if a straight line (trip) is within the area """
    ext = LinearRing(area.exterior.coords)
    line = LineString([(pickup_lon, pickup_lat),(dropoff_lon, dropoff_lat)])
    inter_p = line.intersection(ext)

    if (Point(pickup_lon, pickup_lat).within(area) == True) & (Point(dropoff_lon, dropoff_lat).within(area) == True):
        return -1
    elif Point(pickup_lon, pickup_lat).within(area) == True:
        return gpy.distance((pickup_lat, pickup_lon),(inter_p.coords[0][1], inter_p.coords[0][0])).miles
    elif Point(dropoff_lon, dropoff_lat).within(area) == True:
        return gpy.distance((dropoff_lat, dropoff_lon),(inter_p.coords[0][1], inter_p.coords[0][0])).miles
    elif line.intersection(ext).is_empty == False:
        coords = [(p.x, p.y) for p in inter_p]
        return gpy.distance((coords[0][1], coords[0][0]),(coords[1][1], coords[1][0])).miles
    else:
        return 0

def congested_area_processing(df):
    """ Call within congested area for congested areas and
        calculate the within area percentage """
    for idx, row in congested_df.iterrows():
        df[row['area']] = df.apply(lambda p : within_congested_area(congested_areas[idx][row['area']], \
            p['pickup_latitude'], p['pickup_longitude'], p['dropoff_latitude'], p['dropoff_longitude']), axis=1)
        df[row['area']] = df.apply(lambda p : p[row['area']]/p['dist_mile'] if p['dist_mile'] > 0 else 0, axis=1)
        df[row['area']] = df[row['area']].apply(lambda p : 1 if p < 0 else p)

    return df

def congested_speed_processing(df):
    """ Multiply congested portion with congested speed """
    for idx, row in congested_df.iterrows():
        df[row['area']+'_group'] = df[row['area']].apply(lambda x : \
            'high' if x > 0.66 else 'mid' if x > 0.33 else 'low' if x > 0 else 'n/a')

    for area in congested_df['area']:
        df[area+'_speed'] = pd.merge(df, congested_agg[congested_agg['area']==area], how='left', \
                                     left_on=[area+'_group','pickup_day','pickup_hour'], \
                                     right_on=['dist_percent','pickup_day','pickup_hour'])['avg_speed']
        df[area+'_speed_na'] = df[area+'_speed'].apply(lambda s : 1 if np.isnan(s)==True else 0)
        df[area+'_speed'] = df[area+'_speed'].fillna(0)

    return df

def population_processing(df):
    """ Search points with trees and remove false positives """
    def nta_population(lon, lat):
        eps = 1e-7 # to make squares
        all_hits = rtree_idx.intersection([lon, lat, lon+eps, lat+eps]) # rtree intersection not allowing points
        real_hits = []

        for p in all_hits:
            if Point(lon, lat).within(neighbor_pop.iloc[p]['geometry']):
                real_hits.append(p)

        if len(real_hits) > 0:
            return [neighbor_pop.loc[real_hits[0]]['Borough'], neighbor_pop.loc[real_hits[0]]['ntaname'],
                    neighbor_pop.loc[real_hits]['Population'].mean(), 0]
        else:
            return ['unknown', 'unknown', 0, 1]

    df[['pickup_borough','pickup_nta','pickup_pop','pickup_pop_na']] = df.apply(lambda p : \
        nta_population(p['pickup_longitude'], p['pickup_latitude']), axis=1).tolist()
    df[['dropoff_borough','dropoff_nta','dropoff_pop','dropoff_pop_na']] = df.apply(lambda p : \
        nta_population(p['dropoff_longitude'], p['dropoff_latitude']), axis=1).tolist()

    return df

def weather_processing(df):
    # try:
    weather = requests.get('http://api.openweathermap.org/data/2.5/weather?lat=' + \
                           str(df['pickup_latitude'].values[0]) + '&lon=' + str(df['pickup_longitude'].values[0]) + \
                           '&appid=' + config.API_KEYS['weather']).json()
    # weather.raise_for_status()
    # except Exception as err:
    #     print("Other error occurred: ", err)  # Python 3.6
    # else:
    print('Weather data successfully extracted')
    temp = (weather['main']['temp'] - 273.15) * 9/5 + 32 # converted to fahrenheit
    weather_data = pd.DataFrame(
        [[temp, weather['clouds']['all'], weather['wind']['deg'], weather['wind']['speed'], 1]],
        columns = ['temp', 'clouds_all', 'wind_deg', 'wind_speed', weather['weather'][0]['main']]
    )

    weather_data = pd.concat([weather_data, weather_cols], axis=1, join='outer')
    weather_data = weather_data.loc[:,~weather_data.columns.duplicated()]
    df = pd.concat([df, weather_data], axis=1, join='outer')

    return df

def aggregation_data_merge(df):
    df = pd.merge(df, nta_agg, how='left', on=['pickup_nta','pickup_day','pickup_hour'])

    dist_interval = pd.IntervalIndex.from_tuples(config.DIST_INTERVAL)
    df['dist_bins'] = df['dist_mile'].apply(lambda d : dist_interval[dist_interval.get_loc(d)]).astype('string')
    df = pd.merge(df, speed_agg, how='left', on=['pickup_borough','pickup_day','pickup_hour','dist_bins'])

    return df

def categorical_processing(df):
    for var in config.CATEGORICAL_VARS:
        df[var] = df[var].astype('category')

    df = pd.get_dummies(df, columns=config.CATEGORICAL_VARS)
    df = pd.concat([df, zero_encoding], axis=1, join='outer')
    df = df.loc[:,~df.columns.duplicated()]

    return df

#----------------------------------------------------------------------------------

def data_processing(df):
    df = datetime_processing(df)
    df = dist_processing(df)
    df = lat_lon_movement_processing(df)
    df = busy_location_processing(df)
    df = congested_area_processing(df)
    df = congested_speed_processing(df)
    df = population_processing(df)
    df = weather_processing(df)
    df = aggregation_data_merge(df)
    df = categorical_processing(df)

    df_scaled = scaler.transform(df[config.FEATURES])

    return df_scaled
