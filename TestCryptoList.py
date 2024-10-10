import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px  # 오류 해결을 위한 추가

# Streamlit 스타일을 위해 HTML과 CSS 추가
st.markdown(
    """
    <style>
    /* 사이드바 배경 및 텍스트 스타일 변경 */
    .sidebar .sidebar-content {
        background-color: #40E0D0;
        color: white;
    }
    .sidebar .sidebar-content h2, h3, h4 {
        color: #ffffff;
    }
    
    /* 페이지 제목 및 헤더 스타일 변경 */
    h2, h3, h4 {
        color: #40E0D0;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
    }
    
    /* 버튼 스타일 변경 */
    .stButton>button {
        background-color: #40E0D0;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px;
        font-weight: bold;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2aa198;
        color: #ffffff;
    }
    
    /* 테이블 스타일링 */
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        padding: 10px;
        text-align: center;
        border-bottom: 1px solid #ddd;
    }
    th {
        background-color: #40E0D0;
        color: white;
        font-weight: bold;
    }
    td {
        color: #333333;
    }
    
    /* 텍스트 영역 및 입력 박스 스타일 */
    .stTextArea textarea, .stTextInput input {
        background-color: #f0f8ff;
        color: #333333;
        font-size: 14px;
        border: 2px solid #40E0D0;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* 선택 박스 스타일 */
    .stSelectbox>div>div {
        border: 2px solid #40E0D0;
        border-radius: 8px;
    }

    /* 사이드바 메뉴 선택 스타일 */
    .css-1aumxhk {
        color: #333333;
        font-weight: bold;
        border-bottom: 2px solid #40E0D0;
        padding-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

def get_all_crypto_info():
    url = "https://api.bithumb.com/public/ticker/ALL_KRW"
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            data = response.json()
            if data['status'] == '0000':
                return data['data']
        except ValueError:
            print("Failed to parse crypto info response as JSON")
    return {}

def get_all_market_info():
    # 종목 정보 가져오기
    market_url = "https://api.bithumb.com/v1/market/all?isDetails=false"    # API 엔드포인트 URL
    headers = {"accept": "application/json"}    # 헤더 설정 (필요 시 수정)
    response = requests.get(market_url, headers=headers)    # API 요청 보내기
    data = response.json()  # 종목 정보 추출
        
    return data

def show_crypto_candlestick_chart(symbol):
    url = f"https://api.bithumb.com/public/candlestick/{symbol}_KRW/1h"  # 최근 1시간 데이터
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == '0000':
            ohlcv_data = data['data']
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.sort_values('timestamp', inplace=True)

            fig = go.Figure(data=[go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                increasing_line_color='blue',
                decreasing_line_color='red'
            )])
            fig.update_layout(
                title=f"{symbol} 실시간 차트",
                xaxis_title="시간",
                yaxis_title="가격 (KRW)",
                template="plotly_dark"
            )
            st.plotly_chart(fig)

'## BitAlgo'

crypto_data = get_all_crypto_info()
market_data = get_all_market_info()

if isinstance(market_data, list):  # market_data가 리스트인지 확인
    processed_data = []
    for market_info in market_data:
        market_key = market_info['market']
        # 'KRW-'를 제거한 후 key로 사용
        clean_market_key = market_key.replace('KRW-', '')
        if clean_market_key in crypto_data:
            processed_data.append([
                f"{market_info['korean_name']} ({market_key})",
                round(float(crypto_data[clean_market_key]['closing_price']), 2),
                float(crypto_data[clean_market_key]['fluctate_rate_24H']),
                float(crypto_data[clean_market_key]['fluctate_24H']),
                round(float(crypto_data[clean_market_key]['acc_trade_value_24H']), 0)
            ])

market_data_df = pd.DataFrame(processed_data, columns=['가상자산명 (Symbol)', '현재가 (KRW)', '24시간 변동률 (%)', '변동액 (KRW)', '거래금액 (24H, KRW)'])

st.dataframe(market_data_df)
if not len(market_data_df):
    st.error("데이터를 가져오지 못했습니다.")

# 사이드바 설정
st.sidebar.title('비트알고')

# 사이드바 메뉴 항목 추가
def show_content(option):
    if option == '프로젝트 소개':
        st.write('''
        **비트알고 프로젝트 소개**
        
        비트알고는 가상화폐 투자자들을 위해 설계된 소규모 프로젝트로, 사용자들이 가상화폐 시장에 쉽게 접근하고, 자동으로 적립식 투자를 할 수 있도록 돕는 자동매매 프로그램입니다.
        
        비트알고는 사용자가 투자에 대한 깊은 지식이 없더라도 안정적이고 지속적인 수익을 추구할 수 있도록 설계되었습니다. 이를 위해 최신 알고리즘과 인공지능 기술을 활용하여 시장의 데이터를 분석하고, 적절한 매수와 매도 시점을 자동으로 결정하여 사용자에게 최적의 투자 경험을 제공합니다.
        
        비트알고는 소규모 팀이 모여 열정적으로 개발한 프로젝트로, 사용자 중심의 기능과 서비스 개선을 위해 지속적으로 노력하고 있습니다. 가상화폐의 복잡성과 변동성을 줄이고, 누구나 쉽게 투자에 참여할 수 있는 환경을 만들어 나가는 것이 우리의 비전입니다.
        
        함께 더 나은 투자 세상을 만들어갑시다!
        ''')

    elif option == '투자 전략':
        st.write('사용자의 위험 성향에 따라 다양한 적립식 투자 전략을 제공합니다.')
        st.write("\n**위험 성향 선택**")
        risk_level = st.selectbox("위험 성향을 선택하세요:", ["낮음", "중간", "높음"])
        st.write(f"선택한 위험 성향: {risk_level}")
        if risk_level == "낮음":
            st.write("안전한 자산에 분산 투자하는 전략을 추천합니다.")
        elif risk_level == "중간":
            st.write("적절한 위험과 수익을 추구하는 자산 분배를 추천합니다.")
        elif risk_level == "높음":
            st.write("높은 수익을 위해 높은 위험을 감수하는 전략을 추천합니다.")

    elif option == '실시간 시세':
        st.write('가상화폐의 실시간 시세와 각 자산의 차트를 확인할 수 있습니다.')
        # Bithumb API에서 실시간 데이터 가져오기
        url = "https://api.bithumb.com/public/ticker/ALL_KRW"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '0000':
                crypto_data = data['data']
                crypto_list = []
                for key, value in crypto_data.items():
                    if isinstance(value, dict):
                        crypto_list.append([
                            key,  # 가상자산명 (Symbol)
                            value.get('korean_name', key),  # 한글 이름이 있을 경우 사용
                            float(value['closing_price']),
                            float(value['fluctate_rate_24H'])
                        ])
                crypto_df = pd.DataFrame(crypto_list, columns=['Symbol', '가상자산명', '현재가 (KRW)', '24시간 변동률 (%)'])
                selected_asset = st.selectbox("가상자산을 선택하세요:", crypto_df['Symbol'].unique())

                if selected_asset:
                    show_crypto_candlestick_chart(selected_asset)

    elif option == '성과 분석':
        st.write('사용자의 투자 성과를 시각화하여 분석합니다.')
        # 샘플 투자 데이터
        data = {
            '날짜': pd.date_range(start='2024-01-01', periods=10, freq='M'),
            '투자 금액 (KRW)': [1000000, 1200000, 1500000, 1300000, 1600000, 1800000, 2000000, 2200000, 2500000, 2700000],
            '수익률 (%)': [5, 7, 3, 4, 6, 8, 9, 5, 7, 6]
        }
        df = pd.DataFrame(data)
        st.dataframe(df)
        # 수익률 차트
        fig = px.bar(df, x='날짜', y='수익률 (%)', title='투자 성과 분석')
        st.plotly_chart(fig)

    elif option == '가이드':
        st.write('초보자를 위한 사용 방법 및 자주 묻는 질문(FAQ)을 제공합니다.')
        st.write("\n**FAQ**")
        faq = {
            "비트알고는 어떤 프로그램인가요?": "비트알고는 적립식 자동매매 프로그램으로, 사용자의 투자 성향에 맞춰 가상화폐를 자동으로 매수/매도합니다.",
            "어떻게 시작하나요?": "계정 생성 후, 투자 성향을 설정하고 원하는 금액을 입금하면 프로그램이 자동으로 매매를 시작합니다.",
            "수익률은 보장되나요?": "수익률은 시장 상황에 따라 달라질 수 있으며, 보장은 어렵습니다."
        }
        for question, answer in faq.items():
            st.write(f"**{question}**")
            st.write(answer)

    elif option == '문의 및 피드백':
        st.write('문의사항 및 피드백을 제출해 주세요.')
        st.text_area("문의 및 피드백 입력", "여기에 입력하세요...")
        if st.button("제출"):
            st.success("문의 및 피드백이 성공적으로 제출되었습니다.")

menu_options = [
    '프로젝트 소개',
    '투자 전략',
    '실시간 시세',
    '성과 분석',
    '가이드',
    '문의 및 피드백'
]

# 사이드바에 체크박스 형태로 메뉴 항목 표시
selected_option = st.sidebar.radio("메뉴 선택", menu_options)
show_content(selected_option)
