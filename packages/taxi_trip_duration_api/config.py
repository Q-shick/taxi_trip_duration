INPUT_VARS = {'pickup_latitude': float, 'pickup_longitude': float,
              'dropoff_latitude': float, 'dropoff_longitude': float}

DIST_THRESHOLD = 0.2

DIST_INTERVAL = [(0.249, 0.566), (0.566, 0.757), (0.757, 0.951), (0.951, 1.168), (1.168, 1.426),
                 (1.426, 1.764), (1.764, 2.261), (2.261, 3.113), (3.113, 5.144), (5.144, 72.461)]

CATEGORICAL_VARS = ['pickup_day','pickup_hour','pickup_minute',
                    'vendor_id','store_and_fwd_flag',
                    'busy_pickup_spot','busy_dropoff_spot',
                    'pickup_borough','dropoff_borough']

FEATURES = ['passenger_count', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude',
            'dist_mile', 'holiday_ind', 'busy_pickup_dist', 'busy_dropoff_dist', 'horizontal_move', 'vertical_move',
            'Manhattan_speed', 'Manhattan_speed_na', 'Lincoln_Tunnel_speed', 'Lincoln_Tunnel_speed_na',
            'I95_Broadway_speed', 'I95_Broadway_speed_na', 'I95_Fort_Lee_speed', 'I95_Fort_Lee_speed_na',
            'Pulaski_Skyway_speed', 'Pulaski_Skyway_speed_na', 'I678_Queens_speed', 'I678_Queens_speed_na',
            'US_1_9_speed', 'US_1_9_speed_na', 'Brooklyn_Bridge_speed', 'Brooklyn_Bridge_speed_na',
            'Long_Island_Exp_speed', 'Long_Island_Exp_speed_na', 'Newark_Airport_speed', 'Newark_Airport_speed_na',
            'JFK_Airport_speed', 'JFK_Airport_speed_na', 'Port_Authority_Terminal_speed', 'Port_Authority_Terminal_speed_na',
            'Grand_Central_Terminal_speed', 'Grand_Central_Terminal_speed_na', 'Whitehall_Ferry_Terminal_speed', 'Whitehall_Ferry_Terminal_speed_na',
            'pickup_pop', 'pickup_pop_na', 'dropoff_pop', 'dropoff_pop_na', 'nta_trips', 'nta_mean_duration', 'nta_na', 'mean_speed',
            'temp', 'clouds_all', 'wind_deg', 'wind_speed', 'Clear', 'Clouds', 'Drizzle', 'Fog', 'Haze', 'Mist', 'Rain', 'Snow',
            'pickup_day_0', 'pickup_day_1', 'pickup_day_2', 'pickup_day_3', 'pickup_day_4', 'pickup_day_5', 'pickup_day_6',
            'pickup_hour_0', 'pickup_hour_1', 'pickup_hour_2', 'pickup_hour_3', 'pickup_hour_4', 'pickup_hour_5',
            'pickup_hour_6', 'pickup_hour_7', 'pickup_hour_8', 'pickup_hour_9', 'pickup_hour_10', 'pickup_hour_11',
            'pickup_hour_12', 'pickup_hour_13', 'pickup_hour_14', 'pickup_hour_15', 'pickup_hour_16', 'pickup_hour_17',
            'pickup_hour_18', 'pickup_hour_19', 'pickup_hour_20', 'pickup_hour_21', 'pickup_hour_22', 'pickup_hour_23',
            'pickup_minute_0', 'pickup_minute_1', 'pickup_minute_2', 'pickup_minute_3', 'pickup_minute_4', 'pickup_minute_5',
            'vendor_id_1', 'vendor_id_2', 'store_and_fwd_flag_N', 'store_and_fwd_flag_Y',
            'busy_pickup_spot_-1', 'busy_pickup_spot_0', 'busy_pickup_spot_1', 'busy_pickup_spot_2', 'busy_pickup_spot_3',
            'busy_pickup_spot_4', 'busy_pickup_spot_5', 'busy_pickup_spot_6', 'busy_pickup_spot_7', 'busy_pickup_spot_8',
            'busy_pickup_spot_9', 'busy_pickup_spot_10', 'busy_pickup_spot_11',
            'busy_dropoff_spot_-1', 'busy_dropoff_spot_0', 'busy_dropoff_spot_1', 'busy_dropoff_spot_2', 'busy_dropoff_spot_3',
            'busy_dropoff_spot_4', 'busy_dropoff_spot_5', 'busy_dropoff_spot_6', 'busy_dropoff_spot_7', 'busy_dropoff_spot_8',
            'pickup_borough_Bronx', 'pickup_borough_Brooklyn', 'pickup_borough_Manhattan', 'pickup_borough_Queens', 'pickup_borough_Staten Island', 'pickup_borough_unknown',
            'dropoff_borough_Bronx', 'dropoff_borough_Brooklyn', 'dropoff_borough_Manhattan', 'dropoff_borough_Queens', 'dropoff_borough_Staten Island', 'dropoff_borough_unknown']
