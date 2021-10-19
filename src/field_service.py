import sys
import cplex
# import numpy as np

TOLERANCE =10e-6 

class Orden:
    def __init__(self):
        self.id = 0
        self.beneficio = 0
        self.trabajadores_necesarios = 0
    
    def load(self, row):
        self.id = int(row[0])
        self.beneficio = int(row[1])
        self.trabajadores_necesarios = int(row[2])


class FieldWorkAssignment:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []

        self.map_var = {} # "nombre_variable": indice -> ej: "X1,1,2,3": 10
        self.names = []
        self.cantidad_dias = 6
        self.cantidad_turnos_por_dia = 5 

    def load(self,filename):
        # Abrimos el archivo.
        f = open(filename)

        # Leemos la cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Leemos la cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Leemos cada una de las ordenes.
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            row = f.readline().split(' ')
            orden = Orden()
            orden.load(row)
            self.ordenes.append(orden)
        
        # Leemos la cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Leemos los conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            row = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Leemos las ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            row = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,row)))
            
        # Leemos la cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Leemos las ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            row = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,row)))
        
        
        # Leemos la cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Leemos las ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            row = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,row)))
        
        # Cerramos el archivo.
        f.close()


def get_instance_data():
    # file_location = sys.argv[1].strip()
    file_location = "../Data/input_field_service.txt"
    instance = FieldWorkAssignment()
    instance.load(file_location)
    return instance
    

