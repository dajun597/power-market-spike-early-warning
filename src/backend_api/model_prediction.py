import json
import joblib
import pandas as pd
from pathlib import Path

from src.features.feature_engineer import spike_feature
from src.backend_api.risk import risk_analysis

def get_project_root():
    current=Path(__file__).resolve()
    for parent in current.parents:
        if parent.joinpath('models_storage').exists():
            return parent
    raise FileNotFoundError('Project root not found')

Base_dir=get_project_root()
model_dir=Base_dir.joinpath('models_storage')


class SpikePredictor:
    def __init__(self):
        self.model=joblib.load(model_dir.joinpath('lgb_model.pkl'))

        with open(model_dir.joinpath('lgb_selected_feature.json'), 'r') as f:
            self.lgb_selected_feature = json.load(f)

        with open(model_dir.joinpath('config.json'),'r') as t:
            self.config = json.load(t)

        self.threshold = self.config['threshold']

    def predict(self,df: pd.DataFrame)->pd.DataFrame:
        clean_df=spike_feature(df)

        x=clean_df[self.lgb_selected_feature].copy()

        if hasattr(self.model, 'predict_proba'):
            probs=self.model.predict_proba(x)[:,1]
        else:
            raise ValueError('model does not support predict_proba')

        preds=(probs>=self.threshold).astype(int)

        result=clean_df.copy()
        result['spike_precentage']=probs
        result['is_spike']=preds
        result['risk_level']=result['spike_precentage'].apply(risk_analysis)
        return result