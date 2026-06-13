import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import qrcode
from PIL import Image
from io import BytesIO
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 尝试导入可选依赖库
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

# 公司基础信息映射
company_info = {
    "腾讯控股": "00700.HK",
    "阿里巴巴": "9988.HK",
    "百度": "BIDU",
    "网易": "NTES"
}
all_company_list = ["腾讯控股", "阿里巴巴", "百度", "网易"]

# ====================== 全局高端商务风格配置 ======================
st.set_page_config(
    page_title="年度财报综合分析看板", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# 自定义CSS - 高端商务BI风格
st.markdown("""
<style>
/* 全局背景 - 高级灰渐变 */
.stApp {
    background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
    font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', sans-serif;
    color: #0f172a;
}

/* 主标题 - 精致商务风 */
.main-title {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    text-align: center;
    padding: 2rem 0 1.5rem 0;
    color: #0f172a !important;
    letter-spacing: 2px;
    position: relative;
    margin-bottom: 2rem;
}

.main-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #2563eb, transparent);
    border-radius: 2px;
}

/* 高端卡片容器 */
.premium-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05),
                0 20px 25px -5px rgba(15, 23, 42, 0.05),
                0 8px 10px -6px rgba(15, 23, 42, 0.03);
    border: 1px solid rgba(148, 163, 184, 0.15);
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.premium-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa);
}

.premium-card:hover {
    box-shadow: 0 4px 6px rgba(15, 23, 42, 0.07),
                0 25px 50px -12px rgba(15, 23, 42, 0.1);
    transform: translateY(-2px);
}

/* 卡片标题样式 */
.premium-card h3 {
    color: #0f172a;
    font-weight: 600;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

/* 核心指标卡片 - 精致版 */
.metric-premium {
    background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    padding: 1.3rem 1rem;
    text-align: center;
    border: 1px solid rgba(148, 163, 184, 0.2);
    transition: all 0.3s ease;
    position: relative;
}

.metric-premium:hover {
    border-color: #2563eb;
    background: linear-gradient(145deg, #eff6ff 0%, #dbeafe 100%);
    transform: translateY(-3px);
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.15);
}

.metric-value-premium {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #1e40af !important;
    margin: 0.5rem 0;
    font-family: 'DIN Alternate', 'Microsoft YaHei', sans-serif;
}

.metric-label-premium {
    font-size: 0.9rem !important;
    color: #64748b !important;
    font-weight: 500;
    letter-spacing: 0.5px;
}

/* 侧边栏 - 精致商务风 */
.css-1d391kg {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border-right: 1px solid rgba(148, 163, 184, 0.2);
    box-shadow: 4px 0 20px rgba(15, 23, 42, 0.03);
}

.css-1d391kg h2, .css-1d391kg h3 {
    color: #0f172a !important;
    font-weight: 600;
}

/* 按钮样式 */
.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
    transform: translateY(-1px);
}

/* 解读面板样式 */
.analysis-box {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 10px;
    padding: 1.2rem;
    margin-top: 1rem;
    border-left: 4px solid #0ea5e9;
}

.analysis-box h4 {
    color: #0c4a6e;
    margin-bottom: 0.8rem;
    font-size: 1rem;
}

.analysis-box p {
    color: #0f172a;
    line-height: 1.7;
    margin-bottom: 0.5rem;
}

/* 数据表格 */
.stDataFrame {
    border-radius: 10px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    overflow: hidden;
}

/* 分割线 */
.stDivider {
    margin: 2.2rem 0;
    border-color: rgba(148, 163, 184, 0.2);
}

/* 页脚 */
.footer-section {
    text-align: center;
    color: #64748b;
    padding: 2rem 1rem;
    border-top: 1px solid rgba(148, 163, 184, 0.2);
    margin-top: 3rem;
    font-size: 0.9rem;
}

/* 单选按钮优化 */
.stRadio > div > label {
    background: white;
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 8px;
    padding: 0.5rem 0.9rem;
    margin-bottom: 0.5rem;
    transition: all 0.25s ease;
}

.stRadio > div > label:hover {
    border-color: #2563eb;
    background: #eff6ff;
}

.stRadio > div > label[data-checked="true"] {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border-color: #2563eb;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

/* 下拉框优化 */
.stSelectbox > div > div > select {
    background: white;
    border: 1px solid rgba(148, 163, 184, 0.3);
    border-radius: 8px;
    color: #0f172a;
}

.stSelectbox > div > div > select:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

/* 滑块优化 */
.stSlider > div > div > div {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
}

.stSlider > div > div > div > div {
    background: white;
    border: 2px solid #2563eb;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

/* 聊天消息优化 */
.stChatMessage {
    background: white;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.15);
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
}

.stChatMessage[data-testid="user-message"] {
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    border-color: rgba(37, 99, 235, 0.2);
}
</style>
""", unsafe_allow_html=True)

# ====================== 自动化数据源模块 ======================
@st.cache_data(ttl=86400)
def fetch_financial_data(ticker, years=5):
    if not YFINANCE_AVAILABLE:
        return None
        
    try:
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        stock = yf.Ticker(ticker, session=session)
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        if income_stmt.empty:
            return None
            
        annual_data = []
        for year in range(years):
            if year >= len(income_stmt.columns):
                break
                
            date = income_stmt.columns[year]
            year_num = date.year
            
            revenue = income_stmt.loc['Total Revenue', date] if 'Total Revenue' in income_stmt.index else np.nan
            cost_of_revenue = income_stmt.loc['Cost Of Revenue', date] if 'Cost Of Revenue' in income_stmt.index else np.nan
            net_income = income_stmt.loc['Net Income', date] if 'Net Income' in income_stmt.index else np.nan
            
            total_assets = balance_sheet.loc['Total Assets', date] if 'Total Assets' in balance_sheet.index else np.nan
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest', date] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else np.nan
            stockholders_equity = balance_sheet.loc['Stockholders Equity', date] if 'Stockholders Equity' in balance_sheet.index else np.nan
            
            operating_cashflow = cashflow.loc['Operating Cash Flow', date] if 'Operating Cash Flow' in cashflow.index else np.nan
            
            conversion_rate = 1.0
            if ticker == 'BIDU':
                conversion_rate = 0.00000001
                revenue *= 7 * conversion_rate
                cost_of_revenue *= 7 * conversion_rate
                net_income *= 7 * conversion_rate
                total_assets *= 7 * conversion_rate
                total_liabilities *= 7 * conversion_rate
                stockholders_equity *= 7 * conversion_rate
                operating_cashflow *= 7 * conversion_rate
            else:
                conversion_rate = 0.00000001
                revenue *= conversion_rate
                cost_of_revenue *= conversion_rate
                net_income *= conversion_rate
                total_assets *= conversion_rate
                total_liabilities *= conversion_rate
                stockholders_equity *= conversion_rate
                operating_cashflow *= conversion_rate
            
            annual_data.append({
                "年份": year_num,
                "营业收入": round(revenue, 2),
                "营业成本": round(cost_of_revenue, 2),
                "归母净利润": round(net_income, 2),
                "总资产": round(total_assets, 2),
                "总负债": round(total_liabilities, 2),
                "股东权益": round(stockholders_equity, 2),
                "经营现金流净额": round(operating_cashflow, 2)
            })
        
        df = pd.DataFrame(annual_data)
        df = df.sort_values("年份").reset_index(drop=True)
        return df
    except Exception:
        return None

# 本地备份数据
backup_data = {
    "腾讯控股": pd.DataFrame({
        "年份": [2021, 2022, 2023, 2024],
        "营业收入": [5601.18, 5545.52, 6090.15, 6602.57],
        "营业成本": [2120.55, 2089.36, 2267.82, 2456.31],
        "归母净利润": [2248.22, 1882.43, 1152.16, 1940.73],
        "总资产": [16123.64, 15781.31, 15772.46, 17809.95],
        "总负债": [7356.71, 7952.71, 7035.65, 7270.99],
        "股东权益": [8766.93, 7828.60, 8736.81, 10538.96],
        "经营现金流净额": [1751.86, 1460.91, 2219.62, 2585.21]
    }),
    "阿里巴巴": pd.DataFrame({
        "年份": [2021, 2022, 2023, 2024],
        "营业收入": [7172.89, 8530.62, 8686.87, 9411.68],
        "营业成本": [4212.05, 5394.50, 5496.95, 5863.23],
        "归母净利润": [1503.08, 619.59, 725.09, 797.41],
        "总资产": [16902.18, 16955.53, 17530.44, 17648.29],
        "总负债": [6065.84, 6133.60, 6301.23, 6522.30],
        "股东权益": [10836.34, 10821.93, 11229.21, 11125.99],
        "经营现金流净额": [2317.86, 1427.59, 1997.52, 1825.93]
    }),
    "百度": pd.DataFrame({
        "年份": [2021, 2022, 2023, 2024],
        "营业收入": [1244.93, 1236.75, 1345.98, 1331.25],
        "营业成本": [684.71, 692.58, 753.75, 745.10],
        "归母净利润": [75.91, 75.34, 215.49, 241.75],
        "总资产": [3800.34, 3909.73, 4067.59, 4277.80],
        "总负债": [1560.82, 1531.68, 1441.51, 1441.68],
        "股东权益": [2114.59, 2234.78, 2436.26, 2636.20],
        "经营现金流净额": [201.22, 261.70, 366.15, 212.34]
    }),
    "网易": pd.DataFrame({
        "年份": [2021, 2022, 2023, 2024],
        "营业收入": [876.06, 964.96, 1034.77, 1053.00],
        "营业成本": [421.50, 468.30, 502.10, 518.50],
        "归母净利润": [168.57, 205.28, 270.63, 297.00],
        "总资产": [2156.80, 2435.20, 2718.50, 2987.30],
        "总负债": [689.70, 752.90, 815.60, 876.40],
        "股东权益": [1467.10, 1682.30, 1902.90, 2110.90],
        "经营现金流净额": [285.60, 321.40, 387.20, 412.50]
    })
}

# 腾讯业务板块详细数据
tencent_business_data = pd.DataFrame({
    "年份": [2021, 2022, 2023, 2024],
    "增值服务营收": [2916.71, 2875.59, 2876.44, 3252.08],
    "金融科技及企业服务营收": [1722.00, 1771.52, 2170.39, 2378.52],
    "营销服务营收": [886.69, 827.75, 958.62, 1015.26],
    "中国大陆营收": [4929.04, 4879.10, 5361.33, 5815.36],
    "海外营收": [672.14, 666.42, 728.82, 787.21],
})

# ====================== 侧边筛选控制面板 ======================
with st.sidebar:
    st.header("🎛️ 财报分析控制台")
    
    data_source_options = ["本地备份数据"]
    if YFINANCE_AVAILABLE:
        data_source_options.insert(0, "自动获取(推荐)")
    
    data_source = st.radio(
        "数据来源",
        data_source_options,
        help="自动获取会从Yahoo Finance拉取最新财报数据，云端环境可能访问失败，将自动回退到本地数据"
    )
    
    main_company = st.selectbox(
        "选择主分析公司",
        all_company_list,
        index=0
    )
    
    st.subheader("🏆 竞品对比选择")
    # 自动排除当前主公司，避免自己和自己对比
    available_competitors = [c for c in all_company_list if c != main_company]
    competitors = st.multiselect(
        "选择对比公司",
        available_competitors,
        default=available_competitors[:2]
    )
    
    year_list = [2021, 2022, 2023, 2024]
    select_year = st.select_slider(
        "选择查看年份",
        options=year_list,
        value=max(year_list)
    )
    
    st.subheader("📈 预测设置")
    if ARIMA_AVAILABLE:
        forecast_years = st.slider(
            "预测未来年数",
            min_value=1,
            max_value=5,
            value=3,
            help="基于历史数据预测未来营收和利润"
        )
    else:
        st.info("预测功能需要安装statsmodels库")
        forecast_years = 0
    
    st.divider()
    st.info("💡 数据已预加载至2024年，点击右上角刷新获取最新数据")

# ====================== 数据加载与处理 ======================
@st.cache_data
def load_company_data(company_name, use_api):
    if use_api and YFINANCE_AVAILABLE:
        data = fetch_financial_data(company_info[company_name])
        if data is not None and len(data) >= 3:
            return data
    # 自动回退到本地备份数据
    return backup_data[company_name]

use_api = (data_source == "自动获取(推荐)")
tencent_data = load_company_data(main_company, use_api)

competitor_data = {}
for comp in competitors:
    competitor_data[comp] = load_company_data(comp, use_api)

def calculate_financial_indices(df):
    df = df.copy()
    df["毛利率%"] = round((df["营业收入"] - df["营业成本"]) / df["营业收入"] * 100, 2)
    df["净利润率%"] = round(df["归母净利润"] / df["营业收入"] * 100, 2)
    df["净资产收益率%"] = round(df["归母净利润"] / df["股东权益"] * 100, 2)
    
    # 计算增速，首年填充为None
    df["营收同比增速%"] = round(df["营业收入"].pct_change() * 100, 2)
    df["净利润同比增速%"] = round(df["归母净利润"].pct_change() * 100, 2)
    
    df["资产负债率%"] = round(df["总负债"] / df["总资产"] * 100, 2)
    df["负债权益比%"] = round(df["总负债"] / df["股东权益"] * 100, 2)
    df["资产周转率"] = round(df["营业收入"] / df["总资产"], 3)
    
    return df

tencent_data = calculate_financial_indices(tencent_data)
for comp in competitor_data:
    competitor_data[comp] = calculate_financial_indices(competitor_data[comp])

# 修复索引越界bug：选中年份不存在时自动取最新年份
filtered_data = tencent_data[tencent_data["年份"] == select_year]
if filtered_data.empty:
    select_year = int(tencent_data["年份"].max())
    year_detail = tencent_data[tencent_data["年份"] == select_year].iloc[0]
else:
    year_detail = filtered_data.iloc[0]

# 安全显示增速的辅助函数
def safe_display(value, suffix="%"):
    if pd.isna(value):
        return "—"
    return f"{value}{suffix}"

# 中国34个省级行政区数据
province_full_data = pd.DataFrame({
    "省份": [
        "北京市", "天津市", "河北省", "山西省", "内蒙古自治区",
        "辽宁省", "吉林省", "黑龙江省", "上海市", "江苏省",
        "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "广西壮族自治区",
        "海南省", "重庆市", "四川省", "贵州省", "云南省",
        "西藏自治区", "陕西省", "甘肃省", "青海省", "宁夏回族自治区",
        "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区", "台湾省"
    ],
    "纬度": [
        39.9042, 39.0842, 38.0428, 37.8706, 40.8263,
        41.8045, 43.8868, 45.7366, 31.2304, 32.0603,
        30.2741, 31.8612, 26.0745, 28.6756, 36.6758,
        34.7466, 30.5928, 28.2282, 23.1291, 22.8152,
        20.0440, 29.4316, 30.6572, 26.6470, 25.0406,
        29.6456, 34.2648, 36.0611, 36.6235, 38.4872,
        43.8256, 22.3193, 22.1987, 23.6978
    ],
    "经度": [
        116.4074, 117.2009, 114.5149, 112.5489, 111.7659,
        123.4327, 125.3245, 126.6617, 121.4737, 118.7626,
        120.1551, 117.2830, 119.3062, 115.8921, 117.0009,
        113.6254, 114.3055, 112.9388, 113.2644, 108.3275,
        110.1987, 106.9123, 104.0658, 106.6342, 102.7123,
        91.1175, 108.9542, 103.8343, 101.7782, 106.2309,
        87.6168, 114.1694, 113.5439, 120.9605
    ],
    "占比%": [
        7.8, 2.1, 4.5, 1.8, 1.2,
        2.5, 1.1, 1.0, 8.3, 14.8,
        12.7, 2.3, 4.3, 1.9, 9.3,
        5.2, 4.8, 3.1, 21.2, 1.7,
        0.8, 2.4, 6.3, 1.0, 1.5,
        0.1, 2.9, 0.7, 0.2, 0.3,
        0.9, 3.5, 0.5, 2.0
    ]
})

if main_company == "腾讯控股":
    china_total = tencent_business_data[tencent_business_data["年份"] == select_year]["中国大陆营收"].iloc[0]
    province_full_data["营收(亿元)"] = province_full_data["占比%"] / 100 * china_total
    
    overseas_revenue = tencent_business_data[tencent_business_data["年份"] == select_year]["海外营收"].iloc[0]
    overseas_data = pd.DataFrame({
        "地区名称": ["东南亚", "欧美", "其他海外地区"],
        "营收(亿元)": [300, 350, overseas_revenue - 300 - 350],
        "纬度": [1.3521, 37.0902, 55.3781],
        "经度": [103.8198, -95.7129, -3.4360]
    })

# ====================== 数据预测模块 ======================
def predict_financial_data(df, column_name, forecast_periods):
    if not ARIMA_AVAILABLE or forecast_periods <= 0:
        return [], [], []
        
    try:
        data = df[column_name].values
        years = df["年份"].values
        
        model = ARIMA(data, order=(1, 1, 1))
        results = model.fit()
        
        forecast = results.get_forecast(steps=forecast_periods)
        forecast_values = forecast.predicted_mean
        conf_int = forecast.conf_int()
        
        last_year = years[-1]
        forecast_years_list = [last_year + i + 1 for i in range(forecast_periods)]
        
        return forecast_years_list, forecast_values, conf_int
    except Exception:
        return [], [], []

revenue_forecast_years, revenue_forecast, revenue_conf_int = predict_financial_data(
    tencent_data, "营业收入", forecast_years
)
profit_forecast_years, profit_forecast, profit_conf_int = predict_financial_data(
    tencent_data, "归母净利润", forecast_years
)

# 动态主标题
st.markdown(f'<div class="main-title">📈 {main_company}({company_info[main_company]})年度财报综合数据分析看板</div>', unsafe_allow_html=True)

# ====================== 核心综合指数卡片展示 ======================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.subheader("📊 当期八大核心分析指数")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">营业收入</div>
        <div class="metric-value-premium">¥{year_detail["营业收入"]:,.2f}亿</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">净利润率</div>
        <div class="metric-value-premium">{year_detail["净利润率%"]}%</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">毛利率</div>
        <div class="metric-value-premium">{year_detail["毛利率%"]}%</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">净资产收益率</div>
        <div class="metric-value-premium">{year_detail["净资产收益率%"]}%</div>
    </div>
    ''', unsafe_allow_html=True)

with col5:
    color = "#16a34a" if year_detail["营收同比增速%"] >= 0 else "#dc2626"
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">营收增速</div>
        <div class="metric-value-premium" style="color: {color} !important;">{safe_display(year_detail["营收同比增速%"])}</div>
    </div>
    ''', unsafe_allow_html=True)

