# Packages
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime
import hashlib

# Columns defined
num_cols = ['Video publish time','Comments added','Shares','Dislikes','Likes','Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration','Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)','avg_view_duration','engagement_ratio','views/sub_gained']
seleted_aggregates = ['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'avg_view_duration', 'engagement_ratio','views/sub_gained']

selected_aggregate_coloumns = ['Video title','Published Date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed','avg_view_duration', 'engagement_ratio','views/sub_gained']


# Helper functions

def style_negative(v,props=''):
    try:
        return props if v < 0 else None
    except:
        pass
    
def style_possitive(v,props=''):
    try:
        return props if v > 0 else None
    except:
        pass

def df_to_pct(x):
    if(isinstance(x, (float, int))):
        return f'{x:.2%}'
    else:
        return x
    
    
def audience_from(x):
    if(x == 'US'):
        return 'USA'
    elif(x == 'IN'):
        return 'India'
    else:
        return 'Others'
# Setting cache
@st.cache_data
# Loading data
def load_data():
    df_ag_video = pd.read_csv('ag_mterics_video.csv')
    # Formatted Column Name
    df_ag_video.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                      'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                      'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']
    
    
    # Formatting Columns
    
    # Time Format
    df_ag_video['Video publish time'] = pd.to_datetime(df_ag_video['Video publish time'],format="%b %d, %Y")
    # Into minute and secs
    df_ag_video['Average view duration'] = df_ag_video['Average view duration'].apply( lambda x: datetime.strptime(x,'%H:%M:%S') )
    # New Columns
    # Average view duration in secs
    df_ag_video['avg_view_duration'] = df_ag_video['Average view duration'].apply( lambda x: x.second + x.minute * 60 + x.hour * 3600 )
    # Engagement ration : comments + shares + likes + shares / view
    df_ag_video['engagement_ratio'] =  ( df_ag_video['Comments added'] + df_ag_video['Shares'] + df_ag_video['Dislikes'] + df_ag_video['Likes'] ) / df_ag_video['Views']
    # Subscription gained against views
    df_ag_video['views/sub_gained'] = df_ag_video['Views'] / df_ag_video['Subscribers gained']
    # Sorting value Desc published time
    df_ag_video.sort_values('Video publish time',ascending=False,inplace=True)
    
    # Metrics by country
    df_ag_country  = pd.read_csv('ag_mterics_by_country.csv')
    # Comments 
    df_ag_comments = pd.read_csv('ag_mterics_video.csv')
    # Performance over time
    df_ag_time = pd.read_csv('video_performance.csv')
    # Format column
    df_ag_time['Date'] = pd.to_datetime(df_ag_time['Date'],format='mixed')
    # df_ag_video_save = df_ag_video.copy()
    # df_ag_video_save.set_index('Video',inplace=True)
    # df_ag_video_save.to_csv('ag_mterics_video.csv')
    # st.dataframe(df_ag_time)
    
    return df_ag_video, df_ag_country, df_ag_comments, df_ag_time 
    # print(df_ag_video['Video publish time'])
    
#create dataframes from the function 
df_ag_video, df_ag_country, df_ag_comments, df_ag_time = load_data()
# Database Connection 
# conn = st.connection('mysql', type='sql')

# Hashing Algorithm
# text = "Hello World"
# hash_object = hashlib.md5(text.encode())
# st.write(hash_object.hexdigest())

# Engineering Data
df_ag_video_copy = df_ag_video.copy()
df_ag_video_copy_nums = df_ag_video_copy[num_cols]

metrics_date_12_mon = df_ag_video_copy['Video publish time'].max() - pd.DateOffset(months =24)
median_agg = df_ag_video_copy_nums[df_ag_video_copy_nums['Video publish time'] >=  metrics_date_12_mon ].drop(columns=['Video publish time','Average view duration']).median()
#Just numeric columns 

df_ag_video_copy_nums_med = df_ag_video_copy_nums.loc[:,(df_ag_video_copy_nums.columns != 'Video publish time') & (df_ag_video_copy_nums.columns != 'Average view duration') ].div(median_agg)



# Dashboard 

dashboard_sidebar = st.sidebar

menu_selected = dashboard_sidebar.selectbox('Aggregate or Individual Video',['Aggregate Metrics','Individual Video Analysis'])


if(menu_selected == 'Aggregate Metrics'):
    st.header("Shebin KP Aggregate Metrics")

    df_ag_metrics = df_ag_video_copy[seleted_aggregates]
    
    metric_date_6_mon = df_ag_metrics['Video publish time'].max() - pd.DateOffset(months=24)
    metric_date_12_mon = df_ag_metrics['Video publish time'].max() - pd.DateOffset(months=48)
    metric_date_6_mon_median = df_ag_metrics[df_ag_metrics['Video publish time'] >= metric_date_6_mon].median()
    metric_date_12_mon_median = df_ag_metrics[df_ag_metrics['Video publish time'] >= metric_date_12_mon].median()
    
    
    col1, col2, col3, col4, col5 = st.columns(5)


    columns = [col1, col2, col3, col4, col5]
    
    count = 0
    for i in metric_date_6_mon_median.index:
        with columns[count]:
            if((i != 'Video publish time' ) ):
                delta = (metric_date_6_mon_median[i] - metric_date_12_mon_median[i])/metric_date_12_mon_median[i]
                st.metric(label=i, value= round(metric_date_6_mon_median[i],1),delta="{:.2%}".format(delta))
                count += 1
                if count >= 5:
                    count = 0
                    

    df_ag_video_copy['Published Date'] = df_ag_video_copy['Video publish time'].apply(lambda x:x.date())
    df_ag_video_final =  df_ag_video_copy.loc[:,selected_aggregate_coloumns]
    
    # This is has problem with axis
    # df_ag_video_final_num = df_ag_video_copy.apply(lambda x :   x if (df_ag_video_copy.dtype == 'float64' or df_ag_video_copy.dtype == 'int64') else None , axis=0 ).dropna(axis=0)
    
    # select_dtypes is faster slick and better 
    df_ag_video_final_num = df_ag_video_copy.select_dtypes(include=['float64', 'int64'])
    df_ag_video_final_num_median = df_ag_video_final_num.index.to_list()
   
    
    st.dataframe(df_ag_video_final.style.hide().applymap(style_negative,props='color:red;').applymap(style_possitive,props='color:green;').format(df_to_pct))
    
elif(menu_selected == 'Individual Video Analysis'):
    
    st.header("Individual Video Analysis")
    videos = tuple(df_ag_video['Video title'])
    video_select = st.selectbox('Select Video', videos)
    st.subheader("Country based analysis")
    df_selected_video = df_ag_country[df_ag_country['Video Title'] == video_select]
    df_selected_video['From'] = df_selected_video['Country Code'].apply(audience_from)
    df_selected_video.sort_values('Is Subscribed', ascending=False , inplace= True)   
    # st.write(video_select)
    st.bar_chart(df_selected_video, x="Is Subscribed", y="Views", color="From", horizontal=True , height=400 )

  
    
    