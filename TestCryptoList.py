import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px  # 오류 해결을 위한 추가

def load_korean_names():
    try:
        df = pd.read_csv('./mnt/data/crypto_korean_names.csv')
        return dict(zip(df['코인'], df['코인 이름']))
    except Exception as e:
        st.error(f"코인 이름 CSV 파일을 로드하는 데 실패했습니다: {e}")
        return {}

# 가상자산 정보 가져오기 함수
def get_all_crypto_info():
    url = "https://api.bithumb.com/public/ticker/ALL_KRW"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if data['status'] == '0000':
                return data['data']
        except ValueError:
            st.error("데이터를 파싱하는 데 실패했습니다.")
    else:
        st.error("데이터를 가져오지 못했습니다.")
    return {}

# 성과 분석: 매주 1,000원 적립식 투자 로직
def show_investment_performance():
    st.markdown("<h2 style='font-size:30px;'>모의 투자</h2>", unsafe_allow_html=True)
    # 사용자로부터 투자 금액 입력 받기
    weekly_investment = st.number_input("주간 투자 금액을 입력하세요 (원):", min_value=1000, step=1000)

    # 가상자산 가격 데이터 받아오기
    url = "https://api.bithumb.com/public/ticker/BTC_KRW"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == '0000':
            current_price = float(data['data']['closing_price'])
        else:
            st.error("데이터를 가져오지 못했습니다.")
            return
    else:
        st.error("데이터를 가져오지 못했습니다.")
        return

    # 매주 투자 시뮬레이션
    historical_url = "https://api.bithumb.com/public/candlestick/BTC_KRW/24h"
    historical_response = requests.get(historical_url)
    if historical_response.status_code == 200:
        historical_data = historical_response.json()
        if historical_data['status'] == '0000':
            price_data = [float(entry[2]) for entry in historical_data['data'][-12:]]  # 최근 12개의 일간 종가 데이터 사용
        else:
            st.error("역사적 데이터를 가져오지 못했습니다.")
            return
    else:
        st.error("역사적 데이터를 가져오지 못했습니다.")
        return

    investment_data = {
        '날짜': pd.date_range(end=pd.Timestamp.now(), periods=12, freq='W').strftime('%Y-%m-%d'),
        '가격 (KRW)': price_data
    }
    df = pd.DataFrame(investment_data)

    # 투자 로직: 매주 가격에 맞춰 적립식으로 투자
    df['투자 금액 (KRW)'] = weekly_investment
    df['매수량'] = df['투자 금액 (KRW)'] / df['가격 (KRW)']
    df['누적 매수량'] = df['매수량'].cumsum()
    df['누적 투자 금액 (KRW)'] = weekly_investment * (df.index + 1)
    df['평균 매수 가격 (KRW)'] = (df['누적 투자 금액 (KRW)'] / df['누적 매수량']).astype(int)
    df['수익률 (%)'] = ((df['가격 (KRW)'] - df['평균 매수 가격 (KRW)']) / df['평균 매수 가격 (KRW)']) * 100

    # 결과 출력
    st.write(df)
    st.write(f"총 투자 금액: {df['누적 투자 금액 (KRW)'].iloc[-1]} KRW")
    st.write(f"총 매수량: {df['누적 매수량'].iloc[-1]:.6f} 코인")
    st.write(f"최종 수익률: {df['수익률 (%)'].iloc[-1]:.2f}%")

    # 성과를 시각화 (막대 그래프로 나타내기)
    fig = px.bar(df, x='날짜', y='수익률 (%)', title='가상자산 가격 변동 및 투자 수익률')
    st.plotly_chart(fig)

# 프로젝트 소개 페이지
def show_project_intro():
    st.markdown("<h2 style='font-size:30px;'>비트알고 프로젝트 소개</h2>", unsafe_allow_html=True)
    st.write('''
비트알고는 가상화폐 투자자들을 위한 교육 중심의 플랫폼으로, 사용자들이 가상화폐 시장에 쉽게 접근하고 학습할 수 있도록 돕는 투자 교육 플랫폼입니다.

비트알고는 투자에 대한 깊은 지식이 없는 사용자도 가상화폐 시장의 기초부터 배워나갈 수 있으며, 차트를 분석하거나 어려웠던 경제 용어 등 
많은 것들을 학습할 수 있습니다.
이러한 과정에서 투자의 원리를 배우고 성장할 수 있도록 설계되었습니다.
비트알고는 사용자 중심의 기능과 교육 서비스를 지속적으로 개선하며, 
누구나 쉽게 가상화폐 투자를 이해하고 참여할 수 있는 환경을 만들어가는 것을 목표로 하고 있습니다. 
    ''')

# 가이드 페이지
def show_guide():
    st.markdown("<h2 style='font-size:30px;'>초보자를 위한 사용 방법 및 자주 묻는 질문(FAQ)</h2>", unsafe_allow_html=True)
    st.write('''
    **FAQ**
    1. **비트알고는 어떤 프로그램인가요?**
        - 비트알고는 적립식 자동매매 프로그램으로,기", "알고있으면 좋은 경제 지식", "모의 투자",  "코인 토픽" ,"가이드", "문의 및 피드백"])

if page == "프로젝트 소개":
    show_project_intro()
elif page == "모의 투자":
    show_investment_performance()
elif page == "실시간 가상자산 시세":
    show_live_prices()
elif page == "가이드":
    show_guide()
elif page == "문의 및 피드백":
    show_feedback()
elif page == "알고있으면 좋은 경제 지식":
    show_edu()

# 페이지 하단 푸터 추가
st.markdown(
    """
    <footer style='text-align: center; margin-top: 50px;'>
        <hr>
        <p>Copyright Team 비트지니어스 - 비트알고 프로젝트 © 2024. All Rights Reserved.</p> 
    </footer>
    """,
    unsafe_allow_html=True
)
