## MODULE WITH FUNCTIONS USED FOR THE PROJECT





"------------------------------------------------------------------------------"
#############
## Imports ##
#############

## Python libraries

import json

import pandas as pd

from sklearn.cluster import KMeans


## Ancillary modules

from utils.parameters import (
    gm_rename,
    yr,
    n_clusters,
    original_features
)





"------------------------------------------------------------------------------"
#################################
## General ancillary functions ##
#################################


## Pretty print a dictionary and preserving special characters
def json_dump_dict(dictionary):
    """
    Pretty print a dictionary and preserving special characters
        args:
            dictionary (dictionary): dict that will be pretty printed
        returns:
            -
    """

    print(json.dumps(dictionary, indent=4, ensure_ascii=False).encode("utf8").decode())

    return



##
def finding_clusters_match(c_dict, gm_dict):
    """
    """

    orig_c_key = [c_key for c_key in c_dict]
    for c_key in orig_c_key:

        match_num = 1
        best_match = "not_found"
        for gm_key in gm_dict:
            delta_check = len(set(gm_dict[gm_key]) - set(c_dict[c_key]))/len(set(gm_dict[gm_key]))

            if delta_check < match_num:
                match_num = delta_check
                best_match = gm_key

        c_dict[best_match] = c_dict.pop(c_key)

    return c_dict



## Coupling the cluster dictionary with the data original classification.
def finding_clusters_match(c_dict, gm_dict):
    """
    """

    match_map = {}
    matches_used = []
    orig_c_key = [c_key for c_key in c_dict]
    for c_key in orig_c_key:

        match_num = 1
        best_match = "not_found"
        for gm_key in gm_dict:
            delta_check = len(set(gm_dict[gm_key]) - set(c_dict[c_key]))/len(set(gm_dict[gm_key]))

            if (delta_check < match_num) & (gm_key not in matches_used):
                match_num = delta_check
                best_match = gm_key

        c_dict[best_match] = c_dict.pop(c_key)
        matches_used.append(best_match)
        match_map[int(c_key)] = best_match

    return c_dict, match_map



##
def cluster_metrics(c_dict, gm_dict):
    """
    """

    c_dict_res = {}
    for key in c_dict:
        c_dict_res[key] = {
            "-"*10: "-"*10,
            "Correct": len(set(gm_dict[key])) - len((set(gm_dict[key]) - set(c_dict[key]))),
            "Incorrect": len(set(c_dict[key]) - set(gm_dict[key])),
            "Missing": len(set(gm_dict[key]) - set(c_dict[key]))
        }

    return c_dict_res





"------------------------------------------------------------------------------"
################################
## Problem specific functions ##
################################


##
def adding_cluster_feature(df_ime):
    """
    """

    ## List of features that will be used of the clustering process.
    feats = [feat for feat in original_features if
            (original_features[feat]["feature"] == True) &
            (original_features[feat]["selected"] == True)
            ]
    print("Features fed for clustering analysis ({}):".format(len(feats)))
    i = 1
    for f in feats:
        print("{}. {}".format(i, f))
        i += 1

    ## Determining clusters using k-means and attaching column
    kmeans = KMeans(n_clusters=5)
    df_ime["cluster"] = kmeans.fit_predict(df_ime.loc[:, feats])


    return df_ime



##
def cluster_dictionary(df_ime):
    """
    """

    ## Creating dictionaries of clusters and states
    gm_dict = {gm_v: list(df_ime.loc[df_ime["GM"] == gm_v, "NOM_ENT"]) for gm_v in df_ime["GM"].unique()}
    c_dict = {str(c_v): list(df_ime.loc[df_ime["cluster"] == c_v, "NOM_ENT"]) for c_v in df_ime["cluster"].unique()}
    # json_dump_dict(c_dict)

    ## Updating c_dict and df_ime keys based on match with gm_dict
    c_dict, match_map = finding_clusters_match(c_dict, gm_dict)
    df_ime["cluster"] = df_ime["cluster"].map(match_map)

    return gm_dict, c_dict, df_ime



##
def clustering_dataframes(gm_dict, c_dict):
    """
    """

    ## Reference clustering
    gm_df = pd.DataFrame.from_dict(gm_dict, orient="index").transpose().fillna("-")
    gm_df.sort_index(axis=1, inplace=True)
    gm_df.index = pd.MultiIndex.from_tuples([(yr, i) for i in gm_df.index])

    ## Resulting clustering
    c_df = pd.DataFrame.from_dict(c_dict, orient="index").transpose().fillna("-")
    c_df.sort_index(axis=1, inplace=True)
    c_df = c_df.append(pd.DataFrame.from_dict(cluster_metrics(c_dict, gm_dict)))
    c_df.index = pd.MultiIndex.from_tuples([(yr, i) for i in c_df.index])

    return gm_df, c_df
