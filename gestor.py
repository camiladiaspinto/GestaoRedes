import socket
import sys
import json
import threading
import os
import time


p_lock = threading.Lock()

def get_last_P(filename='last_P.txt'):
    with p_lock:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                last_P, last_P_timestamp = map(float, file.read().split())
        else:
            last_P = 0
            last_P_timestamp = 0
            with open(filename, 'w') as file:
                file.write(f"{last_P} {last_P_timestamp}")
        return last_P, last_P_timestamp

def update_last_P(current_time, P, filename='last_P.txt'):
    with p_lock:
        with open(filename, 'w') as file:
            file.write(f"{P} {current_time}")

def is_valid_request(P, last_P, V, last_P_timestamp,current_time):
    with p_lock:
        if P == last_P and current_time - last_P_timestamp < V:
            print(f"[Error]: Not allowed to identify another request with the same I-ID for {V} seconds.")
            return False
        return True

def process_data():
    S = 0  # mecanismo de segurança que é zero
    NS = 0
    Q = 0
    Y = int(sys.argv[1])
    N = int(sys.argv[2])
    
    W = []
    for i in range(3, N+3):
        pair = sys.argv[i].split(',')
        if len(pair) != 2:
            print("Erro: Formato inválido para o par (I-ID, H ou N).")
            sys.exit(1)
        instancia, valor = str(pair[0]), str(pair[1])
        W.append((instancia, valor))

    return S,NS,Q,Y, N, W

def build_data_strings(S, NS, Q, Y, N, W):
    s_data = str(S) + '\0'
    ns_data = str(NS) + '\0'
    q_data = str(Q) + '\0'
    y_data = str(Y) + '\0'
    n_data = str(N) + '\0'

    W_str = ';'.join([f'{pair[0]},{pair[1]}' for pair in W])
    W_bytes = W_str.encode('utf-8')

    return s_data, ns_data, q_data, y_data, n_data, W_bytes

def main():
    ip = '127.0.0.1'
    port = 1234
    current_time = time.time()
   
    client_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    S,NS,Q,Y,N,W=process_data()

    s_data, ns_data, q_data, y_data, n_data, W_bytes = build_data_strings(S, NS, Q, Y, N, W)

    data_bytes = s_data.encode('utf-8') + ns_data.encode('utf-8') + q_data.encode('utf-8') + y_data.encode(
        'utf-8') + n_data.encode('utf-8') + W_bytes

    try:
        # Verifica se o pedido é válido  
        last_P, last_P_timestamp = get_last_P('last_P.txt')
        P = last_P + 1
        update_last_P(current_time, P)
        V = 10 

        if not is_valid_request(P,last_P, V, last_P_timestamp,current_time):
            error_message = "[Erro]: Pedido inválido. Aguarde alguns segundos e tente novamente."
            print(error_message)
            return
            
    except Exception as e:
        print(f"Erro ao verificar a validade do pedido: {str(e)}")
        return
    
    server_address = (ip, port)
    client_socket.sendto(data_bytes, server_address)

    response, _ = client_socket.recvfrom(4096)

    print('Received response from server:', response.decode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    main()