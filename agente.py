import time
import random
import numpy as np
from matriz import MatrixZ


class AgentManagement:
    def __init__(self):
        self.start_timestamp = time.time()
        self.port, self.m, self.k, self.t, self.v, self.x = self.ReadConfigFile()

    #funcao que lê as configurações no ficheiro 
    def ReadConfigFile(self):
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
    def GetTime(self):
        current_time = time.time()
        uptime_seconds = current_time - self.start_timestamp
        return uptime_seconds
    
    

def main():
    agent = AgentManagement()
    uptime = agent.GetTime()
    print(f'O agente está em execução há {uptime} segundos.')
    configurations = agent.ReadConfigFile()
    print("configuraçoes:", configurations)
    matriz = MatrixZ(agent.m, agent.k)

    print("------------------primeiro-------------------")
    for i in range(agent.k):
        print(matriz.z[i])

    #atualiza a matriz z
    while True:
       matriz.UpdateMatrix()

       for i in range(agent.k):
            print(matriz.z[i])

        # aguarda o intervalo de atualização T (convertido de milissegundos para segundos),que está no ficheiro de config
       time.sleep(agent.t / 1000)

if __name__ == "__main__":
    main()