import http.client
import json

url = "/api/item/buscarAI?1=1&todosLosCampos=amortiguador%20%20TTR&criteriaComparison=equals&mostrarAgotados=true&tieneQueEstarEnRemate=false&sort=estado&order=asc&offset=0&max=10&filialCode=001"
conn = http.client.HTTPSConnection("pedidos.impocali.com")
conn.request("GET", url)
response = conn.getresponse()

# Verificar si la solicitud fue exitosa (código de estado 200)
if response.status == 200:
    # Imprimir la respuesta en formato JSON
    data = json.loads(response.read().decode('utf-8'))
    print(data)
else:
    # Imprimir un mensaje de error si la solicitud falla
    print(f"Error en la solicitud. Código de estado: {response.status}")
conn.close()
