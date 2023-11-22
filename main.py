import time
import random
import numpy as np
from matriz import MatrixZ
from mib import MIB
import socket
import threading
import pickle
import os
import json

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

#função de entrada na tabela a keys, não é necessario haver prevalencia de dados, quando o servidor desliga os dados vão embora
def entrada_tabela_keys(mib, key_id, key_value, ip, port, date, hora, visibility):
    #iid das entradas da tabela das keys
    iid_key_id = "0.3.2.1."+str(key_id)+".1"
    iid_key_value = "0.3.2.1."+str(key_id)+".2"
    iid_key_requester = "0.3.2.1."+str(key_id)+".3"
    iid_key_expiration_date = "0.3.2.1."+str(key_id)+".4"
    iid_key_expiration_time = "0.3.2.1."+str(key_id)+".5"
    iid_key_visibility = "0.3.2.1."+str(key_id)+".6"

    key_id = str(key_id)
    
    #listas das entradas das keys 
    lista_key_id = [iid_key_id,"keyId", key_id, "read-only", "current", "The identification of a generated key."]
    lista_key_value = [iid_key_value,"keyValue", key_value, "read-only", "current", "The value of a generated key (K bytes/characters long)."]
    lista_key_requester = [iid_key_requester,"KeyRequester", f"{ip}:{str(port)}", "read-only", "current", "The identification of the manager/client that initially requested the key."]
    lista_key_expiration_date = [iid_key_expiration_date,"keyExpirationDate", date, "read-only", "current", "The date (YY*104+MM*102+DD) when the key will expire."]
    lista_key_expiration_time = [iid_key_expiration_time,"keyExpirationTime", hora, "read-only", "current", "The time (HH*104+MM*102+SS) when the key will expire."]
    lista_key_visibility = [iid_key_visibility,"keyVisibility", visibility, "read-write", "current", "0 – Key value is not visible; 1 – key value is only visible to the requester; 2 – key value is visible to anyone."]

    lista = [lista_key_id, lista_key_value, lista_key_requester, lista_key_expiration_date, lista_key_expiration_time, lista_key_visibility]

#função de entrada na mib do system e config, tem de ser preenchida logo no inicio do programa 
def entradas_mib(mib,matriz,k,t,v,x,m):
    k = str(k)
    t = str(t)
    v = str(v)
    x = str(x)

    mib.add_iid_entry("0.1.1", ["systemRestartDate", matriz.get_creation_date() ,"read-only", "current", "The date (YY*104+MM*102+DD) when the agent has started a new Z matrix."])
    mib.add_iid_entry("0.1.2", ["systemRestarTime", matriz.get_creation_time() ,"read-only", "current", "The time (HH*104+MM*102+SS) when the agent has started a new Z matrix."])
    mib.add_iid_entry("0.1.3", ["systemKeySize", k, "read-only", "current", "The number of bytes (K) of each generated key."])
    mib.add_iid_entry("0.1.4", ["systemIntervalUpdate", t, "read-only", "current", "The number of milliseconds of the updating interval of the internal Z matrix."])
    mib.add_iid_entry("0.1.5", ["systemMaxNumberOfKeys", x, "read-only", "current", "“The maximum number of generated keys that are still valid."])
    mib.add_iid_entry("0.1.6", ["systemKeysTimeToLive", v, "read-only", "current", "The number of seconds of the TTL of the generated keys."])
    mib.add_iid_entry("0.2.1", ["configMasterKey", m, "read-write", "current", "The master double key M with at least K*2 bytes in size."])
    mib.add_iid_entry("0.2.2", ["configFirstCharOfKeysAlphabet", str(33), "read-write", "current", "The ASCII code of the first character of the alphabet used in the keys."])
    mib.add_iid_entry("0.2.3", ["configCardinalityOfKeysAlphabet", str(94), "read-write", "current", "The number of characters (Y) in the alphabet used in the keys."])


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
    return NL, L

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


def handle_client(data,client_address,matriz,mib, UDPServerSocket):
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
            i = 0
            NL, L = handle_get_primitiva(parsed_data)
            for i in range(int(NL)):
                L_i = L[i]
                L_iid = L_i[0]
                L_lexiograficamente = L_i[1]
                print(L_lexiograficamente)
                if len(L_iid) == 5: #para o caso de ser o system ou o config
                    print("tamanho", len(L_iid))
                    response = mib.get_entry_by_iid(L_iid)
                    print(response)
                elif len(L_iid) == 11:  #exemplo 0.3.2.1.0.3 (ultimos dois são a key id)
                    response = mib.get_entry_by_iid(L_iid)
                    print(response)
                elif len(L_iid) == 13:
                    L_iid_aux = L_iid[:11]
                    lista = mib.get_entry_by_iid(L_iid_aux)
                    for sublist in lista:
                        if sublist[0] == L_iid:
                            print(f"Valor encontrado na sublista: {sublist}")
                    
                    response = sublist
                    
                if response is not None:
                    response_str = json.dumps(response)
                    UDPServerSocket.sendto(response_str.encode(), client_address)


        elif int(Y) == 2:
            handle_set_primitiva(parsed_data)
            key, key_id = matriz.GenerateKey()
            response = f"Generated Key: {key}, ID: {key_id}"
            UDPServerSocket.sendto(response.encode(), client_address)
            
        elif int(Y)==3:
            handle_response_primitiva(parsed_data)
        
        print(f"Thread para cliente {client_address} encerrada.")

#função que inicia o server udp, udp comm
def StartUDPServer(port, ip, matriz, mib):
    localIP = ip
    localPort = port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP listening")

    while True:
        data, client_address = UDPServerSocket.recvfrom(4096)           
        # Criar uma nova thread para lidar com o pedido do cliente
        client_thread = threading.Thread(target=handle_client, args=(data, client_address, matriz, mib,UDPServerSocket))
        client_thread.start()

def main():
    ip, port, m, k, t, v, x = ReadConfigFile()
    matriz = MatrixZ(m, k)
    mib = MIB()
    entradas_mib(mib, matriz,k,t,v,x,m)
    start_timestamp = time.time()
    print("N:",matriz.get_Ncount())
    StartMatrixUpdateThread = threading.Thread(target=StartMatrixUpdate, args=(t,matriz))
    StartMatrixUpdateThread.start()
    StartUDPServer(port,ip,matriz,mib)  
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