from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# કેશ અને ટાઈમસ્ટોર
cached_data = []
last_fetch_time = 0

def fetch_live_jk_rates():
    global cached_data, last_fetch_time
    current_time = time.time()
    
    # દર ૧ સેકન્ડે જ નવો ડેટા લાવશે જેથી JK Sons પર લોડ ના પડે અને રિસ્પોન્સ ફાસ્ટ રહે
    if current_time - last_fetch_time < 1 and cached_data:
        return cached_data

    timestamp = int(current_time * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=4)
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
                        
                        # RJT ગોલ્ડનો લાઈવ ભાવ પકડીને 22 અને 18 કેરેટ ઓટો-કેલ્ક્યુલેટ કરો
                        if "GLD 999 IMP RJT" in product.upper():
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
                cached_data = live_data
                last_fetch_time = current_time
                return live_data

    except Exception as e:
        print(f"Error fetching live data: {e}")
        
    return cached_data

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
