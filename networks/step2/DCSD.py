import numpy as np
import igraph as ig
import networkx as nx


class DCSD:
    def __init__(self) -> None:
        pass

    def gen_network(self, serie):
        meio = middlePoint(serie)
        base = 2
        nn = 10

        vet_x = serie
        #print(vet_x)

        vetor_binario = self.calcula_vetor_binario(vet_x, meio);
        vet_decimal = self.vetor_bi2decimal(vetor_binario, nn);
        g = self.mat_adjacencia(vet_decimal,nn,base);

        mat_adj_nova = self.calcula_matriz_adj_soh_dos_nohs_conectados(g);
        #grafoFinal = nx.from_numpy_matrix(mat_adj_nova)
        grafoFinal = ig.Graph.Adjacency(mat_adj_nova, mode='undirected')
        #ig.plot(grafoFinal, f"VG_Graph.pdf")
        return mat_adj_nova

    def calcula_matriz_adj_soh_dos_nohs_conectados(self, mat):
        #recebe matriz de adjacencia e calcula diametro da rede.
        #primeiro tem que remover todas as linhas e colunas nulas da matriz se nao da erro na funcao
        
        tam = len(mat[0,:])
        
        indice = 0 #indice auxiliar pra matriz
        tam_novo = tam

        for i in range(tam):
            if indice < tam_novo:
                if sum(mat[indice,:]) == 0: #remove a linha e a coluna i dessa matriz. (se a linha eh toda zero, a coluna tb eh)
                    mat_aux = np.delete(mat,indice,0) #deleta a linha i
                    mat = np.delete(mat_aux,indice,1) #deleta a coluna i
                    if tam_novo - indice > 1:	#quando a diferenca entre eles eh 1 ja ta no final			
                        tam_novo = len(mat[indice,:])
                else:
                    indice = indice + 1 #soh anda o indice se nao deletar nenhuma linha/coluna
            else:
                break

                

        return(mat)

    def calcula_vetor_binario(self, x, meio):
        #recebe um vetor x e transforma ele em um vetor binario. aqui x vai de -1 ate 1. 
        #se x >= 0 vou dar valor de 1 se x <0 vou dar valor zero
        #retorna vetor binario com 0 e 1 de tamanho len(x)
        

        vet_binario = np.zeros(len(x))
        
        for i in range(len(x)):
            if x[i] >=meio:
                vet_binario[i] = 1
            else:
                vet_binario[i] = 0
        
        return(vet_binario.astype(int))

    def vetor_bi2decimal(self, vet_bi, n):
        #recebe vetor binario e vai pegar numero de tamanho n pra transformar pra decimal. anda de um em um
        #n = tamanho da palavra
        #retorna vetor decimal 
        tam = len(vet_bi)
        
        vet_dec = np.zeros(0)

        
        for i in range(tam-n+1) :#precisa ir ate tam-n 
            
            v = vet_bi[i:i+n]
            string_v = ''
            for j in range(len(v)): #transforma o vetor v em string
                string_v = string_v + str(v[j])
                        
            vet_dec = np.append(vet_dec,int(string_v,2))
        return(vet_dec.astype(int));

    def to_igraph(self, vet_dec, n, base):
        #tenho no maximo N = 2^n vertices no grafo. n = tamanho da palavra escolhida na hora da conversao
        #vet_dec(i) se conecta com seu vizinho vet_dec(i+1)
        tam_mat = base**n
        count = 0
        g = ig.Graph()
        g.add_vertices(tam_mat)
        for i in range(tam_mat):
            g.vs[i]["label"] = i+1

        valor = vet_dec[count]

        for i in range(1, len(vet_dec)):
            prox_valor = vet_dec[i]
            addEdge(g, valor, prox_valor)
            valor = prox_valor;


        graphAux = ig.Graph()
        numVertices = 0
        labels = []

        for i in g.vs:
            if i.degree() > 0:
                numVertices = numVertices + 1;
                labels.append(i["label"])

        print('labels= ', labels)

        print('numVertices= ', numVertices)
    
        print('numArestas= ', len(g.es))
        graphAux.add_vertices(numVertices);

        for i in range(numVertices):
            graphAux.vs[i]["label"] = labels[i]
    
        for i in range(len(g.es)):
            src = g.vs[g.es[i].source]["label"]
            dst = g.vs[g.es[i].target]["label"]

            print('src= ', src)
            print('dst= ', dst)

            src_ = 0
            dst_ = 0

            for j in graphAux.vs:
                if j["label"] == src:
                    src_ = j.index
                if j["label"] == dst:
                    dst_ = j.index

            graphAux.add_edge(src_, dst_);

        return graphAux
    
    def mat_adjacencia(self, vet_dec, n, base):
        #tenho no maximo N = 2^n vertices no grafo. n = tamanho da palavra escolhida na hora da conversao
        #vet_dec(i) se conecta com seu vizinho vet_dec(i+1)
        tam_mat = base**n
        
        mat_adj = np.zeros(shape=(tam_mat,tam_mat))

        for i in range(len(vet_dec)-1):
            j1 = vet_dec[i]#posicao do no inicial na mat_adj
            j2 = vet_dec[i+1]
            
            mat_adj[j1,j2] = 1
            mat_adj[j2,j1] = 1

            #marca esse campo da mat adjacencia como 1. matriz simetrica
            #if j1 != j2: #nao vai permitir autoconexao
            #	mat_adj[j1,j2] = 1
            #	mat_adj[j2,j1] = 1
        
        return(mat_adj.astype(int))

def middlePoint(csv_file) -> int:
    menor = 99999
    maior = -99999

    for i in range(len(csv_file)):
        if menor > csv_file[i]:
            menor = csv_file[i]
        if maior < csv_file[i]:
            maior = csv_file[i]

    return (maior + menor) / 2

def addEdge(g, v1, v2):
    if g.get_eid(v1, v2, directed=False, error=False) == -1:
        g.add_edge(v1, v2)


