import time
import random
import numpy as np

class MatrixZ:
    def __init__(self, m, k):
        self.m = m
        self.k = k
        self.za = self.GenerateMatrixZa()
        self.zb = self.GenerateMatrixZb()
        self.zc = np.zeros((self.k, self.k), dtype=np.uint8)
        self.zd = np.zeros((self.k, self.k), dtype=np.uint8)
        self.z = self.GenerateMatrixZ()

    #funcao da rotaçao
    def rotate(self, m, n):
        return m[-n:] + m[:-n]

    #funcao da transposta
    def transpose(self, m):
        num_rows = len(m)
        num_cols = len(m[0])
        transposed = [[0] * num_rows for _ in range(num_cols)]
        
        for i in range(num_cols):
            for j in range(num_rows):
                transposed[i][j] = m[j][i]
        
        return transposed

    #funcao para gerar Za
    def GenerateMatrixZa(self):
        za = []
        for i in range(self.k):
            if i == 0:
                za.append(list(map(int, self.m)))
            else:
                rotated_M = self.rotate(self.m, i)
                za.append(list(map(int, rotated_M)))
        return za

    #funcao parar gerar Zb
    def GenerateMatrixZb(self):
        zb = []
        for j in range(self.k):
            if j == 0:
                zb.append(list(map(int, self.m)))
            else:
                rotated_m = self.rotate(self.m, j)
                zb.append(list(map(int, rotated_m)))
        
        zb = self.transpose(zb)
        
        return zb

    #funcao para gerar Z
    def GenerateMatrixZ(self):
        for i in range(self.k):
            for j in range(self.k):
                array_c = self.za[i][j]
                random.seed(array_c)
                self.zc[i, j] = random.randint(0, 255)
                array_d = self.zb[i][j]
                random.seed(array_d)
                self.zd[i, j] = random.randint(0, 255)

        z_result = [[0] * self.k for _ in range(self.k)]

        #XOR 
        for i in range(self.k):
            for j in range(self.k):
                z_result[i][j] = self.za[i][j] ^ self.zb[i][j] ^ self.zc[i][j] ^ self.zd[i][j]

        return z_result
    
    #funcao para fazer update; T é o periodo e está no ficheiro de config
    def UpdateMatrix(self):

        #passo 1: faz o rotate de todas as linhas completas em relacao ao random em que o tamanho maximo é k-1
        for i in range(self.k):
            random.seed(int(self.z[i][0]))
            self.z[i] = self.rotate(self.z[i], random.randint(0, self.k - 1))
        

        #passo 2: roda verticalmente n vezes (de cima para baixo)
        for j in range(self.k):
            column_j = [self.z[i][j] for i in range(self.k)]
            random.seed(int(self.z[0][j]))
            rotated_column = self.rotate(column_j, random.randint(0, self.k - 1))
            for i in range(self.k):
                self.z[i][j] = rotated_column[i]

      # função para gerar a chave com base na matriz Z e no número de atualizações

    def GenerateKey(self, N):
        print(N)
        array_i = int(N + self.z[0][0])
        random.seed(array_i)
        i = random.randint(0, self.k - 1)

        array_j = int(self.z[i][0])
        random.seed(array_j)  
        j = random.randint(0, self.k - 1)

        # Calcula a chave através da expressão C = xor(Zi*,transpose(Z*j))
        key_i = self.za[i]
        key_j = [self.z[m][j] for m in range(self.k)]
        
        # Calcula a chave usando XOR
        key = [key_i[m] ^ key_j[m] for m in range(self.k)]
        print(key)
        return bytes(key)


