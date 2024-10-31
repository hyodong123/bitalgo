import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import plotly.express as px  # 오류 해결을 위한 추가
import streamlit.components.v1 as components
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup  # BeautifulSoup 모듈 정의 추가
from googlesearch import search  # Google 검색을 위한 추가

########################### 비트알고 프로젝트 소개 ##############################

# 비트알고 프로젝트 소개
def show_project_intro():
    st.write("**비트알고 프로젝트**")
    st.write('''
        비트알고 프로젝트는 사용자에게 실시간 가상자산 시세 정보를 제공하고,
        다양한 기술적 분석 도구를 활용하여 시장 데이터를 시각화하는 플랫폼입니다.
        주요 기능으로는 가상자산 시세 확인, 이동평균, MACD, 볼린저 밴드 등 다양한 기술적 지표를 제공하여
        사용자들이 보다 효과적으로 투자 결정을 할 수 있도록 돕습니다.
    ''')

    # 워드 클라우드 생성 및 표시 (프로젝트 주요 키워드)
    try:
        # 웹에서 한글 폰트 다운로드
        font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        font_path = "./NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(font_url, font_path)

        # 키워드 추출 및 워드클라우드 생성
        keywords = '비트알고 실시간 가상자산 시세 기술적 분석 이동평균 MACD 볼린저밴드 CCI 투자 암호화폐 거래소 트레이딩 스토캐스틱 RSI 알트코인 비트코인 이더리움 리플 기술적지표 추세분석 거래량 패턴분석 포트폴리오 관리 위험관리 차트분석 cryptocurrency blockchain real-time trading moving average Bollinger Bands MACD CCI investment crypto exchange stochastic RSI altcoin Bitcoin Ethereum Ripple technical analysis trend analysis volume analysis pattern analysis portfolio management risk management chart analysis market data visualization'
        keyword_list = keywords.split()
        keyword_counts = Counter(keyword_list)

        wordcloud = WordCloud(font_path=font_path, width=1200, height=800, background_color='white', max_words=200, collocations=False).generate_from_frequencies(keyword_counts)
        
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        st.pyplot(plt)
    except ModuleNotFoundError:
        st.error("WordCloud 모듈을 찾을 수 없습니다. 'pip install wordcloud' 명령어로 설치하세요.")
    except FileNotFoundError:
        st.error("한글 폰트를 찾을 수 없습니다. 폰트 경로를 확인하세요.")
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
        
########################### 실시간 가상자산 시세 ##############################
# 가상자산 정보 가져오기 함수
def get_all_crypto_info():
    url = "https://api.bithumb.com/public/ticker/ALL_KRW"
    response = requests.get(url, timeout=10)
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

