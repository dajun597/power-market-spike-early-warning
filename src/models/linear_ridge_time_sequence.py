from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV,TimeSeriesSplit
import numpy as np

def ridge_time_sequence(x_train,y_train):
    ridge_pipe=Pipeline([
        ('scaler', StandardScaler()),
        ('ridge', Ridge())
    ])
    param_grid={'ridge__alpha':np.logspace(-5,3,20)}

    tscv=TimeSeriesSplit(n_splits=5)

    grid_search=GridSearchCV(
        estimator=ridge_pipe,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )

    grid_search.fit(x_train, y_train)
    best_model = grid_search.best_estimator_

    print('best alpha:',grid_search.best_params_['ridge__alpha'])
    print('best cv mse:',grid_search.best_score_*-1)

    return best_model,grid_search.best_params_['ridge__alpha'],-grid_search.best_score_*-1