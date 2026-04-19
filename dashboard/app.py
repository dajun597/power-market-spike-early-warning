import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')
st.sidebar.header('Data Input')

uploaded_file=st.file_uploader('Upload CSV File',type=['csv'])

if uploaded_file is not None:
    df=pd.read_csv(uploaded_file)


    st.write('Data Preview')
    st.write(df.head(5))

    st.write('Column Names')
    st.write(df.columns.tolist())

    df['time']=pd.to_datetime(df['time'])
    df=df.sort_values('time').reset_index(drop=True)

    st.write('Time Range')
    st.write(df['time'].min(),'to',df['time'].max())

    latest_row=df.iloc[-1]

    st.write('Latest Record')
    st.write(latest_row)

    st.header('Current Snapshot')

    col1,col2,col3=st.columns(3)
    col1.metric('Latest Time',str(latest_row['time']))
    col2.metric('Latest Spike Probability',round(latest_row['y_prob'],4))
    col3.metric('Spike Probability',latest_row['risk_level'])

    st.header('Latest Risk Trend')
    recent_df=df.tail(24)

    fig1=px.line(
        recent_df,
        x='time',
        y='y_prob',
        title='Recent Spike Probability',
        labels={
            'time':'',
            'y_prob':'Spike Forecast Risk'
        }
    )
    fig1.update_xaxes(tickangle=45,tickformat='%H:%M',dtick=60*60*1000)
    st.plotly_chart(fig1,use_container_width=True)

    st.header('Driver Snapshot')
    col4,col5,col6,col7=st.columns(4)
    col4.metric('Net Imbalance Volume',round(latest_row['NetImbalanceVolume'],2))
    col5.metric('CCGT Lag 1', round(latest_row['CCGT_lag_1'], 2))
    col6.metric('WIND Lag 1', round(latest_row['WIND_lag_1'], 2))
    col7.metric('PS Lag 1', round(latest_row['PS_lag_1'], 2))
else:
    print('File has to be csv.')