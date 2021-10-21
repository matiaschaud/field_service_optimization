import numpy as np

cantidad_trabajadores = 20
cantidad_trabajadores_maximo_por_orden = 5
cantidad_ordenes = 200
min_beneficio = 2500
max_beneficio = 15000
cantidad_conflictos_trabajadores = 3
cantidad_ordenes_correlativas = 15
cantidad_ordenes_conflictivas = 5
cantidad_ordenes_repetitivas = 15

with open("input_field_service.txt","w") as archivo:
    archivo.write(f"{cantidad_trabajadores}\n")
    archivo.write(f"{cantidad_ordenes}\n")
    for i in range(cantidad_ordenes):
        archivo.write(f"{i} {np.random.randint(min_beneficio,max_beneficio,1)[0]} {np.random.randint(1,cantidad_trabajadores_maximo_por_orden,1)[0]}\n")
    archivo.write(f"{cantidad_conflictos_trabajadores}\n")
    for i in range(cantidad_conflictos_trabajadores):
        while (True):
            t_1 = np.random.randint(0, cantidad_trabajadores,1)[0]
            t_2 = np.random.randint(0, cantidad_trabajadores,1)[0]
            if t_1 != t_2:
                break
        archivo.write(f"{t_1} {t_2}\n")

    archivo.write(f"{cantidad_ordenes_correlativas}\n")
    for i in range(cantidad_ordenes_correlativas):
        while (True):
            o_1 = np.random.randint(0, cantidad_ordenes,1)[0]
            o_2 = np.random.randint(0, cantidad_ordenes,1)[0]
            if o_1 != o_2:
                break
        archivo.write(f"{o_1} {o_2}\n")

    archivo.write(f"{cantidad_ordenes_conflictivas}\n")
    for i in range(cantidad_ordenes_conflictivas):
        while (True):
            o_1 = np.random.randint(0, cantidad_ordenes,1)[0]
            o_2 = np.random.randint(0, cantidad_ordenes,1)[0]
            if o_1 != o_2:
                break
        archivo.write(f"{o_1} {o_2}\n")

    archivo.write(f"{cantidad_ordenes_repetitivas}\n")
    for i in range(cantidad_ordenes_repetitivas):
        while (True):
            o_1 = np.random.randint(0, cantidad_ordenes,1)[0]
            o_2 = np.random.randint(0, cantidad_ordenes,1)[0]
            if o_1 != o_2:
                break
        archivo.write(f"{o_1} {o_2}\n")