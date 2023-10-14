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
    
    def StartMatrixUpdate(self):
        matriz = MatrixZ(self.m, self.k)
        while True:
            matriz.UpdateMatrix()
            self.update_count += 1  # Incrementa o contador de atualizações
            #print(f"Matriz atualizada {self.update_count} vezes.")
            time.sleep(self.t / 1000)  # Aguarda o intervalo de atualização T (em segundos)
            time.sleep(5)
            #print(self.update_count)
            
    def UDPServer(self):
        localIP     = "127.0.0.1"

        localPort   = 1234

        #cria o socket 
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  
        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDPServerSocket.bind((localIP,localPort))
        print("UDP server up and listening")


        while True:
            data, client_address = UDPServerSocket.recvfrom(4096)
            print(f'Received data from {client_address}: {data.decode()}')
            
            if(data.decode()== 'set1'):
                print('primitiva set')
                chave = self.matriz.GenerateKey(self.update_count)
                print("Chave gerada:", chave)
                print(self.update_count)
 
             # Execute o algoritmo de atualização da matriz Z
                self.matriz.UpdateMatrix()

                # Envie a chave de volta para o cliente
                UDPServerSocket.sendto(chave, client_address)

                # Send a response back to the client
                response = 'Hello, client! Your message was received.'
                UDPServerSocket.sendto(response.encode(), client_address)

    def StartThreads(self):
        udp_server_thread = threading.Thread(target=self.StartUDPServer)
        matrix_update_thread = threading.Thread(target=self.StartMatrixUpdate)

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
    udp_server_thread = threading.Thread(target=agent.StartUDPServer)
    udp_server_thread.start()
    #matriz = MatrixZ(agent.m, agent.k)


    #print("------------------primeiro-------------------")
    #for i in range(agent.k):
        #print(matriz.z[i])

    #atualiza a matriz z
    #while True:
       #matriz.UpdateMatrix()
       #print("nova")
       #for i in range(agent.k):
            #print(matriz.z[i])

        # aguarda o intervalo de atualização T (convertido de milissegundos para segundos),que está no ficheiro de config
       #time.sleep(agent.t / 1000)
       #time.sleep(5)
       #break


if __name__ == "__main__":
    main()