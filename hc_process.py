# -*- coding: utf-8 -*-
# @Time    : 3/23/2021 9:02 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : hc_process.py
# @Software: PyCharm

import py_dss_interface
import random
import functions

# # Hosting Capacity Methodology
v_threshold = 1.05
p_step = 10
# random.seed(114)
# p_step = 10
# v_threshold = 1.05
# kva_to_kw = 1
# pf = 1
# circuit_pu = 1.045
# load_mult = 0.2
# percent = 0.2


def hc_process(kva_to_kw, pf, circuit_pu, load_mult, percent, location):
    random.seed(location)
    dss_file = r"C:\PauloRadatz\GitHub\NEPSE_Python_OpenDSS\ckt5\Master_ckt5.dss"
    dss = py_dss_interface.DSSDLL()
    dss.text(f"Compile [{dss_file}]")
    dss.text("Set Maxiterations=100")
    dss.text("set maxcontrolit=100")
    dss.text("edit Reactor.MDV_SUB_1_HSB x=0.0000001")
    dss.text("edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.00000001")
    dss.text(f"edit vsource.source pu={circuit_pu}")
    # Ex 1
    # a) Voltage profile at peak load and at offpeak load
    dss.text(f"batchedit load..* mode=1")
    dss.text(f"set loadmult={load_mult}")
    dss.solution_solve()
    # dss.text("plot profile phases=all")
    # b) Maximum and Minimum feeder voltages and c) Active and reactive power at the feederhead
    total_p_feederhead, total_q_feederhead, voltage_min, voltage_max = functions.get_powerflow_results(dss)
    # Ex 2
    # a) Find all MV three-phase buses
    buses = dss.circuit_allbusnames()
    mv_buses = list()
    mv_bus_voltage_dict = dict()
    for bus in buses:
        dss.circuit_setactivebus(bus)
        if bus == "sourcebus":
            pass
        elif dss.bus_kVbase() >= 1.0 and len(dss.bus_nodes()) == 3:
            mv_buses.append(bus)
            mv_bus_voltage_dict[bus] = dss.bus_kVbase()
    # b) Select 20% of the MV three-phase buses
    selected_buses = random.sample(mv_buses, int(percent * len(mv_buses)))
    # c) Add PV systems
    for bus in selected_buses:
        functions.define_3ph_pvsystem(dss, bus, mv_bus_voltage_dict[bus], p_step * kva_to_kw, p_step)
        functions.add_bus_marker(dss, bus, "red", 2)
    dss.text("Interpolate")
    dss.solution_solve()
    # dss.text("Plot circuit")
    ov_violation = False
    thermal_violation = False
    i = 0
    while not ov_violation and not thermal_violation and i < 1000:
        i += 1
        functions.increment_pv_size(dss, p_step, kva_to_kw, pf, i)
        total_p_feederhead, total_q_feederhead, voltage_min, voltage_max = functions.get_powerflow_results(dss)

        if voltage_max >= v_threshold:
            ov_violation = True

        dss.lines_first()
        for _ in range(dss.lines_count()):
            if dss.lines_read_phases() == 3:
                dss.circuit_setactiveelement(dss.lines_read_name())
                current = dss.cktelement_currentsmagang()
                rating_current = dss.cktelement_read_normamps()

                if max(current[0:12:2]) / rating_current > 1:
                    thermal_violation = True
                    break
            dss.lines_next()
    print(f"Overvoltage violation {ov_violation}\nThermal violation {thermal_violation}")
    penetration_level = (i - 1) * len(selected_buses) * p_step
    functions.increment_pv_size(dss, p_step, kva_to_kw, pf, i - 1)
    total_p_feederhead, total_q_feederhead, voltage_min, voltage_max = functions.get_powerflow_results(dss)
    total_pv_p, total_pv_q = functions.get_total_pv_powers(dss)

    return penetration_level, total_pv_p, total_pv_q, total_p_feederhead, total_q_feederhead, voltage_min, voltage_max, ov_violation, thermal_violation



