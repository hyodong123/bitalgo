import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import plotly.express as px  # 오류 해결을 위한 추가
from googletrans import Translator
import streamlit.components.v1 as components
from collections import Counter
import re

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

def show_investment_performance():
    st.markdown("<h2 style='font-size:30px;'>모의 투자</h2>", unsafe_allow_html=True)
    
    # 가상자산 데이터 가져오기
    crypto_info = get_all_crypto_info()
    korean_names = load_korean_names()

    if not crypto_info:
        st.error("가상자산 데이터를 가져올 수 없습니다.")
        return

    # 사용자로부터 투자 금액 및 코인 선택 입력 받기
    weekly_investment = st.number_input("주간 투자 금액을 입력하세요 (원):", min_value=1000, step=1000)
    selected_coin = st.selectbox("투자할 코인을 선택하세요:", list(korean_names.values()))

    # 선택한 코인에 대한 정보 가져오기
    coin_key = list(korean_names.keys())[list(korean_names.values()).index(selected_coin)]
    url = f"https://api.bithumb.com/public/ticker/{coin_key}_KRW"
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
    historical_url = f"https://api.bithumb.com/public/candlestick/{coin_key}_KRW/24h"
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
        - 예, 비트알고는 가상화폐 시장에 익숙하지 않은 초보자도 쉽게 사용할 수 있도록 다양한 정보를 제공합니다.
    4. **교육 자료는 어떤 내용으로 구성되어 있나요?**
        - 기본적인 가상화폐 투자 개념부터 차트 분석, 경제 지표 해석, 리스크 관리 방법까지 다양한 교육 자료를 제공합니다. 
          또한, 실시간 가상화폐 뉴스와 시장 분석 정보를 통해 최신 동향을 학습할 수 있습니다.
    5. **어떤 디바이스에서 사용할 수 있나요?**
        - 비트알고는 웹 기반 플랫폼으로, PC 및 모바일 브라우저에서 모두 사용할 수 있습니다. 언제 어디서든 간편하게 접속하여 가상화폐시장에 접근할 수 있습니다. 
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
                historical_prices = [float(entry[2]) for entry in historical_data['data']]
                historical_dates = [pd.to_datetime(entry[0], unit='ms').strftime('%Y-%m-%d %H:%M:%S') for entry in historical_data['data']]
                
                historical_df = pd.DataFrame({'시간': historical_dates, '가격 (KRW)': historical_prices})
                
                # 가격 변동 캔들스틱 차트
                ohlc_data = []
                for entry in historical_data['data'][-24:]:
                    timestamp = pd.to_datetime(entry[0], unit='ms').strftime('%Y-%m-%d %H:%M:%S')
                    open_price = float(entry[1])
                    high_price = float(entry[3])
                    low_price = float(entry[4])
                    close_price = float(entry[2])
                    ohlc_data.append([timestamp, open_price, high_price, low_price, close_price])
                
                ohlc_df = pd.DataFrame(ohlc_data, columns=['시간', '시가', '고가', '저가', '종가'])
                
                # 캔들스틱 차트 생성
                fig_candlestick = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.1)
                fig_candlestick.add_trace(go.Candlestick(
                    x=ohlc_df['시간'],
                    open=ohlc_df['시가'],
                    high=ohlc_df['고가'],
                    low=ohlc_df['저가'],
                    close=ohlc_df['종가'],
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    name='캔들스틱 차트'
                ), row=1, col=1)
                
                # 거래량 데이터 추가
                volume_data = [float(entry[5]) for entry in historical_data['data'][-24:]]
                ohlc_df['거래량'] = volume_data
                
                fig_candlestick.add_trace(go.Bar(
                    x=ohlc_df['시간'],
                    y=ohlc_df['거래량'],
                    name='거래량',
                    marker_color='blue'
                ), row=2, col=1)
                
                # 툴팁 한글로 변경
                fig_candlestick.update_traces(
                    hovertext=[f"날짜: {row['시간']}<br>시가: {row['시가']} KRW<br>고가: {row['고가']} KRW<br>저가: {row['저가']} KRW<br>종가: {row['종가']} KRW<br>거래량: {row['거래량']}" for index, row in ohlc_df.iterrows()],
                    hoverinfo='text',
                    row=1, col=1
                )
                
                # 차트 옆에 설명 추가
                fig_candlestick.update_layout(
                    title=f'{selected_coin} 가격 변동 (캔들스틱 차트)',
                    xaxis_title='시간',
                    yaxis_title='가격 (KRW)',
                    xaxis_rangeslider_visible=False,
                    annotations=[
                        dict(
                            x=1.05,
                            y=0.5,
                            xref='paper',
                            yref='paper',
                            showarrow=False,
                            align='left',
                            font=dict(size=12)
                        )
                    ]
                )
                
                st.plotly_chart(fig_candlestick)

                  # 캔들스틱 차트 설명 추가
                st.write('''
                    **캔들스틱 차트란?**
                    
                    캔들스틱 차트는 특정 시간 동안의 시가, 고가, 저가, 종가를 시각화한 것입니다. 
                    - **시가(Open)**: 해당 시간대의 첫 거래 가격
                    - **고가(High)**: 해당 시간대의 최고 거래 가격
                    - **저가(Low)**: 해당 시간대의 최저 거래 가격
                    - **종가(Close)**: 해당 시간대의 마지막 거래 가격
                    
                    초록색 막대는 종가가 시가보다 높을 때 나타나며, 이는 해당 시간대에 가격이 상승했음을 의미합니다. 
                         
                    반면 빨간색 막대는 종가가 시가보다 낮을 때 나타나며, 이는 가격이 하락했음을 의미합니다.
                ''')

                # 도미넌스 차트 추가 (선 그래프 형태)
                # 선택한 코인에 따라 실제 도미넌스 데이터 반영
                try:
                    if coin_symbol == 'BTC':
                        dominance_data = [45 + i % 5 for i in range(12)]  # 비트코인 도미넌스 데이터 (예시)
                    elif coin_symbol == 'ETH':
                        dominance_data = [20 + i % 3 for i in range(12)]  # 이더리움 도미넌스 데이터 (예시)
                    else:
                        dominance_data = [10 + i % 2 for i in range(12)]  # 기타 코인 도미넌스 데이터 (예시)
                except Exception as e:
                    st.error("도미넌스 데이터를 가져오는 중 오류가 발생했습니다: " + str(e))
                    return
                
                fig_dominance = go.Figure()
                fig_dominance.add_trace(
                    go.Scatter(
                        x=historical_df['시간'],
                        y=dominance_data,
                        mode='lines+markers',
                        name='도미넌스 (%)',
                        line=dict(color='blue')
                    )
                )
                fig_dominance.update_layout(title=f'{selected_coin} 도미넌스 차트', xaxis_title='시간', yaxis_title='도미넌스 (%)')
                st.plotly_chart(fig_dominance)
                
                # 간단한 설명 추가
                st.write('''
                    **도미넌스 차트란?**
                    
                    도미넌스는 해당 자산이 전체 시장에서 차지하는 비율을 의미합니다. 일반적으로 도미넌스가 높을수록 해당 자산의 시장 내 영향력이 크다는 것을 나타냅니다.
                ''')
            else:
                st.error("역사적 데이터를 가져오지 못했습니다.")
        else:
            st.error("역사적 데이터를 가져오지 못했습니다.")