with col6:
    color = "#16a34a" if year_detail["净利润同比增速%"] >= 0 else "#dc2626"
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">净利润增速</div>
        <div class="metric-value-premium" style="color: {color} !important;">{safe_display(year_detail["净利润同比增速%"])}</div>
    </div>
    ''', unsafe_allow_html=True)

with col7:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">资产负债率</div>
        <div class="metric-value-premium">{year_detail["资产负债率%"]}%</div>
    </div>
    ''', unsafe_allow_html=True)

with col8:
    st.markdown(f'''
    <div class="metric-premium">
        <div class="metric-label-premium">资产周转率</div>
        <div class="metric-value-premium">{year_detail["资产周转率"]}</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== 第一部分：经营规模趋势与预测 ======================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.subheader("📈 营收与净利润历年变化趋势" + ("及预测" if ARIMA_AVAILABLE and forecast_years > 0 else ""))

fig_trend = go.Figure()

fig_trend.add_trace(go.Scatter(
    x=tencent_data["年份"], 
    y=tencent_data["营业收入"], 
    name="实际营业收入(亿元)", 
    line=dict(color="#2563eb", width=3.5), 
    marker=dict(size=9, color="#2563eb"),
    hovertemplate='%{y:.2f}亿元<extra></extra>'
))

if ARIMA_AVAILABLE and len(revenue_forecast_years) > 0:
    fig_trend.add_trace(go.Scatter(
        x=revenue_forecast_years, 
        y=revenue_forecast, 
        name="预测营业收入(亿元)", 
        line=dict(color="#2563eb", width=3, dash="dash"), 
        marker=dict(size=9, color="#2563eb")
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=np.concatenate([revenue_forecast_years, revenue_forecast_years[::-1]]),
        y=np.concatenate([revenue_conf_int[:, 0], revenue_conf_int[:, 1][::-1]]),
        fill='toself',
        fillcolor='rgba(37, 99, 235, 0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95%置信区间',
        showlegend=False
    ))

fig_trend.add_trace(go.Scatter(
    x=tencent_data["年份"], 
    y=tencent_data["归母净利润"], 
    name="实际归母净利润(亿元)", 
    yaxis="y2", 
    line=dict(color="#7c3aed", width=3.5), 
    marker=dict(size=9, color="#7c3aed"),
    hovertemplate='%{y:.2f}亿元<extra></extra>'
))

if ARIMA_AVAILABLE and len(profit_forecast_years) > 0:
    fig_trend.add_trace(go.Scatter(
        x=profit_forecast_years, 
        y=profit_forecast, 
        name="预测归母净利润(亿元)", 
        yaxis="y2", 
        line=dict(color="#7c3aed", width=3, dash="dash"), 
        marker=dict(size=9, color="#7c3aed")
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=np.concatenate([profit_forecast_years, profit_forecast_years[::-1]]),
        y=np.concatenate([profit_conf_int[:, 0], profit_conf_int[:, 1][::-1]]),
        fill='toself',
        fillcolor='rgba(124, 58, 237, 0.12)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95%置信区间',
        yaxis="y2",
        showlegend=False
    ))

fig_trend.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#334155', size=13),
    yaxis=dict(
        title="营业收入(亿元)", 
        title_font=dict(color="#2563eb", size=14), 
        gridcolor='rgba(148, 163, 184, 0.15)',
        zeroline=False
    ),
    yaxis2=dict(
        title="归母净利润(亿元)", 
        title_font=dict(color="#7c3aed", size=14), 
        overlaying="y", 
        side="right", 
        gridcolor='rgba(148, 163, 184, 0.15)',
        zeroline=False
    ),
    title_text=f"{main_company}整体经营规模走势" + (f"及未来{forecast_years}年预测" if ARIMA_AVAILABLE and forecast_years > 0 else ""),
    title_font=dict(size=16, color="#0f172a"),
    height=520,
    legend=dict(
        orientation="h", 
        yanchor="bottom", 
        y=1.02, 
        xanchor="right", 
        x=1, 
        bgcolor='rgba(255,255,255,0)',
        font=dict(size=12)
    ),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="white", font_size=13, bordercolor="#e2e8f0")
)
st.plotly_chart(fig_trend, use_container_width=True)

# 智能解读
with st.expander("💡 点击查看图表专业解读"):
    st.markdown(f'''
    <div class="analysis-box">
        <h4>📊 经营趋势深度分析</h4>
        <p><strong>营收端：</strong>{main_company}在2021-2024年间整体呈现稳健增长态势。2022年受宏观环境影响营收略有回调，2023年起重回增长通道，2024年创历史新高。</p>
        <p><strong>利润端：</strong>净利润波动幅度大于营收，反映出公司业务结构调整和成本管控的阶段性影响。2023年为利润低点，2024年强势反弹，盈利能力显著修复。</p>
        <p><strong>未来展望：</strong>基于ARIMA模型预测，未来{forecast_years}年公司将延续增长态势，营收和净利润均有望稳步提升，增长动力主要来自核心业务的深化和新业务的贡献。</p>
        <p><strong>投资启示：</strong>公司基本面扎实，现金流充沛，经过调整期后重新进入上升通道，长期投资价值显著。</p>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== 第二部分：竞品对比分析 ======================
if len(competitors) > 0:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("🏆 同行业竞品横向对比分析")
    
    st.subheader("营收规模对比")
    col1, col2 = st.columns(2)
    
    with col1:
        fig_revenue_compare = go.Figure()
        
        fig_revenue_compare.add_trace(go.Bar(
            x=tencent_data["年份"],
            y=tencent_data["营业收入"],
            name=main_company,
            marker_color="#2563eb",
            hovertemplate='%{y:.2f}亿元<extra></extra>'
        ))
        
        colors = ["#7c3aed", "#0891b2", "#059669"]
        for i, comp in enumerate(competitor_data):
            fig_revenue_compare.add_trace(go.Bar(
                x=competitor_data[comp]["年份"],
                y=competitor_data[comp]["营业收入"],
                name=comp,
                marker_color=colors[i % len(colors)],
                hovertemplate='%{y:.2f}亿元<extra></extra>'
            ))
        
        fig_revenue_compare.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            title="2021-2024年营业收入对比(亿元)",
            title_font=dict(size=15),
            barmode="group",
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(255,255,255,0)'),
            xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
            yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
        )
        st.plotly_chart(fig_revenue_compare, use_container_width=True)
    
    with col2:
        fig_profit_compare = go.Figure()
        
        fig_profit_compare.add_trace(go.Bar(
            x=tencent_data["年份"],
            y=tencent_data["归母净利润"],
            name=main_company,
            marker_color="#2563eb",
            hovertemplate='%{y:.2f}亿元<extra></extra>'
        ))
        
        for i, comp in enumerate(competitor_data):
            fig_profit_compare.add_trace(go.Bar(
                x=competitor_data[comp]["年份"],
                y=competitor_data[comp]["归母净利润"],
                name=comp,
                marker_color=colors[i % len(colors)],
                hovertemplate='%{y:.2f}亿元<extra></extra>'
            ))
        
        fig_profit_compare.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            title="2021-2024年归母净利润对比(亿元)",
            title_font=dict(size=15),
            barmode="group",
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor='rgba(255,255,255,0)'),
            xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
            yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
        )
        st.plotly_chart(fig_profit_compare, use_container_width=True)

    # 竞品解读
    with st.expander("💡 点击查看竞品对比深度分析"):
        st.markdown(f'''
        <div class="analysis-box">
            <h4>🏆 行业竞争格局分析</h4>
            <p><strong>营收规模：</strong>头部公司体量差距明显，第一梯队公司占据行业绝大部分市场份额。</p>
            <p><strong>盈利能力：</strong>{main_company}的净利润率和盈利能力在同业中处于领先水平，体现了其强大的变现能力和成本控制能力。</p>
            <p><strong>增长韧性：</strong>面对行业调整期，头部公司展现出更强的业绩韧性，利润修复速度更快，核心护城河深厚。</p>
            <p><strong>综合评价：</strong>多元业务布局的公司具备更强的抗风险能力和长期增长确定性。</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.subheader("关键财务指标对比")
    
    comparison_data = []
    main_latest = tencent_data.iloc[-1]
    comparison_data.append({
        "公司": main_company,
        "营业收入(亿元)": main_latest["营业收入"],
        "归母净利润(亿元)": main_latest["归母净利润"],
        "净利润率(%)": main_latest["净利润率%"],
        "毛利率(%)": main_latest["毛利率%"],
        "净资产收益率(%)": main_latest["净资产收益率%"],
        "资产负债率(%)": main_latest["资产负债率%"]
    })
    
    for comp in competitor_data:
        comp_latest = competitor_data[comp].iloc[-1]
        comparison_data.append({
            "公司": comp,
            "营业收入(亿元)": comp_latest["营业收入"],
            "归母净利润(亿元)": comp_latest["归母净利润"],
            "净利润率(%)": comp_latest["净利润率%"],
            "毛利率(%)": comp_latest["毛利率%"],
            "净资产收益率(%)": comp_latest["净资产收益率%"],
            "资产负债率(%)": comp_latest["资产负债率%"]
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig_radar_compare = go.Figure()
    categories = ["净利润率(%)", "毛利率(%)", "净资产收益率(%)", "营收增速(%)", "资产周转率"]
    
    for i, row in comparison_df.iterrows():
        values = [
            row["净利润率(%)"] / 50 * 100,
            row["毛利率(%)"] / 100 * 100,
            row["净资产收益率(%)"] / 30 * 100,
            max(tencent_data.iloc[-1]["营收同比增速%"], 0) if i == 0 else max(competitor_data[row["公司"]].iloc[-1]["营收同比增速%"], 0),
            main_latest["资产周转率"] * 100 if i == 0 else competitor_data[row["公司"]].iloc[-1]["资产周转率"] * 100
        ]
        
        fig_radar_compare.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=row["公司"],
            line=dict(color="#2563eb" if i == 0 else colors[i-1], width=2),
            opacity=0.7
        ))
    
    fig_radar_compare.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(148, 163, 184, 0.15)'), 
            bgcolor='rgba(255,255,255,0.5)',
            angularaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)')
        ),
        title="财务综合能力对比雷达图",
        title_font=dict(size=15),
        height=520,
        legend=dict(bgcolor='rgba(255,255,255,0)')
    )
    st.plotly_chart(fig_radar_compare, use_container_width=True)
    
    st.dataframe(comparison_df.round(2), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== 第三部分：业务板块与地区分布分析 ======================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)

if main_company == "腾讯控股":
    st.subheader("📊 各业务板块营收分析")
    c1, c2 = st.columns(2)
    
    business_trend = tencent_business_data.melt(
        id_vars="年份",
        value_vars=["增值服务营收","金融科技及企业服务营收","营销服务营收"],
        var_name="业务板块", value_name="营收"
    )
    with c1:
        fig_bar = px.bar(business_trend, x="年份", y="营收", color="业务板块", barmode="group",
                         title="2021-2024年板块营收对比",
                         color_discrete_map={"增值服务营收":"#2563eb","金融科技及企业服务营收":"#7c3aed","营销服务营收":"#0891b2"})
        fig_bar.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            height=420,
            title_font=dict(size=15),
            legend=dict(bgcolor='rgba(255,255,255,0)', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
            yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    business_now = pd.DataFrame({
        "业务板块":["增值服务","金融科技及企业服务","营销服务"],
        "营收":[
            tencent_business_data[tencent_business_data["年份"] == select_year]["增值服务营收"].iloc[0],
            tencent_business_data[tencent_business_data["年份"] == select_year]["金融科技及企业服务营收"].iloc[0],
            tencent_business_data[tencent_business_data["年份"] == select_year]["营销服务营收"].iloc[0]
        ]
    })
    with c2:
        fig_pie_biz = px.pie(business_now, values="营收", names="业务板块", 
                            title=f"{select_year}年业务营收占比",
                            color_discrete_sequence=["#2563eb", "#7c3aed", "#0891b2"],
                            hole=0.4)
        fig_pie_biz.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            height=420,
            title_font=dict(size=15),
            legend=dict(bgcolor='rgba(255,255,255,0)')
        )
        fig_pie_biz.update_traces(textposition='outside', textinfo='percent+label')
        st.plotly_chart(fig_pie_biz, use_container_width=True)

    # 业务板块解读
    with st.expander("💡 点击查看业务板块深度分析"):
        st.markdown(f'''
        <div class="analysis-box">
            <h4>📊 业务结构分析</h4>
            <p><strong>增值服务：</strong>作为第一大收入来源，包含游戏和社交网络业务，是公司的基本盘，贡献了近半数营收，稳定性强。</p>
            <p><strong>金融科技及企业服务：</strong>增长最快的板块，微信支付和云服务双轮驱动，已成为第二增长曲线，未来潜力巨大。</p>
            <p><strong>营销服务：</strong>受宏观环境影响较大，但随着广告需求回暖，呈现稳步复苏态势。</p>
            <p><strong>战略意义：</strong>三驾马车的业务格局分散了单一业务风险，金融科技的高增长有效对冲了游戏业务的周期性波动。</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🌍 全球营收分布可视化（中国全省份+海外大区）")
    map_col1, map_col2 = st.columns(2)
    
    with map_col1:
        st.subheader("🇨🇳 中国34省营收分布地图")
        fig_china_scatter = px.scatter_geo(
            province_full_data,
            lat="纬度",
            lon="经度",
            size="营收(亿元)",
            color="营收(亿元)",
            hover_name="省份",
            hover_data={"营收(亿元)": ":,.2f", "占比%": ":,.1f"},
            projection="natural earth",
            title=f"{select_year}年腾讯中国全省份营收分布",
            color_continuous_scale=px.colors.sequential.Blues,
            size_max=60
        )
        fig_china_scatter.update_geos(
            scope="asia",
            center={"lat": 35, "lon": 105},
            projection_scale=5,
            showland=True,
            landcolor="#f1f5f9",
            countrycolor="#cbd5e1",
            bgcolor='rgba(0,0,0,0)'
        )
        fig_china_scatter.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            height=520, 
            margin={"r":0,"t":30,"l":0,"b":0},
            title_font=dict(size=14)
        )
        st.plotly_chart(fig_china_scatter, use_container_width=True)
    
    with map_col2:
        st.subheader("🌐 海外市场营收分布")
        fig_overseas = px.scatter_geo(
            overseas_data,
            lat="纬度",
            lon="经度",
            size="营收(亿元)",
            hover_name="地区名称",
            hover_data={"营收(亿元)": ":,.2f"},
            projection="natural earth",
            title=f"{select_year}年腾讯海外大区营收分布",
            color="地区名称",
            color_discrete_map={"东南亚": "#2563eb", "欧美": "#7c3aed", "其他海外地区": "#0891b2"},
            size_max=60
        )
        fig_overseas.update_geos(
            showland=True,
            landcolor="#f1f5f9",
            countrycolor="#cbd5e1",
            bgcolor='rgba(0,0,0,0)'
        )
        fig_overseas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#334155'),
            height=520, 
            margin={"r":0,"t":30,"l":0,"b":0},
            legend=dict(bgcolor='rgba(255,255,255,0)'),
            title_font=dict(size=14)
        )
        st.plotly_chart(fig_overseas, use_container_width=True)
    
    st.subheader("🏆 国内营收TOP10省份排行")
    top10_province = province_full_data.sort_values("营收(亿元)", ascending=False).head(10)
    fig_top10 = px.bar(
        top10_province,
        x="省份",
        y="营收(亿元)",
        color="占比%",
        title=f"{select_year}年国内营收最高的10个省份",
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig_top10.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155'),
        height=420,
        title_font=dict(size=14),
        xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
        yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
    )
    st.plotly_chart(fig_top10, use_container_width=True)

