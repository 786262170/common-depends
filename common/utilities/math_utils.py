from typing import Union

import numpy as np
import qtlib


def standardize(input_list, method="z-score"):
    """
    数据标准化处理
    :param input_list:
    :param method:
    :return:
    """
    return qtlib.standardize_complete(input_list, method)


def median_rid_extremum(input_list, tolerance=5):
    """
    中位数去极值
    :param input_list:
    :param tolerance:
    :return:
    """
    return qtlib.median_rid_extremum(input_list, tolerance)


def standardize_benchmark(input_list, mean_list, std_list):
    """
    用基准的均值和标准差进行标准化
    :param input_list:
    :param mean_list: 基准均值
    :param std_list: 基准标准差
    :return:
    """
    return qtlib.standardize(input_list, mean_list, std_list)


def standardize_benchmark_py(input_list, mean, std):
    res = [(i - mean) / std if not np.isnan(i) and std != 0 else None
           for i in input_list]
    return res


def to_ten_thousand(num: Union[int, float]):
    if num == 0:
        return num
    return float(num) / 10000


def to_percentage(num_a, num_b):
    if num_a == 0:
        return num_a
    if num_b == 0:
        raise RuntimeError(f"illegal num_b:{num_b}. Please checking")
    return float(num_a) / float(num_b)