def add_constraint_matrix(my_problem, data):
    # restriccion ejemplo: X1,1,1,1 + X1,1,1,2 + ... + X1,1,1,9 <= 1
    # Restricción 1: No se pueden realizar varias ordenes en un mismo turno si comparten trabajadores
    for trabajador in range(data.cantidad_trabajadores):
        for turno in range(data.cantidad_turnos_por_dia):
            for dia in range(data.cantidad_dias):
                indices = []
                values = []
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden}"])
                    values.append(1)
                row = [indices,values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
    
    # Restricción 2: Una orden de trabajo debe tener sus To trabajadores para poder ser resuelta.
    for orden in data.ordenes:
        indices = []
        values = []
        for trabajador in range(data.cantidad_trabajadores):
            for turno in range(data.cantidad_turnos_por_dia):
                for dia in range(data.cantidad_dias):
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden.id}"])
                    values.append(1)
        indices.append(data.map_var[f"Z{orden.id}"])
        values.append(orden.trabajadores_necesarios * -1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])

    # Restricción 3: Una orden se puede realizar solo en un horario
    for orden in data.ordenes:
        indices = []
        values = []
        for turno in range(data.cantidad_turnos_por_dia):
            for dia in range(data.cantidad_dias):
                indices.append(data.map_var[f"Y{turno},{dia},{orden.id}"])
                values.append(1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[1])
    
    for turno in range(data.cantidad_turnos_por_dia):
        for dia in range(data.cantidad_dias):
            for orden in data.ordenes:
                indices = []
                values = []
                for trabajador in range(data.cantidad_trabajadores):
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden.id}"])
                    values.append(1)
                indices.append(data.map_var[f"Y{turno},{dia},{orden.id}"])
                values.append(orden.trabajadores_necesarios * -1)
                row = [indices,values]
                my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])
                # E (=)
                # L (<=)

    # Restricción 4: Ningún trabajador puede trabajar los 6 días de la semana
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for dia in range(data.cantidad_dias):
            indices.append(data.map_var[f"D{trabajador},{dia}"])
            values.append(1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[5])

    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(data.cantidad_dias):
            indices = []
            values = []
            for turno in range(data.cantidad_turnos_por_dia):
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden}"])
                    values.append(1)
            indices.append(data.map_var[f"D{trabajador},{dia}"])
            values.append(-5)
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])

    # Restricción 5: Ningún trabajador puede trabajar los 5 turnos en un día.
    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(data.cantidad_dias):
            indices = []
            values = []
            for turno in range(data.cantidad_turnos_por_dia):
                for orden in range(data.cantidad_ordenes):
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden}"])
                    values.append(1)
            row = [indices,values]
            my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[4])

    # Restricción 6: Los trabajadores son remunerados segun la cantidad de ordenes asignadas
    # * 0  a  5 ordenes: 1000
    # * 5  a 10 ordenes: 1200
    # * 10 a 15 ordenes: 1400
    # * > 15 ordenes: 1500
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for turno in range(data.cantidad_turnos_por_dia):
            for dia in range(data.cantidad_dias):
                for orden in data.ordenes:
                    indices.append(data.map_var[f"X{trabajador},{turno},{dia},{orden.id}"])
                    values.append(1)
        indices.append(data.map_var[f"W{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])
    
    for trabajador in range(data.cantidad_trabajadores):
        indices = []
        values = []
        for W in (range(1,5)):
            indices.append(data.map_var[f"W{W}{trabajador}"])
            values.append(1)
        indices.append(data.map_var[f"W{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["E"], rhs=[0])

    for trabajador in range(data.cantidad_trabajadores):
        # A2t <= A1t
        indices = []
        values = []
        indices.append(data.map_var[f"A2{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A1{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])
        # A3t <= A2t
        indices = []
        values = []
        indices.append(data.map_var[f"A3{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A2{trabajador}"])
        values.append(-1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])

    for trabajador in range(data.cantidad_trabajadores):
        # 5*A1t <= W1t <= 5
        # W1t <= 5
        indices = []
        values = []
        indices.append(data.map_var[f"W1{trabajador}"])
        values.append(1)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[5])
        # 5*A1t <= W1t
        indices = []
        values = []
        indices.append(data.map_var[f"W1{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A1{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["G"], rhs=[0])
        # (10-5) A2t <= W2t <= (10-5) * A1t
        # W2t <= (10-5) * A1t
        indices = []
        values = []
        indices.append(data.map_var[f"W2{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A1{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])
        # (10-5) A2t <= W2t
        indices = []
        values = []
        indices.append(data.map_var[f"W2{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A2{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["G"], rhs=[0])
        # (15-10) A3t <= W3t <= (15-10) * A2t
        # W3t <= (15-10) * A2t
        indices = []
        values = []
        indices.append(data.map_var[f"W3{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A2{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])
        # (15-10) A3t <= W3t
        indices = []
        values = []
        indices.append(data.map_var[f"W3{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A3{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["G"], rhs=[0])    
        # 0 <= W4t <= (20-15) * A3t
        # W4t <= (20-15) * A3t
        indices = []
        values = []
        indices.append(data.map_var[f"W4{trabajador}"])
        values.append(1)
        indices.append(data.map_var[f"A3{trabajador}"])
        values.append(-5)
        row = [indices,values]
        my_problem.linear_constraints.add(lin_expr=[row], senses=["L"], rhs=[0])
        # Esta restricción ya esta cubierta?
        # 0 <= W4t
        # indices = []
        # values = []
        # indices.append(data.map_var[f"W4{trabajador}"])
        # values.append(1)
        # indices.append(1)
        # values.append(0)
        # row = [indices,values]
        # my_problem.linear_constraints.add(lin_expr=[row], senses=["G"], rhs=[0]) 


def populate_by_row(my_problem, data):
    
    # Definimos y agregamos las variables.
    coeficientes_funcion_objetivo = []
    # Appendeamos primero los beneficios de las ordenes (positivas)

    # Añadimos las variables Zo
    for orden in data.ordenes:
        coeficientes_funcion_objetivo.append(orden.beneficio)
        name = f"Z{orden.id}"
        data.names.append(name)
        data.map_var[name]=len(coeficientes_funcion_objetivo)-1

    # Añadimos las variables Xthdo
    for trabajador in range(data.cantidad_trabajadores):
        for turno in range(data.cantidad_turnos_por_dia):
            for dia in range(data.cantidad_dias):
                for orden in range(data.cantidad_ordenes):
                    coeficientes_funcion_objetivo.append(0)
                    name = f"X{trabajador},{turno},{dia},{orden}"
                    data.names.append(name)
                    data.map_var[name]=len(coeficientes_funcion_objetivo)-1

    # Añadimos las variables Yhdo
    for turno in range(data.cantidad_turnos_por_dia):
        for dia in range(data.cantidad_dias):
            for orden in range(data.cantidad_ordenes):
                coeficientes_funcion_objetivo.append(0)
                name = f"Y{turno},{dia},{orden}"
                data.names.append(name)
                data.map_var[name]=len(coeficientes_funcion_objetivo)-1
    # Añadimos las variables Dtd
    for trabajador in range(data.cantidad_trabajadores):
        for dia in range(data.cantidad_dias):
            coeficientes_funcion_objetivo.append(0)
            name = f"D{trabajador},{dia}"
            data.names.append(name)
            data.map_var[name]=len(coeficientes_funcion_objetivo)-1


    # Añadimos las variables A1t, A2t, A3t, A4t
    for trabajador in range(data.cantidad_trabajadores):
        for aux in range(1,4):
            coeficientes_funcion_objetivo.append(0)
            name = f"A{aux}{trabajador}"
            data.names.append(name)
            data.map_var[name]=len(coeficientes_funcion_objetivo)-1

    # Como hasta acá todas las variables son booleanas, corresponde:
    lb = [0]*len(coeficientes_funcion_objetivo)
    ub = [1]*len(coeficientes_funcion_objetivo)
    types = ['B']*len(coeficientes_funcion_objetivo)

    # Definimos las variables W1t, W2t, W3t, W4t
    pagas = {1: 1000, 2: 1200, 3:1400, 4:1500}
    
    for trabajador in range(data.cantidad_trabajadores):
        for aux in range(1,5):
            coeficientes_funcion_objetivo.append(pagas[aux]*(-1))
            name = f"W{aux}{trabajador}"
            data.names.append(name)
            data.map_var[name]=len(coeficientes_funcion_objetivo)-1

    # Guardamos en una variable los distintos tipos posibles para utilizarlos dentro de variables.add
    t = my_problem.variables.type

    lb = lb + [0] * (data.cantidad_trabajadores * 4)
    ub = ub + [5] * (data.cantidad_trabajadores * 4)
    types = types + [t.integer]*(data.cantidad_trabajadores * 4)

    # Añadimos las variables Wt
    for trabajador in range(data.cantidad_trabajadores):
        coeficientes_funcion_objetivo.append(0)
        name = f"W{trabajador}"
        data.names.append(name)
        data.map_var[name]=len(coeficientes_funcion_objetivo)-1
    
    lb = lb + [0] * (data.cantidad_trabajadores)
    ub = ub + [20] * (data.cantidad_trabajadores)
    types = types + [t.integer]*(data.cantidad_trabajadores)

    my_problem.variables.add(obj = coeficientes_funcion_objetivo, lb = lb , ub = ub, types = types, names = data.names) 

    # Seteamos direccion del problema
    my_problem.objective.set_sense(my_problem.objective.sense.maximize)
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.minimize)

    # Definimos las restricciones del modelo. Encapsulamos esto en una funcion. 
    add_constraint_matrix(my_problem, data)

    # Exportamos el LP cargado en myprob con formato .lp. 
    # Util para debug.
    my_problem.write('balanced_assignment.lp')

def solve_lp(my_problem, data):
    
    # Resolvemos el ILP.
    
    my_problem.solve()

    # Obtenemos informacion de la solucion. Esto lo hacemos a traves de 'solution'. 
    x_variables = my_problem.solution.get_values()
    objective_value = my_problem.solution.get_objective_value()
    status = my_problem.solution.get_status()
    status_string = my_problem.solution.get_status_string(status_code = status)

    print('Funcion objetivo: ',objective_value)
    print('Status solucion: ',status_string,'(' + str(status) + ')')

    # Imprimimos las variables usadas.
    for i in range(len(x_variables)):
        # Tomamos esto como valor de tolerancia, por cuestiones numericas.
        if x_variables[i] > TOLERANCE:
            # pass
            print(str(data.names[i]) + ':' , x_variables[i])

def main():
    
    # Obtenemos los datos de la instancia.
    data = get_instance_data()
    # ~ print(vars(data))
    # ~ for orden in data.ordenes:
        # ~ print(vars(orden))
    
    # Definimos el problema de cplex.
    prob_lp = cplex.Cplex()
    
    # Armamos el modelo.
    populate_by_row(prob_lp,data)

    # Resolvemos el modelo.
    solve_lp(prob_lp,data)


if __name__ == '__main__':
    main()