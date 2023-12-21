import httpx

url = "https://pedidos.impocali.com/api/item/buscarAI?1=1&todosLosCampos=amortiguador%20%20TTR&criteriaComparison=equals&mostrarAgotados=true&tieneQueEstarEnRemate=false&sort=estado&order=asc&offset=0&max=10&filialCode=001"

# Realizar la solicitud GET a la URL
with httpx.Client() as client:
    response = client.get(url)

    # Verificar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Imprimir la respuesta en formato JSON
        print(response.json())
    else:
        # Imprimir un mensaje de error si la solicitud falla
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
