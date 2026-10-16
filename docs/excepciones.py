"""
EXCEPCIONES: eventos que ocurren durante la ejecución que indican que algo impide el programa 
try: intentar
except: si sucede ese error, haz x
raise: levantar error, lanza explícitamente una excepción
finally: se ejecuta siempre sin importar si hubo o no excepción -> Cerrar conexiones/archivos, liberar recursos
else: es lo que se va a ejecutar si NO hubo ningún error

SINTAXIS
try:
    #bloque de código que quiero tratar de realizar
except Error:
    #bloque de código que quiero que se ejecture si ocurre la excepción

"""

#Error que aparece al intentar dividir entre 0
try:
    x = 10
    y = 0
    resultado = x/y
except ZeroDivisionError: #Error que aparece al intentar dividir entre 0
    print('No puedo dividir entre cero')


#Error 
try:
    numero = int('hola')
    print(numero)
except ValueError:
    print('favor de dar un numeral')


#Error al concatenar un no str
texto = 'Hola clase'  #aqui casteamos el 'num'
num = 22
frase = texto + str(num)
print(frase)


texto = 'Hola clase' #aqui la excepción si no casteamos
num = 22
try:
    frase = texto + num
except TypeError:
    print('Tipos de datos distintos')


#Error que aparece al solicitar un dato que no está en la lista
try:
    fruta = ['manzanas', 'plátano', 'sandía']
    print(fruta[6])
except IndexError:
    print('fruta inexistente')


#Error que aparece al buscar un dato que no está en el diccionario
try:
    estudiante = {
        'nombre': 'Pedro',
        'apellido': 'Páramo'
    }
    print(estudiante['email'])
except KeyError:
    print('La clave no existe')


def dividir():
    try:
        num1 = int(input('Ingresa el primer numero: '))
        num2 = int(input('Ingresa el segundo número: '))
        resultado = num1/num2
        print(f'El resultado es: {resultado}')
    except ValueError:
        print('Solo permite número enteros')
    except ZeroDivisionError:
        print('La calculadora no puede divir entre 0')
    except Exception as error: #errores de manera general, error tendrá os detalles de la excepción
        print(f'ocurrió un error inesperado: {error}')
    finally:
        print('Gracias por usar la calculadora')

dividir()


try:
    bebidas = ['coca-cola', 'agua saborizada', 'chocolate caliente']
    bebidas_deseadas = input('Ingresa la bebida que quieres:')
    if bebidas_deseadas not in bebidas:
        raise ValueError(f'Esa bebida no está disponible') #raise -> levantando una excepción
    else:
        print(f'tu bebida {bebidas_deseadas} está en la lista')
except ValueError as error:
    print(f'Error: {error}')