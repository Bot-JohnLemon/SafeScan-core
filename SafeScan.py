import os
import mysql.connector
import requests
import time
import urllib.parse

API_KEY="041d19bcac27e35f69b115a322a969098f73f9a4330a31862a31e4867f3fdba2"

def contador_dia():
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "1234",
        "database": "SafeScan_database"
    }
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        consulta = "SELECT * FROM SafeScan WHERE date >= now() - INTERVAL 24 HOUR"
        cursor.execute(consulta)
        archivos = cursor.fetchall()
        cursor.close()
        conn.close()

    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return 0


    contador = 0
    for i in archivos:
        contador=+1
    return contador

def ubicaciones_archivos():
    directorio_especifico = (input("Introducela ruta especifica:\n>>  "))
    ubicaciones_archivos = []
    for raiz, directorios, nombres_archivos in os.walk(directorio_especifico):
        for nombre_archivo in nombres_archivos:
            ruta_completa = os.path.join(raiz, nombre_archivo)
            ubicaciones_archivos.append(ruta_completa)
    return ubicaciones_archivos

def api():
#   CONDICIONAL TIPO DE API KEY VIRUS TOTAL
    res=(input("¿Tiene usted una version premium de VirusTotal?\n>>>  "))
    if (res == "si"):
        print("Ok esto es un codigo preliminar que no cuenta con la adaptacion de VirusTotal Premium. Exit")
        exit
#   CANTIDAD DE ARCHIVOS --> MINUTO
    ubicaciones_registradas = ubicaciones_archivos()
    total_archivos_dia = 0 #    ===================================>>   COMMENTAR
    total_archivos_dia = contador_dia()
    cantidad_archivos = len(ubicaciones_registradas)
    print("\nHAY UN TOTAL DE ", cantidad_archivos, " ARCHIVOS:\n")
    for ubicacion_registrada in ubicaciones_registradas:
        print(ubicacion_registrada)
    if (total_archivos_dia >= 500):
        print("No se pueden enviar mas archivos, se ha superado el limite diario")
        exit
    if cantidad_archivos > 4:
        print("Para no superar el limite de envio de archivos por minuto,\nse enviara 1 archivo cada 15 secs...")
        ids = envio_de_archivos(ubicaciones_registradas, 15)
    else:
        ids = envio_de_archivos(ubicaciones_registradas, 0)
    print("\n===========>>>   ANALISIS   <<<===========\n")
    hashes = obtener_analisis(ids)
    print("\n===========>>>   REPORTES   <<<===========\n")
    obtener_reporte(hashes)

def envio_de_archivos(ubicaciones_registradas, delay):
    ids = []
    for ubicacion in ubicaciones_registradas:
        ubicacion_tamaño = os.path.getsize(ubicacion)
        if ubicacion_tamaño <= 33554432: 
            url = "https://www.virustotal.com/api/v3/files"
            files = { "file": (ubicacion, open(ubicacion, "rb")) }
            headers = {
                "accept": "application/json",
                "x-apikey": API_KEY
            }
        elif ubicacion_tamaño > 33554432 and ubicacion_tamaño < 681574400:  
            url = "https://www.virustotal.com/api/v3/files/upload_url"
            files = { "file": (ubicacion, open(ubicacion, "rb")) }
            headers = {
                "accept": "application/json",
                "x-apikey": API_KEY
            }
            response = requests.get(url, headers=headers)
        else:
            print("El tamaño de un archivo a enviar es superior a 650MB, por lo tanto no se puede enviar...Exit")
            exit
        print("\nTiempo de espera: ", delay, "segundos...")
        time.sleep(delay)
        response = requests.post(url, files=files, headers=headers)
        if response.status_code == 200:
            data = response.json()
            id = data["data"]["id"]
            ids.append(id)
        else:
                print("Error, ha fallado el envio del archivo a VirusTotal")
        print("--->  Enviando el archivo:\n--->  ", ubicacion, "\nID: ", id)
    return ids

