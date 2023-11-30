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
from datetime import datetime, timedelta

p_lock = threading.Lock()
mib_lock = threading.Lock()

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

#funcao para remover as chaves quando for o tempo delas
def remove_expired_keys(mib):
    current_date_time = datetime.now()

    with mib_lock:
        for key_id in mib.get_all_keys():
            if key_id.startswith("0.3.2.1."):
                sublist = mib.get_entry_by_iid(key_id)
                print("sublist", sublist)
                for sub_entry in sublist:
                    if sub_entry[1] == 'keyExpirationDate':
                        expiration_date = sub_entry[2]
                        print("date:", expiration_date)
                    if sub_entry[1] == 'keyExpirationTime':
                        expiration_time = sub_entry[2]
                        print("time: ", expiration_time)

                if expiration_date and expiration_time:
                    try:
                        expiration_date_time = datetime.strptime(expiration_date + expiration_time, "%y%m%d%H%M%S")
                        print("expiration:", expiration_date_time)
                        print("current: ", current_date_time)
                        if current_date_time > expiration_date_time:
                            # A chave expirou, remover da MIB
                            mib.remove_entry_by_key_id(key_id)
                            print(f"Chave {key_id} removida da MIB.")
                    except ValueError as e:
                        print(f"Erro ao converter data e hora: {e}")



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
    mib.add_iid_entry("0.3.2.1."+str(key_id),lista)

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
    mib.add_iid_entry("0.3.1", ["dataNumberOfValidKeys", 0, "read-only", "current", "The number of elements in the dataTableGeneratedKeys."])

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

def handle_set_primitiva(parsed_data,matriz,mib,client_ip,client_port,v,x):
    NW = str(parsed_data[5])
    W_data = parsed_data[6].split(';')
        #volta a formar uma tupla de pares 
    W = [(pair.split(',')[0], pair.split(',')[1]) for pair in W_data]
    error_list = []
    n_chaves = mib.get_entry_by_iid("0.3.1")[1]
    print("N chaves: ", n_chaves)

    #verifica se é possivel adicionar mais chaves, se for acima de x não pode adicionar
    if n_chaves < x:
        key, key_id_aux = matriz.GenerateKey()
        key_id = matriz.get_Ncount()
        now = datetime.now()
        v = timedelta(seconds=v)
        nova_now = now + v
        date = nova_now.strftime("%y%m%d")
        time = nova_now.strftime("%H%M%S")
        lista = mib.get_entry_by_iid('0.3.1')
        valor_novo = lista[1] + 1
        lista[1] = valor_novo
        mib.update_iid_entry('0.3.1', lista)
        entrada_tabela_keys(mib, key_id, key, client_ip, client_port, date, time, 2)
        response = f"Generated Key: {key}, ID: {key_id}"
        error_list = ""
    else:
        error_list.append("[Erro]: O numero de chaves atingiu o maximo")
        response = ""

    return response, error_list

def handle_get_primitiva(parsed_data,mib):
    response = {}
    error_list = []
    NL = str(parsed_data[5])
    print(NL)
    L_data = parsed_data[7].split(';')
        #volta a formar uma tupla de pares 
    L = [(pair.split(',')[0], pair.split(',')[1]) for pair in L_data]
    print(L)
    for i in range(int(NL)):
        L_i = L[i]
        L_iid = L_i[0]
        L_lexiograficamente = int(L_i[1])
        
        # Para o caso de ser o system ou o config
        if len(L_iid) == 5:
            # Obter a entrada inicial
            results = {}
            response_entry = mib.get_entry_by_iid(L_iid)
            print(response_entry)

            # Adicionar à resposta, adaptando conforme necessário
            results[L_iid] = response_entry

            # Imprimir X entradas seguintes
            next_entries = mib.get_all_keys()

            # Encontrar a posição da entrada inicial
            start_index = next_entries.index(L_iid)

            # Iterar sobre as entradas seguintes e incluí-las na resposta
            for entry_key in next_entries[start_index + 1:start_index + 1 + L_lexiograficamente]:
                if entry_key.startswith("0.3.2.1."):
                    sublist = mib.get_entry_by_iid(entry_key)

                    # Itera sobre as sub-listas e adiciona à resposta
                    for sub_entry in sublist:
                        results[sub_entry[0]] = sub_entry[1:]
                        
                else: 
                    entry_value = mib.get_entry_by_iid(entry_key)
                    print(f"Chave: {entry_key}, Lista: {entry_value}")
                    results[entry_key] = entry_value

            #print(results)
            response = {key_id: results[key_id] for key_id in list(results)[:L_lexiograficamente+1]}
                
        elif len(L_iid) == 9:  #exemplo 0.3.2.1.0.3 (o ultimo numero é a key id)
            response = mib.get_entry_by_iid(L_iid)
            print(response)
        elif len(L_iid) == 11 or len(L_iid) == 12:
            L_iid_aux = L_iid[:-2]
            #print(L_iid_aux)
            lista = mib.get_entry_by_iid(L_iid_aux)
            #print(lista)
            results = {}

            # Imprimir X entradas seguintes
            next_entries = mib.get_all_keys()
            
            # Encontrar a posição da entrada inicial
            L_iid_teste = next_entries.index(L_iid_aux)
            for entry_key in next_entries[L_iid_teste:]:
                sublist = mib.get_entry_by_iid(entry_key)
                for sub_entry in sublist:
                    results[sub_entry[0]] = sub_entry[1:]

            #print(results)
            start_adding = False

            for entry_key, value in results.items():
                if entry_key == L_iid:
                    start_adding = True
                if start_adding:
                    response[entry_key] = value
            
            print(response)
            response_keys = list(response.keys())[:L_lexiograficamente]
            response = {key: response[key] for key in response_keys}
            
        #Verifica se a chave existe na mib
        if response is not None:
            response_str = json.dumps(response, default=bytes_to_hex_string)
            error_list = ""
        else:
            error_list.append("[Erro]: Chave nao existe")
            response_str = ""

    return response_str, error_list

