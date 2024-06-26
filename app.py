import enum
from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

def calcular_promedio(nota1, nota2, nota3):
    return (nota1 + nota2 + nota3) / 3


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/buscar', methods=['POST'])
def buscar():
    try:
        spp = request.form['cui']

        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="steven123XD",
            database="matpro"
        )
        cursor = conn.cursor()

        sql = """SELECT semestre FROM alumnos WHERE CUI = %s """
        cursor.execute(sql, (spp,))
        resultado = cursor.fetchone()

        sql5 = """SELECT Correo FROM alumnos WHERE CUI =  %s"""
        cursor.execute(sql5,(spp,))
        resultado01 =cursor.fetchone()

        sql6 = """SELECT Nombre FROM alumnos WHERE CUI = %s"""
        cursor.execute(sql6,(spp,))
        resultado02 = cursor.fetchone()

        sql7 ="""SELECT Apellido FROM alumnos WHERE CUI = %s"""
        cursor.execute(sql7,(spp,))
        resultado03 = cursor.fetchone()

        if resultado:
            semestre_alumno = resultado[0]
            Correo_alumno = resultado01[0]
            NombreCompleto = resultado02[0]
            ApellidoCompleto = resultado03[0]
            sql2 = """SELECT Nombre FROM cursos WHERE Semestre = %s"""
            cursor.execute(sql2, (semestre_alumno,))
            cursos_resultado = cursor.fetchall()

            if cursos_resultado:
                cursos = [curso[0] for curso in cursos_resultado]
            else:
                cursos = []
            profesores = []
            apellidos = []
            codigoCurso = []
            
            #cursos pasados
            Cursopasadosnombre= []

            sqlp="""SELECT CodCurso FROM matricula WHERE CodAlumno = %s AND Nota01 != -1;"""
            cursor.execute(sqlp,(spp, ))
            codigoCursopasados_resultado = cursor.fetchall()
            if codigoCursopasados_resultado:
                codigoCursopasados = [codcur[0] for codcur in codigoCursopasados_resultado]
            else:
                codigoCursopasados= []
            print(codigoCursopasados)
            for j in codigoCursopasados:
                nuevo3 = """SELECT Nombre FROM matpro.cursos WHERE matpro.cursos.Codigo_Curso = %s"""
                cursor.execute(nuevo3, (j,))
                auxi=cursor.fetchone()
                
                if auxi:
                    Cursopasadosnombre.append(auxi)
                else:
                    print(f"No se encontró un curso para el código {j}")

            for i, curso in enumerate(cursos,start=1):

                #Codigo de los nombres del docente
                nuevo = """SELECT Nombres FROM cursos INNER JOIN docentes ON Codigo_Docente = idDocentes WHERE cursos.Nombre = %s;"""
                cursor.execute(nuevo,(curso,))
                profesor_resultado = cursor.fetchone()
                profesores.append(profesor_resultado)

                #Codigo de los apellidos del docente
                nuevo1 = """SELECT Apellido FROM cursos INNER JOIN docentes ON Codigo_Docente = idDocentes WHERE cursos.Nombre = %s;"""
                cursor.execute(nuevo1,(curso,))
                apellido_resultado = cursor.fetchone()
                apellidos.append(apellido_resultado)

                #Codigo del curso
                nuevo2 = """SELECT Codigo_Curso FROM matpro.cursos WHERE matpro.cursos.Nombre = %s;"""
                cursor.execute(nuevo2,(curso,))
                codigo_resultado = cursor.fetchone()
                codigoCurso.append(codigo_resultado)

            ##############################################################
            docentesA = [ap[0] for ap in apellidos]
            docentes = [docente[0] for docente in profesores]
            codigos = [cod[0] for cod in codigoCurso]
            nombrepas = [codn[0] for codn in Cursopasadosnombre]

            cantidad = len(cursos)
            cantidad2 = len(codigoCursopasados)
            ##############################################################
            #Promedios
            promediosporcurso=[]
            for j in codigoCursopasados:
                sql = """SELECT Nota01, Nota02, Nota03 FROM matricula WHERE CodAlumno = %s AND CodCurso=%s AND Nota01<>-1;"""
                cursor.execute(sql,(spp,j,))
                resultados=cursor.fetchall()

                prom= None

                for fila in resultados:
                    nota01, nota02, nota03 = fila
                    prom = calcular_promedio(nota01,nota02,nota03)
                    print(f"Curso: {j}, Nota01: {nota01}, Nota02: {nota02}, Nota03: {nota03}")
                promediosporcurso.append(prom)
            
            sumatoriadecursospasados = sum(promediosporcurso)
            
            promgen=0
            if(semestre_alumno-1!=0):
                sql="""SELECT Cursos_ID FROM cursos WHERE Semestre = %s ORDER BY Cursos_ID DESC LIMIT 1;"""
                cursor.execute(sql,(semestre_alumno-1,))
                print(semestre_alumno-1)
                cantcursossem=cursor.fetchone()
                promgen=sumatoriadecursospasados/cantcursossem[0]
            else:
                promgen=-3

            ###CALCULO DEL SEMESTRE
            conteosemestre=[0,0,0,0,0,0,0,0,0,0]
            for j in codigos:
                sql="""SELECT Semestre FROM cursos WHERE Codigo_Curso=%s"""
                cursor.execute(sql,(j,))
                auxi=cursor.fetchone()
                if auxi is not None:
                    sem = auxi[0]  # Extraer el primer elemento de la tupla
                    sem = int(sem)  # Convertirlo a entero
                
                for i in range(10):
                    if i==sem-1:
                        conteosemestre[i]+=1

            auximayor=0
            auxisubm=0

            for j in conteosemestre:
                if j>auximayor:
                    auximayor=j
                    auxisubm=auximayor
            
            semestreactual=0
            if auximayor==auxisubm:
                semestreactual=conteosemestre.index(auxisubm)+1
            else:
                semestreactual=conteosemestre.index(auximayor)+1


            for i in range(10):
                print(conteosemestre[i])


            return render_template('resultado.html',semestreactual=semestreactual,promgen=promgen,promcurso=promediosporcurso,nombrepas=nombrepas,num2=cantidad2,cursospasados=codigoCursopasados,code = codigos,  apellidos=docentesA, cui=spp, semestre=semestre_alumno, correo = Correo_alumno, nombre=NombreCompleto, apellido=ApellidoCompleto, num = cantidad, cursos=cursos, docentes=docentes)
        else:
            return render_template('error.html', mensaje="No se encontró ningún alumno con el CUI proporcionado.")

    except mysql.connector.Error as e:
        return render_template('error.html', mensaje="Error al conectar a la base de datos: " + str(e))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
