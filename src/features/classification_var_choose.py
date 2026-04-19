import pandas as pd
def class_var_choose(var_list,dataset,class_var):
    result=[]
    for i in var_list:
        error_bin=pd.qcut(dataset[str(i)],q=5,duplicates='drop')
        class_gap=dataset.groupby(error_bin)[class_var].mean()
        score=abs(class_gap.iloc[-1]-class_gap.iloc[0])
        result.append(
            {'var':i,'score':score}
        )

    result_df=pd.DataFrame(result).sort_values(by='score',ascending=False)
    return result_df