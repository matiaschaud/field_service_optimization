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
        self.map_var = {}
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

    # Restricción 1: No se pueden realizar varias ordenes en un mismo turno, si comparten trabajadores
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
                    coeficientes_funcion_objetivo.append(-1000)
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

    # Como hasta acá todas las variables son booleanas, corresponde:
    lb = [0]*len(coeficientes_funcion_objetivo)
    ub = [1]*len(coeficientes_funcion_objetivo)
    types = ['B']*len(coeficientes_funcion_objetivo)
    		
    
    my_problem.variables.add(obj = coeficientes_funcion_objetivo, lb = lb , ub = ub, types = types, names = data.names) 

    # Seteamos direccion del problema
    # ~ my_problem.objective.set_sense(my_problem.objective.sense.maximize)
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