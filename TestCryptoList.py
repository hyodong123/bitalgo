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
    
    # 매주 1,000원씩 적립식 투자 시뮬레이션
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
    

    # 매주 투자할 금액
    weekly_investment = 1000
    
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
    
    # 성과를 시각화
    fig = px.bar(df, x='날짜', y='수익률 (%)', title='가상자산 가격 변동 및 투자 수익률')
    st.plotly_chart(fig)

# 프로젝트 소개 페이지
def show_project_intro():
    st.write('''
    **비트알고 프로젝트 소개**

비트알고는 가상화폐 투자자들을 위해 설계된 소규모 프로젝트로, 사용자들이 가상화폐 시장에 쉽게 접근하고, 자동으로 적립식 투자를 할 수 있도록 돕는 자동매매 프로그램입니다.

비트알고는 사용자가 투자에 대한 깊은 지식이 없더라도 인공지능 알고리즘을 이용해 시장의 데이터를 분석하여 적절한 매수와 매도 시점을 자동으로 결정합니다. 비트알고는 사용자에게 정기적인 수익을 얻는 데 도움을 주고자 개발되었습니다. 매수 상황은 사용자가 결정할 수 있으며, 사용자 선택에 따른 매수/매도 알고리즘을 따로 구현할 예정입니다.

비트알고는 소규모 팀이 모여 열정적으로 개발한 프로젝트로, 사용자 중심의 기능과 서비스 개선을 위해 지속적으로 노력하고 있습니다. 가상화폐의 복잡성과 변동성을 줄이고, 누구나 쉽게 투자에 참여할 수 있는 환경을 만들어 나가는 것이 우리의 비전입니다.

함께 더 나은 투자 세상을 만들어갑시다!
    ''')

# 가이드 페이지
def show_guide():
    st.write('''
    **초보자를 위한 사용 방법 및 자주 묻는 질문(FAQ)을 제공합니다.**

    **FAQ**
    1. **비트알고는 어떤 프로그램인가요?**
        - 비트알고는 적립식 자동매매 프로그램으로, 사용자의 투자 성향에 맞춰 가상화폐를 자동으로 매수/매도합니다.
    2. **어떻게 시작하나요?**
        - 계정 생성 후, 투자 성향을 설정하고 원하는 금액을 입금하면 프로그램이 자동으로 매매를 시작합니다.
    3. **수익률은 보장되나요?**
        - 수익률은 시장 상황에 따라 달라질 수 있으며, 보장은 어렵습니다.
    ''')
# 문의 및 피드백 페이지
def show_feedback():
    st.write('문의사항 및 피드백을 제출해 주세요.')
    feedback = st.text_area("문의 및 피드백 입력", "여기에 입력하세요...")
    if st.button("제출"):
        st.success("문의 및 피드백이 성공적으로 제출되었습니다.")
        # 문의 및 피드백 처리 로직 추가 가능

# 실시간 가상자산 시세 확인 페이지
def show_live_prices():
    st.write("**실시간 가상자산 시세**")
    
    # 가상자산 데이터 가져오기
    crypto_info = get_all_crypto_info()
    korean_names = load_korean_names()  # 코인 이름 데이터 로드

    if not crypto_info:
        st.error("가상자산 데이터를 가져올 수 없습니다.")
        return
    
    # 데이터프레임 생성 및 표시
    prices_data = {
        '코인': [],
        '코인 이름': [],
        '현재가 (KRW)': [],
        '전일 대비 (%)': []
    }
    
    for key, value in crypto_info.items():
        if key == 'date':
            continue
        prices_data['코인'].append(key)
        prices_data['코인 이름'].append(korean_names.get(key, key))
        prices_data['현재가 (KRW)'].append(value['closing_price'])
        prices_data['전일 대비 (%)'].append(value['fluctate_rate_24H'])
    
    df_prices = pd.DataFrame(prices_data)
    st.dataframe(df_prices)
    
    # 특정 코인의 시세를 그래프로 표현
    selected_coin = st.selectbox("시세를 보고 싶은 코인을 선택하세요", df_prices['코인 이름'])
    coin_data = crypto_info.get(df_prices[df_prices['코인 이름'] == selected_coin]['코인'].values[0])
    if coin_data:
        st.write(f"**{selected_coin} 시세 그래프**")
        coin_symbol = df_prices[df_prices['코인 이름'] == selected_coin]['코인'].values[0]
        historical_url = f"https://api.bithumb.com/public/candlestick/{coin_symbol}_KRW/24h"
        historical_response = requests.get(historical_url)
        if historical_response.status_code == 200:
            historical_data = historical_response.json()
            if historical_data['status'] == '0000':
                historical_prices = [float(entry[2]) for entry in historical_data['data'][-12:]]
                historical_dates = [pd.to_datetime(entry[0], unit='ms').strftime('%Y-%m-%d %H:%M:%S') for entry in historical_data['data'][-12:]]
                
                historical_df = pd.DataFrame({'시간': historical_dates, '가격 (KRW)': historical_prices})
                fig = px.line(historical_df, x='시간', y='가격 (KRW)', title=f'{selected_coin} 가격 변동')
                st.plotly_chart(fig)
            else:
                st.error("역사적 데이터를 가져오지 못했습니다.")
        else:
            st.error("역사적 데이터를 가져오지 못했습니다.")


# 페이지 라우팅
page = st.sidebar.radio("메뉴 선택", ["프로젝트 소개", "실시간 가상자산 시세", "3개월 전부터 투자를 한다면..",  "가이드", "문의 및 피드백"])

if page == "프로젝트 소개":
    show_project_intro()
elif page == "3개월 전부터 투자를 한다면..":
    show_investment_performance()
elif page == "실시간 가상자산 시세":
    show_live_prices()
elif page == "가이드":
    show_guide()
elif page == "문의 및 피드백":
    show_feedback()
    
# 페이지 하단 푸터 추가
st.markdown(
    """
    <footer style='text-align: center; margin-top: 50px;'>
        <hr>
        <p>비트알고 프로젝트 © 2024. All Rights Reserved.</p>
    </footer>
    """,
    unsafe_allow_html=True
)