def obtener_analisis(ids):
    hashes = []
    for id in ids:
        id = urllib.parse.quote(id)
        url = f"https://www.virustotal.com/api/v3/analyses/{id}"
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY
        }
        url = requests.get(url, headers=headers)
        data = url.json()
        sha256 = data["meta"]["file_info"]["sha256"]
        print(sha256, "  ------->  analisis completo")
        hashes.append(sha256)
    return hashes

def obtener_reporte(hashes):
    registros_totales = []
    for hash in hashes:
        hash = urllib.parse.quote(hash)
        url = f"https://www.virustotal.com/api/v3/files/{hash}"
        
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY
        }
        print("\nHASH: ", hash)
        print("URL: ", url)
        response = requests.get(url, headers=headers)
        data = response.json()
        #print(response.text)
        type_description = data["data"]["attributes"]["type_description"]
        last_modification_date = data["data"]["attributes"]["last_modification_date"]
        size = data["data"]["attributes"]["size"]
        harmless = data["data"]["attributes"]["last_analysis_stats"]["harmless"]
        suspicious = data["data"]["attributes"]["last_analysis_stats"]["suspicious"]
        malicious = data["data"]["attributes"]["last_analysis_stats"]["malicious"]
        undetected = data["data"]["attributes"]["last_analysis_stats"]["undetected"]
        print("TIPO: ", type_description)
        print("ULTIMA MODIFICACION: ", last_modification_date)
        print("TAMAÑO: ", size, "KB")
        print("INOFENSIVO: ", harmless, " %")
        print("SOSPECHOSO: ", suspicious, " %")
        print("MALICIOSO: ", malicious, " %")
        print("INDETECTABLE: ", undetected, " %")
        print("\n\n\n")
        registros_totales = [type_description,last_modification_date,size,hash,harmless,suspicious,malicious,undetected]
        insertar_base_de_datos_mariadb(registros_totales)

    return registros_totales

def insertar_base_de_datos_mariadb(registro_datos):
    config = {
        'user': 'root',
        'password': '1234',
        'host': 'localhost'
        }
    try:
        conexion = mysql.connector.connect(**config)
    except mysql.connector.Error as Error:
        print(f"Error de conexión: {Error}")
    cursor = conexion.cursor()
    database = 'SafeScan_database'
    cursor.execute("SHOW DATABASES LIKE %s", (database,))
    database_exists = cursor.fetchone()
    if database_exists:
        cursor.execute('Use SafeScan_database')
        type_description = registro_datos[0]
        last_modification_date = registro_datos[1]
        size = registro_datos[2]
        sha256 = registro_datos[3]
        harmless = registro_datos[4]
        suspicious = registro_datos[5]
        malicious = registro_datos[6]
        undetected = registro_datos[7]
        query1= 'insert into SafeScan(type_description,last_modification_date,size,sha256,harmless,suspicious,malicious,undetected) values(%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query1, (type_description,last_modification_date,size,sha256,harmless,suspicious,malicious,undetected))
        conexion.commit()
        cursor.close()
        conexion.close()   
    else:
        create_dabase = 'Create database SafeScan_database'
        cursor.execute(create_dabase)
        cursor.execute('Use SafeScan_database')
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS SafeScan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type_description VARCHAR(50),
            last_modification_date VARCHAR(50),
            size VARCHAR(50),
            sha256 VARCHAR(100),
            harmless VARCHAR(10),
            suspicious VARCHAR(10),
            malicious VARCHAR(10),
            undetected VARCHAR(10),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )'''
        cursor.execute(create_table_query)
        type_description = registro_datos[0]
        last_modification_date = registro_datos[1]
        size = registro_datos[2]
        sha256 = registro_datos[3]
        harmless = registro_datos[4]
        suspicious = registro_datos[5]
        malicious = registro_datos[6]
        undetected = registro_datos[7]
        query1= 'insert into SafeScan(type_description,last_modification_date,size,sha256,harmless,suspicious,malicious,undetected) values(%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.execute(query1, (type_description,last_modification_date,size,sha256,harmless,suspicious,malicious,undetected))
        conexion.commit()
        cursor.close()
        conexion.close()

api()