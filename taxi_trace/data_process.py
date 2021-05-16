import pandas as pd
import numpy as np
import json
import argparse


def parse_time(t: str):
    """Convert timestamp to seconds

    Args:
        t (str): timestamp in format HH:mm:ss

    Returns:
        seconds (int): seconds from 00:00:00
    """
    h_m_s = t.split(":")
    return int(h_m_s[0]) * 60 * 60 + int(h_m_s[1]) * 60 + int(h_m_s[2])


def add_to_dict(row: pd.Series, path_dict: dict):
    path_dict["path"].append([row["lat"], row["lon"], parse_time(row["time"])])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rows", type=int, default=10000)

    args = parser.parse_args()
    num_of_rows = args.rows

    df = pd.read_csv("./sample_taxi.csv", nrows=num_of_rows)

    id_list = list(df["taxi_id"])
    id_list = np.unique(id_list)

    all_path = []

    for id in id_list:
        df_id = df.loc[df["taxi_id"] == id]
        df_id = df_id.sort_values("time")

        path_dict = {"path": []}
        df_id.apply(add_to_dict, args=(path_dict, ), axis=1)
        # for i in range(len(df_id)):
        #     row = df_id.iloc[i]
        #     path_dict["path"].append([row["lat"], row["lon"], i])

        all_path.append(path_dict)

    with open("./data/taxi_data_{}.js".format(num_of_rows), "w") as f:
        f.write("let taxi_tracks = ")
        json.dump(all_path, f)

    print(
        "Finished writing data to ./data/taxi_data_{}.js".format(num_of_rows))
