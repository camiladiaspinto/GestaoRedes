import socket
import sys
import os
import time

ip = '127.0.0.1'
port = 1234
filename = 'last_P.txt'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Obtém os valores da PDU a partir dos argumentos da linha de comando e converte para inteiros para ser mais fácil tratar dos dados
S = 0  # mecanismo de segurança que é zero
NS = 0
Q = 0
Y = int(sys.argv[1])  # identificação da primitiva
V = 10
"""
# verifica se o arquivo existe e lê o valor nele, senão cria e começa do zero o p e o timestamp (v segundos)
if os.path.exists(filename):
    with open(filename, 'r') as file:
        P, last_P_timestamp = map(float, file.read().split())
else:
    P = 0
    last_P_timestamp = 0
    #se nao existir, cria
    with open(filename, 'w') as file:
        file.write(f"{P} {last_P_timestamp}")
"""
N = int(sys.argv[2])  # quantidade de pares
NR = int(sys.argv[3])  # quantidade de pares de erros

W = []  # Lista de pares
R = []  # Lista de erros

#tratamento de dados
# começa na posição 4 e vai desde essa posição até ao fim da quantidade de pares
for i in range(4, 4 + N):
    pair = sys.argv[i].split(',')
    if len(pair) != 2:
        print("Erro: Formato inválido para o par (I-ID, H ou N).")
        sys.exit(1)
    instancia = str(pair[0])
    valor = str(pair[1])
    W.append((instancia, valor))

# começa na quantidade final da lista pares e vai até ao final da lista erros
for i in range(4 + N, 4 + N + NR):
    pair = sys.argv[i].split(',')
    if len(pair) != 2:
        print("Erro: Formato inválido para o par (I-ID, E).")
        sys.exit(1)
    instancia = str(pair[0])
    erro = str(pair[1])
    R.append((instancia, erro))
"""
current_time = time.time()
if P == float(open(filename).read().split()[0]):
    # Verifica se o intervalo de tempo entre os pedidos é menor que V segundos
    if current_time - last_P_timestamp < V:
        print(f"Erro: Não é permitido identificar outro pedido com o mesmo I-ID durante {V} segundos.")
        sys.exit(1)
"""
s_data = str(S) + '\0'
ns_data = str(NS) + '\0'
q_data = str(Q) + '\0'
y_data = str(Y) + '\0'

"""last_P_timestamp = current_time

# Incrementa o valor de P para o próximo pedido e escreve no ficheiro, com o timestamp
P += 1
with open(filename, 'w') as file:
    file.write(f"{P} {last_P_timestamp}")"""

#p_data = str(P) + '\0'
n_data = str(N) + '\0'
nr_data = str(NR) + '\0'

# forma uma tupla de dados e depois transforma em bytes
W_str = ';'.join([f'{pair[0]},{pair[1]}' for pair in W])
R_str = ';'.join([f'{pair[0]},{pair[1]}' for pair in R])
W_bytes = W_str.encode('utf-8')
R_bytes = R_str.encode('utf-8')

# concatena as strings e transforma em bytes
x_data = '\0'
bytes = s_data.encode('utf-8') + ns_data.encode('utf-8') + q_data.encode('utf-8') + y_data.encode(
    'utf-8') + n_data.encode('utf-8') + nr_data.encode('utf-8') + W_bytes + x_data.encode(
    'utf-8') + R_bytes
print(bytes)

server_address = (ip, port)
client_socket.sendto(bytes, server_address)
response, _ = client_socket.recvfrom(4096)
decoded_response = response.decode('utf-8')
print('Received response from server:', decoded_response)

client_socket.close()