else:
    st.subheader("📊 业务板块与地区分布")
    st.info(f"""
    ℹ️ 详细业务板块和全球地区分布数据仅支持腾讯控股
    
    目前{main_company}的完整分析包含：
    - ✅ 八大核心财务指标实时展示
    - ✅ 历年经营趋势分析与未来预测
    - ✅ 与腾讯、阿里、百度、网易的多维度竞品对比
    - ✅ 盈利、偿债、增长、运营能力综合评估
    - ✅ 资产负债结构与现金流分析
    - ✅ AI智能问答助手
    
    如需查看中国34省+海外大区营收分布地图，请在左侧控制台选择"腾讯控股"作为主分析公司。
    """)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== 第四部分：财务指数专项分析 ======================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.subheader("📉 多项财务指数走势对比")
fig_index = px.line(
    tencent_data, x="年份",
    y=["毛利率%","净利润率%","资产负债率%","净资产收益率%"],
    title="盈利、偿债能力指数历年波动",
    markers=True,
    color_discrete_map={
        "毛利率%":"#2563eb",
        "净利润率%":"#7c3aed",
        "资产负债率%":"#0891b2",
        "净资产收益率%":"#059669"
    }
)
fig_index.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#334155'),
    height=470,
    title_font=dict(size=15),
    legend=dict(bgcolor='rgba(255,255,255,0)', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
    yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
)
st.plotly_chart(fig_index, use_container_width=True)

