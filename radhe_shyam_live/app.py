from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# તેં મોકલેલા સ્ક્રીનશોટ પ્રમાણેના કન્ફર્મ લાસ્ટ પ્રાઈસ (ડિફોલ્ટ રેટ્સ)
last_fetched_rates = [
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
    global last_fetched_rates
    url = "https://jksons.in/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            rows = soup.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    rate = cells[1].text.strip()
                    
                    # જો ટેબલમાં રેટ પડેલા હોય તો એને લાઈવ અપડેટ કરો
                    if product and rate:
                        live_data.append({
                            "item_name": product,
                            "buy_price": rate,
                            "sell_price": rate
                        })
            
            if live_data:
                last_fetched_rates = live_data
                return live_data
                
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    # જો માર્કેટ બંધ હોય તો સ્ક્રીનશોટ વાળા સેવ કરેલા આંકડા જ બતાવશે
    return last_fetched_rates

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_jk_rates()
    return jsonify(rates)

if __name__ == '__main__':
    app.run(debug=True, port=5000)