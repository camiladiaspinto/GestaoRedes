import socket
import sys
import random
import json
ip = '127.0.0.1'
port = 1234


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Obtém os valores da PDU a partir dos argumentos da linha de comando e converte para inteiros para ser mais fácil tratar dos dados
S = 0 #mecanismo de segurança que é zero 
NS = 0
P = random.randint(1,100)  #identificação do pedido 
Y = int(sys.argv[1]) #identidicaçaõ da primitiva 

#Falta isot: não é permitido que durante V segundos o gestor identifique outro pedido com o mesmo I-ID, duvida 
NW = int(sys.argv[2]) #quantidade de pares 
NR = int(sys.argv[3])  #quantidade de pares de erros 

W = []  # Lista de pares
R=[] #Lista de erros 

if int(Y) == 2:
    #começa na posicção 4 e vai desde essa posição até ao fim da quantidade de pares
    for i in range(4, 4 + NW):
        pair = sys.argv[i].split(',')
        if len(pair) != 2:
            print("Erro: Formato inválido para o par (I-ID, H ou N).")
            sys.exit(1)
        instancia = str(pair[0])
        valor = str(pair[1])
        W.append((instancia, valor))
    #começa na quantidade final da lista pares e vai até ao final da lista erros 
    for i in range(4+NW, 4+NW+ NR): 
        pair = sys.argv[i].split(',')
        if len(pair) != 2:
                print("Erro: Formato inválido para o par (I-ID, E).")
                sys.exit(1)
        instancia = str(pair[0])
        erro = str(pair[1])
        R.append((instancia, erro))
        
else:
    print("Primitiva não suportada.")
    sys.exit(1)

s_data=str(S) + '\0'
ns_data=str(NS) + '\0'
y_data=str(Y) + '\0'
p_data=str(P) + '\0'
nw_data=str(NW) + '\0'
nr_data=str(NR) + '\0'

#forma uma tupla de dados e depois transforma em bytes 
W_str = ';'.join([f'{pair[0]},{pair[1]}' for pair in W])
R_str = ';'.join([f'{pair[0]},{pair[1]}' for pair in R])
W_bytes = W_str.encode('utf-8')
R_bytes = R_str.encode('utf-8')

#concatena as strings e tranforma em bytes 

x_data='\0'
bytes= s_data.encode('utf-8')+ns_data.encode('utf-8')+y_data.encode('utf-8')+p_data.encode('utf-8')+nw_data.encode('utf-8')+nr_data.encode('utf-8')+W_bytes+x_data.encode('utf-8')+R_bytes
print(bytes)


#para função de teste antes de implementar isto: # jfpereira: mais tarde será algo deste tipo (temos de ter uma thread por pedido recebido)
        # https://cppsecrets.com/users/110711510497115104971101075756514864103109971051084699111109/Python-UDP-Server-with-Multiple-Clients.php
        # codigo não funcional, é só um esboço
        # c_thread = threading.Thread(target = self.handle_request, args = (data, client_address, matrizZ, MIB))
        # c_thread.daemon = True
        # c_thread.start()
        # a função handle_request terá todo o código para tratar dos pedidos

server_address = (ip, port)
num_requests = 10  

for _ in range(num_requests):
    client_socket.sendto(bytes, server_address)
    response, _ = client_socket.recvfrom(4096)
    print('Received response from server:', response)

client_socket.close()
