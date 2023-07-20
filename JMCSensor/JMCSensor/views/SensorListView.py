from rest_framework import generics
from ..serializers.SensorListSerializer import SensorDataSerializer
from ..models.SensorData import SensorData
from rest_framework.response import Response
from filterpy.kalman import KalmanFilter
import numpy as np
import matplotlib.pyplot as plt
from rest_framework.views import APIView
from PIL import Image
import pandas as pd
from django.http import FileResponse
import statistics
import base64
import io
import jwt
import math

class SensorDataListView(APIView):
    def get_queryset(self):
        userId = self.kwargs['userId']
        return SensorData.objects.filter(userId=userId)

    def get(self, request, *args, **kwargs):
        body = request.data
        token = body.get('token') 
        
        if not token:
            return Response({'success': False, 'message': 'Acceso no autorizado'}, status=401)
        
        try:
            decoded_token = jwt.decode(token, 'tu_clave_secreta_aqui', algorithms=['HS256'])

            queryset = self.get_queryset()

            serializer = SensorDataSerializer(queryset, many=True)
            formatted_data = serializer.data
            print(formatted_data)

            atributos_separados = {}

            for objeto in formatted_data:
                for atributo, valor in objeto.items():
                    if atributo != "userId":
                        if atributo not in atributos_separados:
                            atributos_separados[atributo] = []
                        atributos_separados[atributo].append(valor)

            # Resto del código para el método GET ...

            response_data = {
                # Datos de la respuesta ...
            }

            return Response(response_data)
        except jwt.ExpiredSignatureError:
            return Response({'success': False, 'message': 'Token expirado'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'success': False, 'message': 'Token inválido'}, status=401)

    def post(self, request, userId, format=None):
        body = request.data
        token = body.get('token') 

        if not token:
            return Response({'success': False, 'message': 'Acceso no autorizado'}, status=401)

        try:
            decoded_token = jwt.decode(token, 'tu_clave_secreta_aqui', algorithms=['HS256'])

            queryset = self.get_queryset()

            serializer = SensorDataSerializer(queryset, many=True)
            formatted_data = serializer.data
            print(formatted_data)

            atributos_separados = {}

            for objeto in formatted_data:
                for atributo, valor in objeto.items():
                    if atributo != "userId":
                        if atributo not in atributos_separados:
                            atributos_separados[atributo] = []
                        atributos_separados[atributo].append(valor)

            #METODO PARA SEPARAR EN OBJETOS ATRIBUTOS_SEPARADOS Y LOS ORDENA
            gas_values, brightness_values, humidity_values, temperature_values, pressure_values = separar_objetos(atributos_separados)
            print("gas_values")
            print(gas_values)

            #METODO PARA CALCULAR ESTADISTICAS
            media_gas, mediana_gas, moda_gas, desviacion_gas, rango_gas = calcular_estadisticas(gas_values)
            media_brightness, mediana_brightness, moda_brightness, desviacion_brightness, rango_brightness = calcular_estadisticas(brightness_values)
            media_humidity, mediana_humidity, moda_humidity, desviacion_humidity, rango_humidity = calcular_estadisticas(humidity_values)
            media_temperature, mediana_temperature, moda_temperature, desviacion_temperature, rango_temperature = calcular_estadisticas(temperature_values)
            media_pressure, mediana_pressure, moda_pressure, desviacion_pressure, rango_pressure = calcular_estadisticas(pressure_values)

            #METODO PARA CALCULAR CANTIDAD DE CLASES POR OBJETO
            gas_classes = calcular_numero_clases(gas_values)
            brightness_classes = calcular_numero_clases(brightness_values)
            humidity_classes = calcular_numero_clases(humidity_values)
            temperature_classes = calcular_numero_clases(temperature_values)
            pressure_classes = calcular_numero_clases(pressure_values)

            #METODO PARA CALCULAR LOS RANGOS
            gas_rango, brightness_rango, humidity_rango, temperature_rango, pressure_rango = calcular_rangos(gas_values, brightness_values, humidity_values, temperature_values, pressure_values)

            #METODO PARA CALCULAR ANCHO DE CLASES
            gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho = calcular_anchos(gas_rango, gas_classes, brightness_rango, brightness_classes, humidity_rango, humidity_classes, temperature_rango, temperature_classes, pressure_rango, pressure_classes)

            #TRANSFORMAR DE LISTAS A PANDAS SERIES
            gas_values = pd.Series(gas_values)
            brightness_values = pd.Series(brightness_values)
            humidity_values = pd.Series(humidity_values)
            temperature_values = pd.Series(temperature_values)
            pressure_values = pd.Series(pressure_values)

            #METODO PARA REDONDEAR ANCHO DE CLASE DE ACUERDO A DECIMALES DE LOS DATOS
            gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho = calcular_anchos_r(gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho, gas_values, brightness_values, humidity_values, temperature_values, pressure_values)

            #METODO PARA CALCULAR LOS LIMITES, MASRCAS DE CLASE, FRECUENCIA ABSOLUTA Y NUMERO DE CLASES (1, 2, 3, 4, ... N)
            gas_lim_inf, gas_lim_sup, gas_marca_clase, gas_frecuencia_absoluta, gas_clase = calcular_limites(gas_ancho, gas_classes, gas_values)
            brightness_lim_inf, brightness_lim_sup, brightness_marca_clase, brightness_frecuencia_absoluta, brightness_clase = calcular_limites(brightness_ancho, brightness_classes, brightness_values)
            humidity_lim_inf, humidity_lim_sup, humidity_marca_clase, humidity_frecuencia_absoluta, humidity_clase = calcular_limites(humidity_ancho, humidity_classes, humidity_values)
            temperature_lim_inf, temperature_lim_sup, temperature_marca_clase, temperature_frecuencia_absoluta, temperature_clase = calcular_limites(temperature_ancho, temperature_classes, temperature_values)
            pressure_lim_inf, pressure_lim_sup, pressure_marca_clase, pressure_frecuencia_absoluta, pressure_clase = calcular_limites(pressure_ancho, temperature_classes, pressure_values)

            #METODO PARA CREAR HISTOGRAMA
            gas_histograma = crear_histograma(gas_marca_clase, gas_frecuencia_absoluta, 'gas_histograma.png', 'Gas', gas_values)
            brightness_histograma = crear_histograma(brightness_marca_clase, brightness_frecuencia_absoluta, 'brightness_histograma.png', 'Luminosidad', brightness_values)
            humidity_histograma = crear_histograma(humidity_marca_clase, humidity_frecuencia_absoluta, 'humidity_histograma.png', 'Humedad', humidity_values)
            temperature_histograma = crear_histograma(temperature_marca_clase, temperature_frecuencia_absoluta, 'temperature_histograma.png', 'Temperatura', temperature_values)
            pressure_histograma = crear_histograma(pressure_marca_clase, pressure_frecuencia_absoluta, 'pressure_histograma.png', 'Presión atmosférica', pressure_values)

            f = KalmanFilter(dim_x=2, dim_z=1)

            initial_temperature = temperature_values[0]
            initial_rate_of_change = 0
            f.x = np.array([[initial_temperature], [initial_rate_of_change]])

            process_noise = 0.01
            measurement_noise = 1.0
            f.Q = process_noise
            f.R = measurement_noise

            estimated_states = []

            for temperature in temperature_values:
                sensor_measurement = temperature
                f.predict()
                f.update(sensor_measurement)
                estimated_state = f.x
                estimated_states.append(estimated_state.T)

            temperature_prediction = estimated_states[-1][0, 0]

            histogramas = [gas_histograma, brightness_histograma, humidity_histograma, temperature_histograma, pressure_histograma]
            respuestas_gas = []
            respuestas_brightness = []
            respuestas_humidity = []
            respuestas_temperature = []
            respuestas_pressure = []

            for histograma_nombre in histogramas:
                imagen_histograma = Image.open(histograma_nombre)

                # Convertir la imagen a base64
                buffer = io.BytesIO()
                imagen_histograma.save(buffer, format='PNG')
                imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

                respuesta = {
                    'content_type': 'text/plain',
                    'content': imagen_base64,
                    'filename': histograma_nombre
                }

                if histograma_nombre == gas_histograma:
                    respuestas_gas.append(respuesta)
                elif histograma_nombre == brightness_histograma:
                    respuestas_brightness.append(respuesta)
                elif histograma_nombre == humidity_histograma:
                    respuestas_humidity.append(respuesta)
                elif histograma_nombre == temperature_histograma:
                    respuestas_temperature.append(respuesta)
                elif histograma_nombre == pressure_histograma:
                    respuestas_pressure.append(respuesta)

            archivo_url = 'histogramas.txt'

            response_data = {
                'success': True,
                'message': 'Generado correctamente',
                'token': token,
                'graficas_url': archivo_url,
                'data': formatted_data,
                'respuestas_gas': respuestas_gas,
                'respuestas_brightness': respuestas_brightness,
                'respuestas_humidity': respuestas_humidity,
                'respuestas_temperature': respuestas_temperature,
                'respuestas_pressure': respuestas_pressure,
                'media_gas': media_gas,
                'mediana_gas': mediana_gas,
                'moda_gas': moda_gas,
                'desviacion_estandar_gas': desviacion_gas,
                'rango_gas': rango_gas,
                'media_brightness': media_brightness,
                'mediana_brightness': mediana_brightness,
                'moda_brightness': moda_brightness,
                'desviacion_estandar_brightness': desviacion_brightness,
                'rango_brightness': rango_brightness,
                'media_humidity': media_humidity,
                'mediana_humidity': mediana_humidity,
                'moda_humidity': moda_humidity,
                'desviacion_estandar_humidity': desviacion_humidity,
                'rango_humidity': rango_humidity,
                'media_temperature': media_temperature,
                'mediana_temperature': mediana_temperature,
                'moda_temperature': moda_temperature,
                'desviacion_estandar_temperature': desviacion_temperature,
                'rango_temperature': rango_temperature,
                'media_pressure': media_pressure,
                'mediana_pressure': mediana_pressure,
                'moda_pressure': moda_pressure,
                'desviacion_estandar_pressure': desviacion_pressure,
                'rango_pressure': rango_pressure,
                'prediccion': temperature_prediction,
            }

            return Response(response_data)
        except jwt.ExpiredSignatureError:
            return Response({'success': False, 'message': 'Token expirado'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'success': False, 'message': 'Token inválido'}, status=401)

