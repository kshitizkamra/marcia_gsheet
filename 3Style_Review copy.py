import hmac
import streamlit as st
import pandas as pd
import numpy as np
import sys
import glob
import os
from sqlalchemy import create_engine
import altair as alt
import plotly.express as px
import datetime
import time
import math
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide",initial_sidebar_state='expanded')
st.cache_data.clear()
conn = st.connection("my_database")
db_data=conn.query("select * from final_data;")
db_sales_data=conn.query("select * from final_sales")
db_sales_data_for_side_filter=conn.query("select * from final_sales")
db_latlong=conn.query("select * from latlong")


st.title ("Style Review")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 0.5rem;
                    padding-right: 0.5rem;
                    line-height: 100%;
                    text-align: center;
                    font-size : 15px;
                    gap: 1rem;

                }
              .divider{
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
            }

                .box-font {
    font-size:14px !important;
    
}
 
            .value-font {
    font-size:15px !important;
    
}
                   </style>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.title('Filters')
    today = datetime.datetime.now()
    next_year = today.year + 1
    start_date = db_sales_data_for_side_filter['order_created_date'].min()
    end_date = db_sales_data_for_side_filter['order_created_date'].max()

    date_range = st.date_input(
    "Date Range",
    (start_date,end_date),
    start_date,
    end_date,
    format="MM.DD.YYYY",
    )

    db_channel=conn.query("select distinct channel from master;")
    channel_list = db_channel['channel'].values.tolist()
    channels = st.multiselect(
      "Channel",
      channel_list,
      channel_list,
    )

    db_seller=conn.query("select distinct channel_x,seller_id from final_sales;")
    db_seller=db_seller[(db_seller['channel_x'].isin(channels))]
    db_seller=db_seller.drop(['channel_x'],axis=1)
    db_seller=db_seller.drop_duplicates()
    seller_list = db_seller['seller_id'].values.tolist()
    seller = st.multiselect(
      "Seller_id",
      seller_list,
      seller_list,
    )

    db_gender=conn.query("select distinct gender,seller_id from final_sales;")
    db_gender=db_gender[(db_gender['seller_id'].isin(seller))]
    db_gender=db_gender.drop(['seller_id'],axis=1)
    db_gender=db_gender.drop_duplicates()
    gender_list = db_gender['gender'].values.tolist()
    genders = st.multiselect(
      "Gender",
      gender_list,
      gender_list,
    )

    db_brands=conn.query("select distinct brand,gender,seller_id from final_sales;")
    db_brands=db_brands[(db_brands['seller_id'].isin(seller))]
    db_brands=db_brands.drop(['seller_id'],axis=1)
    db_brands=db_brands.drop_duplicates()
    db_brands=db_brands[(db_brands['gender'].isin(genders))]
    db_brands=db_brands.drop(['gender'],axis=1)
    db_brands=db_brands.drop_duplicates()
    brands_list = db_brands['brand'].values.tolist()
    brands = st.multiselect(
      "Brands",
      brands_list,
      brands_list,
    )

    db_article_type=conn.query("select distinct article_type,brand from master")
    db_article_type=db_article_type[(db_article_type['brand'].isin(brands))]
    db_article_type=db_article_type.drop(['brand'],axis=1)
    db_article_type=db_article_type.drop_duplicates()
    article_type_list = db_article_type['article_type'].values.tolist()
    article_type = st.multiselect(
      "Article Types",
      article_type_list,
      article_type_list,
    )

    

try: 
    
  db_data=db_data[(db_data['order_created_date'].dt.date >= date_range[0]) & (db_data['order_created_date'].dt.date <=date_range[1] )]
  db_data=db_data[(db_data['channel'].isin(channels))]
  db_data=db_data[(db_data['seller_id'].isin(seller))]
  db_data=db_data[(db_data['gender'].isin(genders))]
  db_data=db_data[(db_data['brand'].isin(brands))]
  db_data=db_data[(db_data['article_type'].isin(article_type))]

  db_sales_data=db_sales_data[(db_sales_data['order_created_date'].dt.date >= date_range[0]) & (db_sales_data['order_created_date'].dt.date <=date_range[1] )]
  db_sales_data=db_sales_data[(db_sales_data['channel_x'].isin(channels))]
  db_sales_data=db_sales_data[(db_sales_data['seller_id'].isin(seller))]
  db_sales_data=db_sales_data[(db_sales_data['gender'].isin(genders))]
  db_sales_data=db_sales_data[(db_sales_data['brand'].isin(brands))]
  db_sales_data=db_sales_data[(db_sales_data['article_type'].isin(article_type))]

