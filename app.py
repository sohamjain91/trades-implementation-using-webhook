from flask import Flask, request, jsonify
import json
import socket
import neo_api_client
from neo_api_client import NeoAPI
import pandas as pd
from kotak_api import margin_info, net_positions, order_place, on_error, on_message, process_trade

app = Flask(__name__)

client = None
is_client_logged_in = False

@app.route('/login', methods=['GET'])
def login():
    global client
    client = NeoAPI(consumer_key="", consumer_secret="", 
                    environment='prod', on_message=on_message, on_error=on_error, on_close=None, on_open=None)

    client.login(mobilenumber="+", password="")
    return "Login initiated, please provide OTP."


@app.route('/otp', methods=['POST'])
def otp():
    global is_client_logged_in
    data = json.loads(request.data)
    otp = data['otp']
    client.session_2fa(OTP=otp)
    is_client_logged_in = True
    return "Login successful."

@app.route('/')
def test_fun():
    return 'hello'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = json.loads(request.data)
        order_response = process_trade(client, data)
        print(order_response)
        return "Trade processed"
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
