import time
import random
import numpy as np
from matriz import MatrixZ
import socket
import threading


class AgentManagement:
    def __init__(self):
        self.start_timestamp = time.time()
        self.port, self.m, self.k, self.t, self.v, self.x = self.ReadConfigFile()
        self.update_count = 0
        self.matriz = MatrixZ(self.m, self.k) 

    #funcao que lê as configurações no ficheiro 
    def ReadConfigFile(self):
        try:
            with open('config.txt', 'r') as file:
                lines = file.readlines()
                port = int(lines[0].strip())
                m = lines[1].strip()
                k = int(lines[2].strip())
                t = int(lines[3].strip())
                v = int(lines[4].strip())
                x = int(lines[5].strip())
            return port, m, k, t, v, x
        except FileNotFoundError:
            print('O ficheiro nao foi encontrado')

    #funcao do tempo
    def GetTime(self):
        current_time = time.time()
        uptime_seconds = current_time - self.start_timestamp
        return uptime_seconds
    
    #função que inicializa o update da matriz, e obtem o N--udpate_count
    def StartMatrixUpdate(self):
        #matriz = MatrixZ(self.m, self.k)
        while True:
            self.matriz.UpdateMatrix()
            self.update_count += 1  # Incrementa o contador de atualizações
            #print(f"Matriz atualizada {self.update_count} vezes.")
            time.sleep(self.t / 1000)  # Aguarda o intervalo de atualização T (em segundos)
            time.sleep(5)
            #print(self.update_count)
            
    #função que inicia o server udp, udp comm
    def StartUDPServer(self):
        localIP     = "127.0.0.1"
        localPort   = 1234

        #cria o socket 
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  
        #para permitir reutilização de portas
        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDPServerSocket.bind((localIP,localPort))
        print("UDP listening")

        while True:
            data, client_address = UDPServerSocket.recvfrom(4096)
            print(f'Received data from {client_address}: {data.decode()}')
            
            if(data.decode()== 'set'):
                print('primitiva set')
                print(type(self.update_count))
                key = self.matriz.GenerateKey(self.update_count)
                print("Generated Key:", key) 
                #algoritmo de atualização da matriz Z, devido a isto " algoritmo anterior de atualização da matriz Z tem de ser executado antes de outros pedidos de geração de chave serem atendidos"
                self.matriz.UpdateMatrix()

                #envia a chave de volta para o cliente, e vai enviar também o identificador D(mas ainda não sei,está no ponto vi)
                UDPServerSocket.sendto(key, client_address)
            else:
                #envia mensagem de volta
                response = 'your message was received and its not a set.'
                UDPServerSocket.sendto(response.encode(), client_address)

    #funnção de criação da thread
    def StartThreads(self):
        #cria thread responsável pela atualização da matriz
        udp_server_thread = threading.Thread(target=self.StartUDPServer)
        matrix_update_thread = threading.Thread(target=self.StartMatrixUpdate)
        #inicializa thread
        udp_server_thread.start()
        matrix_update_thread.start()

def main():
    agent = AgentManagement()
    uptime = agent.GetTime()
    matriz = MatrixZ(agent.m, agent.k) 

    agent.StartThreads()
    #print(f'O agente está em execução há {uptime} segundos.')
    #configurations = agent.ReadConfigFile()
    #print("configuraçoes:", configurations)
 
if __name__ == "__main__":
    main()