# 코인 이름 로드 함수
def load_korean_names():
    try:
        df = pd.read_csv('./mnt/data/crypto_korean_names.csv')
        return dict(zip(df['코인'], df['코인 이름']))
    except Exception as e:
        st.error(f"코인 이름 CSV 파일을 로드하는 데 실패했습니다: {e}")
        return {}

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
                historical_volumes = [float(entry[5]) for entry in historical_data['data']]
                
                historical_df = pd.DataFrame({'시간': historical_dates, '가격 (KRW)': historical_prices, '거래량': historical_volumes})
                
                # 이동평균(Moving Average) 계산 및 추가
                historical_df['이동평균 (5일)'] = historical_df['가격 (KRW)'].rolling(window=5).mean()
                historical_df['이동평균 (10일)'] = historical_df['가격 (KRW)'].rolling(window=10).mean()
                
                # RSI (Relative Strength Index) 계산
                delta = historical_df['가격 (KRW)'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                historical_df['RSI (14)'] = 100 - (100 / (1 + rs))
                
                # MACD (Moving Average Convergence Divergence) 계산
                short_ema = historical_df['가격 (KRW)'].ewm(span=12, adjust=False).mean()
                long_ema = historical_df['가격 (KRW)'].ewm(span=26, adjust=False).mean()
                historical_df['MACD'] = short_ema - long_ema
                historical_df['Signal Line'] = historical_df['MACD'].ewm(span=9, adjust=False).mean()
                
                # 볼린저 밴드 (Bollinger Bands) 계산
                historical_df['볼린저 중간선'] = historical_df['가격 (KRW)'].rolling(window=20).mean()
                historical_df['볼린저 상단'] = historical_df['볼린저 중간선'] + (historical_df['가격 (KRW)'].rolling(window=20).std() * 2)
                historical_df['볼린저 하단'] = historical_df['볼린저 중간선'] - (historical_df['가격 (KRW)'].rolling(window=20).std() * 2)
                
                # CCI (Commodity Channel Index) 계산
                tp = (historical_df['가격 (KRW)'] + historical_df['가격 (KRW)'] + historical_df['가격 (KRW)']) / 3
                ma = tp.rolling(window=20).mean()
                md = tp.rolling(window=20).apply(lambda x: np.fabs(x - x.mean()).mean(), raw=True)
                historical_df['CCI'] = (tp - ma) / (0.015 * md)
                
                # 슬라이더 바 기능 추가 (기간 설정)
                start_date, end_date = st.slider(
                    "기간을 선택하세요",
                    min_value=pd.to_datetime(historical_df['시간']).min().to_pydatetime(),
                    max_value=pd.to_datetime(historical_df['시간']).max().to_pydatetime(),
                    value=(pd.to_datetime(historical_df['시간']).min().to_pydatetime(), pd.to_datetime(historical_df['시간']).max().to_pydatetime())
                )
                
                # 선택된 기간으로 데이터 필터링
                mask = (
                    (pd.to_datetime(historical_df['시간']) >= start_date) &
                    (pd.to_datetime(historical_df['시간']) <= end_date)
                )
                filtered_df = historical_df.loc[mask]
                
                # 가격 변동 및 이동평균 차트
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=filtered_df['시간'],
                    y=filtered_df['가격 (KRW)'],
                    mode='lines',
                    name='가격 (KRW)'
                ))
                
                # 선택된 추가 기능에 따라 차트에 추가
                options = st.multiselect(
                    "추가할 기술적 지표를 선택하세요", ['이동평균 (5일)', '이동평균 (10일)', 'MACD', '볼린저 밴드', 'CCI']
                )
                
                if '이동평균 (5일)' in options:
                    fig.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['이동평균 (5일)'],
                        mode='lines',
                        name='이동평균 (5일)',
                        line=dict(dash='dot')
                    ))
                if '이동평균 (10일)' in options:
                    fig.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['이동평균 (10일)'],
                        mode='lines',
                        name='이동평균 (10일)',
                        line=dict(dash='dash')
                    ))
                
                # MACD 차트를 별도로 표시
                if 'MACD' in options:
                    st.write(f"**{selected_coin} MACD 지표**")
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='purple')
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['Signal Line'],
                        mode='lines',
                        name='Signal Line',
                        line=dict(color='blue', dash='dot')
                    ))
                    fig_macd.update_layout(title=f'{selected_coin} MACD', xaxis_title='시간', yaxis_title='값')
                    st.plotly_chart(fig_macd)
                
                # CCI 차트를 별도로 표시
                if 'CCI' in options:
                    st.write(f"**{selected_coin} CCI 지표**")
                    fig_cci = go.Figure()
                    fig_cci.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['CCI'],
                        mode='lines',
                        name='CCI',
                        line=dict(color='brown')
                    ))
                    fig_cci.update_layout(title=f'{selected_coin} CCI', xaxis_title='시간', yaxis_title='값')
                    st.plotly_chart(fig_cci)
                
                # 볼린저 밴드 차트를 추가
                if '볼린저 밴드' in options:
                    fig.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['볼린저 상단'],
                        mode='lines',
                        name='볼린저 상단',
                        line=dict(color='green', dash='dot')
                    ))
                    fig.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['볼린저 하단'],
                        mode='lines',
                        name='볼린저 하단',
                        line=dict(color='red', dash='dot')
                    ))
                
                fig.update_layout(title=f'{selected_coin} 가격 및 기술적 지표', xaxis_title='시간', yaxis_title='가격 (KRW)')
                st.plotly_chart(fig)
                
                # RSI 차트 별도 시각화
                if 'RSI (14)' in options:
                    st.write(f"**{selected_coin} RSI (14) 지표**")
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(
                        x=filtered_df['시간'],
                        y=filtered_df['RSI (14)'],
                        mode='lines',
                        name='RSI (14)',
                        line=dict(color='orange')
                    ))
                    fig_rsi.update_layout(title=f'{selected_coin} RSI (14)', xaxis_title='시간', yaxis_title='RSI')
                    st.plotly_chart(fig_rsi)
                
                # 거래량 차트 추가
                st.write(f"**{selected_coin} 거래량**")
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(
                    x=filtered_df['시간'],
                    y=filtered_df['거래량'],
                    name='거래량',
                    marker_color='blue'
                ))
                fig_volume.update_layout(title=f'{selected_coin} 거래량', xaxis_title='시간', yaxis_title='거래량')
                st.plotly_chart(fig_volume)
                
                # 간단한 설명 추가
                if '이동평균 (5일)' in options or '이동평균 (10일)' in options:
                    st.write('''
                        **이동평균(Moving Average)이란?**
                        
                        이동평균은 일정 기간 동안의 평균 가격을 의미하며, 가격 변동의 방향성을 확인하는 데 사용됩니다. 
                        - **단기 이동평균 (5일)**: 최근 5일 동안의 평균 가격을 나타내며, 단기적인 추세를 파악하는 데 유용합니다.
                        - **장기 이동평균 (10일)**: 최근 10일 동안의 평균 가격을 나타내며, 보다 긴 추세를 확인하는 데 사용됩니다.
                    ''')
                
                if 'RSI (14)' in options:
                    st.write('''
                        **RSI (Relative Strength Index)란?**
                        
                        RSI는 자산의 과매수 또는 과매도 상태를 나타내는 기술적 지표입니다. 
                        - **RSI > 70**: 자산이 과매수 상태에 있으며 가격 조정 가능성이 높음을 의미합니다.
                        - **RSI < 30**: 자산이 과매도 상태에 있으며 반등 가능성이 있음을 의미합니다.
                    ''')
                
                if 'MACD' in options:
                    st.write('''
                        **MACD (Moving Average Convergence Divergence)란?**
                        
                        MACD는 단기 이동평균과 장기 이동평균의 차이를 이용해 가격 추세의 강도와 방향을 나타내는 지표입니다. Signal Line과의 교차를 통해 매수/매도 신호를 판단합니다.
                    ''')
                
                if '볼린저 밴드' in options:
                    st.write('''
                        **볼린저 밴드 (Bollinger Bands)란?**
                        
                        볼린저 밴드는 이동평균선을 중심으로 표준편차를 이용해 가격 변동성을 시각화한 지표입니다. 상단 밴드와 하단 밴드 사이의 간격을 통해 변동성을 확인할 수 있습니다.
                    ''')
                
                if 'CCI' in options:
                    st.write('''
                        **CCI (Commodity Channel Index)란?**
                        
                        CCI는 자산 가격의 변동성을 측정하여 과매수 및 과매도 상태를 파악하는 데 사용되는 지표입니다. 
                        - **CCI > 100**: 자산이 과매수 상태에 있으며 조정 가능성이 있음을 의미합니다.
                        - **CCI < -100**: 자산이 과매도 상태에 있으며 반등 가능성이 있음을 의미합니다.
                    ''')
            else:
                st.error("역사적 데이터를 가져오지 못했습니다.")
        else:
            st.error("역사적 데이터를 가져오지 못했습니다.")


