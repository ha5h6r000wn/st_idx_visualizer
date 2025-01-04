import streamlit as st

from visualization.stg_idx import generate_stg_idx_charts
from visualization.style import generate_style_charts

st.set_page_config(
    page_title='股票交易咨询权益研究',
    page_icon='📊',
    layout='wide',
)

st.title('股票交易咨询权益研究')

# 使用tabs来切换页面
tab1, tab2 = st.tabs(['策略指数', '风格研判'])

with tab1:
    generate_stg_idx_charts()

with tab2:
    generate_style_charts()
