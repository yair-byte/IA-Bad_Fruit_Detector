# -*- coding: utf-8 -*-
"""
GUI.py

Programa para manejar una interfaz grafica para el proyecto 
"Detector de frutas en mal estado basado en Inteligencia Artificial"
"""
#imports 
import tkinter as tk
from PIL import Image, ImageTk
from time import sleep
from pySerialTransfer import pySerialTransfer as txfer
import numpy as np # linear algebra
import sys
import threading


#Variables globales

imagen_actual = 0
estado_actual = 0
tiempo_identificacion = 0
tiempo_periodo = 0
cantidad_naranja_mal_estado = 0
cantidad_naranja_buen_estado = 0
cantidad_manzana_mal_estado = 0
cantidad_manzana_buen_estado = 0
cantidad_banana_mal_estado = 0
cantidad_banana_buen_estado = 0


# Let's create the Tkinter window
window = tk.Tk()
window.title("Clasificador de frutas")

#Funciones
def cargar_imagen ():
    """Configura la seccion de imagen de la interfaz.
        Parametros
        -----------
        image : Image
            Es el archivo de imagen. Puede ser .jpg or .png
    """

    tk.Label(window, text = "Clasificador v1.2").grid(row = 0)
    #Para abrir una imagen usando el nombre de archivo.
    
    global imagen_actual
    image = imagen_actual
    image = image.resize((400,400))
    photo = ImageTk.PhotoImage(image, master=window)
    label = tk.Label(window, image=photo)
    label.image = photo # keep a reference!
    label.grid(row=0, column = 1)
    

def cargar_estado():
    """Configura la seccion del estado de la fruta.
        Parametros
        -----------
        estado: 0 a 5
            Es el estado de la fruta como lo reconoce el sensor. 
            0 - indica que es una naranja en mal estado
            1 - indica que es una naranja en buen estado
            2 - indica que es una manzana en mal estado
            3 - indica que es una manzana en buen estado
            4 - indica que es una banana en mal estado
            5 - indica que es una banana en buen estado
    """
    
    global cantidad_naranja_mal_estado
    global cantidad_naranja_buen_estado
    global cantidad_manzana_mal_estado
    global cantidad_manzana_buen_estado
    global cantidad_banana_mal_estado
    global cantidad_banana_buen_estado
    global estado_actual

    estado_str = ''
    
    #Defino el estado
    if estado_actual == 0:
        estado_str = "NARANJA EN MAL ESTADO"
        cantidad_naranja_mal_estado += 1 
    elif estado_actual == 1:
        estado_str = "NARANJA EN BUEN ESTADO"
        cantidad_naranja_buen_estado += 1
    elif estado_actual == 2:
        estado_str = "MANZANA EN MAL ESTADO"
        cantidad_manzana_mal_estado += 1 
    elif estado_actual == 3:
        estado_str = "MANZANA EN BUEN ESTADO"
        cantidad_manzana_buen_estado += 1
    elif estado_actual == 4:
        estado_str = "BANANA EN MAL ESTADO"
        cantidad_banana_mal_estado += 1 
    else:
        estado_str = "BANANA EN BUEN ESTADO"
        cantidad_banana_buen_estado += 1
        
    #'Estado de la fruta' is placed on position 20 (row - 2 and column - 0)
    tk.Label(window, text = "Estado de la fruta").grid(row = 2)
    # second input-field is placed on position 21 (row - 2 and column - 1) 
    entry_estado = tk.Entry(window, width=26)
    entry_estado.grid(row = 2, column = 1)
    entry_estado.insert(0, estado_str)
    if estado_actual == 0:
        entry_estado.config(readonlybackground="red")
    elif estado_actual == 1:
        entry_estado.config(readonlybackground="green")
    elif estado_actual == 2:
        entry_estado.config(readonlybackground="red")
    elif estado_actual == 3:
        entry_estado.config(readonlybackground="green")
    elif estado_actual == 4:
        entry_estado.config(readonlybackground="red")
    else:
        entry_estado.config(readonlybackground="green")

        
        
    entry_estado.config(state='readonly')

def cargar_tiempo ():
    """Configura la seccion del tiempo de indentificacion.
        Parametros
        -----------
        tiempo: float
            Es el tiempo que demoro el sistema en indentificar la fruta.
    """
    global tiempo_identificacion
    global tiempo_periodo
    
    #'Tiempo de periodo ' is placed on position 30 (row - 3 and column - 0)
    tk.Label(window, text = "Periodo").grid(row = 3)
    #third input-field is placed on position 31 (row - 3 and column - 1) 
    entry_tiempo = tk.Entry(window, width=22)
    entry_tiempo.grid(row = 3, column = 1)
    entry_tiempo.insert(0, (tiempo_periodo+str(' ms')))
    entry_tiempo.config(state='readonly')

    #'Tiempo de la identificacion' is placed on position 30 (row - 3 and column - 0)
    tk.Label(window, text = "Tiempo de la identificacion").grid(row = 4)
    #third input-field is placed on position 31 (row - 3 and column - 1) 
    entry_tiempo = tk.Entry(window, width=22)
    entry_tiempo.grid(row = 4, column = 1)
    entry_tiempo.insert(0, (tiempo_identificacion+str(' ms')))
    entry_tiempo.config(state='readonly')
    
    
   
    

