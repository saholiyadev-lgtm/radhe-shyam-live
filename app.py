from flask import Flask, render_template, jsonify
import requests
import time

app = Flask(__name__)

# ડિફોલ્ટ બેકઅપ ડેટા
default_rates = [
    {"item_name": "GOLD", "buy_price": "4019.05", "sell_price": "4019.05"},
    {"item_name": "SILVER", "buy_price": "55.99", "sell_price": "55.99"},
    {"item_name": "USD INR", "buy_price": "96.320", "sell_price": "96.320"},
    {"item_name": "GLD 999 IMP AMD T+1", "buy_price": "146230", "sell_price": "146230"},
    {"item_name": "GLD 999 IMP RJT T+1", "buy_price": "146250", "sell_price": "146250"},
    {"item_name": "SLVCHORSA T+1", "buy_price": "221000", "sell_price": "221000"},
    {"item_name": "SLVPETI999 T+1", "buy_price": "225000", "sell_price": "225000"},
    {"item_name": "SLV 999 (1 KG BAR) T+1", "buy_price": "227000", "sell_price": "227000"}
]

def fetch_jk_rates():
    # JK Sons નું લાઈવ AJAX / Socket API Endpoint
    # અહીં જ ડાયરેક્ટ રિયલ-ટાઇમ લાઈવ રેટ્સ આવે છે
    url = f"https://jksons.in/webservices/getrates.php?_={int(time.time()*1000)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://jksons.in/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data
    except Exception as e:
        print(f"Error fetching live API: {e}")
        
    return default_rates

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_jk_rates()
    response = jsonify(rates)
    # કેશિંગ બંધ કરવા માટે હેડર્સ
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