#################################################모의투자##############################################
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

########################### 카드 뉴스 ##############################

# API 키 설정
NEWS_API_KEY = 'ae924ae2406048d39816221dd4632006'

# NewsAPI에서 뉴스 데이터를 가져오는 함수
def get_crypto_news():
    NEWS_API_KEY = 'ae924ae2406048d39816221dd4632006'
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
    stop_words = set([
        'the', 'and', 'of', 'in', 'to', 'a', 'is', 'for', 'on', 'with', 'that', 'by', 'from',
        'at', 'as', 'an', 'it', 'this', 'be', 'are', 'was', 'were', 'or', 'but', 'not', 'have',
        'has', 'had', 'can', 'could', 'should', 'would', 'about', 'more', 'some', 'other',
        'into', 'also', 'which', 'up', 'out', 'if', 'will', 'one', 'all', 'no', 'do', 'does',
        'did', 'just', 'than', 'so', 'only', 'over', 'its', 'new', 'like', 'how', 'when', 'them',
        'these', 'those', 'then', 'he', 'she', 'they', 'his', 'her', 'their', 'our', 'us',
        's', 'de', 'el', 'la', 'в', 'un', 'en', '2024'
    ])
    filtered_words = [word for word in words if word not in stop_words]
    word_counts = Counter(filtered_words)
    return word_counts.most_common(top_n)

