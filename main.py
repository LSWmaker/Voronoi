# -*- coding: UTF-8 -*-
"""
describe:
@author: lsw
@file: pytoexe.py
@time: 2023/01/11 14:38
"""
import csv
import math
import time

import pandas as pd
import numpy as np
import stripy
from tqdm import tqdm


def draw_voronoi_area(all_lons, all_lans, need_sit):
    """
    根据输入的点绘制维诺图，该维诺图为球面
    :param need_sit: 需要重点标记的站点
    :param all_lans: 所有站点纬度
    :param all_lons: 所有站站的经度
    """
    # 经纬度数转弧度
    lons, lats = np.radians(all_lons), np.radians(all_lans)
    # 从lon lat点阵列中删除重复项
    lons, lats = stripy.spherical.remove_duplicate_lonlat(lons, lats)

    # 构建对象
    mesh = stripy.spherical.sTriangulation(lons=lons, lats=lats, tree=True)

    need_lon, need_lat, voronoi_area = find_name_site(need_sit, mesh)
    need_site = [need_lon, need_lat]

    return need_site, voronoi_area


def find_name_site(need_sit, mesh):
    """
    绘制指定点及其所在的区域
    :param need_name: 所需点的名称
    :param mesh: stripy对象
    :return: 所需点的经纬度及所在区域的各顶点
    """
    try:
        need_lon = float(need_sit[0])
        need_lat = float(need_sit[1])
    except:
        print(need_sit)

    v_lons, v_lats, regions = mesh.voronoi_points_and_regions()
    vlons, vlats = np.degrees(v_lons), np.degrees(v_lats)

    reg = regions[int(mesh.nearest_vertex(np.radians(need_lon), np.radians(need_lat))[0])]

    sit = []
    for i in range(len(reg)):
        i0, i1 = reg[i - 1], reg[i]
        sit.append([vlons[i0], vlats[i0]])
        sit.append([vlons[i1], vlats[i1]])

    lis1 = []
    [lis1.append(data) for data in sit if data not in lis1]
    return need_lon, need_lat, lis1


if __name__ == '__main__':
    print("请将包含站点信息的csv文件置于本程序所在文件夹下，csv文件格式如下：")
    print("主机号,编号,名称,经度,纬度")
    print("1,1,站点,1.9999,0.5555")
    print("第一行为列名，主机号、编号、名称可以随意命名但必须有这几个列名，其中经度纬度使用弧度或度均可，第二行开始为相应的信息，"
          "该格式为navicat数据库管理工具将站点表导出为csv的格式，站点越多越好，较少的话容易无法形成区域\n")

    time.sleep(3)

    print("正在读取文件...")
    csv_data = pd.read_csv('inf.csv', encoding='utf-8')

    all_sit = csv_data.to_numpy().tolist()
    out_str = []
    out_data = []
    out_data.append(["主机号", "站点号", "顶点坐标"])

    for i in all_sit:
        a1 = math.fabs(i[3] - i[4])
        if a1 < 5:
            i[3] = math.degrees(i[3])
            i[4] = math.degrees(i[4])

    a = np.asarray(csv_data[['经度']]).T
    b = a[0, 0]
    if b < 10:
        all_lons, all_lans = np.asarray(csv_data[['经度']]).T, np.asarray(csv_data[['纬度']]).T
        all_lons = np.degrees(all_lons)
        all_lans = np.degrees(all_lans)
    else:
        all_lons, all_lans = np.asarray(csv_data[['经度']]).T, np.asarray(csv_data[['纬度']]).T
    print("读取完毕，共" + str(len(csv_data)) + "个站点")

    print("开始生成维诺区域...")
    for i in tqdm(all_sit):
        need_site, voronoi_area = draw_voronoi_area(all_lons, all_lans, i[3:])
        new_v = []
        new_v_str = str((need_site[0])) + "\t" + str((need_site[1]))
        for j in voronoi_area:
            newj = [0, 0]
            newj[0] = (j[0])
            newj[1] = (j[1])
            new_v.append(newj)
            new_v_str += "\t" + str((j[0])) + "\t" + str((j[1]))

        key = str([i[0], i[1]]).replace("'", "")
        value = str(new_v)
        out_str.append(new_v_str + "\n")
        outData1 = i[0]
        outData2 = i[1]
        outData3 = new_v
        out_data.append([outData1, outData2, outData3])

        if len(voronoi_area) < 3:
            print(key + "-" + value)

    # 写入CSV文件
    with open("voronoi_area_" + str(len(out_str)) + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for row in out_data:
            writer.writerow(row)

    print("CSV文件" + "voronoi_area_" + str(len(out_str)) + '.csv' + "已创建。")

    print("维诺区域生成完毕，5秒后自动退出")
    time.sleep(5)
