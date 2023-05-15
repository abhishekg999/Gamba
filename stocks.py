import finnhub

with open("api.key", "r") as f:
    API_KEY = f.read()

# Setup client
finnhub_client = finnhub.Client(api_key=API_KEY)

# Stock candles
res = finnhub_client.recommendation_trends(symbol='AAPL')

print(res)


# import websocket

# def on_message(ws, message):
#     print(message)

# def on_error(ws, error):
#     print(error)

# def on_close(ws):
#     print("### closed ###")

# def on_open(ws):
#     ws.send('{"type":"subscribe","symbol":"AAPL"}')
#     ws.send('{"type":"subscribe","symbol":"AMZN"}')

# if __name__ == "__main__":
#     ws = websocket.WebSocketApp(f"wss://ws.finnhub.io?token={API_KEY}",
#                               on_message = on_message,
#                               on_error = on_error,
#                               on_close = on_close)
#     ws.on_open = on_open
#     ws.run_forever()