except:
    db_data=db_data
    db_sales_data=db_sales_data


db_data_forward=db_data[db_data['order_type']=='Forward']
db_data_reverse=db_data[db_data['order_type']=='Reverse']
db_sales_data=db_sales_data[db_sales_data['order_status']=='C']

db_vendor_style_code=db_data[['vendor_style_code','image_link','brand','gender','article_type','color','fabric','cost']]
db_vendor_style_code=db_vendor_style_code.drop_duplicates()
db_search_style_code=db_vendor_style_code['vendor_style_code'].drop_duplicates()
search_style_code_list = db_search_style_code.values.tolist()
search_style_code = st.multiselect(
      "Search/Select Style Code",
      search_style_code_list,
      placeholder="Search/Select Style Code",
      label_visibility='collapsed'
    )
if len(search_style_code)>0 :
   db_style_code=db_vendor_style_code[(db_vendor_style_code['vendor_style_code'].isin(search_style_code))]
   st.session_state['page_number'] = 1
else :
    db_style_code=db_vendor_style_code.copy()
db_style_code['order_count']=db_style_code['vendor_style_code'].map(db_sales_data['vendor_style_code'].value_counts())
db_style_code=db_style_code.sort_values('order_count',ascending=False)
db_style_code.reset_index(inplace=True)
db_style_code.drop(['index'],axis=1,inplace=True)
db_style_code.index +=1
db_style_code.fillna(0,inplace=True)

# db_sales_data=db_sales_data.drop(['order_release_id','sku_code_x','channel_y','sku_code_y','vendor_sku_code'],axis=1)
# db_sales_data['order_count']=1
total_pages=len(db_style_code)

if 'page_number' not in st.session_state:
   st.session_state['page_number'] = 1
else:
    page_number = st.session_state['page_number']


