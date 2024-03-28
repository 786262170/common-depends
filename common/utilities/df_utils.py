# coding=utf8
from typing import Iterable, List, Optional, Tuple, Union

import pandas as pd
import toolz


# -- df crud ---
def query_paging(df: pd.DataFrame, limit: int = 100, page: int = 1):
    if int(page) > 0:
        return df[((page - 1) * limit):(page * limit)]
    return df


def order_by_field(df: pd.DataFrame,
                   order_by: Union[str, List[str]] = None,
                   desc: bool = False):
    if order_by and df.columns:
        df = df.sort_values(by=order_by, ascending=desc)
    return df


def df_astype(df: pd.DataFrame):
    df = df.fillna("")
    df = df.astype(str)
    return df


def df_records_num(df, **kwgs) -> Tuple[list, int]:
    count = len(df)
    page, limit = kwgs.pop('page', 1), kwgs.pop("limit", 100)
    order_by, desc = kwgs.pop('order_by', None), kwgs.pop("desc", False)
    df = toolz.pipe(df, lambda x: query_paging(x, limit, page),
                    lambda x: order_by_field(x, order_by, desc), df_astype)
    return df.to_dict("records"), count


def get_group(g: pd.DataFrame, key):
    if key in g.groups:
        return g.get_group(key)
    return pd.DataFrame().reindex(columns=g.obj.columns)


class PandasMixin:
    """pandas辅助"""

    @staticmethod
    def df_get_item_value(df, col1, col1_value, col2) -> any:
        """返回满足col1列值条件的col2列最后一个元素值"""
        return df.at[df.index[df[col1] == col1_value].values[-1], col2]

    @staticmethod
    def df_set_item_value(df, col1, col1_value, col2, col2_value) -> None:
        """修改满足col1列值条件的col2列最后一个元素值"""
        df.at[df.index[df[col1] == col1_value].values[-1], col2] = col2_value

    @staticmethod
    def df_get_col_value(df, col1, col1_value, col2) -> any:
        """返回满足col1列值条件的col2列元素值列表"""
        return df.loc[df[col1] == col1_value, col2].values

    @staticmethod
    def df_set_col_value(df, col1, col1_value, col2, col2_value) -> None:
        """修改满足col1列值条件的col2列元素值"""
        df.loc[df[col1] == col1_value, col2] = col2_value

    @staticmethod
    def df_add_row(df, rows) -> any:
        """在末尾增加一行或多行记录"""
        return df.append(pd.DataFrame(rows), ignore_index=True)

    @staticmethod
    def df_insert_row_1(df, col, col_value, rows) -> any:
        """在满足col1列值条件的末尾插入行"""
        i = df.index[(df[col] == col_value)].values[-1]
        df_1 = df.loc[0:i, :].append(pd.DataFrame(rows), ignore_index=True)
        return df_1.append(df.loc[i + 1:, :], ignore_index=True)

    @staticmethod
    def df_insert_row_2(df, col1, col1_value, col2, col2_value, rows) -> any:
        """在满足col1、col2两列值条件的末尾插入行"""
        i = df.index[(df[col1] == col1_value)
                     & (df[col2] == col2_value)].values[-1]
        df_1 = df.loc[0:i, :].append(pd.DataFrame(rows), ignore_index=True)
        return df_1.append(df.loc[i + 1:, :], ignore_index=True)

    @staticmethod
    def df_drop_row_1(df, col, col_value) -> None:
        """删除指定某列值的行"""
        df.drop(df.index[(df[col] == col_value)], inplace=True)

    @staticmethod
    def df_drop_row_2(df, col1, col1_value, col2, col2_value) -> None:
        """删除指定某两列值的行"""
        df.drop(df.index[(df[col1] == col1_value) & (df[col2] == col2_value)],
                inplace=True)

    @staticmethod
    def df_group(
        df,
        by: Union[str, List[str]],
        include: Optional[Union[str, Iterable]] = None,
        exclude: Optional[Union[str, Iterable]] = None,
    ) -> dict:
        """分组，仅展示满足include、exclude条件的结果"""
        if df.empty:
            return {}
        pos_mapper = {}
        # 避免FutureWarning
        if isinstance(by, list) and len(by) == 1:
            by = by[0]
        for k, g in df.groupby(by=by):
            if include:
                if isinstance(include, str):
                    include = {include}
                if k not in include:
                    continue
                pos_mapper[k] = g
            if exclude:
                if isinstance(exclude, str):
                    exclude = {exclude}
                if k in exclude:
                    continue
            pos_mapper[k] = g
        return pos_mapper
