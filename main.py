import requests
from fastapi import FastAPI
import mysql.connector
import datetime
import pyodbc
import json
import cx_Oracle
from decimal import Decimal

def pedido_wms(pl):
    pl = str(pl)
    dsn = cx_Oracle.makedsn(host='10.100.5.176', port=1521, service_name = 'prod.stproddb.dns.oraclevcn.com')
    con = cx_Oracle.connect(user='DEVELOP', password='M#n4g3R_01', dsn=dsn)
    cursor = con.cursor()
    cursor.execute("""select 
                        distinct(shipping_pckwrk_view.ordnum)as orden, 
                        case when inventory_pckwrk_view.stoloc like 'MOVIL%' then 'En Picking' 
                            when inventory_pckwrk_view.stoloc like 'CON%' then 'En Pickig' 
                            when inventory_pckwrk_view.stoloc like 'MESAE%' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like 'ESTMESAE%' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like '%-STG' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like 'STGD%' then 'En Despacho' 
                            when inventory_pckwrk_view.stoloc like 'TRL0%' then 'En Camion' 
                            else 'Despachado' end as estado,
                            ord.adddte as fecha_pase_bodega,
                            (select max(pckwrk_view.pckdte)
                                        from pckwrk_view
                                        where pckwrk_view.ordnum = ord.ordnum
                                        and pckwrk_view.wrktyp = 'K'
                                        and pckwrk_view.dtl_pckqty > 0) fecha_empaque,
                                        dispatch_dte as fecha_despacho
                        from 
                        shipping_pckwrk_view 
                        left outer join inventory_pckwrk_view 
                        on shipping_pckwrk_view.ordnum = inventory_pckwrk_view.ordnum 
                        and shipping_pckwrk_view.wh_id = inventory_pckwrk_view.wh_id 
                        left outer join trlr 
                        on shipping_pckwrk_view.trlr_id = trlr.trlr_id 
                        left outer join ord 
                        on ord.ordnum = shipping_pckwrk_view.ordnum
                        where 
                        --ord.stcust='805015305' --codigo cliente
                        shipping_pckwrk_view.ordnum = """+pl+""" order by ord.adddte""")
                        
    resultado = cursor.fetchone()

    if resultado == None:

        cursor.close()
        con.close()
        
        dsn = cx_Oracle.makedsn(host='10.100.3.219', port=1521, service_name = 'ARCH.starchdb.dns.oraclevcn.com')
        con = cx_Oracle.connect(user='DEVELOP', password='M#n4g3R_01', dsn=dsn)
        cursor = con.cursor()
        cursor.execute(""" select 
                        distinct(shipping_pckwrk_view.ordnum)as orden, 
                        case when inventory_pckwrk_view.stoloc like 'MOVIL%' then 'En Picking' 
                            when inventory_pckwrk_view.stoloc like 'CON%' then 'En Pickig' 
                            when inventory_pckwrk_view.stoloc like 'MESAE%' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like 'ESTMESAE%' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like '%-STG' then 'En Empaque' 
                            when inventory_pckwrk_view.stoloc like 'STGD%' then 'En Despacho' 
                            when inventory_pckwrk_view.stoloc like 'TRL0%' then 'En Camion' 
                            else 'Despachado' end as estado,
                            ord.adddte as fecha_pase_bodega,
                            (select max(pckwrk_view.pckdte)
                                        from pckwrk_view
                                        where pckwrk_view.ordnum = ord.ordnum
                                        and pckwrk_view.wrktyp = 'K'
                                        and pckwrk_view.dtl_pckqty > 0) fecha_empaque,
                                        dispatch_dte as fecha_despacho
                        from 
                        shipping_pckwrk_view 
                        left outer join inventory_pckwrk_view 
                        on shipping_pckwrk_view.ordnum = inventory_pckwrk_view.ordnum 
                        and shipping_pckwrk_view.wh_id = inventory_pckwrk_view.wh_id 
                        left outer join trlr 
                        on shipping_pckwrk_view.trlr_id = trlr.trlr_id 
                        left outer join ord 
                        on ord.ordnum = shipping_pckwrk_view.ordnum
                        where 
                        --ord.stcust='805015305' --codigo cliente
                        shipping_pckwrk_view.ordnum = '"""+pl+"""' order by ord.adddte """)
        resultado = cursor.fetchone()
        
                
    return resultado

def establecer_conexion_infdrv():
    cnxn = pyodbc.connect('DSN=Infdrv1')
    cursor = cnxn.cursor()
    return cursor

app = FastAPI()

@app.get("/helloWorld")
def read_root():
    return {"Hello": "World"}

