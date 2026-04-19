from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.model_selection import TimeSeriesSplit

def RF_class(x_train, y_train, params):
    rf_model = RandomForestClassifier(
        random_state=88,
        n_jobs=-1,
        **params
    )

    tscv = TimeSeriesSplit(n_splits=3)

    selector = RFECV(
        estimator=rf_model,
        cv=tscv,
        scoring='f1',
        step=2,
        n_jobs=-1
    )

    selector.fit(x_train, y_train)
    selected_feature = x_train.columns[selector.get_support()].tolist()

    return selector, selected_feature