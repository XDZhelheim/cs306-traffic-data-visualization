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

df=pd.read_csv("../sample_taxi_after_clean.csv", nrows=100000)
df["time"]=df["time"].apply(parse_time)

k=1000

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

    df_k=df_after.loc[df_after["distance"]<0.1][0:k]

    if not len(df_k):
        return "No enough data"

    estimate_wait_time=df_k["time"].sum()/len(df_k)-curr_time
    estimate_wait_time=round(estimate_wait_time)
    estimate_wait_time=str(datetime.timedelta(seconds=estimate_wait_time))
    app.logger.debug(estimate_wait_time)

    return estimate_wait_time

if __name__ == "__main__":
    app.run(debug=True)