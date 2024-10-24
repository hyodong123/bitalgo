import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
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
# 경제 지식을 제공하는 페이지 함수
def show_edu():
    st.markdown("<h2 style='font-size:30px;'>알고 있으면 좋은 경제 지식</h2>", unsafe_allow_html=True)
    
    st.write('''
    **1. 가상화폐란 무엇인가요?**
    가상화폐(cryptocurrency)는 온라인 상에서 사용되는 디지털 화폐로, 블록체인 기술을 기반으로 합니다. 대표적으로 비트코인과 이더리움이 있으며, 
    기존 화폐와 달리 중앙 기관이 발행하지 않고, 분산 원장을 통해 거래가 이루어집니다.

    **2. 인플레이션과 디플레이션**
    - **인플레이션**은 물가가 상승하여 화폐의 가치가 하락하는 현상을 말합니다. 예를 들어, 같은 돈으로 살 수 있는 물건의 양이 줄어드는 것이죠.
    - **디플레이션**은 그 반대로 물가가 하락하여 화폐의 가치가 상승하는 현상입니다. 이 경우, 돈의 가치가 높아지지만 경제 성장이 둔화될 수 있습니다.

    **3. 블록체인(Blockchain)이란?**
    블록체인은 데이터를 블록 단위로 저장하며, 여러 블록들이 체인처럼 연결된 구조를 가지고 있습니다. 이를 통해 분산된 네트워크 내에서 
    투명하고 안전하게 데이터를 저장하고, 위변조를 방지할 수 있습니다. 가상화폐는 이 블록체인 기술을 바탕으로 만들어졌습니다.

    **4. 리스크 관리**
    가상화폐 투자나 주식 투자에서는 리스크 관리가 매우 중요합니다. 손실을 최소화하고, 예상하지 못한 시장 변동에 대비하는 것이 필요합니다. 
    대표적인 리스크 관리 방법으로는 자산 분산 투자, 손절매 전략 등이 있습니다.

    **5. 도미넌스 (Dominance)**
    도미넌스는 특정 가상화폐가 시장에서 차지하는 비중을 의미합니다. 예를 들어, 비트코인의 도미넌스가 높다는 것은 
    전체 가상화폐 시장에서 비트코인의 비중이 크다는 뜻입니다. 도미넌스는 시장 흐름을 파악하는 중요한 지표 중 하나입니다.

    **6. 가상화폐와 규제**
    각국 정부는 가상화폐에 대해 다양한 규제를 시행하고 있습니다. 일부 국가는 가상화폐를 합법적으로 인정하고 규제를 통해 시장을 보호하려고 하지만, 
    다른 국가는 가상화폐의 불법 활동과 관련된 우려로 강력한 제재를 가하고 있습니다. 가상화폐 투자 시, 해당 국가의 법적 규제를 고려하는 것이 중요합니다.
    ''')

    # 추가적인 자료를 표 형식으로 제공할 수도 있습니다.
    edu_data = {
        "개념": ["가상화폐", "블록체인", "인플레이션", "디플레이션", "리스크 관리"],
        "설명": [
            "디지털 화폐, 분산 원장 기술을 사용하여 중앙 기관 없이 거래",
            "데이터를 블록 단위로 저장하여 투명하고 안전하게 관리",
            "화폐 가치 하락, 물가 상승",
            "화폐 가치 상승, 물가 하락",
            "투자 손실 최소화, 자산 분산 및 손절매 전략"
        ]
    }
    
    edu_df = pd.DataFrame(edu_data)
    st.write(edu_df)

    # 이미지나 추가 시각화 자료를 넣을 수도 있습니다.
    st.image(
    "https://www.siminsori.com/news/photo/201801/200764_50251_4925.jpg",
    caption="블록체인 구조",
    use_column_width=True
)

# 가이드 페이지
def show_guide():
    st.markdown("<h2 style='font-size:30px;'>초보자를 위한 사용 방법 및 자주 묻는 질문(FAQ)</h2>", unsafe_allow_html=True)
    st.write('''
    **FAQ**
    1. **비트알고는 어떤 플랫폼인가요?**
        - 비트알고 투자 보조 플랫폼으로 사용자가 가상화폐에 관해 배울 수 있는 학습환경을 제공합니다.
    2. **어떤 정보가 제공되나요?**
        - 실시간 가상화폐 시세 및 도미넌스 차트를 제공합니다.
        - 또한 사용자가 정보를 찾아보기 보단 한분에 원하는 정보를 볼 수 있도록 제공 합니다.
    3. **초보자도 쉽게 이용할 수 있나요?**
        - 예, 비트알고는 가상화폐 시장에 익숙하지 않은 초보자도 쉽게 사용할 수 있도록 직관적인 인터페이스와 다양한 가이드를 제공합니다.
    4. **교육 자료는 어떤 내용으로 구성되어 있나요?**
        - 기본적인 가상화폐 투자 개념부터 차트 분석, 경제 지표 해석, 리스크 관리 방법까지 다양한 교육 자료를 제공합니다. 
          또한, 실시간 가상화폐 뉴스와 시장 분석 정보를 통해 최신 동향을 학습할 수 있습니다.
    4. **어떤 디바이스에서 사용할 수 있나요?**
        - 비트알고는 웹 기반 플랫폼으로, PC 및 모바일 브라우저에서 모두 사용할 수 있습니다. 언제 어디서든 간편하게 접속하여 가상화폐시장에 접근할 수 있습니다.
        - 
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
    
    if not crypto_info:
        st.error("가상자산 데이터를 가져올 수 없습니다.")
        return
    
    # 데이터프레임 생성 및 표시
    prices_data = {
        '코인': [],
        '현재가 (KRW)': [],
        '전일 대비 (%)': []
    }
    
    for key, value in crypto_info.items():
        if key == 'date':
            continue
        prices_data['코인'].append(key)
        prices_data['현재가 (KRW)'].append(value['closing_price'])
        prices_data['전일 대비 (%)'].append(value['fluctate_rate_24H'])
    
    df_prices = pd.DataFrame(prices_data)
    st.dataframe(df_prices)
    
    # 특정 코인의 시세를 그래프로 표현
    selected_coin = st.selectbox("시세를 보고 싶은 코인을 선택하세요", df_prices['코인'])
    coin_data = crypto_info.get(selected_coin)
    if coin_data:
        st.write(f"**{selected_coin} 시세 그래프**")
        historical_url = f"https://api.bithumb.com/public/candlestick/{selected_coin}_KRW/24h"
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
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴 선택",  # required
        options=["프로젝트 소개", "실시간 가상자산 시세", "모의 투자", "알고있으면 좋은 경제 지식", "가이드", "문의 및 피드백"],  # required
        icons=["house", "graph-up", "wallet", "book", "question-circle", "envelope"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
    )

# 선택된 메뉴에 따라 페이지 라우팅
if selected == "프로젝트 소개":
    show_project_intro()
elif selected == "실시간 가상자산 시세":
    show_live_prices()
elif selected == "모의 투자":
    show_investment_performance()
elif selected == "알고있으면 좋은 경제 지식":
    show_edu()
elif selected == "가이드":
    show_guide()
elif selected == "문의 및 피드백":
    show_feedback()

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
