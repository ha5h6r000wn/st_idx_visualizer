import streamlit as st

from visualization.stg_idx import generate_stg_idx_charts
from visualization.style import generate_style_charts

st.set_page_config(
    page_title='股票交易咨询权益研究',
    page_icon='📊',
    layout='wide',
)

st.title('股票交易咨询权益研究')

# 使用sidebar来选择页面
page = st.sidebar.radio('请选择', ['策略指数', '风格研判'])

# 根据选择显示对应的内容
if page == '策略指数':
    generate_stg_idx_charts()
elif page == '风格研判':
    generate_style_charts()
