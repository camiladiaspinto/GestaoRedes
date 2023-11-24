##classe mib com dicionario, tipo blackbox, faz tudo relacionado á mib aqui nesta classe, e a main só recebe e envia coisas

class MIB:
    def __init__(self):
        self.snmpKeysMib = {} #cria dicionario 

    #metodo para ter a mib toda
    def get_mib(self):
        return self.snmpKeysMib

    def add_iid_entry(self, iid, list):
        self.snmpKeysMib[iid] = list
    
    #metodo para ter a lista de um iid especifico 
    def get_entry_by_iid(self, iid):
        return self.snmpKeysMib.get(iid, None)
    
    def get_all_keys(self):
        all_keys = []
        for key in self.snmpKeysMib.keys():
            all_keys.append(key)
        return all_keys

    