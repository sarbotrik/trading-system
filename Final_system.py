import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import talib as ta
from nselib import derivatives
from nselib import capital_market
from datetime import datetime
import math
from scipy.stats import norm

from streamlit_option_menu import option_menu

st.title('Derivatives Trading System')

selected=option_menu('Menu Bar',options=['Explorer','Price Calculator','Trend Analyser','Strategies','Payoff and metrics'],orientation='Vertical')

if selected=='Explorer':
    st.title('Explorer')
    #Getting the option chain data
    option_chain,filters,levels=st.tabs(['Option Chain','Filters','Levels'])
    with option_chain:
        expiry=st.date_input('Enter the expiry date')
        date_time=expiry.strftime('%d-%m-%Y')
        data=derivatives.nse_live_option_chain('NIFTY',expiry_date=date_time)
        
        st.dataframe(data)
    with filters:
        expiry_date=st.date_input('Expiry Date')
        expiry=expiry_date.strftime('%d-%m-%Y')
        
        strike=st.number_input('Strike Price')
        
        data2=derivatives.nse_live_option_chain('NIFTY',expiry_date=expiry)
        data3=data2[data2['Strike_Price']==strike]

        type=st.sidebar.selectbox('Option Type',options=['CE','PE'])
        if type=='CE':
            data4=data3[['CALLS_OI','CALLS_Chng_in_OI','CALLS_Volume','CALLS_IV','CALLS_LTP','CALLS_Net_Chng','CALLS_Bid_Qty','CALLS_Ask_Qty','CALLS_Ask_Price','CALLS_Bid_Price']]
       
        elif type=='PE':
            data4=data3[['PUTS_OI','PUTS_Chng_in_OI','PUTS_Volume','PUTS_IV','PUTS_LTP','PUTS_Net_Chng','PUTS_Bid_Qty','PUTS_Ask_Qty','PUTS_Ask_Price','PUTS_Bid_Price']]
        
        
        st.dataframe(data4)

    with levels:
        expiry_date=st.date_input('Enter expiry date')
        expiry=expiry_date.strftime('%d-%m-%Y')
        data=derivatives.nse_live_option_chain('NIFTY',expiry)
        data_OI_Puts=data[data['PUTS_Chng_in_OI']==max(data['PUTS_Chng_in_OI'])]
        data_OI_Calls=data[data['CALLS_Chng_in_OI']==max(data['CALLS_Chng_in_OI'])]

        lower_level=data_OI_Puts['Strike_Price']
        upper_level=data_OI_Calls['Strike_Price']
        st.markdown(f'The lower level is {lower_level}')
        st.markdown(f'The upper level is {upper_level}')

       




if selected=="Price Calculator":
    st.title('Price Calculator')

    submit4=st.button('Find Implied Volatility')

    if submit4:
        strike_price=st.number_input('Enter the strike price')
        expiry_date=st.date_input('Enter the expiry date')
        expiry=expiry_date.strftime('%d-%m-%Y')
        type=st.selectbox('Option Type',options=['CE','PE'])

        if type=='CE':
            data=derivatives.nse_live_option_chain('NIFTY',expiry_date=expiry)
            data3=data[data['Strike_Price']==strike_price]
            data4=data3['CALLS_IV']
            st.write(data4)
              
        elif type=='PE':
             data=derivatives.nse_live_option_chain('NIFTY',expiry)
             data3=data[data['Strike_Price']==strike_price]
             data4=data3['PUTS_IV']
             st.write(data4)
         
    



    
    S=st.number_input('Enter the spot price')
    K=st.number_input('Enter the strike price')
    time_to_expiry=st.number_input('Enter time to expiry')
    r=0.04
    
    volatility=st.number_input('Enter the IV')
    T=time_to_expiry/365
    vol=volatility/100

    option_type=st.sidebar.selectbox('Option Type',options=['CE','PE'])
    if option_type=='CE':
        d1=(math.log(S/K)+(r+0.5*vol**2)*T)/(vol*math.sqrt(T))
        d2=d1-(vol*math.sqrt(T))
        call_price=S*norm.cdf(d1,0,1)-K*math.exp(-r*T)*norm.cdf(d2,0,1)
        st.write(f'The call option price is {call_price}')

    elif option_type=='PE':
        d1=(math.log(S/K)+(r+0.5*vol**2)*T)/(vol*math.sqrt(T))
        d2=d1-(vol*math.sqrt(T))
        put_price=K*math.exp(-r*T)*norm.cdf(-d2,0,1)-S*norm.cdf(-d1,0,1)
        st.write(f'The put option price is {put_price}')




elif selected=="Trend Analyzer":
    st.title('Trend Analyzer')

elif selected=='Strategies':
    st.title('Strategies')
    underlying_trend=st.sidebar.selectbox('Trend Type',options=['Bullish','Bearish','Neutral','Rangebreak'])