@app.get("/consulta_pedido/{tipo_doc}/{num_doc}")
def read_items(tipo_doc: str, num_doc: int):
    cursor = establecer_conexion_infdrv()

    cursor.execute("""
        SELECT  cot1_status, max(sepa_packing_list), asbo_fecha_cierre||" "||asbo_hora_cierre
        FROM vymcot1, outer plisepa, outer pliasbo
        WHERE LOWER(cot1_td_cotizacion) = LOWER(?)
        AND cot1_no_cotizacion = ?
        AND cot1_td_cotizacion = sepa_td_cotizacion
        AND cot1_no_cotizacion = sepa_no_cotizacion
        AND cot1_td_cotizacion = asbo_tdoc_orig
        AND cot1_no_cotizacion = asbo_doc_orig
        AND asbo_code_tarea = "006"
        group by 1, 3
    """, (tipo_doc, num_doc))

    
    resultado = cursor.fetchone()
    #print(resultado)
    
    # Cierra el cursor y la conexión
    cursor.close()

    if resultado:
        estado_pedido = resultado[0]
        #print(estado_pedido)
        if estado_pedido == '3':
            mensaje = "ANULADO"
        elif estado_pedido == '4':
            mensaje = ["CONFIRMADO"]
            mensaje.append(resultado[2]) 
        elif estado_pedido == '5':
            mensaje = pedido_wms(resultado[1])
            mensaje = mensaje+ (resultado[2],)                
        elif estado_pedido == '6':
            mensaje = pedido_wms(resultado[1])
            mensaje = mensaje+ (resultado[2],)      
        else:
            mensaje = "DESCONOCIDO"
    else:
        mensaje = "El pedido "+tipo_doc+" "+str(num_doc)+" no se encuentra en nuestra base de datos."

    return {"mensaje": mensaje}


@app.get("/consulta_detalle_pedido/{tipo_doc}/{num_doc}")
def detalle(tipo_doc: str, num_doc: int):
    cursor = establecer_conexion_infdrv()

    cursor.execute("""
         SELECT cot1_td_cotizacion||cot1_no_cotizacion, cot1_fecha_doc,
        DECODE(cot1_status, 3, 'ANULADO', 4, 'CONFIRMADO', 5, 'EN BODEGA', 6, 'FACTURADO', 'OTRO'),
        SUM((cot2_precio_arti - cot2_descto_global - cot2_descto_linea2 - cot2_descto_linea)*(cot2_cant_enviada))
        FROM vymcot1, vymcot2
        WHERE LOWER(cot1_td_cotizacion) = LOWER(?)
        AND cot1_no_cotizacion = ?
        AND cot1_td_cotizacion = cot2_td_cotizacion
        AND cot1_no_cotizacion = cot2_no_cotizacion
        GROUP BY 1, 2, 3
    """, (tipo_doc, num_doc))

    resultado = cursor.fetchone()

    cursor.execute("""
        SELECT cot2_code_articulo, cot2_cant_solic, cot2_cant_enviada
        FROM vymcot2
        WHERE cot2_td_cotizacion = ?
        AND cot2_no_cotizacion = ?   
    """, (tipo_doc, num_doc))

    resultado2 = cursor.fetchall()

    cursor.close()

    # Convertir Decimals a float antes de construir el diccionario de respuesta
    total = float(resultado[3])
    items = [{"cot2_code_articulo": row[0], "cot2_cant_solic": float(row[1]), "cot2_cant_enviada": float(row[2])} for row in resultado2]

    # Construye el diccionario de respuesta
    response_dict = {
        "detalle": {
            "cot1_td_cotizacion": resultado[0],
            "cot1_fecha_doc": resultado[1].strftime("%Y-%m-%d"),
            "cot1_status": resultado[2],
            "cot1_total": total
        },
        "items": items
    }

    return response_dict


@app.get("/consulta_pedidos_activos/{code_cliente}")
def pedidosActivos(code_cliente: str):
    cursor = establecer_conexion_infdrv()

    cursor.execute("""
        SELECT cot1_td_cotizacion||cot1_no_cotizacion, cot1_fecha_doc,
        DECODE(cot1_status, 3, 'ANULADO', 4, 'CONFIRMADO', 5, 'EN BODEGA', 6, 'FACTURADO', 'OTRO')
        FROM vymcot1
        WHERE cot1_code_cliente = ?
        ORDER BY cot1_fecha_doc DESC
        limit 10
    """, (code_cliente,))

    resultados = cursor.fetchall()

    cursor.close()

    if resultados:
        # Construye una lista de diccionarios para representar todos los pedidos activos
        pedidos_activos = []
        for resultado in resultados:
            pedido = {
                "cot1_td_cotizacion": resultado[0],
                "cot1_fecha_doc": resultado[1].strftime("%Y-%m-%d"),
                "cot1_status": resultado[2],
            }
            pedidos_activos.append(pedido)
        
        return {"pedidos_activos": pedidos_activos}
    else:
        return {"mensaje": "Cliente no encontrado o sin pedidos activos."}