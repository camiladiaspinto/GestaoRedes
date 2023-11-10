import time
import random
import numpy as np
from matriz import MatrixZ
import socket
import threading
import pickle

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
        #client_thread = threading.Thread(target=handle_client_request, args=(data, client_address, matriz, UDPServerSocket))
        #client_thread.start()
        # https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php
        # codigo não funcional, é só um esboço
        # c_thread = threading.Thread(target = self.handle_request, args = (data, client_address, matrizZ, MIB))
        # c_thread.daemon = True
        # c_thread.start()
        # a função handle_request terá todo o código para tratar dos pedidos
           
        # Obter o IP e a porta de origem do cliente
        client_ip, client_port = client_address
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
        P = str(parsed_data[4])
        print(P)
        NW = str(parsed_data[5])
        print(NW)
        NR = str(parsed_data[6])
        print(NR)
        #separa os dados da lista pelos pares 
        W_data = parsed_data[7].split(';')
        #volta a formar uma tupla de pares 
        W = [(pair.split(',')[0], pair.split(',')[1]) for pair in W_data]
        print(W)
        R_data = parsed_data[8].split(';')
        R = [(pair.split(',')[0], pair.split(',')[1]) for pair in R_data]
        print(R)

        if int(Y) == 2:
            handle_set_primitive(data, client_address, matriz, UDPServerSocket)
        else:
                response = 'Your message was received, but it is not a set primitive.'
                UDPServerSocket.sendto(response.encode(), client_address)

#NOTA: para implementar o que o prof pediu de uma thread por pedido, esta função ficaria assim:
  #while True:
   #     data, client_address = UDPServerSocket.recvfrom(4096)
     #   client_thread = threading.Thread(target=handle_client_request, args=(data, client_address, matriz, UDPServerSocket))
      #  client_thread.start()

#def handle_client_request(data, client_address, matriz, UDPServerSocket):
    #client_ip, client_port = client_address
    #print('Cliente IP:', client_ip)
    #print('Cliente Porta:', client_port)
    # Tratamento dos dados(copy e paste do que esta na startupd server)
    #Separa os dados pela terminação '\0' e descodifica os bytes
    #parsed_data = data.decode().split('\0')
    #print(parsed_data)

    #acede ás posições dos dados
    #S = parsed_data[0]
    #print(S)
    #NS = str(parsed_data[1])
    #print(NS)
    #Y = str(parsed_data[2])
    #print(Y)
    #P = str(parsed_data[3])
    #print(P)
    #NW = str(parsed_data[4])
    #print(NW)
    #NR = str(parsed_data[5])
    #print(NR)
    #separa os dados da lista pelos pares 
    #W_data = parsed_data[6].split(';')
    #volta a formar uma tupla de pares 
    #W = [(pair.split(',')[0], pair.split(',')[1]) for pair in W_data]
    #print(W)
    #R_data = parsed_data[7].split(';')
    #R = [(pair.split(',')[0], pair.split(',')[1]) for pair in R_data]
    #print(R)

    #if int(Y) == 2:
     #   handle_set_primitive(data, client_address, matriz, UDPServerSocket)
    #else:
     #   print('outras primitivas')
        #outras primitivas 


def handle_set_primitive(data, client_address, matriz, UDPServerSocket):
    print('Received a set primitive.')       
    key, key_id = matriz.GenerateKey()
    response = f"Generated Key: {key}, ID: {key_id}"
    UDPServerSocket.sendto(response.encode(), client_address)

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
    