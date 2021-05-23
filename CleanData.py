import json
import math
import urllib.request

import pandas as pd


def deleteDataOutOfBound(f):
    #   原始数据有9843421条数据
    #   严格把数据点控制在深圳纬度范围内（113°46'~114°37')则剩下9827698条数据
    # afterDeleteLon = f[(113.766667 <= f['lon']) & (f['lon'] <= 114.616667)]
    # print(afterDeleteLon)
    #   严格把数据点控制在深圳经度范围内（22°27'~22°52')则剩下9828203条数据
    # afterDeleteLat = f[(22.45 <= f['lat']) & (f['lat'] <= 22.866667)]
    # print(afterDeleteLat)
    #   严格把数据点控制在深圳经纬度范围内,则剩下9827696条数据
    afterDelete = f[(113.766667 <= f['lon']) & (f['lon'] <= 114.616667) & (20.45 <= f['lat']) & (f['lat'] <= 25.866667)]
    return afterDelete


def z_turn(x, y):
    # gcj02坐标转百度坐标
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * math.pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * math.pi)
    bd09_Lng = z * math.cos(theta) + 0.0065
    bd09_Lat = z * math.sin(theta) + 0.006
    lat = str(bd09_Lng)
    lng = str(bd09_Lat)
    return lat, lng


def getDistrictStreedAndId(f):
    for i in range(0, 10):
        lat, lon = z_turn(f.iloc[i, 3], f.iloc[i, 2])
        url = "http://api.map.baidu.com/geocoder/v2/?location=" + lat + "," + lon + "&output=json&pois=1&ak=YWdGplhYjUGQ3GtpKNeuTM2S"
        req = urllib.request.urlopen(url)  # json格式的返回数据
        res = req.read().decode("utf-8")  # 将其他编码的字符串解码成unicode
        m = json.loads(res)
        jsonResult = m.get('result')
        address = jsonResult.get('addressComponent')
        f.iloc[i, 6] = address.get('district')
        f.iloc[i, 7] = address.get('street')
        f.iloc[i, 8] = address.get('streetNumber')
    return f


import math


def parse_time(t: str):
    """Convert timestamp to seconds
    Args:
        t (str): timestamp in format HH:mm:ss
    Returns:
        seconds (int): seconds from 00:00:00
    """
    h_m_s = t.split(":")
    return int(h_m_s[0]) * 60 * 60 + int(h_m_s[1]) * 60 + int(h_m_s[2])


from geopy.distance import geodesic


def deleteIllegalSpeed(f):
    id_list = np.unique(list(f["taxi_id"]))
    f_new = pd.DataFrame()
    for id in id_list:
        f_id = f.loc[f["taxi_id"] == id].sort_values("time")
        last_time = parse_time(f_id.iloc[0, 1])
        last_lat = f_id.iloc[0, 3]
        last_lon = f_id.iloc[0, 2]
        for index, row in f_id.iterrows():
            if last_time == parse_time(row["time"]):
                continue
            distance = geodesic((last_lat, last_lon), (row["lat"], row["lon"])).m
            time = parse_time(row["time"]) - last_time
            if distance / time <= 45:
                last_lat = row["lat"]
                last_lon = row["lon"]
                last_time = parse_time(row["time"])
            else:
                print(index)
                f_id = f_id.drop(index)
        f_new = f_new.append(f_id)
    return f_new


if __name__ == "__main__":
    f = pd.read_csv("./sample_taxi.csv")
    # f[['district', 'street', 'street_id']] = None
    afterDeleteDataOutOfBound = deleteDataOutOfBound(f)
    # afterAddInfo = getDistrictStreedAndId(afterDeleteDataOutOfBound)
    afterAddInfo = afterDeleteDataOutOfBound
    afterDeleteIllegalSpeed = deleteIllegalSpeed(afterAddInfo)
    afterDeleteIllegalSpeed.to_csv("./sample_taxi_after_clean.csv", index=False, sep=',')
