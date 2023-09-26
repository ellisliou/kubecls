import pandas as pd
import json


def pad_dict_list(dict_list, padel):
    lmax = 0
    for lname in dict_list.keys():
        lmax = max(lmax, len(dict_list[lname]))
    for lname in dict_list.keys():
        ll = len(dict_list[lname])
        if  ll < lmax:
            dict_list[lname] += [padel] * (lmax - ll)
    return dict_list

jsonFile = open('report template.json','r')
df_json=pad_dict_list(json.load(jsonFile),0)

df_json = pd.DataFrame(df_json)
df_json.to_excel('report_template.xlsx')