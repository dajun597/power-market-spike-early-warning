import pandas as pd
from pathlib import Path
def hh_to_hour(time_variable_name,df,keep_variable_list,save_filepath):
    try:
        df['time']=pd.to_datetime(df[time_variable_name])
        df['hour']=df['time'].dt.floor('h')
        hourly_df=df.groupby('hour',as_index=False)[keep_variable_list].mean()
        hourly_df=hourly_df.rename(columns={'hour':'time'})
        hourly_df.to_csv(Path(save_filepath),index=False)
        print(f'variable {time_variable_name} change to time, saved to {Path(save_filepath).resolve()}')
    except Exception as e:
        print(e)
