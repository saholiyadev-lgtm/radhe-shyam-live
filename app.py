from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# ડિફોલ્ટ બેકઅપ
last_fetched_rates = [
    {"item_name": "GOLD", "buy_price": "4042.05", "sell_price": "4042.05"},
    {"item_name": "SILVER", "buy_price": "57.62", "sell_price": "57.62"},
    {"item_name": "USD INR", "buy_price": "95.390", "sell_price": "95.390"},
    {"item_name": "GLD 999 IMP AMD T+1", "buy_price": "147260", "sell_price": "147260"},
    {"item_name": "GLD 999 IMP RJT T+1", "buy_price": "147280", "sell_price": "147280"},
    {"item_name": "GLD 22 CARAT (RJT)", "buy_price": "135006.67", "sell_price": "135006.67"},
    {"item_name": "GLD 18 CARAT (RJT)", "buy_price": "110460.00", "sell_price": "110460.00"},
    {"item_name": "SLVCHORSA T+1", "buy_price": "220580", "sell_price": "220580"},
    {"item_name": "SLVPETI999 T+1", "buy_price": "224500", "sell_price": "224500"},
    {"item_name": "SLV 999 (1 KG BAR) T+1", "buy_price": "226500", "sell_price": "226500"}
]

def fetch_jk_rates():
    global last_fetched_rates
    
    timestamp = int(time.time() * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    rate = cells[1].text.strip()
                    
                    if product and rate and product.upper() != "SYMBOL":
                        live_data.append({
                            "item_name": product,
                            "buy_price": rate,
                            "sell_price": rate
                        })
                        
                        # RJT ગોલ્ડનો લાઈવ ભાવ પકડીને 22 અને 18 કેરેટ ઉમેરો
                        if "GLD 999 IMP RJT" in product.upper():
                            try:
                                clean_rate = float(rate.replace(',', ''))
                                
                                # 22 Carat ગણતરી: (Price * 22) / 24
                                c22_rate = round((clean_rate * 22) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 22 CARAT (RJT)",
                                    "buy_price": f"{c22_rate:,.2f}",
                                    "sell_price": f"{c22_rate:,.2f}"
                                })
                                
                                # 18 Carat ગણતરી: (Price * 18) / 24
                                c18_rate = round((clean_rate * 18) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 18 CARAT (RJT)",
                                    "buy_price": f"{c18_rate:,.2f}",
                                    "sell_price": f"{c18_rate:,.2f}"
                                })
                            except ValueError:
                                pass

            if len(live_data) > 0:
                last_fetched_rates = live_data
                return live_data
                
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return last_fetched_rates

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_jk_rates()
    response = jsonify(rates)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