def cargar_cantidades():
    """Configura la seccion del tiempo de las cantidades de frutas en
        buen estado y en mal estado va detectando el sistema.
        Utiliza las variables internas para llevar una cuenta de ello.
    """
    
    
    global cantidad_naranja_mal_estado
    global cantidad_naranja_buen_estado
    global cantidad_manzana_mal_estado
    global cantidad_manzana_buen_estado
    global cantidad_banana_mal_estado
    global cantidad_banana_buen_estado
    
    #'Cantidad de naranjas en mal estado' is placed on position 40 (row - 4 and column - 0)
    tk.Label(window, text = "Cantidad de naranjas en mal estado").grid(row = 5)
    #fourth input-field is placed on position 41 (row - 4 and column - 1)
    entry_cantidad_naranja_mal = tk.Entry(window, width=22)
    entry_cantidad_naranja_mal.grid(row = 5, column = 1) 
    entry_cantidad_naranja_mal.insert(0, cantidad_naranja_mal_estado)
    entry_cantidad_naranja_mal.config(state='readonly')


    #'Cantidad de naranjas en buen estado' is placed on position 50 (row - 5 and column - 0)
    tk.Label(window, text = "Cantidad de naranjas en buen estado").grid(row = 6)
    #fifth input-field is placed on position 51 (row - 5 and column - 1) 
    entry_cantidad_naranja_bien = tk.Entry(window, width=22)
    entry_cantidad_naranja_bien.grid(row = 6, column = 1) 
    entry_cantidad_naranja_bien.insert(0, cantidad_naranja_buen_estado)
    entry_cantidad_naranja_bien.config(state='readonly')
    
    
    #'Cantidad de manzanas en mal estado' is placed on position 60 (row - 6 and column - 0)
    tk.Label(window, text = "Cantidad de manzanas en mal estado").grid(row = 7)
    #fourth input-field is placed on position 61 (row - 6 and column - 1)
    entry_cantidad_manzana_mal = tk.Entry(window, width=22)
    entry_cantidad_manzana_mal.grid(row = 7, column = 1) 
    entry_cantidad_manzana_mal.insert(0, cantidad_manzana_mal_estado)
    entry_cantidad_manzana_mal.config(state='readonly')


    #'Cantidad de manzanas en buen estado' is placed on position 70 (row - 7 and column - 0)
    tk.Label(window, text = "Cantidad de manzanas en buen estado").grid(row = 8)
    #fifth input-field is placed on position 71 (row - 7 and column - 1) 
    entry_cantidad_manzana_bien = tk.Entry(window, width=22)
    entry_cantidad_manzana_bien.grid(row = 8, column = 1) 
    entry_cantidad_manzana_bien.insert(0, cantidad_manzana_buen_estado)
    entry_cantidad_manzana_bien.config(state='readonly')
    
    
    #'Cantidad de bananas en mal estado' is placed on position 80 (row - 8 and column - 0)
    tk.Label(window, text = "Cantidad de bananas en mal estado").grid(row = 9)
    #fourth input-field is placed on position 81 (row - 8 and column - 1)
    entry_cantidad_banana_mal = tk.Entry(window, width=22)
    entry_cantidad_banana_mal.grid(row = 9, column = 1) 
    entry_cantidad_banana_mal.insert(0, cantidad_banana_mal_estado)
    entry_cantidad_banana_mal.config(state='readonly')


    #'Cantidad de bananas en buen estado' is placed on position 90 (row - 9 and column - 0)
    tk.Label(window, text = "Cantidad de bananas en buen estado").grid(row = 10)
    #fifth input-field is placed on position 91 (row - 5 and column - 1) 
    entry_cantidad_banana_bien = tk.Entry(window, width=22)
    entry_cantidad_banana_bien.grid(row = 10, column = 1) 
    entry_cantidad_banana_bien.insert(0, cantidad_banana_buen_estado)
    entry_cantidad_banana_bien.config(state='readonly')

def actualizar_datos():
    """Muestra en pantalla los los datos que fueron previamente
        guardados en las  variables internas. Esta funcion llama a 
        cargar_imagen, cargar_estado y cargar_tiempo.
    """

    cargar_estado()
    cargar_tiempo()
    cargar_cantidades()
    #loop. Se volvera a ejecutar esta funcion despues de 1 segundo
    #window.after(100,mostrar_datos)
    
def actualizar_imagen():
    """Muestra en pantalla los los datos que fueron previamente
        guardados en las variables internas. Esta funcion llama a 
        cargar_imagen, cargar_estado y cargar_tiempo.
    """

    cargar_imagen()

    #loop. Se volvera a ejecutar esta funcion despues de 1 segundo
    #window.after(100,mostrar_datos)

