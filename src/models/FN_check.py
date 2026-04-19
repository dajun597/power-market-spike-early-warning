def fn_check(x_test,y_test,y_pred,y_prob,threshold):
    df_test = x_test.copy()
    df_test['y_true'] = y_test
    df_test['y_pred'] = y_pred
    df_test['y_prob'] = y_prob

    fn = df_test[(df_test['y_true'] == 1) & (df_test['y_pred'] == 0)]
    fn['distance'] = abs(fn['y_prob'] - float(threshold))
    fn['is_bound'] = (fn['distance'] < 0.05).astype(int)
    is_bourd_rate=len(fn[fn['is_bound'] == 1])/len(fn)

    print(f'FN bound rate: {is_bourd_rate}')

    fn_df = fn[fn['is_bound'] == 0]
    tn_df=df_test[df_test['y_true'] == 1]

    return fn_df,tn_df
