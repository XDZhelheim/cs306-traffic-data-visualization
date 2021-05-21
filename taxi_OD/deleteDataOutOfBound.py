import pandas as pd
import math


def z_turn(x, y):
    # gcj02坐标转百度坐标
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * math.pi)
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * math.pi)
    bd09_Lng = z * math.cos(theta) + 0.0065
    bd09_Lat = z * math.sin(theta) + 0.006
    lat = str(bd09_Lng)
    lng = str(bd09_Lat)
    return lat, lng


def deleteDataOutOfBound(f):
    #   原始数据有9843421条数据
    #   严格把数据点控制在深圳纬度范围内（113°46'~114°37')则剩下9827698条数据
    # afterDeleteLon = f[(113.766667 <= f['lon']) & (f['lon'] <= 114.616667)]
    # print(afterDeleteLon)
    #   严格把数据点控制在深圳经度范围内（22°27'~22°52')则剩下9828203条数据
    # afterDeleteLat = f[(22.45 <= f['lat']) & (f['lat'] <= 22.866667)]
    # print(afterDeleteLat)
    #   严格把数据点控制在深圳经纬度范围内,则剩下9827696条数据
    f = f[(113.766667 <= f['lng1']) & (f['lng1'] <= 114.616667) & (20.45 <= f['lat1']) & (f['lat1'] <= 25.866667)]
    afterDelete = f[
        (113.766667 <= f['lng2']) & (f['lng2'] <= 114.616667) & (20.45 <= f['lat2']) & (f['lat2'] <= 25.866667)]
    return afterDelete


def changeIntoBaidu(f):
    for i in range(0, f.shape[0]):
        lat1, lng1 = z_turn(f.iloc[i, 2], f.iloc[i, 1])
        lat2, lng2 = z_turn(f.iloc[i, 5], f.iloc[i, 4])
        f.iloc[i, 1] = lng1
        f.iloc[i, 2] = lat1
        f.iloc[i, 4] = lng2
        f.iloc[i, 5] = lat2
        # print(i)
    return f


if __name__ == '__main__':
    f = pd.read_csv("data/all_data.csv")
    f = deleteDataOutOfBound(f)
    f = changeIntoBaidu(f)
    f.to_csv("data/all_data_3.csv", index=False, sep=',')
