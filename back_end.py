import flask
import json

# 暂时用不到，直接浏览器打开 map.html

app=flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("tencent_map.html")

@app.route("/get_data", methods=["GET"])
def get_data():
    with open("./taxi_data_10000_2.json", "r") as f:
        response=json.load(f)

    return json.dumps(response)

if __name__ == "__main__":
    app.run(debug=True)