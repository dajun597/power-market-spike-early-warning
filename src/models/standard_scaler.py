from sklearn.preprocessing import StandardScaler
def standardize(x_train,x_test):
    scaler=StandardScaler()
    x_train_scaled=scaler.fit_transform(x_train)
    x_test_scaled=scaler.transform(x_test)

    return x_train_scaled,x_test_scaled