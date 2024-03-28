# vim set fileencoding=utf-8
"""单元测试工具"""


def almost_equal(val1, val2, accuracy=1e-6):
    return abs(val1 - val2) < accuracy


def almost_equal_relative(val1, val2, accuracy=1e-4):
    if val1 == 0:
        if abs(val2) < accuracy:
            return True
        else:
            return False
    return abs(val2 / val1 - 1.0) < accuracy


def df_column_equal(df, col, accuracy=1e-6):
    df = df[~df.apply(lambda row: almost_equal(row[col + '_x'], row[
        col + '_y'], accuracy),
                      axis=1)]
    return len(df) == 0
