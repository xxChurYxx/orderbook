import os
import subprocess

# Lista de librerías requeridas
libraries = ['mplfinance', 'pandas', 'numpy', 'python-binance']

# Comprobar si cada librería está instalada y, en caso contrario, instalarla
for library in libraries:
    try:
        __import__(library)
        print(f'{library} ya está instalada.')
    except ImportError:
        print(f'{library} no está instalada. Instalando...')
        subprocess.call(['pip', 'install', library])

# Mensaje de finalización
print("ES TODO ESPARTANO, HORA DE EJECUTAR EL SCRIPT")
