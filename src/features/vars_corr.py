import pandas as pd


def corr_with_target(
    df,
    target,
    cols=None,
    method='pearson',
    absolute=True,
    top_n=None
):
    """
    计算所有变量与指定 target 的相关性（回归 EDA 工具）

    Parameters
    ----------
    df : pd.DataFrame
    target : str
        目标变量，必须是数值列
    cols : list[str], optional
        指定参与计算的列（默认所有数值列）
    method : str
        'pearson' / 'spearman' / 'kendall'
    absolute : bool
        是否按绝对值排序
    top_n : int, optional
        只返回前 N 个最相关变量

    Returns
    -------
    pd.Series
        排序后的相关性结果
    """

    # 只选数值列
    num_df = df.select_dtypes(include='number')

    if target not in num_df.columns:
        raise ValueError(f"{target} 必须是数值列")

    # 如果指定 cols
    if cols is not None:
        valid_cols = [c for c in cols if c in num_df.columns and c != target]

        if not valid_cols:
            raise ValueError("cols 中没有有效的数值列")

        num_df = num_df[valid_cols + [target]]

    # 计算相关性
    corr = num_df.corrwith(num_df[target], method=method)

    # 去掉 target 自身
    corr = corr.drop(target, errors='ignore')

    # 排序
    if absolute:
        corr = corr.sort_values(key=lambda s: s.abs(), ascending=False)
    else:
        corr = corr.sort_values(ascending=False)

    # 截取 top_n
    if top_n is not None:
        corr = corr.head(top_n)

    return corr