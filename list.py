from flask import Flask, render_template
import requests

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

@app.route('/')
def index():
    crypto_data = get_all_crypto_info()
    market_data = get_all_market_info()
    print("Crypto Data:", crypto_data)
    print("Market Data:", market_data)
    # 마켓 데이터를 순회하며 필요한 정보만 정리
    processed_data = []

    if isinstance(market_data, list):  # market_data가 리스트인지 확인
        for market_info in market_data:
            market_key = market_info['market']
            # 'KRW-'를 제거한 후 key로 사용
            clean_market_key = market_key.replace('KRW-', '')
            if clean_market_key in crypto_data:
                processed_data.append({
                    'korean_name': market_info['korean_name'],
                    'market': market_key,
                    'closing_price': crypto_data[clean_market_key].get('closing_price', 'N/A'),
                    'fluctate_rate_24H': crypto_data[clean_market_key].get('fluctate_rate_24H', 'N/A'),
                    'fluctate_24H': crypto_data[clean_market_key].get('fluctate_24H', 'N/A'),
                    'acc_trade_value_24H': crypto_data[clean_market_key].get('acc_trade_value_24H', 'N/A')
                })
    if not processed_data:
        print("No data was processed. Please check API responses.")
    
    return render_template('index.html', processed_data=processed_data)

if __name__ == '__main__':
    app.run(debug=True)