def separar_objetos(atributos_separados):
    datos_agrupados = {}

    gas_values = sorted(atributos_separados["gas"])
    datos_agrupados["gas"] = {"valores": gas_values}

    brightness_values = sorted(atributos_separados["brightness"])
    datos_agrupados["brightness"] = {"valores": brightness_values}

    humidity_values = sorted(atributos_separados["humidity"])
    datos_agrupados["humidity"] = {"valores": humidity_values}

    temperature_values = sorted(atributos_separados["temperature"])
    datos_agrupados["temperature"] = {"valores": temperature_values}

    pressure_values = sorted(atributos_separados["pressure"])
    datos_agrupados["pressure"] = {"valores": pressure_values}

    return gas_values, brightness_values, humidity_values, temperature_values, pressure_values

def calcular_numero_clases(datos):
    n = len(datos)
    k = 1 + round(3.332 * math.log10(n))

    return int(k)

def calcular_rangos(gas_values, brightness_values, humidity_values, temperature_values, pressure_values):
    gas_rango = max(gas_values) - min(gas_values)
    brightness_rango = max(brightness_values) - min(brightness_values)
    humidity_rango = max(humidity_values) - min(humidity_values)
    temperature_rango = max(temperature_values) - min(temperature_values)
    pressure_rango = max(pressure_values) - min(pressure_values)

    return gas_rango, brightness_rango, humidity_rango, temperature_rango, pressure_rango

