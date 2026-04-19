from sklearn.metrics import mean_squared_error,mean_absolute_error
def evaluating_model(y_test,y_pred):
    mse=mean_squared_error(y_test,y_pred)
    mae=mean_absolute_error(y_test,y_pred)
    mape=(abs(y_test-y_pred)/y_test).mean()*100

    print("MSE: ",mse)
    print("MAE: ",mae)
    print("RMSE: ",mse**0.5)
    print(f"MAPE: {mape}%")

    return{
        "mse":mse,
        "mae":mae,
        "Rmse":mse**0.5,
        "mape":mape
    }
