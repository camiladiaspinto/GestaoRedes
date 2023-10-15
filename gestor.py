import socket

# Cria um socket UDP 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('127.0.0.1', 1234)  

while True:
    # Envia
    message = input('Enter message to send to the server: ')
    client_socket.sendto(message.encode(), server_address)

    # Recebe
    response, _ = client_socket.recvfrom(4096)
    print('Received response from server:', response)