# 뉴스 카드 UI 생성 함수 (리스트 형식 및 이미지 포함)
def create_news_list_with_images(articles):
    # 실시간 핫토픽 출력 - 실시간 검색어처럼 변경
    top_keywords = get_top_keywords(articles)
    st.markdown("<h2 style='font-size:24px; color:#FF6347; text-align:left; margin-bottom:20px;'>Hot Keyword</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    hot_topics_html_1 = "<div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px;'><ul style='list-style:none; padding:0; font-size:16px; color:#333;'>"
    hot_topics_html_2 = "<div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px;'><ul style='list-style:none; padding:0; font-size:16px; color:#333;'>"

    for i, (word, count) in enumerate(top_keywords):
        arrow_icon = "<span style='color:green;'>&uarr;</span>" if i % 2 == 0 else "<span style='color:red;'>&darr;</span>"
        if i < 5:
            hot_topics_html_1 += f"<li style='margin: 8px 0;'><span style='color:#007ACC;'>&#8226; {word}</span> {arrow_icon} - {count}건</li>"
        else:
            hot_topics_html_2 += f"<li style='margin: 8px 0;'><span style='color:#007ACC;'>&#8226; {word}</span> {arrow_icon} - {count}건</li>"

    hot_topics_html_1 += "</ul></div>"
    hot_topics_html_2 += "</ul></div>"

    with col1:
        st.markdown(hot_topics_html_1, unsafe_allow_html=True)
    with col2:
        st.markdown(hot_topics_html_2, unsafe_allow_html=True)

    # 주요 뉴스 리스트 출력
    for i, article in enumerate(articles[:10]):
        title = article.get('title')
        translated_title = title if title else ''
        url = article.get('url')
        image_url = article.get('urlToImage') if 'urlToImage' in article else article.get('image', {}).get('thumbnail', {}).get('contentUrl')
        description = article.get('description', '설명이 없습니다.')
        translated_description = description if description else ''

        news_card_html = f"""
        <div style='display: flex; align-items: flex-start; padding: 20px; border: 1px solid #ddd; border-radius: 15px; margin-bottom: 20px; background-color: #ffffff;'>
            <div style='flex: 1; margin-right: 20px;'>
                <img src='{image_url}' style='width: 300px; height: auto; border-radius: 10px;' />
            </div>
            <div style='flex: 2;'>
                <h3 style='color: #333; font-size: 22px; margin-bottom: 10px;'>&#11088; {translated_title}</h3>
                <p style='color: #555; font-size: 16px; margin-bottom: 20px; line-height: 1.5;'>{translated_description}</p>
                <a href='{url}' target='_blank' style='display: block; text-align: right;'><button style='background-color:#6b4e16; color:white; padding:10px 25px; border:none; cursor:pointer; border-radius: 5px;'>
                        기사 원문 보기
                    </button>
                </a>
            </div>
        </div>
        """
        st.markdown(news_card_html, unsafe_allow_html=True)

    # 관련 뉴스 이미지 출력
    if len(articles) > 10:
        st.markdown("<h2 style='font-size:24px; color:#007ACC; text-align:left; margin-top: 40px;'>관련 뉴스</h2>", unsafe_allow_html=True)
        for i in range(10, min(14, len(articles))):
            image_url = articles[i].get('urlToImage') if 'urlToImage' in articles[i] else articles[i].get('image', {}).get('thumbnail', {}).get('contentUrl')
            title = articles[i].get('title')
            translated_title = title if title else ''
            url = articles[i].get('url')
            if image_url:
                image_html = f"""
                <a href="{url}" target="_blank">
                    <div style="position: relative; margin-bottom: 20px;">
                        <img src="{image_url}" style="width:100%; height:auto; border-radius: 10px;" />
                        <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0, 0, 0, 0.5); color: #fff; padding: 5px; text-align: center; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;">
                            {translated_title}
                        </div>
                    </div>
                </a>
                """
                st.markdown(image_html, unsafe_allow_html=True)

def show_card_news():
    st.markdown("""
    <meta name='google' content='notranslate'>
    <h2 style='font-size:30px; color:#007ACC; text-align:center;'>카드 뉴스</h2>
<p style='text-align:center; color:#555;'>이 페이지는 최신 암호화폐 관련 뉴스를 제공합니다. 실시간 핫 키워드와 주요 기사를 확인해보세요.</p>    """, unsafe_allow_html=True)
    
    # API로부터 뉴스 데이터 가져오기
    articles = get_combined_news()

    if articles:
        create_news_list_with_images(articles)
    else:
        st.write("표시할 뉴스가 없습니다.")



########################### 알고 있으면 좋은 경제 지식 ##############################

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

#########################################경제 용어 사전 (네이버 api)#####################################

# 네이버 API 키 설정
NAVER_CLIENT_ID = 'BwZoRgXSJQ3l55bVrIKk'
NAVER_CLIENT_SECRET = 'd_sagtQMyV'

def show_glossary():
    st.markdown("""
        <div style='text-align: center;'>
            <h2 style='font-size: 36px; font-weight: bold; color: #4CAF50;'>경제 용어 사전</h2>
            <p style='font-size: 18px;'>원하는 용어를 검색해보세요:</p>
        </div>
    """, unsafe_allow_html=True)
    
    search_term = st.text_input("용어 입력", placeholder="예: 비트코인, 인플레이션 등")
    
    if search_term:
        try:
            # 네이버 검색 API를 사용하여 검색 결과 가져오기
            url = "https://openapi.naver.com/v1/search/encyc.json"
            headers = {
                "X-Naver-Client-Id": NAVER_CLIENT_ID,
                "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
            }
            params = {"query": search_term, "display": 5}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['items']:
                descriptions = []
                for item in data['items']:
                    title = item['title'].replace('<b>', '').replace('</b>', '')
                    description = item['description'].replace('<b>', '').replace('</b>', '')
                    link = item['link']
                    descriptions.append(f"""
                        <div style='border: 1px solid #ddd; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 6px 12px 0 rgba(0, 0, 0, 0.15);'>
                            <h3 style='font-size: 26px; color: #333; margin-bottom: 10px;'>{title}</h3>
                            <p style='font-size: 18px; color: #555; line-height: 1.6;'>{description}</p>
                            <div style='text-align: center; margin-top: 20px;'>
                                <button style='background-color: #4CAF50; color: white; border: none; padding: 12px 25px; text-align: center; text-decoration: none; display: inline-block; font-size: 18px; border-radius: 8px; cursor: pointer;' onclick="window.open('{link}', '_blank')">자세히 보기</button>
                            </div>
                        </div>
                    """)
                
                full_description = '\n'.join(descriptions)
                st.markdown(full_description, unsafe_allow_html=True)
            else:
                st.warning(f"'{search_term}'에 대한 정보를 찾을 수 없습니다.")
        except requests.exceptions.HTTPError as http_err:
            st.error(f"HTTP 오류 발생: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            st.error(f"연결 오류 발생: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            st.error(f"타임아웃 오류 발생: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            st.error(f"요청 오류 발생: {req_err}")

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



# 페이지 하단 푸터 추가
def footer():
    st.markdown(
        """
        <footer style="text-align: center; margin-top: 50px;">
            <hr>
            <p>&copy; 2024 Team 비트지니어스 - 비트알고 프로젝트. All Rights Reserved.</p>
        </footer>
        """,
        unsafe_allow_html=True
    )

# 페이지 라우팅
with st.sidebar:
    selected = option_menu(
        menu_title="메뉴 선택",  # required
        options=["프로젝트 소개", "실시간 가상자산 시세", "모의 투자", "카드 뉴스", "알고있으면 좋은 경제 지식", "경제용어사전", "가이드", "문의 및 피드백"],  # required
        icons=["house", "graph-up", "wallet", "newspaper", "book", "question-circle", "envelope"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
    )

# 선택된 메뉴에 따라 페이지 라우팅
if selected == "프로젝트 소개":
    show_project_intro()
    footer()
elif selected == "실시간 가상자산 시세":
    show_live_prices()
    footer()
elif selected == "모의 투자":
    show_investment_performance()
    footer()
elif selected == "카드 뉴스":
    show_card_news()  # 카드 뉴스 페이지 함수 호출
    footer()
elif selected == "알고있으면 좋은 경제 지식":
    show_edu()
    footer()
elif selected == "경제용어사전":
    show_glossary()
    footer()
elif selected == "가이드":
    show_guide()
    footer()
elif selected == "문의 및 피드백":
    show_feedback()
    footer()
