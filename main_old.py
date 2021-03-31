# -*- coding: utf-8 -*-
# @Time    : 3/23/2021 9:02 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : hc_process.py
# @Software: PyCharm

import py_dss_interface
import random
import functions

# Hosting Capacity Methodology
random.seed(114)
p_step = 10
v_threshold = 1.05
kva_to_kw = 1
pf = 1

dss_file = r"C:\PauloRadatz\GitHub\NEPSE_Python_OpenDSS\ckt5\Master_ckt5.dss"

dss = py_dss_interface.DSSDLL()

dss.text(f"Compile [{dss_file}]")
dss.text("Set Maxiterations=100")
dss.text("set maxcontrolit=100")
dss.text("edit Reactor.MDV_SUB_1_HSB x=0.0000001")
dss.text("edit Transformer.MDV_SUB_1 %loadloss=0.0000001 xhl=0.00000001")
dss.text("edit vsource.source pu=1.045")

# Ex 1
# a) Voltage profile at peak load and at offpeak load
dss.text(f"batchedit load..* mode=1")
dss.text("set loadmult=0.2")
dss.solution_solve()
# dss.text("plot profile phases=all")

# b) Maximum and Minimum feeder voltages
voltages = dss.circuit_allbusvmagpu()
voltage_min = min(voltages)
voltage_max = max(voltages)

# c) Active and reactive power at the feederhead
total_p_feederhead = -1 * dss.circuit_totalpower()[0]
total_q_feederhead = -1 * dss.circuit_totalpower()[1]

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
percent = 0.1
selected_buses = random.sample(mv_buses, int(percent * len(mv_buses)))

# c) Add PV systems
for bus in selected_buses:
    functions.define_3ph_pvsystem(dss, bus, mv_bus_voltage_dict[bus], p_step * kva_to_kw, p_step)
    functions.add_bus_marker(dss, bus, "red", 2)
dss.text("Interpolate")
dss.solution_solve()
# dss.text("Plot circuit")
total_p_feederhead = -1 * dss.circuit_totalpower()[0]
total_q_feederhead = -1 * dss.circuit_totalpower()[1]
voltages = dss.circuit_allbusvmagpu()
voltage_min = min(voltages)
voltage_max = max(voltages)

# functions.volt_var(dss)

ov_violation = False
thermal_violation = False
i = 0
while not ov_violation and not thermal_violation and i < 100:
    i += 1
    dss.pvsystems_first()
    for _ in range(dss.pvsystems_count()):
        dss.text(f"edit pvsystem.{dss.pvsystems_read_name()} pmpp={p_step * i} kva={kva_to_kw * p_step * i} pf={pf} pfpriority=yes")
        dss.pvsystems_next()
    dss.solution_solve()
    voltages = dss.circuit_allbusvmagpu()
    voltage_max = max(voltages)
    voltage_min = min(voltages)
    total_p_feederhead = -1 * dss.circuit_totalpower()[0]
    total_q_feederhead = -1 * dss.circuit_totalpower()[1]

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
        dss.lines_next()

penetration_level = (i - 1) * len(selected_buses) * p_step
print(f"Overvoltage violation {ov_violation}\nThermal violation {thermal_violation}")

dss.pvsystems_first()
for _ in range(dss.pvsystems_count()):
    dss.text(f"edit pvsystem.{dss.pvsystems_read_name()} pmpp={p_step * (i - 1)} kva={kva_to_kw * p_step * (i - 1)} pf={pf} pfpriority=yes")
    dss.pvsystems_next()
dss.solution_solve()
voltages = dss.circuit_allbusvmagpu()
voltage_max = max(voltages)
voltage_min = min(voltages)
total_p_feederhead = -1 * dss.circuit_totalpower()[0]
total_q_feederhead = -1 * dss.circuit_totalpower()[1]

total_pv_p_list = list()
total_pv_q_list = list()
dss.pvsystems_first()
for _ in range(dss.pvsystems_count()):
    dss.circuit_setactiveelement(f"PVsystem.{dss.pvsystems_read_name()}")
    total_pv_p_list.append(-1 * sum(dss.cktelement_powers()[0:6:2]))
    total_pv_q_list.append(-1 * sum(dss.cktelement_powers()[1:6:2]))
    dss.pvsystems_next()

total_pv_p = sum(total_pv_p_list)
total_pv_q = sum(total_pv_q_list)
print("here")
