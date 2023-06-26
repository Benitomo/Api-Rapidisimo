import requests
from fastapi import FastAPI
import mysql.connector
import datetime
import pyodbc

conn = mysql.connector.connect(
user='davidc', password='1mp0c4l1C5', host='10.167.240.9', database='my-bd-test')
    #Creating a cursor object using the cursor() method
cur = conn.cursor()

cnxn = pyodbc.connect('DSN=Infdrv1')
cursor = cnxn.cursor()

app = FastAPI()


@app.get("/helloWorld")
def read_root():
    return {"Hello": "World"}


@app.get("/rapidisimo")
def rapidisimo():

    api_key = "890304140"
    url = 'http://www.jetpackadmin.com/webserv/impocali/wsimpocali.php'
    params = {
        'access_key': api_key,
        'user': 'CAWC3',
        'format': 'json',
        'num': '2000'
    }

    response = requests.get(url, params=params)


        # Comprobar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Obtener la respuesta en formato JSON
        json_data = response.json()
        
        # Recorrer los datos y guardarlos en la base de datos
        for servicio in json_data["servicios"]:
            numidinterno = servicio["post"]["numidinterno"]
            id_solicitud = servicio["post"]["id_solicitud"]
            id_ticket = servicio["post"]["id_ticket"]
            nodo = servicio["post"]["nodo"]
            novedad = servicio["post"]["novedad"]
            observaciones = servicio["post"]["observaciones"]
            fec_asigna_servicio = servicio["post"]["fec_asigna_servicio"] if servicio["post"]["fec_asigna_servicio"] and servicio["post"]["fec_asigna_servicio"] != '0000-00-00 00:00:00' else '1000-01-01'
            fecha_despacho_servicio = servicio["post"]["fecha_despacho_servicio"] if servicio["post"]["fecha_despacho_servicio"] and servicio["post"]["fecha_despacho_servicio"] != '0000-00-00 00:00:00' else '1000-01-01'
            fecha_activa_servicio = servicio["post"]["fecha_activa_servicio"] if servicio["post"]["fecha_activa_servicio"] and servicio["post"]["fecha_activa_servicio"] != '0000-00-00 00:00:00' else '1000-01-01'
            fecha_llegada_punto = servicio["post"]["fecha_llegada_punto"] if servicio["post"]["fecha_llegada_punto"] and servicio["post"]["fecha_llegada_punto"] != '0000-00-00 00:00:00' else '1000-01-01'
            fec_final_servicio = servicio["post"]["fec_final_servicio"] if servicio["post"]["fec_final_servicio"] and servicio["post"]["fec_final_servicio"] != '0000-00-00 00:00:00' else '1000-01-01'


            print("id: "+numidinterno)
            print("idso: "+id_solicitud)
            print("id_ticket: "+id_ticket)
            print("nodo: "+nodo)
            print("novedad: "+novedad)
            print("observaciones: "+observaciones)
            print("fec_asigna_servicio: "+fec_asigna_servicio)
            print("fecha_despacho_servicio: "+fecha_despacho_servicio)
            print("fecha_activa_servicio: "+fecha_activa_servicio)
            print("fecha_llegada_punto: "+fecha_llegada_punto)
            print("fec_final_servicio: "+fec_final_servicio)

            idticket = id_ticket[-6:]
            print("este es el id de domi: "+idticket)
            cursor.execute("select domi_tipo_doc, domi_num_doc from vymdomi where domi_id = "+idticket)
            row = cursor.fetchone()
            if row is not None:
                domi_tipo_doc = row[0]
                domi_num_doc = row[1]
            else:
                domi_tipo_doc = None
                domi_num_doc = None
            
            cur.execute("""
            INSERT INTO tiempos_rapi (numidinterno, id_solicitud, id_ticket, nodo, novedad, observaciones, 
            fec_asigna_servicio, fecha_despacho_servicio, fecha_activa_servicio, fecha_llegada_punto, fec_final_servicio, td_factura, no_factura)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            id_solicitud = VALUES(id_solicitud),
                            id_ticket = VALUES(id_ticket),
                            nodo = VALUES(nodo),
                            novedad = VALUES(novedad),
                            observaciones = VALUES(observaciones),
                            fec_asigna_servicio = VALUES(fec_asigna_servicio),
                            fecha_despacho_servicio = VALUES(fecha_despacho_servicio),
                            fecha_activa_servicio = VALUES(fecha_activa_servicio),
                            fecha_llegada_punto = VALUES(fecha_llegada_punto),
                            fec_final_servicio = VALUES(fec_final_servicio),
                            td_factura = VALUES(td_factura),
                            no_factura = VALUES(no_factura)

                        """,
                        (numidinterno,id_solicitud,id_ticket,nodo,novedad,observaciones,fec_asigna_servicio,
                        fecha_despacho_servicio,fecha_activa_servicio,fecha_llegada_punto,fec_final_servicio,domi_tipo_doc,domi_num_doc))

            # Confirmar los cambios en la base de datos
            conn.commit()
            
        print("Datos insertados exitosamente")

        return {"Datos insertados exitosamente"}

    else:
        # La solicitud no fue exitosa, imprimir el código de estado
        print('Error en la solicitud. Código de estado:', response.status_code)

        
        return {'Error en la solicitud. Código de estado:', response.status_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)