def calcular_anchos(gr, gc, br, bc, hr, hc, tr, tc, pr, pc):
    gas_ancho = gr/gc
    brightness_ancho = br/bc
    humidity_ancho = hr/hc
    temperature_ancho = tr/tc
    pressure_ancho = pr/pc

    return gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho

def calcular_anchos_r(gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho, gas_values, brightness_values, humidity_values, temperature_values, pressure_values):
    def calcular_decimales(ancho, valores):
        decimales_temp = valores.apply(contar_decimales)
        max_decimales_temp = decimales_temp.max()
        max_decimales_temp = max_decimales_temp + 1
        ancho = round(ancho, max_decimales_temp)

        return ancho
    
    gas_ancho = calcular_decimales(gas_ancho, gas_values)

    brightness_ancho = calcular_decimales(brightness_ancho, brightness_values)
    
    humidity_ancho = calcular_decimales(humidity_ancho, humidity_values)

    temperature_ancho = calcular_decimales(temperature_ancho, temperature_values)

    pressure_ancho = calcular_decimales(pressure_ancho, pressure_values)

    return gas_ancho, brightness_ancho, humidity_ancho, temperature_ancho, pressure_ancho

def contar_decimales(numero):
    if isinstance(numero, float):
        decimales = str(numero).split('.')[-1]
        return len(decimales)
    else:
        return 0
    
def calcular_limites(ancho, classes, datos):

    def calcular_limites(amplitud, num_clases, datos):
        marcas_clase = []
        validar = True

        for i in range(num_clases):
            min_valor = min(datos)
            limite_inferior = (min_valor + i * amplitud)
            limite_superior = (limite_inferior + amplitud)
            marca_clase = (limite_inferior + limite_superior) / 2
            marcas_clase.append(marca_clase)

            clase = f"Clase {i+1}"
            if validar:
                frecuencia_absoluta = sum(limite_inferior <= dato <= limite_superior for dato in datos)
                validar = False
            else:
                frecuencia_absoluta = sum(limite_inferior < dato <= limite_superior for dato in datos)

        return limite_inferior, limite_superior, marcas_clase, frecuencia_absoluta, clase

    lim_inf, lim_sup, marcas_clase, frecuencia_absoluta, clase = calcular_limites(ancho, classes, datos)
        
    return lim_inf, lim_sup, marcas_clase, frecuencia_absoluta, clase

def crear_histograma(marca_clase, frecuencia_absoluta, nombre_archivo, atributo, datos):

    k = calcular_numero_clases(datos)
    marca_clase_texto = list(map(str, marca_clase))

    plt.hist(x=datos, bins=k, color='#F2AB6D', rwidth=0.85)
    plt.title('Histograma de ' + atributo)
    plt.xlabel(atributo)
    plt.ylabel('Frecuencia')

    plt.xticks(marca_clase, marca_clase_texto, rotation='vertical')
    plt.savefig(nombre_archivo)

    return nombre_archivo

def calcular_estadisticas(valores):
    media = statistics.mean(valores)
    mediana = statistics.median(valores)
    moda = statistics.mode(valores)
    desviacion_estandar = statistics.stdev(valores)
    rango = max(valores) - min(valores)
    return media, mediana, moda, desviacion_estandar, rango