#Funcion para guardar los datos del sistema para su posterior envio a la interfaz
def guardar_datos(estado, tiempo, tiempo2):
    """Guarda los parametros para su posterior muestra en pantalla.
        Parametros
        -----------

        estado: 0 1 2 3 4 5 

        tiempo: int
            Es el tiempo que demoro el sistema en indentificar la fruta.
            
            tiempo2: int
                Es el tiempo que demoro el sistema en un periodo.
    """
    

    global estado_actual
    global tiempo_identificacion
    global tiempo_periodo
    
    #Guardo los parametros en las variables internas


    estado_actual = estado
    tiempo_identificacion = tiempo
    tiempo_periodo = tiempo2
    
def guardar_imagen(imagen):
    """Guarda los parametros para su posterior muestra en pantalla.
        Parametros
        -----------
        image : Image
            Es el archivo de imagen. Puede ser .jpg or .png

    """
    
    global imagen_actual

    
    #Guardo los parametros en las variables internas
    imagen_actual = imagen



def verifStatePacket(enlace):
    
    if enlace.status == txfer.CRC_ERROR:
        print('ERROR: CRC_ERROR')
        enlace.close()
        sys.exit()
    elif enlace.status == txfer.PAYLOAD_ERROR:
        print('ERROR: PAYLOAD_ERROR')
        enlace.close()
        sys.exit()
    elif enlace.status == txfer.STOP_BYTE_ERROR:
        print('ERROR: STOP_BYTE_ERROR')
        enlace.close()
        sys.exit()
    else:
        print('ERROR: {}'.format(enlace.status))
        enlace.close()
        sys.exit()
    



#Codigo principal



class App(threading.Thread):


    def __init__(self, tk_root):
        
        
        self.root = tk_root
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        #variables internas
           
        file = []
        
        dim1 = 96
        dim2 = 96
        canales = 3
        TAMANO_INPUT = dim2*dim1*canales
        array = np.arange(0, TAMANO_INPUT, 1)
        
        #########################

        try:
            
            link = txfer.SerialTransfer('COM3',baud=2000000)
            link.open()
            sleep(5)
            loop_active = True
            
            while loop_active:
                
                if link.available():
                   
                    id_pack = link.idByte
                    
                    
                    if(id_pack==0):
                        
                        file += link.rx_obj(list, start_pos=0, obj_byte_size=link.bytesRead,list_format=('h'))
                        
                        
                    elif(id_pack==1):
                        
                        file += link.rx_obj(list, start_pos=0, obj_byte_size=link.bytesRead,list_format=('h'))
                        
                        
                    elif(id_pack==2):
                        
                        
                        
                        file += link.rx_obj(list, start_pos=0, obj_byte_size=link.bytesRead,list_format=('h'))
                        
                        if(len(file)==TAMANO_INPUT):    #imagen correcta
                            
                            print("la imagen llego bien")
                            array = np.reshape(file, (canales, dim2, dim1))
                            #cambiar formato de imagen
                            _canal,_fila,_columna = array.shape
                            arr_new = np.zeros((_columna,_fila,_canal),dtype="float32")
                            for canal,elem in enumerate(array):
                                for fila,elem2 in enumerate(elem):
                                    for columna,valor in enumerate(elem2):
                                        
                                        arr_new[columna,fila,canal] = valor
                                        
                                        
                            #RESULT TIENE LA IMAGE PIL
                            result = Image.fromarray(np.array(((arr_new+512)*(255))/1024).astype(np.uint8))
                        
                            guardar_imagen(result)
                            
                            actualizar_imagen()
                            
                        else:
                            
                            print("la imagen no llego bien (paquetes desordenados o error en el buffer rx)")
                            
                        
                        file = []
                        
                        
                            
                        
                    elif(id_pack==3):
      
                        
                        respuesta = link.rx_obj(list, start_pos=0, obj_byte_size=link.bytesRead,list_format=('l'))
                        # Campos a guardar
                        
                        #print(respuesta[0])

                        clase_inferida =  (int(respuesta[0]))
                        tiempo_inferencia = str(int(respuesta[1]))                        
                        tiempo_periodo = str(int(respuesta[2]))
                       
                        #print("tiempo inferencia:")
                        #print(tiempo_inferencia)
                        #print("tiempo tot")
                        #print(tiempo_periodo)
                        
                     
                      
                        
                    
                     
                        guardar_datos(clase_inferida,tiempo_inferencia,tiempo_periodo)
                        
                        actualizar_datos()
                        
                        
                    else:
                        print("ERORR ID PACK")
                        sys.exit()
                    
                        

                        
                    
                elif link.status < 0:
                    
                    verifStatePacket(link)
                    
                    

                ################### fin comunicacion serie 
         
            
        except :
            print("No se pudo establecer comunicacion con el microcontrolador")
            sys.exit()

            
            
            



APP = App(window)

window.mainloop()
