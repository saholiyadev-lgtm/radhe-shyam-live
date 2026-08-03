from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# છેલ્લો સાચો ડેટા સાચવી રાખવા માટે (જેથી ક્યારેય સાઈટ ખાલી ના થાય)
last_valid_data = []

def fetch_live_jk_rates():
    global last_valid_data
    
    timestamp = int(time.time() * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            
            # ટેબલમાંથી રો શોધો
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    product = cells[0].text.strip()
                    rate = cells[1].text.strip()
                    
                    # હેડર વગરનો સાચો ભાવ જ ફિલ્ટર કરો
                    if product and rate and "SYMBOL" not in product.upper() and "RATE" not in rate.upper():
                        live_data.append({
                            "item_name": product,
                            "buy_price": rate,
                            "sell_price": rate
                        })
                        
                        # GLD 999 IMP RJT નો ભાવ પકડીને 22K અને 18K ગણો
                        if "GLD 999" in product.upper() and "RJT" in product.upper():
                            try:
                                clean_rate = float(rate.replace(',', ''))
                                
                                c22_rate = round((clean_rate * 22) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 22 CARAT (RJT)",
                                    "buy_price": f"{c22_rate:,.2f}",
                                    "sell_price": f"{c22_rate:,.2f}"
                                })
                                
                                c18_rate = round((clean_rate * 18) / 24, 2)
                                live_data.append({
                                    "item_name": "GLD 18 CARAT (RJT)",
                                    "buy_price": f"{c18_rate:,.2f}",
                                    "sell_price": f"{c18_rate:,.2f}"
                                })
                            except ValueError:
                                pass

            if len(live_data) > 0:
                last_valid_data = live_data
                return live_data

    except Exception as e:
        print(f"Fetch Error: {e}")
        
    # જો કોઈ કારણસર નવો ડેટા ના મળે તો જૂનો સાચો ડેટા બતાવો પણ સ્ક્રીન ખાલી ના થવા દો
    return last_valid_data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rates')
def get_rates():
    rates = fetch_live_jk_rates()
    response = jsonify(rates)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
