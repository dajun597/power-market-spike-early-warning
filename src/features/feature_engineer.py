import pandas as pd

def spike_feature(df: pd.DataFrame) -> pd.DataFrame:
    df=df.copy()
    df=df.dropna()
    col_list=['CCGT','INTIRL','NPSHYD','OCGT','OTHER','PS','WIND','TotalAcceptedBidVolume','NetImbalanceVolume','demand_prediction']
    missing_col=[col for col in col_list if col not in df.columns.tolist()]
    if missing_col:
        raise KeyError(f'Missing columns: {missing_col}')

    else:
        df['CCGT_lag_1']=df['CCGT'].shift(1)
        df['INTIRL_lag_1']=df['INTIRL'].shift(1)
        df['NPSHYD_lag_1']=df['NPSHYD'].shift(1)
        df['OCGT_lag_1']=df['OCGT'].shift(1)
        df['OTHER_lag_1']=df['OTHER'].shift(1)
        df['PS_lag_1']=df['PS'].shift(1)
        df['WIND_lag_1']=df['WIND'].shift(1)
        df['TotalAcceptedBidVolume_lag_1']=df['TotalAcceptedBidVolume'].shift(1)

        df['ccgt_wind_ratio'] = df['CCGT_lag_1'] / df['WIND_lag_1']
        df['imbalance_ccgt'] = df['NetImbalanceVolume'] / df['CCGT_lag_1']
        df['ps_imbalance'] = df['PS_lag_1'] * df['NetImbalanceVolume']

        df=df.drop(columns=['CCGT','INTIRL','NPSHYD','OCGT','OTHER','PS','WIND','TotalAcceptedBidVolume'])

        need_list=['demand_prediction', 'NetImbalanceVolume', 'ccgt_wind_ratio',
           'imbalance_ccgt', 'ps_imbalance', 'offer_bid_spread', 'month', 'time',
           'is_spike', 'CCGT_lag_1', 'INTIRL_lag_1', 'NPSHYD_lag_1', 'OCGT_lag_1',
           'OTHER_lag_1', 'PS_lag_1', 'WIND_lag_1',
           'TotalAcceptedBidVolume_lag_1']

        df=df.drop(columns=[col for col in df.columns.tolist() if col not in need_list])

        need_col=[col for col in need_list if col not in df.columns.tolist()]
        if need_col:
            raise KeyError(f'Needed columns: {need_col}')
        else:
            return df








