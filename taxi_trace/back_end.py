import flask
import pandas as pd
import datetime
import haversine as hs

# 暂时用不到，直接浏览器打开 map.html

app=flask.Flask(__name__)

def parse_time(t: str):
    """Convert timestamp to seconds

    Args:
        t (str): timestamp in format HH:mm:ss

    Returns:
        seconds (int): seconds from 00:00:00
    """
    h_m_s = t.split(":")
    return int(h_m_s[0]) * 60 * 60 + int(h_m_s[1]) * 60 + int(h_m_s[2])

df=pd.read_csv("../sample_taxi_after_clean.csv", nrows=1000000)
df["time"]=df["time"].apply(parse_time)

k=10000

data = pd.read_csv('../taxi_OD/OD_distance_data.csv')

@app.route("/")
def index():
    return flask.render_template("wait_time_pred.html")

@app.route("/distance")
def distance():
    return flask.render_template("taxi_distance_pred.html")

@app.route("/get_wait_time", methods=["GET"])
def get_wait_time():
    location=flask.request.args.get("location")
    location=location.split(",")
    location=list(map(float, location))
    app.logger.debug(location)

    curr_time=datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
    app.logger.debug(curr_time)

    global df

    df_after=df.loc[(df["time"]>curr_time) & (df["time"]-curr_time<30*60) & (df["is_passenger"]==0)]

    df_after["distance"]=abs(df_after["lon"]-location[1])+abs(df_after["lat"]-location[0])
    df_after=df_after.sort_values("distance")

    df_k=df_after.loc[df_after["distance"]<0.005][0:k]

    if not len(df_k):
        return "No enough data"

    time_1=df_k.loc[df["time"]-curr_time<=300, "time"]
    if len(time_1):
        less_than_5=time_1.sum()/len(time_1)-curr_time
    else:
        less_than_5=0

    time_2=df_k.loc[(df["time"]-curr_time>300) & (df["time"]-curr_time<=900), "time"]
    if len(time_2):
        g_5_l_15=time_2.sum()/len(time_2)-curr_time
    else:
        g_5_l_15=0

    time_3=df_k.loc[df["time"]-curr_time>900, "time"]
    if len(time_3):
        greater_than_15=time_3.sum()/len(time_3)-curr_time
    else:
        greater_than_15=0

    estimate_wait_time=0.6*less_than_5+0.25*g_5_l_15+0.15*greater_than_15

    estimate_wait_time=round(estimate_wait_time)
    estimate_wait_time=str(datetime.timedelta(seconds=estimate_wait_time))
    app.logger.debug(estimate_wait_time)

    return estimate_wait_time

def dist_func(location2, row):
    loc1 = (float(row['lng1']), float(row['lat1']))
    return float(hs.haversine(loc1, location2))

@app.route("/get_distance", methods=["GET"])
def get_distance():
    global data

    location=flask.request.args.get("location")
    location=location.split(",")
    location=list(map(float, location))
    location.reverse()
    app.logger.debug(location)

    data['near_distance'] = data.apply (lambda row: dist_func(location, row), axis=1)
    data_sorted = data.sort_values('near_distance')
    data_sorted = data_sorted.loc[data_sorted["near_distance"] <= 2]
    total = data_sorted['distance'].sum()
    row_count = data_sorted.shape[0]
    if row_count == 0:
        return "not enough data!"
    else:
        return str(round(total/row_count, 2)) + " km"

if __name__ == "__main__":
    app.run(debug=True)
