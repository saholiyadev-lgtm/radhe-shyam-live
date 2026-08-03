from flask import Flask, render_template, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

API = "https://bcast.jksons.in:7768/VOTSBroadcastStreaming/Services/xml/GetLiveRateByTemplateID/jksons"

last_data = []

def fetch_rates():

    global last_data

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/xml,text/xml,*/*"
    }

    try:

        r = requests.get(API, headers=headers, timeout=15)

        r.raise_for_status()

        root = ET.fromstring(r.text)

        data = []

        for item in root.iter():

            tag = item.tag.lower()

            if "item" in tag:

                name = ""
                rate = ""

                for c in item:

                    t = c.tag.lower()

                    if "name" in t or "symbol" in t:

                        name = c.text.strip()

                    elif "rate" in t or "buy" in t or "price" in t:

                        rate = c.text.strip()

                if name and rate:

                    data.append({
                        "item_name": name,
                        "buy_price": rate,
                        "sell_price": rate
                    })

        if data:
            last_data = data

    except Exception as e:

        print(e)

    return last_data


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/api/rates")
def api():

    return jsonify(fetch_rates())


if __name__ == "__main__":

    app.run()