# API 키 설정
NEWS_API_KEY = 'ae924ae2406048d39816221dd4632006'

# googletrans 번역기 설정
translator = Translator()

# NewsAPI에서 뉴스 데이터를 가져오는 함수
def get_crypto_news():
    keywords = ["cryptocurrency", "bitcoin", "ethereum", "blockchain"]
    unique_articles = []
    seen_titles = set()

    for keyword in keywords:
        url = f"https://newsapi.org/v2/everything?q={keyword}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data['articles']

            # 중복 기사 제거 (제목을 기준으로 중복된 기사 제거)
            for article in articles:
                title = article.get('title')
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_articles.append(article)
        else:
            st.error(f"'{keyword}' 뉴스 데이터를 가져오는 데 실패했습니다.")

    return unique_articles

# GDELT API에서 뉴스 데이터를 가져오는 함수
def get_gdelt_crypto_news():
    gdelt_url = "https://api.gdeltproject.org/api/v2/doc/doc?query=cryptocurrency&mode=artlist&format=json&maxrecords=100"
    response = requests.get(gdelt_url)

    if response.status_code == 200:
        try:
            news_data = response.json()
            articles = news_data.get("articles", [])
            return articles  # 기사 목록 반환
        except ValueError:
            st.error("GDELT 뉴스 데이터의 JSON 파싱에 실패했습니다.")
            return []
    else:
        st.error(f"GDELT 뉴스 데이터를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
        return []

# NewsAPI와 GDELT 뉴스 데이터를 통합하는 함수
def get_combined_news():
    articles = get_crypto_news()  # NewsAPI 뉴스
    gdelt_articles = get_gdelt_crypto_news()  # GDELT 뉴스

    combined_articles = []
    seen_titles = set()

    # NewsAPI 기사 추가 (중복 체크)
    for article in articles:
        title = article.get('title')
        if title not in seen_titles:
            seen_titles.add(title)
            combined_articles.append(article)

    # GDELT 뉴스 기사 추가 (중복 체크)
    for article in gdelt_articles:
        title = article.get('title')
        if title not in seen_titles:
            seen_titles.add(title)
            combined_articles.append(article)

    return combined_articles

# 가장 많이 등장하는 단어를 추출하는 함수
def get_top_keywords(articles, top_n=10):
    all_text = " ".join([article.get('title', '') for article in articles])
    words = re.findall(r'\w+', all_text.lower())
    stop_words = set(['the', 'and', 'of', 'in', 'to', 'a', 'is', 'for', 'on', 'with', 'that', 'by', 'from'])
    filtered_words = [word for word in words if word not in stop_words]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

# 뉴스 카드 UI 생성 함수 (리스트 형식 및 이미지 포함)
def create_news_list_with_images(articles):
    # 실시간 핫토픽 출력 - 실시간 검색어처럼 변경
    top_keywords = get_top_keywords(articles)
    st.markdown("<h2 style='font-size:24px; color:#FF6347; text-align:center; margin-bottom:20px;'>실시간 핫토픽</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    hot_topics_html_1 = "<div style='background-color: #f9f9f9; padding: 20px; border-radius: 10px;'><ul style='list-style:none; padding:0; font-size:18px; color:#333;'>"
    hot_topics_html_2 = "<div style='background-color: #f9f9f9; padding: 20px; border-radius: 10px;'><ul style='list-style:none; padding:0; font-size:18px; color:#333;'>"


    for i, (word, count) in enumerate(top_keywords):
        arrow_icon = "<span style='color:green;'>&uarr;</span>" if i % 2 == 0 else "<span style='color:red;'>&darr;</span>"
        style = "font-weight:bold;" if i < 3 else ""
        if i < 5:
            hot_topics_html_1 += f"<li style='margin: 10px 0; {style}'><span style='color:#007ACC;'>{i+1}. {word}</span> {arrow_icon} - {count}건</li>"
        else:
            hot_topics_html_2 += f"<li style='margin: 10px 0; {style}'><span style='color:#007ACC;'>{i+1}. {word}</span> {arrow_icon} - {count}건</li>"

    hot_topics_html_1 += "</ul>"
    hot_topics_html_2 += "</ul>"

    with col1:
        st.markdown(hot_topics_html_1, unsafe_allow_html=True)
    with col2:
        st.markdown(hot_topics_html_2, unsafe_allow_html=True)

    # 주요 뉴스 리스트 출력
    st.markdown("<h2 style='font-size:24px; color:#007ACC; text-align:center; margin-bottom:20px;'>주요 뉴스</h2>", unsafe_allow_html=True)
    top_articles = sorted(articles, key=lambda x: x.get('source', {}).get('name', ''), reverse=True)[:10]
    for i, article in enumerate(top_articles):
        title = article.get('title') if 'title' in article else article.get('name')
        url = article.get('url')
        image_url = article.get('urlToImage') if 'urlToImage' in article else article.get('image', {}).get('thumbnail', {}).get('contentUrl')

        st.markdown(f"<div style='display: flex; align-items: center; padding: 10px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 15px;'>"
                    f"<div style='flex: 1; margin-right: 15px;'>"
                    f"<img src='{image_url}' style='width: 100%; height: auto; border-radius: 10px;' />"
                    f"</div>"
                    f"<div style='flex: 2;'>"
                    f"<h4 style='color: #333;'>{i+1}. {title}</h4>"
                    f"<a href='{url}' target='_blank'>"
                    f"<button style='background-color:#4CAF50; color:white; padding:10px; border:none; cursor:pointer; border-radius: 5px;'>"
                    f"원본 기사 보러가기"
                    f"</button>"
                    f"</a>"
                    f"</div>"
                    f"</div>", unsafe_allow_html=True)

    # 관련 뉴스 이미지 출력
    st.markdown("<h2 style='font-size:24px; color:#007ACC; text-align:center; margin-top: 40px;'>관련 뉴스</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if len(articles) > 10:
        with col1:
            image_url = articles[10].get('urlToImage') if 'urlToImage' in articles[10] else articles[10].get('image', {}).get('thumbnail', {}).get('contentUrl')
            title = articles[10].get('title') if 'title' in articles[10] else articles[10].get('name')
            url = articles[10].get('url')
            if image_url:
                image_html = f"""
                <a href="{url}" target="_blank">
                    <div style="position: relative;">
                        <img src="{image_url}" style="width:100%; height:auto; border-radius: 10px;" />
                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0, 0, 0, 0.5); color: #fff; padding: 5px; text-align: center; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                            {title}
                        </div>
                    </div>
                </a>
                """
                st.markdown(image_html, unsafe_allow_html=True)

        if len(articles) > 11:
            with col2:
                image_url = articles[11].get('urlToImage') if 'urlToImage' in articles[11] else articles[11].get('image', {}).get('thumbnail', {}).get('contentUrl')
                title = articles[11].get('title') if 'title' in articles[11] else articles[11].get('name')
                url = articles[11].get('url')
                if image_url:
                    image_html = f"""
                    <a href="{url}" target="_blank">
                        <div style="position: relative;">
                            <img src="{image_url}" style="width:100%; height:auto; border-radius: 10px;" />
                            <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0, 0, 0, 0.5); color: #fff; padding: 5px; text-align: center; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                                {title}
                            </div>
                        </div>
                    </a>
                    """
                    st.markdown(image_html, unsafe_allow_html=True)

# 카드 뉴스 페이지 함수
def show_card_news():
    st.markdown("<h2 style='font-size:30px; color:#007ACC; text-align:center;'>카드 뉴스</h2>", unsafe_allow_html=True)
    
    # API로부터 뉴스 데이터 가져오기
    articles = get_combined_news()

    if articles:
        create_news_list_with_images(articles)
    else:
        st.write("표시할 뉴스가 없습니다.")

# 페이지 라우팅
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴 선택",  # required
        options=["프로젝트 소개", "실시간 가상자산 시세", "모의 투자", "카드 뉴스", "알고있으면 좋은 경제 지식", "가이드", "문의 및 피드백"],  # required
        icons=["house", "graph-up", "wallet", "newspaper", "book", "question-circle", "envelope"],  # optional
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
elif selected == "카드 뉴스":
    show_card_news()  # 카드 뉴스 페이지 함수 호출
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
