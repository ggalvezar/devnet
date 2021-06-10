from socket import socket
import paramiko
import sys
import getpass
import argparse
import re

class Ssh_tools:

    def __init__(self,hostIP):
        self.hostIP = hostIP
        self.username = "admin"
        self.password = "cisco123"
        self.port = "22"
        self.salida = ""
        self.error = None
        self.hostname = None
        self.connexion = True
        self.sincodificar = None

    def set_pass(self):
        try:
            self.password = getpass.getpass()
        except Exception as err:
            print('ERROR:', err)

    def set_user(self,user):
        self.username = user

    def get_salida(self):
        return self.salida

    def get_sincodificar(self):
        return self.sincodificar



    def procesar_salida(self):
        cadena_array = self.salida.splitlines()
        for i in [0,1,2]:
            del cadena_array[0]
        print("%-38s %-15s %-12s %-10s %-8s "%("Neighbor ID","Pri State","Up Time","Address", "Interface"))
        for linea in cadena_array:
            my_array = linea.split(sep=None, maxsplit=-1)
            #my_array = linea.split('\s')
            print("%-38s %-15s %-12s %-10s %-8s "%(my_array[0],my_array[1],my_array[2],my_array[3],my_array[4]))



    def get_connexion(self):
        return self.connexion

    def connect(self):
        result_flag = False
        try:
            #print ("Estableciendo conexion...")
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #conectar con el servidor
            self.client.connect(hostname=self.hostIP,port=self.port, username=self.username,password=self.password)
        except paramiko.AuthenticationException:
            print("Fallo la autenticación, por favor verifique las credenciales o ip de HOST")
            result_flag = False
        except paramiko.SSHException as sshException:
            print("No se puede establecer la conexion SSH: %s" % sshException)
            result_flag = False
        except Exception as e:
            print ("Error de conexion",e)
            result_flag = False
            self.client.close()
        else:
            result_flag = True

        return result_flag

    def command(self,comando):
        self.salida = None
        result_flag = True
        try:
            if self.connect():
                entrada, salida, error = self.client.exec_command(comando,timeout=5)
                #print("Ejecutando del comando: {}".format(comando))
                #print("*************************************************************************************\n")
                self.sincodificar = salida.read()
                self.salida =  self.sincodificar.decode('utf8')
                self.error = error.read().decode('utf8')
                #print(self.salida)
                if self.error:
                    print("Problema al ejecutar el comando: " + comando + "ERROR: " + self.error)
                    result_flag = False
                self.client.close()
            else:
                print("NO se puede establecer la conexion...")
                self.connexion = False
                result_flag = False
        except paramiko.SSHException:
            print("Falla al ejecutar el comando: {}".format(comando))
            self.client.close()
            result_flag = False
        except Exception as e:
            print ("Error de conexion",e)
            #self.client.close()

        return result_flag

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("hostIP",help="Remote computer ip")
    args = parser.parse_args()

    equipo_remoto = Ssh_tools(args.hostIP)

    comando = "show ip ospf neighbors vrf IPN"
    if equipo_remoto.get_connexion():
        equipo_remoto.command(comando)
        equipo_remoto.procesar_salida()

