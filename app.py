from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

last_valid_data = []

def fetch_live_jk_rates():
    global last_valid_data
    
    timestamp = int(time.time() * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            
            # ૧. તમામ ટેબલમાંથી ડેટા સ્ક્રેપ કરો
            for row in soup.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    rate = cells[1].text.strip()
                    
                    if product and rate and "SYMBOL" not in product.upper() and "RATE" not in rate.upper():
                        live_data.append({
                            "item_name": product,
                            "buy_price": rate,
                            "sell_price": rate
                        })
                        
                        # GLD 999 IMP RJT પરથી 22K અને 18K નો નવો ભાવ
                        if "GLD 999" in product.upper() and "RJT" in product.upper():
                            try:
                                clean_rate = float(rate.replace(',', ''))
                                
                                c22 = round((clean_rate * 22) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 22 CARAT (RJT)",
                                    "buy_price": f"{c22:,.2f}",
                                    "sell_price": f"{c22:,.2f}"
                                })
                                
                                c18 = round((clean_rate * 18) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 18 CARAT (RJT)",
                                    "buy_price": f"{c18:,.2f}",
                                    "sell_price": f"{c18:,.2f}"
                                })
                            except ValueError:
                                pass

            if len(live_data) > 0:
                last_valid_data = live_data
                return live_data

    except Exception as e:
        print(f"Scraping Error: {e}")
        
    return last_valid_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_live_jk_rates()
    response = jsonify(rates)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