with st.container(border=True) :
      
  col1,col2=st.columns([4,1],vertical_alignment="bottom")
  with col2 :
      subcol1,subcol2,subcol3,subcol4=st.columns([2,3,3,2],vertical_alignment="bottom")

      with subcol1 :
          if st.button("⬅️", use_container_width=True):
              st.session_state['page_number'] -= 1 
              if st.session_state['page_number']==0 :
                  st.session_state['page_number']=total_pages
      with subcol4 :
          if st.button("➡️", use_container_width=True):
              st.session_state['page_number'] += 1 
              if st.session_state['page_number']==total_pages+1 :
                  st.session_state['page_number']=1
      with subcol2:
          page_number = st.number_input("",value=st.session_state['page_number'],min_value=1, max_value=total_pages)
          st.session_state['page_number']=page_number
      with subcol3:
          st.text("/"+str(total_pages))    
  with col1 :
      st.text(db_style_code.loc[st.session_state['page_number'],'vendor_style_code'])
      
  col1,col2=st.columns([0.85,2])

  with col1:
      with st.container(border=True):
          try:
              st.image(db_style_code.loc[st.session_state['page_number'],'image_link'], width=300)
          except: 
              st.text("Please check image url")
              
  with col2:
      subcol1,subcol2,subcol3,subcol4,subcol5=st.columns(5,gap="small")
      
      db_style_data=db_data[db_data['vendor_style_code']==db_style_code.loc[st.session_state['page_number'],'vendor_style_code']]
      orders=db_style_data['final_amount'].count()
      returns=db_style_data['returns'].sum()
      db_style_net_sales=db_style_data[db_style_data['returns']==0]
      value=db_style_net_sales['final_amount'].sum()
      db_style_data['order_count']=1
      
      with subcol1:
          with st.container(border=True):
              st.markdown('<p class="value-font"><b>Orders</b></p>', unsafe_allow_html=True)
              st.markdown('<p class="value-font">'+('{:,}'.format(round(orders),0))+'</p>', unsafe_allow_html=True)
              
      with subcol2:
          with st.container(border=True):
              st.markdown('<p class="value-font"><b>Returns</b></p>', unsafe_allow_html=True)
              st.markdown('<p class="value-font">'+('{:,}'.format(round(returns),0))+'</p>', unsafe_allow_html=True)

      with subcol3:
          with st.container(border=True):
              st.markdown('<p class="value-font"><b>Net Orders</b></p>', unsafe_allow_html=True)
              st.markdown('<p class="value-font">'+('{:,}'.format(round(orders-returns),0))+'</p>', unsafe_allow_html=True)

      with subcol4:
          with st.container(border=True):
              st.markdown('<p class="value-font"><b>Value</b></p>', unsafe_allow_html=True)
              st.markdown('<p class="value-font">'+('{:,}'.format(round(value),0))+'</p>', unsafe_allow_html=True)

      with subcol5:
          with st.container(border=True):
              st.markdown('<p class="value-font"><b>ASP</b></p>', unsafe_allow_html=True)
              try:
                  st.markdown('<p class="value-font">'+('{:,}'.format(round(value/(orders-returns)),0))+'</p>', unsafe_allow_html=True)
              except:
                  st.markdown('<p class="value-font"> 0 </p>', unsafe_allow_html=True)
      
      
      db_style_net_sales['order_created_date']=db_style_net_sales['order_created_date'].dt.date
      db_style_net_sales['order_count']=1
      db_style_net_sales['value']=db_style_net_sales['final_amount']

      with st.container(border=True):
            tab1,tab2=st.tabs(['Sales Trend','ASP-Retrun'])
            with tab1:
              # db_style_net_sales
              db_style_net_sales_graph=db_style_net_sales.groupby(['order_created_date']).agg({'order_count':'sum','final_amount':'sum','value':'mean'})
              
              fig, ax = plt.subplots(1, figsize=(16.7,5))
              
              ax.set_xlabel('Time')
              # ax.set_xticklabels('Date',rotation = 90)
              ax.set_ylabel('Sales Value',color='darkturquoise')
              
              ax.plot(db_style_net_sales_graph.index, db_style_net_sales_graph['final_amount'],color='darkturquoise')
              ax.tick_params(axis='y', labelcolor='darkturquoise')
              # fig.tight_layout()
              st.pyplot(fig)


            with tab2:
               
                db_asp_return=db_sales_data[db_sales_data['vendor_style_code']==db_style_code.loc[st.session_state['page_number'],'vendor_style_code']]
                
                db_asp_return['order_count']=1
                db_asp_return['price']=db_asp_return['final_amount']
                db_asp_return=db_asp_return.groupby(['price']).agg({'final_amount':'mean','order_count':'sum','returns':sum})
                db_asp_return['return%']=db_asp_return['returns']/db_asp_return['order_count'] 
                fig, ax = plt.subplots(1, figsize=(16.3,5))
                ax_2 = ax.twinx()
                ax.set_xlabel('ASP')
                # ax.set_xticklabels('Date',rotation = 90)
                ax.set_ylabel('Return%',color='darkturquoise')
                ax_2.set_ylabel('Orders',color='red')
                ax_2.plot(db_asp_return.index, db_asp_return['order_count'],color='red')
                ax_2.tick_params(axis='y', labelcolor='red')
                ax.plot(db_asp_return.index, db_asp_return['return%'],color='darkturquoise')
                ax.tick_params(axis='y', labelcolor='darkturquoise')
                # fig.tight_layout()
                st.pyplot(fig)
                 
              






            # with tab2:
            #     db_sales_latlong=db_style_net_sales.copy()
            #     db_sales_latlong=db_sales_latlong.groupby(['state']).agg({'final_amount':'sum'})
            #     db_sales_latlong.reset_index(inplace=True)
            #     size=db_sales_latlong['final_amount'].max()
            #     db_sales_latlong['amount']=db_sales_latlong['final_amount']/size*100000
            #     db_sales_latlong=db_sales_latlong.merge(db_latlong,left_on='state',right_on='state')
            #     st.map(db_sales_latlong, latitude='lat', longitude='lon',size='amount')

            # with tab3:
            #     st.subheader("Size Contribution")
            #     db_sales_brand=db_style_net_sales.copy()
            #     db_sales_brand=db_sales_brand.groupby(['size']).agg({'final_amount':'sum'})
            #     db_sales_brand.reset_index(inplace=True)

            #     fig=px.pie(db_sales_brand,values='final_amount',names='size',title=None)
            #     st.plotly_chart(fig,use_container_width=True)         

  
  col1,col2=st.columns([0.85,2],gap="small")
  db_style_data_display=pd.DataFrame()
  with col1:
      
          
          db_style_data_display=db_style_data.copy()
          db_style_data_display.drop(['total_actual_settlement'],axis=1,inplace=True)
          db_style_data_display.loc[db_style_data_display['returns']==1,'cost']=0
          db_style_data_display.loc[db_style_data_display['returns']==1,'customer_paid_amt']=0
          db_style_data_display.loc[db_style_data_display['returns']==1,'platform_fees']=0
          db_style_data_display.loc[db_style_data_display['returns']==1,'tcs_amount']=0
          db_style_data_display.loc[db_style_data_display['returns']==1,'tds_amount']=0
          db_style_data_display['total_actual_settlement']=db_style_data_display['customer_paid_amt']-db_style_data_display['platform_fees']-db_style_data_display['tcs_amount']-db_style_data_display['tds_amount']-db_style_data_display['shipping_fee']-db_style_data_display['pick_and_pack_fee']-db_style_data_display['fixed_fee']-db_style_data_display['payment_gateway_fee']-db_style_data_display['total_tax_on_logistics']

          db_style_data_display=db_style_data_display.groupby(['channel']).agg({'order_count':'sum','returns':'sum','total_actual_settlement':'sum','cost':'sum','order_created_date':'min'})
          db_style_data_display['Net_Sales']=db_style_data_display['order_count']-db_style_data_display['returns']
          db_style_data_display['COGS']=db_style_data_display['cost']
          db_style_data_display['P/L']=db_style_data_display['total_actual_settlement']-db_style_data_display['COGS']
          db_style_data_display['ROI']=db_style_data_display['P/L']/db_style_data_display['COGS']
          db_style_data_display['order_created_date']=db_style_data_display['order_created_date'].dt.date
          first_sale_date=db_style_data_display['order_created_date'].min()
          
          db_style_data_display['days']=(datetime.date.today()-first_sale_date).days
          db_style_data_display['ROS']=db_style_data_display['Net_Sales']/db_style_data_display['days']
          db_style_data_display.drop(['order_created_date','days','cost'],axis=1,inplace=True)
          db_style_data_display.rename(columns={'order_count':'Orders','returns':'Returns','total_actual_settlement':'Settlement'},inplace=True)
          db_style_data_display=db_style_data_display[['Orders','Returns','Net_Sales','Settlement','COGS','P/L','ROI','ROS']]
          db_style_data_display.reset_index(inplace=True)
          db_style_data_display.loc[len(db_style_data_display.index)]=['Total',db_style_data_display['Orders'].sum(),db_style_data_display['Returns'].sum(),db_style_data_display['Net_Sales'].sum(),db_style_data_display['Settlement'].sum(),db_style_data_display['COGS'].sum(),db_style_data_display['P/L'].sum(),db_style_data_display['P/L'].sum()/db_style_data_display['COGS'].sum(),db_style_data_display['ROS'].sum()]
          # db_style_data_display = db_style_data_display.style.format("{:.2}")
          db_style_data_display.set_index('channel',inplace=True)
          db_style_data_display_final=db_style_data_display.T
          
          st.markdown(db_style_data_display_final.style.format("{:,.7}").to_html(), unsafe_allow_html=True)
          # db_style_data_display


  with col2:
          with st.container(border=True):
            db_action_style_data=db_style_data_display.drop(['Total'])
            db_action_style_data.reset_index(inplace=True)
            total_channel=db_action_style_data['channel'].unique().tolist()
            tab=st.tabs(total_channel)
            tab_len=len(total_channel)
            db_styles_action=conn.query("select * from actions_upload;")
            db_actual_action=conn.query("select * from recommendation_upload")
            selling_price_list=conn.query("select distinct selling_price from recommendation_upload")
            selling_price_list=selling_price_list['selling_price'].values.tolist()
            pla_list=conn.query("select distinct pla from recommendation_upload")
            pla_list=pla_list['pla'].values.tolist()
            replenishment_list=conn.query("select distinct replenishment from recommendation_upload")
            replenishment_list=replenishment_list['replenishment'].values.tolist()
            
            for i in range(tab_len):
                with tab[i]:
                        db_styles_action_tab=db_styles_action[db_styles_action['channel']==total_channel[i]]
                        db_actual_action_tab=db_actual_action[db_styles_action['channel']==total_channel[i]]
                        db_action_style_data_tab=db_action_style_data[db_action_style_data['channel']==total_channel[i]]
                        db_action_style_data_tab['return %']=db_action_style_data_tab['Returns']/db_action_style_data_tab['Orders']
                        db_styles_action_tab=db_styles_action_tab[db_styles_action_tab['brand']==db_style_code.loc[st.session_state['page_number'],'brand']]
                        db_styles_action_tab=db_styles_action_tab[db_styles_action_tab['gender']==db_style_code.loc[st.session_state['page_number'],'gender']]
                        db_styles_action_tab=db_styles_action_tab[db_styles_action_tab['article_type']==db_style_code.loc[st.session_state['page_number'],'article_type']]
                        if db_action_style_data_tab['ROS'].sum()>=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='ros','a'].sum() :
                            ros_action="A"
                        elif db_action_style_data_tab['ROS'].sum()>=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='ros','b'].sum() :
                            ros_action="B"
                        else :
                            ros_action="C"
                       
                        if db_action_style_data_tab['ROI'].sum()>=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='roi','a'].sum() :
                            roi_action="A"
                        elif db_action_style_data_tab['ROI'].sum()>=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='roi','b'].sum() :
                            roi_action="B"
                        else :
                            roi_action="C"

                        if db_action_style_data_tab['return %'].sum()<=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='return %','a'].sum() :
                            return_action="A"
                        elif db_action_style_data_tab['return %'].sum()<=db_styles_action_tab.loc[db_styles_action_tab['metrics']=='return %','b'].sum() :
                            return_action="B"
                        else :
                            return_action="C"
                        # db_sales_data.loc[db_sales_data['order_status']=='F','final_amount'].sum()
                        # ros_action
                        # roi_action
                        # return_action

                        
                        
                        db_actual_action_tab=db_actual_action_tab[(db_actual_action_tab['ros']==ros_action)&(db_actual_action_tab['roi']==roi_action)&(db_actual_action_tab['return %']==return_action)]  
                        db_actual_action_tab.reset_index(inplace=True)
                        with st.container(border=True):
                            subcolm1,subcolm2,subcol3=st.columns([1,3,1])    
                            with subcolm1:
                              st.markdown('<p class="small-font">Selling Price</p>', unsafe_allow_html=True)
                            with subcolm2:
                               action_sp=st.selectbox("Select",selling_price_list,index=selling_price_list.index(db_actual_action_tab['selling_price'][0]),label_visibility='collapsed')
                           
                        with st.container(border=True):
                            subcolm1,subcolm2,subcol3=st.columns([1,3,1])
                            with subcolm1:
                              st.markdown('<p class="small-font">PLA</p>', unsafe_allow_html=True)
                            with subcolm2:
                              
                              action_pla=st.selectbox("Select",pla_list,index=pla_list.index(db_actual_action_tab['pla'][0]),label_visibility='collapsed')   
                        
                        with st.container(border=True):
                            subcolm1,subcolm2,subcol3=st.columns([1,3,1])
                            with subcolm1:
                              st.markdown('<p class="small-font">Replenishment</p>', unsafe_allow_html=True)
                            with subcolm2:
                              
                              action_replenishment=st.selectbox("Select",replenishment_list,index=replenishment_list.index(db_actual_action_tab['replenishment'][0]),label_visibility='collapsed')   