elif selected=='Payoff and metrics':
    st.title('Payoff and Metrics Calculator')
    spot_rate=st.sidebar.number_input('Enter the sport rate')
    def call_payoff(sT,strike_price,premium):
        return np.where(sT>strike_price,sT-strike_price,0)-premium

    def put_payoff(sT,strike_price,premium):
        return np.where(sT<strike_price,strike_price-sT,0)-premium
    
    sT=np.arange(0.90*spot_rate,1.1*spot_rate,1)
    r=0.04

    leg_1,leg_2,leg_3=st.columns(3, gap='large')
    with leg_1:
         
          K=st.number_input('Enter the strike price for first')
          premium=st.number_input('Enter the option price for first')
          option_type=st.selectbox('Option Type for first',options=['CE','PE'])
          position_type=st.selectbox('Position Type for first',options=['Long','Short'])
          if option_type=='CE' and position_type=='Long':
               payoff_1=call_payoff(sT,K,premium)
          
          elif option_type=='PE' and position_type=='Long':
               payoff_1=put_payoff(sT,K,premium)


          elif option_type=='CE' and position_type=='Short':
               payoff_1=call_payoff(sT,K,premium)*-1.0

          elif option_type=='PE' and position_type=='Short':
               payoff_1=put_payoff(sT,K,premium)*-1.0


    with leg_2:
         
          K=st.number_input('Enter the strike price for second')
          premium=st.number_input('Enter the option price for second')
          option_type=st.selectbox('Option Type for second',options=['CE','PE'])
          position_type=st.selectbox('Position Type for second',options=['Long','Short'])
          if option_type=='CE' and position_type=='Long':
               payoff_2=call_payoff(sT,K,premium)
          
          elif option_type=='PE' and position_type=='Long':
               payoff_2=put_payoff(sT,K,premium)


          elif option_type=='CE' and position_type=='Short':
               payoff_2=call_payoff(sT,K,premium)*-1.0

          elif option_type=='PE' and position_type=='Short':
               payoff_2=put_payoff(sT,K,premium)*-1.0

    with leg_3:
         
          K=st.number_input('Enter the strike price for third')
          premium=st.number_input('Enter the option price for third')
          option_type=st.selectbox('Option Type for third',options=['CE','PE'])
          position_type=st.selectbox('Position Type for third',options=['Long','Short'])
          if option_type=='CE' and position_type=='Long':
               payoff_3=call_payoff(sT,K,premium)
          
          elif option_type=='PE' and position_type=='Long':
               payoff_3=put_payoff(sT,K,premium)


          elif option_type=='CE' and position_type=='Short':
               payoff_3=call_payoff(sT,K,premium)*-1.0

          elif option_type=='PE' and position_type=='Short':
               payoff_3=put_payoff(sT,K,premium)*-1.0

    payoff_final=payoff_1+payoff_2+payoff_3

    fig,ax=plt.subplots(figsize=(8,5))
    ax.spines['bottom'].set_position('zero')
     
    ax.plot(sT,payoff_final,label='Strategy Payoff',color='b')
    st.pyplot(fig)

    lot_size=st.number_input('Specify the lot size')

    submit=st.button('Show Max Profit')
    if submit:
         max_profit=max(payoff_final)
         st.write(f'The maxiumum profit is {max_profit*25*lot_size}')

    submit2=st.button('Show Max Loss')
    if submit2:
         max_loss=min(payoff_final)
         st.write(f'The maxiumum loss is {max_loss*25*lot_size}')

    
    submitted=st.button('Show maximum starting level')
    def get_max_starting_level():
         PR=np.where(payoff_final==max(payoff_final))
         highest_point=0.90*spot_rate+PR[0]
         st.write(f'The maximum profit zone begins from {highest_point}')
    if submitted:
         get_max_starting_level()

    
    submit3=st.button('Calculate probability of profit')
    S=st.number_input('Enter the spot rate')
    K_1=st.number_input('Enter the lower profit zone')
    K_2=st.number_input('Enter the upper profit zone')
    Time=st.number_input('Enter the days to expiry')
    T=Time/365
    r=0.04
    volatility=st.number_input('Enter the IV')
    vol=volatility/100
    def POP():
        d1_lower=(math.log(S/K_1)+(r+0.5*vol**2)*T)/(vol*math.sqrt(T))
        d2_lower=d1_lower-(vol*math.sqrt(T))

        d1_upper=(math.log(S/K_2)+(r+0.5*vol**2)*T)/(vol*math.sqrt(T))
        d2_upper=d1_upper-(vol*math.sqrt(T))

        POP=norm.cdf(d2_lower)-norm.cdf(d2_upper)
        st.write(f'The probability of profit is {POP*100}')
    if submit3:
         POP()
        
         

    
    
    submit4=st.button('Calculate breakeven level')
    def get_profit_zone():
         PR=np.where(payoff_final>0)
         profit_start=spot_rate*0.90+PR[0]
         st.write(f'The profit zone begins from {profit_start}')
    if submit4:
         get_profit_zone()

    submit5=st.button('Calculate payoff at any level')
    rate=st.number_input('Enter the rate for which you want the profit')
    def get_payoff_custom():
         payoff_level=np.where(payoff_final==rate)
         spot_level=spot_rate*0.90+payoff_level[0]
         st.write(f'The spot level is {spot_level}')
    if submit5:
         get_payoff_custom()

    

        

