import pandas as pd
from pathlib import Path

def simple_clean_data(df):
    if (df.isna().sum()>0).any():
        df=df.dropna()
    if (df.duplicated().sum()>0).any():
        df=df.drop_duplicates()
    print("Data cleaned successfully")
    return df
