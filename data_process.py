import pandas as pd
import numpy as np
import json

def add_to_dict(row: pd.Series, path_dict: dict):
    path_dict["path"].append([row["lat"], row["lon"], row["order"]])

if __name__ == "__main__":
    num_of_taxis = 10000

    df = pd.read_csv("./sample_taxi.csv", nrows=num_of_taxis)

    id_list = list(df["taxi_id"])
    id_list = np.unique(id_list)

    all_path = []

    for id in id_list:
        df_id = df.loc[df["taxi_id"] == id]
        df_id = df_id.sort_values("time")
        df_id["order"] = range(len(df_id))

        path_dict = {"path": []}
        df_id.apply(add_to_dict, args=(path_dict,), axis=1)
        # for i in range(len(df_id)):
        #     row = df_id.iloc[i]
        #     path_dict["path"].append([row["lat"], row["lon"], i])

        all_path.append(path_dict)

    with open("taxi_data_{}.js".format(num_of_taxis), "w") as f:
        f.write("let taxi_tracks = ")
        json.dump(all_path, f)