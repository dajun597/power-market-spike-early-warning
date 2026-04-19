def tt_split_time(y_variable_name,x_variable_list,df,split_percentage):
    y=df[y_variable_name]
    x=df[x_variable_list]

    if type(split_percentage)==float:
        split_idx=int(len(df.index)*split_percentage)
        x_train=x[:split_idx]
        x_test=x[split_idx:]
        y_train=y[:split_idx]
        y_test=y[split_idx:]

        return x_train, x_test, y_train, y_test
    else:
        print('split_percentage must be an float')

