from sklearn.ensemble import RandomForestRegressor

def RF(x_train,y_train,params):
    rf_model=RandomForestRegressor(
        random_state=88,
        n_jobs=-1,
        **params
    )
    rf_model.fit(x_train,y_train)
    return rf_model

