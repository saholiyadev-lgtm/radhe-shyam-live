from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

API_URL = "https://bcast.jksons.in:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/jksons"

# છેલ્લો valid data
last_data = []

def fetch_rates():
    global last_data

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        }

        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()

        lines = response.text.splitlines()

        data = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            parts = line.split()

            # પહેલી value code હોવી જોઈએ
            if not parts[0].isdigit():
                continue

            # પ્રથમ number શોધો (product name પછી)
            first_num = None

            for i in range(1, len(parts)):
                try:
                    float(parts[i].replace(",", ""))
                    first_num = i
                    break
                except:
                    continue

            if first_num is None:
                continue

            name = " ".join(parts[1:first_num])

            numbers = parts[first_num:]

            buy = numbers[0]

            if len(numbers) > 1:
                sell = numbers[1]
            else:
                sell = buy

            data.append({
                "item_name": name,
                "buy_price": buy,
                "sell_price": sell
            })

        # 22K અને 18K Auto Calculate
        for item in data.copy():

            if "GLD 999 IMP RJT" in item["item_name"]:

                try:

                    rate = float(item["buy_price"].replace(",", ""))

                    rate22 = round(rate * 22 / 24, 2)
                    rate18 = round(rate * 18 / 24, 2)

                    data.append({
                        "item_name": "GLD 22 CARAT (RJT)",
                        "buy_price": f"{rate22:.2f}",
                        "sell_price": f"{rate22:.2f}"
                    })

                    data.append({
                        "item_name": "GLD 18 CARAT (RJT)",
                        "buy_price": f"{rate18:.2f}",
                        "sell_price": f"{rate18:.2f}"
                    })

                except:
                    pass

        if data:
            last_data = data

    except Exception as e:
        print("ERROR:", e)

    return last_data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/rates")
def api_rates():
    response = jsonify(fetch_rates())
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
