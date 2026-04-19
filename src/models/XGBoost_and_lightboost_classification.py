from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.feature_selection import RFECV
from sklearn.model_selection import TimeSeriesSplit

def gradient_boost(mode,x_train,y_train,params=None):
    if params is None:
        params = {}

    if str(mode)=='light':
        lgbmodel = LGBMClassifier(
            objective='binary',
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=88,
            n_jobs=1,
            **params
        )
        tscv=TimeSeriesSplit(n_splits=5)
        selector=RFECV(
            estimator=lgbmodel,
            cv=tscv,
            step=1,
            scoring='f1',
            n_jobs=-1,
        )
        selector.fit(x_train,y_train)
        selected_feature=x_train.columns[selector.get_support()].tolist()
        return selector, selected_feature

    elif str(mode)=='xgb':
        xgbmodel = XGBClassifier(
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=88,
            n_jobs=-1,
            **params
        )
        tscv = TimeSeriesSplit(n_splits=3)
        selector = RFECV(
            estimator=xgbmodel,
            cv=tscv,
            step=1,
            scoring='f1',
            n_jobs=-1,
        )
        selector.fit(x_train, y_train)
        selected_feature=x_train.columns[selector.get_support()].tolist()
        return selector, selected_feature
    else:
        print('Invalid mode')



