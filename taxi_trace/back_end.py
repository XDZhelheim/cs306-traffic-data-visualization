import flask
import pandas as pd
import datetime

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

@app.route("/")
def index():
    return flask.render_template("wait_time_pred.html")

@app.route("/get_wait_time", methods=["GET"])
def get_wait_time():
    location=flask.request.args.get("location")
    location=location.split(",")
    location=list(map(float, location))
    app.logger.debug(location)

    curr_time=datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
    app.logger.debug(curr_time)

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

if __name__ == "__main__":
    app.run(debug=True)