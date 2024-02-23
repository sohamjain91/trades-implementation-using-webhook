import neo_api_client
from neo_api_client import NeoAPI
import pandas as pd

def on_message(message):
    print(message)
    
def on_error(error_message):
    print(error_message)

def order_place(client, quantity, ticker, transaction_type):
    
    scriplist = client.scrip_master(exchange_segment="NSE")
    scriplist = pd.read_csv(scriplist)
    symbol_name = scriplist[(scriplist['pSymbolName'] == ticker) & (scriplist['pGroup'] == "EQ")]["pTrdSymbol"].values[0]
    
    
    trade = client.place_order(exchange_segment="NSE", product="MIS", price="", order_type="MKT", quantity=quantity, validity="DAY", 
                       trading_symbol=symbol_name, transaction_type=transaction_type, amo="NO", disclosed_quantity="0",
                       market_protection="0", pf="N",trigger_price="0", tag=None)
    
    return trade
    

def margin_info(client, ticker = "NYKAA"):

    scriplist = client.scrip_master(exchange_segment="NSE")
    scriplist = pd.read_csv(scriplist)
    symbol_code = str(scriplist[(scriplist['pSymbolName'] == ticker) & (scriplist['pGroup'] == "EQ")]["pSymbol"].values[0])
    margin_data = client.margin_required(exchange_segment = "NSE", price = "200", order_type= "MKT", product = "MIS", 
                           quantity = "1", instrument_token = symbol_code, transaction_type = "B")

    cash = margin_data['data']['avlCash']
    margin_used = margin_data['data']['mrgnUsd']
    margin_available = float(cash) - float(margin_used)
    
    data = {"cash":cash,
           "margin_used":margin_used,
           "margin_available":margin_available}
    
    return data

def net_positions(client):
    
    try:
    
        positions_data = client.positions()
        running_trades = []
        for trades in positions_data['data']:
            sym_name = trades['sym']
            buys= trades['flBuyQty']
            sells = trades['flSellQty']
            net_quantity = float(buys)-float(sells)
            running_trades.append([sym_name,buys,sells,net_quantity])

        running_trades = pd.DataFrame(running_trades, columns = ["sym_name","buys","sells","net_quantity"])
        running_trades = running_trades.to_frame()
        
    except:
        
        print("No positions")
    
    return running_trades

def process_trade(client, data, csv_file):

    df = pd.read_csv("quantity.csv")
    df.ticker_name = df.ticker_name.astype('string')
    df.info()
    q = df[df['ticker_name'] == "NYKAA"].values[0][1]

    if data['trade_direction'] == "LE":
        order_response = order_place(client, "q", data['ticker'], "B")

    if data['trade_direction'] == "LX":
        # positions = net_positions(client)
        # net_qty = positions[positions['sym_name'] == data['ticker']]['net_quantity']

        # if net_qty == 1:
        order_response = order_place(client, "q", data['ticker'], "S")

    if data['trade_direction'] == "SE":
        order_response = order_place(client, "q", data['ticker'], "S")

    if data['trade_direction'] == "SX":
        # positions = net_positions(client)
        # net_qty = positions[positions['sym_name'] == data['ticker']]['net_quantity']

        # if net_qty == -1:
        order_response = order_place(client, "q", data['ticker'], "B")

    return order_response