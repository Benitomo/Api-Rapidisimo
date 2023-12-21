import requests

url = "https://pedidos.impocali.com/api/item/buscarAI"

params = {
    'todosLosCampos': 'amortiguador  TTR',
    'criteriaComparison': 'equals',
    'mostrarAgotados': 'true',
    'tieneQueEstarEnRemate': 'false',
    'sort': 'estado',
    'order': 'asc',
    'offset': '0',
    'max': '10',
    'filialCode': '001'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Error en la solicitud. Código de estado: {response.status_code}")
