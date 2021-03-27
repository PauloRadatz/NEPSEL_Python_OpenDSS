# -*- coding: utf-8 -*-
# @Time    : 3/27/2021 12:34 PM
# @Author  : Paulo Radatz
# @Email   : pradatz@epri.com
# @File    : data_analysis.py
# @Software: PyCharm

import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

sns.set_context("talk")
sns.set_style("whitegrid")


mpl_dict = {'figure.facecolor': 'white',
 'axes.labelcolor': '.15',
 'xtick.direction': 'out',
 'ytick.direction': 'out',
 'xtick.color': '.15',
 'ytick.color': '.15',
 'axes.axisbelow': True,
 'grid.linestyle': '--',
 'text.color': '.15',
 'font.family': ['sans-serif'],
 'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif'],
 'lines.solid_capstyle': 'round',
 'patch.edgecolor': 'w',
 'patch.force_edgecolor': True,
 'xtick.top': False,
 'ytick.right': False,
 'axes.grid': True,
 'axes.facecolor': 'white',
 'axes.edgecolor': '.8',
 'grid.color': '.8',
 'axes.spines.left': True,
 'axes.spines.bottom': True,
 'axes.spines.right': True,
 'axes.spines.top': True,
 'xtick.bottom': False,
 'ytick.left': False}

for key, value in mpl_dict.items():
    mpl.rcParams[key] = value

df = pd.read_csv(r"C:\PauloRadatz\GitHub\NEPSE_Python_OpenDSS\ckt5\results.csv")

width_figure = 16
height = 12

def plot(data, x, y, hue, col, row):
 sns.catplot(kind="swarm", x=x, y=y, data=data, hue=hue, col=col, row=row, height=4, aspect=1.5)
 plt.tight_layout()
 plt.show()
 plt.clf()
 plt.close()


df["p_limited"] = df["penetration_level"] - df["total_pv_p"]
plot(data=df[(df["kva_to_kw"] == 1) & (df["circuit_pu"] == 1.045)], x="load_mult", y="penetration_level", hue="location", col="pf", row="percent")
plot(data=df[(df["location"] == 114) & (df["circuit_pu"] == 1.045)], x="load_mult", y="penetration_level", hue="kva_to_kw", col="pf", row="percent")
plot(data=df[(df["location"] == 114) & (df["circuit_pu"] == 1.045)], x="load_mult", y="p_limited", hue="kva_to_kw", col="pf", row="percent")

print("here")