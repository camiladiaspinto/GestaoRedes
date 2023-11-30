import socket
import sys


def process_data():
    if len(sys.argv) < 5:
        print("Erro: Número insuficiente de argumentos.")
        sys.exit(1)
    
    S = 0  # mecanismo de segurança que é zero
    NS = 0
    Q = 0
    Y = int(sys.argv[1])
    N = int(sys.argv[2])
    
    W = []
    for i in range(4, N+4):
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

   
    client_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    S,NS,Q,Y,N,W=process_data()

    s_data, ns_data, q_data, y_data, n_data, W_bytes = build_data_strings(S, NS, Q, Y, N, W)

    data_bytes = s_data.encode('utf-8') + ns_data.encode('utf-8') + q_data.encode('utf-8') + y_data.encode(
        'utf-8') + n_data.encode('utf-8') + W_bytes

    server_address = (ip, port)
    client_socket.sendto(data_bytes, server_address)

    response, _ = client_socket.recvfrom(4096)
    print('Received response from server:', response.decode('utf-8'))

    client_socket.close()

if __name__ == "__main__":
    main()

