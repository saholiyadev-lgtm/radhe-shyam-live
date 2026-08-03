from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import time
import re

app = Flask(__name__)

# સર્વર માટે ગ્લોબલ બેકઅપ ડેટા (સ્ક્રીન ક્યારેય ખાલી નહીં થાય)
last_valid_data = [
    {"item_name": "GOLD", "buy_price": "4065.65", "sell_price": "4065.65"},
    {"item_name": "SILVER", "buy_price": "58.18", "sell_price": "58.18"},
    {"item_name": "USD INR", "buy_price": "95.390", "sell_price": "95.390"},
    {"item_name": "GLD 999 IMP AMD T+1", "buy_price": "147260", "sell_price": "147260"},
    {"item_name": "GLD 999 IMP RJT T+1", "buy_price": "147280", "sell_price": "147280"},
    {"item_name": "GLD 22 CARAT (RJT)", "buy_price": "135006.67", "sell_price": "135006.67"},
    {"item_name": "GLD 18 CARAT (RJT)", "buy_price": "110460.00", "sell_price": "110460.00"},
    {"item_name": "SLVCHORSA T+1", "buy_price": "220580", "sell_price": "220580"},
    {"item_name": "SLVPETI999 T+1", "buy_price": "224500", "sell_price": "224500"},
    {"item_name": "SLV 999 (1 KG BAR) T+1", "buy_price": "226500", "sell_price": "226500"}
]

def fetch_live_jk_rates():
    global last_valid_data
    
    timestamp = int(time.time() * 1000)
    url = f"https://jksons.in/?_={timestamp}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://jksons.in/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_data = []
            
            # તમામ Row સ્કેન કરો
            for row in soup.find_all('tr'):
                cells = [c.text.strip() for c in row.find_all(['td', 'th']) if c.text.strip()]
                if len(cells) >= 2:
                    product = cells[0]
                    rate = cells[1]
                    
                    # હેડર વગરનો સાચો રેટ ફિલ્ટર કરો
                    if "SYMBOL" not in product.upper() and "RATE" not in rate.upper():
                        # જો રેટ ડિજિટલ ફોર્મેટમાં હોય તો જ લો
                        if re.search(r'\d', rate):
                            live_data.append({
                                "item_name": product,
                                "buy_price": rate,
                                "sell_price": rate
                            })
                            
                            # ૨૨K અને ૧૮K માટે ઓટો કેલ્ક્યુલેશન
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

            # જો નવો ડેટા સફળતાપૂર્વક મળ્યો હોય તો જ અપડેટ કરો
            if len(live_data) > 0:
                last_valid_data = live_data

    except Exception as e:
        print(f"Error fetching data: {e}")
        
    # ગમે તે થાય, આ ક્યારેય ખાલી રિટર્ન નહીં કરે
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
