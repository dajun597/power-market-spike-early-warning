import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def scatter_matrix_plot(
    df,
    cols=None,
    max_cols=7,
    sample_size=None,
    diag_kind='hist',
    corner=True,
    figsize=(10, 10),
    with_reg=False,
    alpha=0.5
):
    """
    多变量散点矩阵（适用于回归问题的EDA，支持回归线）
    """

    num_df = df.select_dtypes(include='number')

    if cols is not None:
        valid_cols = [c for c in cols if c in num_df.columns]
        if not valid_cols:
            raise ValueError("cols 中没有有效的数值列")
        num_df = num_df[valid_cols]

    selected_cols = num_df.columns[:max_cols].tolist()
    if len(selected_cols) < 2:
        raise ValueError("至少需要 2 个数值变量来画散点矩阵")

    data = num_df[selected_cols].copy()

    if sample_size is not None and len(data) > sample_size:
        data = data.sample(sample_size, random_state=42)

    if with_reg:
        g = sns.pairplot(
            data=data,
            vars=selected_cols,
            kind='reg',
            diag_kind=diag_kind,
            corner=corner,
            plot_kws={'scatter_kws': {'alpha': alpha}},
        )
    else:
        g = sns.pairplot(
            data=data,
            vars=selected_cols,
            kind='scatter',
            diag_kind=diag_kind,
            corner=corner,
            plot_kws={'alpha': alpha},
        )

    g.fig.set_size_inches(figsize)
    g.fig.suptitle("Scatter Matrix", y=1.02)
    plt.show()

    return g