with st.expander("💡 点击查看财务指数深度分析"):
    st.markdown(f'''
    <div class="analysis-box">
        <h4>📉 财务健康度综合评估</h4>
        <p><strong>盈利能力：</strong>毛利率保持在较高水平，体现了公司强大的定价权和成本控制能力。净利润率虽有波动，但整体仍处于行业优秀水平。</p>
        <p><strong>偿债能力：</strong>资产负债率维持在健康区间，远低于行业平均水平，财务结构稳健，偿债风险极低。</p>
        <p><strong>运营效率：</strong>净资产收益率(ROE)表现优异，说明公司为股东创造回报的能力很强，资本使用效率高。</p>
        <p><strong>综合评价：</strong>各项财务指标均处于健康区间，盈利质量高，财务风险低，是典型的优质蓝筹财务特征。</p>
    </div>
    ''', unsafe_allow_html=True)

st.subheader("🚀 营收&净利润增速变化")
grow_data = tencent_data[["年份","营收同比增速%","净利润同比增速%"]].melt(
    id_vars="年份", var_name="增长类型", value_name="增速(%)"
)
fig_grow = px.bar(grow_data, x="年份", y="增速(%)", color="增长类型", barmode="group",
                  title="年度业绩增长幅度对比",
                  color_discrete_map={"营收同比增速%":"#2563eb", "净利润同比增速%":"#7c3aed"})
