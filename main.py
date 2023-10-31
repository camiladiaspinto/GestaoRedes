import time
import random
import numpy as np
from matriz import MatrixZ
import socket
import threading

# update_count é o número de vezes que a matriz já foi atualizada desde que o agente se iniciou
update_count = 0
# matriz terá de ser global 
matriz = None

#funcao que lê as configurações no ficheiro 
def ReadConfigFile():
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
def GetTime(start_timestamp):
    current_time = time.time()
    uptime_seconds = current_time - start_timestamp
    return uptime_seconds

#função que inicializa o update da matriz, e obtem o N--udpate_count
def StartMatrixUpdate(t):
    global update_count, matriz # Acessa a variável global update_count e matriz
    while True:
        matriz.UpdateMatrix()
        update_count += 1  # Incrementa o contador de atualizações
        time.sleep(t / 1000)  # Aguarda o intervalo de atualização T (em segundos)
        time.sleep(5)

#função que inicia o server udp, udp comm
def StartUDPServer(port):
    localIP = "127.0.0.1"
    localPort = port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP listening")

    while True:
        data, client_address = UDPServerSocket.recvfrom(4096)
        print(f'Received data from {client_address}: {data.decode()}')
        
        if(data.decode() == 'set'):
            print('primitiva set')
            print(type(update_count))
            key = matriz.GenerateKey(update_count)
            print("Generated Key:", key) 
            matriz.UpdateMatrix()
            UDPServerSocket.sendto(key, client_address)
        else:
            response = 'your message was received and its not a set.'
            UDPServerSocket.sendto(response.encode(), client_address)

def main():
    global matriz 
    port, m, k, t, v, x = ReadConfigFile()
    matriz = MatrixZ(m, k)
    start_timestamp = time.time()

    #thread da matriz
    StartMatrixUpdateThread = threading.Thread(target=StartMatrixUpdate, args=(t,))
    StartMatrixUpdateThread.start()


    StartUDPServer(port)  

    uptime = GetTime(start_timestamp) 
    print("O servidor demorou: ", uptime)
    

if __name__ == "__main__":
    main()
