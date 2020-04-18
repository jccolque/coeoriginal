
#Funciones basicas:
def obtener_dni(data):
    if "dni" in data:
        return str(data["dni"]).upper()
    else:
        return str(data["dni_individuo"]).upper()