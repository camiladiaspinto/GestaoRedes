import time
import random
import numpy as np
from matriz import MatrixZ
import socket
import threading

# jfpereira: isto deve estar dentro da class matriz
# matriz terá de ser global 
#jfpereira: não queremos variáveis globais

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
# jfpereira: recebe t em ms e a matrizZ - mais um argumento para a matrizZ
# jfpereira: nota - compreender como são os objetos passados para dentro das funções
# jfpereira: https://realpython.com/python-pass-by-reference/ 
def StartMatrixUpdate(t, matriz):
    #  jfpereira: não queremos isto aqui, a função recebe a matriz como argumento
    while True:
        matriz.UpdateMatrix()
        # jfpereira: é um valor relativo ao objeto matriz(?) -> deve estar no obj matiz
        time.sleep(t)  # Aguarda o intervalo de atualização T (em ms)
        #time.sleep(5) # jfpereira: isto não devia estar aqui

#função que inicia o server udp, udp comm
# jfpereira: isto poda estar na main direto, não precisava de estar numa função
def StartUDPServer(port, ip, matriz):
    # jfpereira: isto deve ser lido do ficheiro de conf
    localIP = ip
    localPort = port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP listening")

    while True:
        data, client_address = UDPServerSocket.recvfrom(4096)
        # jfpereira: mais tarde será algo deste tipo (temos de ter uma thread por pedido recebido)
        # https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php
        # codigo não funcional, é só um esboço
        # c_thread = threading.Thread(target = self.handle_request, args = (data, client_address, matrizZ, MIB))
        # c_thread.daemon = True
        # c_thread.start()
        # a função handle_request terá todo o código para tratar dos pedidos
        print(f'Received data from {client_address}: {data.decode()}')
        
        if(data.decode() == 'set'):
            print('primitiva set')
            key, key_id = matriz.GenerateKey()
            print("Generated Key:", key, "ID:", key_id)
            # jfpereira: não queremos chamar a função update aqui se o enunciado diz para o fazer sempre que geramos uma chave
            # a função gerar chave é que chamará a função update
            # jfpereira: o socket que recebemos não é o mesmo por onde enviamos
            UDPServerSocket.sendto(key, client_address)
        else:
            response = 'your message was received and its not a set.'
            UDPServerSocket.sendto(response.encode(), client_address)

def main():
    #jfpereira:  read local IP
    ip, port, m, k, t, v, x = ReadConfigFile()
    matriz = MatrixZ(m, k)
    start_timestamp = time.time()
    print("N:",matriz.get_Ncount())
    #thread da matriz
    # jfpereira: matriz vai como argumento args(t, matriz)
    StartMatrixUpdateThread = threading.Thread(target=StartMatrixUpdate, args=(t,matriz))
    StartMatrixUpdateThread.start()


    StartUDPServer(port,ip,matriz)  
    # jfpereira: o programa nunca vai chegar aqui, a função StartUDPServer tem um while true...
    uptime = GetTime(start_timestamp) 
    print("O servidor demorou: ", uptime)
    

if __name__ == "__main__":
    main()
