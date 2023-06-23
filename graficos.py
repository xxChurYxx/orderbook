import os
import mplfinance as mpf
import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException

api_key = ''
api_secret = ''
client = Client(api_key, api_secret)

def get_historical_klines(symbol, interval, limit):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

    prices = []
    timestamps = []
    for kline in klines:
        timestamp = int(kline[0]) / 1000  # Convertir el timestamp a segundos
        open_price = float(kline[1])
        high_price = float(kline[2])
        low_price = float(kline[3])
        close_price = float(kline[4])
        volume = float(kline[5])

        prices.append([timestamp, open_price, high_price, low_price, close_price])
        timestamps.append(timestamp)

    return prices, timestamps

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Solicitar al usuario ingresar el símbolo de la moneda
def get_symbol():
    while True:
        symbol = input("Ingresa el símbolo de la moneda (ejemplo: BTCUSDT) o presiona 'q' para salir: ")
        if symbol.lower() == 'q':
            exit()
        if symbol_valid(symbol):
            return symbol
        else:
            print("Moneda incorrecta espartano")

def symbol_valid(symbol):
    # Aquí puedes agregar lógica adicional para validar el símbolo de la moneda según tus necesidades
    return True

# Obtener los datos históricos de precios
limit = 200  # Número de datos por defecto

while True:
    # Solicitar al usuario ingresar una nueva moneda
    symbol = get_symbol()

    try:
        # Obtener los datos históricos de precios
        prices, timestamps = get_historical_klines(symbol, '1h', limit)

        # Crear el dataframe con los datos históricos
        df = pd.DataFrame(prices, columns=['timestamp', 'open', 'high', 'low', 'close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)

        # Configurar el estilo del gráfico
        style = mpf.make_mpf_style(base_mpf_style='classic', gridstyle=':', gridcolor='lightgray')

        # Crear el gráfico de velas
        fig, axlist = mpf.plot(df, type='candle', style=style, title=symbol, ylabel='', returnfig=True)

        # Ocultar la etiqueta "PRICE" en el gráfico
        axlist[0].set_ylabel('')

        # Obtener el orderbook de Binance
        orderbook = client.futures_order_book(symbol=symbol)

        # Obtener los precios y volúmenes de las órdenes de compra y venta dentro del rango
        range_percentage = float(input("Ingresa el porcentaje de rango (ejemplo: 1 para 1%): ")) / 100
        average_price = df['close'].mean()
        range_low = average_price * (1 - range_percentage)
        range_high = average_price * (1 + range_percentage)

        # Obtener los precios y volúmenes de las órdenes de compra dentro del rango
        buy_orders = [(float(order[0]), float(order[1])) for order in orderbook['bids'] if range_low <= float(order[0]) <= range_high]

        # Obtener los precios y volúmenes de las órdenes de venta dentro del rango
        sell_orders = [(float(order[0]), float(order[1])) for order in orderbook['asks'] if range_low <= float(order[0]) <= range_high]

        # Ordenar las órdenes de compra y venta por volumen en orden descendente
        buy_orders.sort(key=lambda x: x[1], reverse=True)
        sell_orders.sort(key=lambda x: x[1], reverse=True)

        # Calcular los promedios ponderados de compras y ventas
        buy_average_prices = []
        sell_average_prices = []

        if len(buy_orders) > 0:
            buy_prices = [order[0] for order in buy_orders]
            buy_volumes = [order[1] for order in buy_orders]
            total_buy_volume = sum(buy_volumes)
            buy_weights = [volume / total_buy_volume for volume in buy_volumes]
            buy_average_prices = [np.average(buy_prices[i:i+2], weights=buy_weights[i:i+2]) for i in range(0, min(len(buy_orders), 4), 2)]

        if len(sell_orders) > 0:
            sell_prices = [order[0] for order in sell_orders]
            sell_volumes = [order[1] for order in sell_orders]
            total_sell_volume = sum(sell_volumes)
            sell_weights = [volume / total_sell_volume for volume in sell_volumes]
            sell_average_prices = [np.average(sell_prices[i:i+2], weights=sell_weights[i:i+2]) for i in range(0, min(len(sell_orders), 4), 2)]


        # Trazar las líneas rojas y verdes en los precios promedio
        for buy_price in buy_average_prices:
            axlist[0].axhline(y=buy_price, color='green')
        for sell_price in sell_average_prices:
            axlist[0].axhline(y=sell_price, color='red')

        # Agregar los precios correspondientes a las líneas en el gráfico
        for i, buy_price in enumerate(buy_average_prices):
            axlist[0].text(df.index[-1], buy_price, f'{buy_price:.2f}', horizontalalignment='right', verticalalignment='center', color='green')
        for i, sell_price in enumerate(sell_average_prices):
            axlist[0].text(df.index[-1], sell_price, f'{sell_price:.2f}', horizontalalignment='right', verticalalignment='center', color='red')

        # Mostrar el gráfico con las líneas rojas y verdes
        mpf.show()

        # Limpiar la consola
        clear_console()

    except BinanceAPIException as e:
        print("Error !!!")
