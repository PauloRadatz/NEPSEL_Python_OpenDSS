# -*- coding: utf-8 -*-
# @Time    : 3/27/2021 11:11 AM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : analysis.py
# @Software: PyCharm

import hc_process
import pandas as pd
import itertools

# Hosting Capacity Methodology
# Inputs
location_list = [114, 115]
circuit_pu_list = [1.045, 1.04]
load_mult_list = [0.2, 0.4]
percent_list = [0.2, 0.9]
kva_to_kw_list = [1, 1.1]
pf_list = [1, -0.97, -0.9]

scenario_list = list()
for scenario in list(itertools.product(*[load_mult_list, location_list, percent_list, circuit_pu_list, kva_to_kw_list, pf_list])):
    scenario_list.append(scenario)

dict_to_df = dict()

location_complete_list = list()
circuit_pu_complete_list = list()
load_mult_complete_list = list()
percent_complete_list = list()
kva_to_kw_complete_list = list()
pf_complete_list = list()

penetration_level_list = list()
total_pv_p_list = list()
total_pv_q_list = list()
total_p_feederhead_list = list()
total_q_feederhead_list = list()
voltage_min_list = list()
voltage_max_list = list()
ov_violation_list = list()
thermal_violation_list = list()

for scenario in scenario_list:
    load_mult, location, percent, circuit_pu, kva_to_kw, pf = scenario

    penetration_level, total_pv_p, total_pv_q, total_p_feederhead, total_q_feederhead, \
    voltage_min, voltage_max, ov_violation, thermal_violation \
        = hc_process.hc_process(kva_to_kw, pf, circuit_pu, load_mult, percent, location)

    # Create a dataframe
    location_complete_list.append(location)
    circuit_pu_complete_list.append(circuit_pu)
    load_mult_complete_list.append(load_mult)
    percent_complete_list.append(percent)
    kva_to_kw_complete_list.append(kva_to_kw)
    pf_complete_list.append(pf)

    penetration_level_list.append(penetration_level)
    total_pv_p_list.append(round(total_pv_p, 2))
    total_pv_q_list.append(round(total_pv_q, 2))
    total_p_feederhead_list.append(total_p_feederhead)
    total_q_feederhead_list.append(total_q_feederhead)
    voltage_min_list.append(voltage_min)
    voltage_max_list.append(voltage_max)
    ov_violation_list.append(ov_violation)
    thermal_violation_list.append(thermal_violation)


dict_to_df["location"] = location_complete_list
dict_to_df["circuit_pu"] = circuit_pu_complete_list
dict_to_df["load_mult"] = load_mult_complete_list
dict_to_df["percent"] = percent_complete_list
dict_to_df["kva_to_kw"] = kva_to_kw_complete_list
dict_to_df["pf"] = pf_complete_list
dict_to_df["penetration_level"] = penetration_level_list
dict_to_df["total_pv_p"] = total_pv_p_list
dict_to_df["total_pv_q"] = total_pv_q_list
dict_to_df["total_feeder_p"] = total_p_feederhead_list
dict_to_df["total_feeder_q"] = total_q_feederhead_list
dict_to_df["voltage_min"] = voltage_min_list
dict_to_df["voltage_max"] = voltage_max_list
dict_to_df["ov_violation"] = ov_violation_list
dict_to_df["thermal_violation"] = thermal_violation_list


df = pd.DataFrame().from_dict(dict_to_df)
df.to_csv(r"C:\PauloRadatz\GitHub\NEPSE_Python_OpenDSS\ckt5\results.csv", index=False)
print("here")


# p_step = 10
# v_threshold = 1.05
# kva_to_kw = 1
# pf = 1
# circuit_pu = 1.045
# load_mult = 0.2
# percent = 0.2