import time
import random
import numpy as np
from matriz import MatrixZ
import socket
import threading
import pickle
import os

#funcao que lê as configurações no ficheiro 
def ReadConfigFile():
    try:
        with open('config.txt', 'r') as file:
            lines = file.readlines()
            ip = lines[0].strip() #passar o localhost como o stor pediu
            port = int(lines[1].strip())
            m = lines[2].strip()
            k = int(lines[3].strip())
            t = int(lines[4].strip()) / 1000 # põem tempo em ms 
            v = int(lines[5].strip())
            x = int(lines[6].strip())
        return ip, port, m, k, t, v, x
    except FileNotFoundError:
        print('O ficheiro nao foi encontrado')

#funcao do tempo
# mais tarde o tempo de uptime será guardado na MIB
def GetTime(start_timestamp):
    current_time = time.time()
    uptime_seconds = current_time - start_timestamp
    return uptime_seconds

#função que inicializa o update da matriz, e obtem o N--udpate_count
def StartMatrixUpdate(t, matriz):
    #  jfpereira: não queremos isto aqui, a função recebe a matriz como argumento
    while True:
        matriz.UpdateMatrix()
        time.sleep(t)  # Aguarda o intervalo de atualização T (em ms)


def handle_set_primitiva(parsed_data):
    NW = str(parsed_data[5])
    W_data = parsed_data[7].split(';')
        #volta a formar uma tupla de pares 
    W = [(pair.split(',')[0], pair.split(',')[1]) for pair in W_data]

def handle_get_primitiva(parsed_data):
    NL = str(parsed_data[5])
    print(NL)
    L_data = parsed_data[7].split(';')
        #volta a formar uma tupla de pares 
    L = [(pair.split(',')[0], pair.split(',')[1]) for pair in L_data]
    print(L)

def handle_response_primitiva(parsed_data):
    NW = str(parsed_data[5])
    W_data = parsed_data[7].split(';')
        #volta a formar uma tupla de pares de erros
    W = [(pair.split(',')[0], pair.split(',')[1]) for pair in W_data]
    NR = str(parsed_data[6])
    print(NR)
    R_data = parsed_data[8].split(';')
    R = [(pair.split(',')[0], pair.split(',')[1]) for pair in R_data]
    print(R)


def handle_client(data,client_address,matriz, UDPServerSocket):
        print(f"Thread para cliente {client_address} iniciada.")
        client_ip, client_port = client_address
        # Obter o IP e a porta de origem do cliente
        print('O clinte IP é:',client_ip)
        print('A porta do cliente é:',client_port)

        #Separa os dados pela terminação '\0' e descodifica os bytes
        parsed_data = data.decode().split('\0')
        print(parsed_data)

       #acede ás posições dos dados
        S = parsed_data[0]
        print(S)
        NS = str(parsed_data[1])
        print(NS)
        Q=str(parsed_data[2])
        print(Q)
        Y = str(parsed_data[3])
        print(Y)
        filename = 'last_P.txt'
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                P, _ = map(float, file.readline().split())
                print(f"P lido do arquivo: {P}")

        if int(Y)==1:
            handle_get_primitiva(parsed_data)

        elif int(Y) == 2:
            handle_set_primitiva(parsed_data)
            key, key_id = matriz.GenerateKey()
            response = f"Generated Key: {key}, ID: {key_id}"
            UDPServerSocket.sendto(response.encode(), client_address)
            
        elif int(Y)==3:
            handle_response_primitiva(parsed_data)
        
        print(f"Thread para cliente {client_address} encerrada.")

#função que inicia o server udp, udp comm
def StartUDPServer(port, ip, matriz):
    localIP = ip
    localPort = port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP listening")

    while True:
        data, client_address = UDPServerSocket.recvfrom(4096)           
        # Criar uma nova thread para lidar com o pedido do cliente
        client_thread = threading.Thread(target=handle_client, args=(data, client_address, matriz, UDPServerSocket))
        client_thread.start()

def main():
    ip, port, m, k, t, v, x = ReadConfigFile()
    matriz = MatrixZ(m, k)
    start_timestamp = time.time()
    print("N:",matriz.get_Ncount())
    StartMatrixUpdateThread = threading.Thread(target=StartMatrixUpdate, args=(t,matriz))
    StartMatrixUpdateThread.start()
    StartUDPServer(port,ip,matriz)  
    uptime = GetTime(start_timestamp) 
    print("O servidor demorou: ", uptime)


if __name__ == "__main__":
    main()

       # https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php
        # codigo não funcional, é só um esboço
        # c_thread = threading.Thread(target = self.handle_request, args = (data, client_address, matrizZ, MIB))
        # c_thread.daemon = True
        # c_thread.start()
        # a função handle_request terá todo o código para tratar dos pedidos