def bytes_to_hex_string(byte_data):
    return byte_data.hex() if isinstance(byte_data, bytes) else byte_data

def get_last_P(filename='last_P.txt'):
    with p_lock:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                P, last_P_timestamp = map(float, file.read().split())
        else:
            P = 0
            last_P_timestamp = 0
            with open(filename, 'w') as file:
                file.write(f"{P} {last_P_timestamp}")
        return P, last_P_timestamp

def update_last_P(P, filename='last_P.txt'):
    with p_lock:
        current_time = time.time()
        with open(filename, 'w') as file:
            file.write(f"{P} {current_time}")

def is_valid_request(P, V, last_P_timestamp,current_time):
    with p_lock:
        #current_time = time.time()
        print(f"Current Time: {current_time}, Last P Timestamp: {last_P_timestamp}")
        if current_time - last_P_timestamp < V:
            print(f"[Error]: Not allowed to identify another request with the same I-ID for {V} seconds.")
            return False
        return True

def handle_client(data,client_address,matriz,mib,v,x,UDPServerSocket):
        print(f"Thread para cliente {client_address} iniciada.")
        client_ip, client_port = client_address
        # Obter o IP e a porta de origem do cliente
        print('O clinte IP é:',client_ip)
        print('A porta do cliente é:',client_port)

        #Separa os dados pela terminação '\0' e descodifica os bytes
        parsed_data = data.decode().split('\0')
        current_time = time.time()
        #print(parsed_data)

       #acede ás posições dos dados
        S = parsed_data[0]
        print(S)
        NS = str(parsed_data[1])
        print(NS)
        Q=str(parsed_data[2])
        print(Q)
        Y = str(parsed_data[3])
        print(Y)
        try:
        # Verifica se o pedido é válido
            
            P, last_P_timestamp = get_last_P('last_P.txt')
            V = ReadConfigFile()[5]  
            print(V)
            print(P)

            if not is_valid_request(P, V, last_P_timestamp,current_time):
                error_message = "[Erro]: Pedido inválido. Aguarde alguns segundos e tente novamente."
                UDPServerSocket.sendto(error_message.encode(), client_address)
                print(f"Erro: Pedido inválido para o cliente {client_address}.")
                return
        except Exception as e:
            print(f"Erro ao verificar a validade do pedido: {str(e)}")
            return

        # Incrementa P e atualiza o timestamp antes de chamar update_last_P
        P += 1
        update_last_P(P)

        remove_expired_keys(mib)

        if int(Y)==1:
            print(mib.get_mib())
            response = {} 
            response, error_list = handle_get_primitiva(parsed_data,mib) 
            if not error_list:
                UDPServerSocket.sendto(response.encode('utf-8'), client_address)
            else:
                error_message = "\n".join(error_list)
                UDPServerSocket.sendto(error_message.encode('utf-8'), client_address)


        elif int(Y) == 2:
            response, error_list = handle_set_primitiva(parsed_data,matriz,mib,client_ip,client_port,v,x)
            if not error_list:
                UDPServerSocket.sendto(response.encode('utf-8'), client_address)
            else:
                error_message = "\n".join(error_list)
                UDPServerSocket.sendto(error_message.encode('utf-8'), client_address)
        
        print(f"Thread para cliente {client_address} encerrada.")

#função que inicia o server udp, udp comm
def StartUDPServer(port, ip, matriz, mib,v,x):
    localIP = ip
    localPort = port
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((localIP, localPort))
    print("UDP listening")

    while True:
        data, client_address = UDPServerSocket.recvfrom(4096)           
        # Criar uma nova thread para lidar com o pedido do cliente
        client_thread = threading.Thread(target=handle_client, args=(data, client_address, matriz, mib,v,x,UDPServerSocket))
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
    StartUDPServer(port,ip,matriz,mib,v,x)  
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
