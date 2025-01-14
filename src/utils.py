def cargar_objeto(ruta):
    with open(ruta, 'r') as archivo:
        lineas = archivo.readlines()
    
    vertices = []
    caras = []
    
    for linea in lineas:
        if linea.startswith('v '):
            partes = linea.split()
            vertices.append((float(partes[1]), float(partes[2]), float(partes[3])))
        elif linea.startswith('f '):
            partes = linea.split()
            cara = [int(partes[i].split('/')[0]) - 1 for i in range(1, len(partes))]
            caras.append(cara)
    
    return vertices, caras

def convertir_coordenadas(coordenadas, escala=1.0):
    return [(x * escala, y * escala, z * escala) for x, y, z in coordenadas]