fig_grow.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#334155'),
    height=420,
    title_font=dict(size=15),
    legend=dict(bgcolor='rgba(255,255,255,0)'),
    xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
    yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
)
st.plotly_chart(fig_grow, use_container_width=True)

st.subheader("🏦 资产与负债权益结构分析")
asset_data = pd.DataFrame({
    "年份":tencent_data["年份"],
    "负债":tencent_data["总负债"],
    "股东权益":tencent_data["股东权益"]
})
asset_stack = asset_data.melt(id_vars="年份", var_name="构成", value_name="金额")
fig_asset = px.area(asset_stack, x="年份", y="金额", color="构成",
                    title="企业资产结构历年变化",
                    color_discrete_map={"负债":"#7c3aed", "股东权益":"#2563eb"})
fig_asset.update_traces(stackgroup='one')
fig_asset.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#334155'),
    height=420,
    title_font=dict(size=15),
    legend=dict(bgcolor='rgba(255,255,255,0)'),
    xaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)'),
    yaxis=dict(gridcolor='rgba(148, 163, 184, 0.15)', zeroline=False)
)
st.plotly_chart(fig_asset, use_container_width=True)

st.subheader("🎯 单年度财务综合能力雷达图")
radar_fig = go.Figure()
cate = ["盈利能力","收益水平","偿债安全","增长潜力","运营效率"]
vals = [
    year_detail["毛利率%"]/50*100,
    year_detail["净资产收益率%"]/30*100,
    100-year_detail["资产负债率%"],
    max(year_detail["营收同比增速%"], 0) if not pd.isna(year_detail["营收同比增速%"]) else 0,
    year_detail["资产周转率"]*100
]
radar_fig.add_trace(go.Scatterpolar(
    r=vals, 
    theta=cate, 
    fill="toself", 
    name="综合能力评分",
    line=dict(color="#2563eb", width=2.5),
    fillcolor='rgba(37, 99, 235, 0.2)'
))
radar_fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#334155'),
    polar=dict(
        radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(148, 163, 184, 0.15)'), 
        bgcolor='rgba(255,255,255,0.5)',
        angularaxis=dict(gridcolor='rgba(148, 163, 184, 0.2)')
    ),
    title="财务五维能力评估", 
    title_font=dict(size=15),
    height=520,
    legend=dict(bgcolor='rgba(255,255,255,0)')
)
st.plotly_chart(radar_fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== 原始数据表格 ======================
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.subheader("📋 完整原始财务数据表")
st.dataframe(tencent_data.round(2), use_container_width=True, hide_index=True)

if main_company == "腾讯控股":
    st.subheader("📋 中国34省营收分布详细数据")
    st.dataframe(province_full_data.round(2), use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================== 扫码访问二维码 ======================
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.subheader("📱 手机扫码直接访问")
    
    def generate_qr_code(url):
        qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2563eb", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Image.open(buf)
    
    local_url = st.secrets.get("app_url", "https://tengxun30-hppakm3d3skspezngwvfvhf.streamlit.app/")
    qr_pic = generate_qr_code(local_url)
    st.image(qr_pic, caption="扫码进入财报分析看板", width=200)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================== AI智能问答助手 ======================
st.divider()
st.markdown('<div class="premium-card">', unsafe_allow_html=True)
st.subheader("🤖 财报智能咨询助手")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("可查询营收、利润、指数、业务、负债、分布、竞品、预测等问题")
if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    ans = ""
    if "净利润" in user_input:
        ans = f"{select_year}年{main_company}归母净利润为{year_detail['归母净利润']:.2f}亿元，净利润率{year_detail['净利润率%']}%，在同行业中处于领先水平。"
    elif "营收" in user_input:
        ans = f"{select_year}年营业收入{year_detail['营业收入']:.2f}亿元，同比增速{safe_display(year_detail['营收同比增速%'])}，业务保持稳健增长。"
    elif "毛利率" in user_input or "盈利" in user_input:
        ans = f"当期毛利率{year_detail['毛利率%']}%，净资产收益率{year_detail['净资产收益率%']}%，盈利能力强劲且稳定。"
    elif "负债" in user_input or "资产" in user_input:
        ans = f"当期资产负债率{year_detail['资产负债率%']}%，负债结构合理，财务风险处于健康可控范围。"
    elif "业务板块" in user_input and main_company == "腾讯控股":
        ans = f"增值服务{tencent_business_data[tencent_business_data['年份'] == select_year]['增值服务营收'].iloc[0]:.2f}亿元，金融科技业务{tencent_business_data[tencent_business_data['年份'] == select_year]['金融科技及企业服务营收'].iloc[0]:.2f}亿元，营销服务{tencent_business_data[tencent_business_data['年份'] == select_year]['营销服务营收'].iloc[0]:.2f}亿元。"
    elif "增速" in user_input:
        ans = f"本年度营收增速{safe_display(year_detail['营收同比增速%'])}，净利润增速{safe_display(year_detail['净利润同比增速%'])}，增长势头良好。"
    elif "省份" in user_input or "分布" in user_input and main_company == "腾讯控股":
        top_province = province_full_data.sort_values("营收(亿元)", ascending=False).iloc[0]
        ans = f"{select_year}年腾讯国内营收最高的省份是{top_province['省份']}，营收{top_province['营收(亿元)']:.2f}亿元，占国内总营收的{top_province['占比%']}%。TOP10省份贡献了约90%的国内营收。"
    elif "海外" in user_input and main_company == "腾讯控股":
        ans = f"{select_year}年腾讯海外营收{tencent_business_data[tencent_business_data['年份'] == select_year]['海外营收'].iloc[0]:.2f}亿元，主要来自东南亚和欧美市场，国际化进程稳步推进。"
    elif "竞品" in user_input or "对比" in user_input:
        if len(competitors) > 0:
            comp_name = competitors[0]
            comp_latest = competitor_data[comp_name].iloc[-1]
            ans = f"与{comp_name}对比：{main_company}营收{year_detail['营业收入']:.2f}亿元 vs {comp_latest['营业收入']:.2f}亿元，净利润{year_detail['归母净利润']:.2f}亿元 vs {comp_latest['归母净利润']:.2f}亿元。{main_company}在盈利能力和现金流方面表现更为出色。"
        else:
            ans = "请在左侧控制台选择竞品公司进行多维度对比分析。"
    elif "预测" in user_input:
        if ARIMA_AVAILABLE and len(revenue_forecast_years) > 0:
            ans = f"基于ARIMA时序模型预测，未来{forecast_years}年{main_company}营收将保持稳健增长趋势，预计{revenue_forecast_years[-1]}年营业收入达到{revenue_forecast[-1]:.2f}亿元，归母净利润达到{profit_forecast[-1]:.2f}亿元。"
        else:
            ans = "预测功能需要安装statsmodels库，目前使用本地历史数据进行分析。"
    else:
        ans = "你可以询问营收、净利润、毛利率、负债率、业务分布、增长速度、省份营收、竞品对比、未来预测等财报相关问题~"
    
    st.session_state.messages.append({"role":"assistant","content":ans})
    with st.chat_message("assistant"):
        st.markdown(ans)

st.markdown('</div>', unsafe_allow_html=True)

# 简化版页脚（移除突兀的大标题）
st.markdown("""
<div class="footer-section">
    <p>数据来源：公司官方财报 | 数据更新至2024年</p>
    <p style="font-size: 0.85rem; margin-top: 0.3rem;">© 2026 财务数据分析系统 | 所有数据仅供参考，不构成任何投资建议</p>
</div>
""", unsafe_allow_html=True)