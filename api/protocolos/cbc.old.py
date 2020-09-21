import os
import re
import socket
import time
from collections import namedtuple
from datetime import date, datetime

from api.models import Cartao_nao_cadastrado, Config, Abast, Bicos
from api.loggers.logs import loggers

class protocoloCBC():

    def __init__(self, host, porta, produtos=None, chaves=None, bicos=None, tipos=None):
        self.porta = porta
        self.host = host
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(1)
        dest = (str(self.host), int(self.porta))
        self.tcp.connect(dest)
        self.chaves = chaves
        self.produtos = produtos
        self.bicos = bicos
        self.tipo = tipos
        self.tipo_default = 0
        self.seta_tipo_default()
        self.state_chave_preco = ''
        config = Config.objects.all().first()
        self.tempo_cmd = float(config.tempo_cmd)

    def conecta(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(1)
        dest = (str(self.host), int(self.porta))
        self.tcp.connect(dest)

    def seta_tipo_default(self):
        for a in self.tipo:
            if self.tipo[a]['padrao']:
                self.tipo_default = int(self.tipo[a]['codigo'])

    def checkSum(self, comando):
        soma = 0
        comando = comando.replace("(", '').replace(")", '')
        for a in comando:
            soma += ord(a)

        saida = hex(soma)[-2::]
        return saida.upper()

    def montaHex(self, endereco):
        modulo = int(str(endereco)[0:2])
        lado = int(str(endereco)[3:4])
        bico = int(str(endereco)[4:5])

        calc = (((modulo*4)+lado)+((bico-1)*64))-1
        hexa = hex(calc)
        if len(hexa) == 3:
            hexa = hexa.replace("x", '').upper()
        else:
            hexa = hexa[-2::].upper()
        return hexa

    def hexa(self, valor):
        hexa = hex(valor)
        if len(hexa) == 3:
            hexa = hexa.replace("x", '').upper()
        else:
            hexa = hexa[-2::].upper()
        return hexa

    def montaHexLado(self, posicao):
        posicao = int(posicao)+4
        pos1 = self.hexa(int(posicao))
        pos2 = self.hexa(int(posicao)+(64*1))
        pos3 = self.hexa(int(posicao)+(64*2))
        pos4 = self.hexa(int(posicao)+(64*3))

        hexas = [str(pos1), str(pos2), str(pos3), str(pos4)]
        return hexas

    def montaHexPerso(self, posicao):
        pos1 = self.hexa(int(posicao))
        pos2 = self.hexa(int(posicao)+(64*1))
        pos3 = self.hexa(int(posicao)+(64*2))
        pos4 = self.hexa(int(posicao)+(64*3))

        hexas = [str(pos1), str(pos2), str(pos3), str(pos4)]
        return hexas

    def comando(self, comando, check=True):
        while True:
            try:
                msg = comando.replace("(", '').replace(")", '')

                if check:
                    check = self.checkSum(comando)
                else:
                    check = ''
                msg = f"""({msg}{check})"""
                self.tcp.send(msg.encode())

                try:
                    status = self.tcp.recv(100).decode('utf-8')
                    status = status.replace('(', '').replace(')', '')
                except socket.timeout:
                    status = "(404)"
                except:
                    status = "(404)"
                return status
                break
            except:
                self.conecta()
            
        
        
    def grava_chave(self, chave, controler='27', turnoI1='0000', turnoF1='0000', turnoI2='0000', turnoF2='0000'):
        grava_chave = f"""?F{controler}G{chave}{turnoI1}{turnoF1}{turnoI2}{turnoF2}"""
        comando = self.comando(grava_chave)
        return comando

    def produto(self, produto, preco):
        if produto in self.produtos:
            if int(preco) in self.produtos[produto]['precos']:
                return self.produtos[produto]['precos'][int(preco)]
        return False

    def bico(self, bico):
        if bico in self.bicos:
            return self.bicos[bico]['produto']
        return False

    def tipos(self, tipo):
        if tipo in self.tipo:
            return self.tipo[tipo]['padrao']
        return False

    def status(self):
        comando = self.comando('&S', check=False)
        return comando

    def leitura_totais(self, bico, modo='L'):
        string = f"&T{bico}{modo}"
        comando = self.comando(string)
        return comando

    def leitura_registro(self, registro):
        string = f"&LR{registro}"
        comando = self.comando(string)
        return comando

    def chave_preco(self, chave):
        if chave in self.chaves:
            return self.chaves[chave]
        else:
            return False

    def troca_preco(self, preco, bico, nivel=0):
        string = f"""&U{bico}{nivel}0{preco}"""
        comando = self.comando(string)
        print(comando)
        if comando == f"""U{bico}""":
            return True
        else:
            return False

    def modo_operacao(self, bico, modo):
        comando = self.comando(f"""&M{bico}{modo}""")
        return comando

    def ativa_identfid(self, bico):
        return self.comando('?CI010120FE')

    def incrementa_identfid(self):
        comando = self.comando('(?I88)', check=False)
        return comando

    def salva_cartao(self, cartao):
        try:
            cartao_nao_cadastrado = Cartao_nao_cadastrado.objects.create(
                cartao=cartao)
            cartao_nao_cadastrado.save()
        except Exception as erro:
            print(erro)
            return({'message': 'Error interno!'}, 500)

        return ({str(cartao_nao_cadastrado.cartao): {
            'cartao': cartao_nao_cadastrado.cartao
        }})
        
    
    def ver_abast(self):
        comando = self.comando('(?V95)', check=False)
        return comando
    
    def encerrante(self,bico):
        comando = self.comando(f'&T{bico}l')
        comando  = comando[4:14]
        return comando

    def ler_identificador(self):
        bicos_atualizados = {}
        bicos_abastecendo = []
        estado_rel = []    
        encerrantes = {}    
        for c in self.status()[1:33]:
            estado_rel.append(c)
        
        while True:
            try:
                comando = self.comando('?A')
                if len(comando) > 2:
                    chave = comando[1:17]
                    bico = comando[17:19]
                    bicos = self.montaHexPerso(int(bico, 16))
                    ver_chave = self.chave_preco(chave)
                    if ver_chave:
                        print(bicos)
                        for bicos_b in bicos:
                            if bicos_b in self.bicos:
                                tipo_chave = self.chave_preco(chave)['tipo']
                                bico_produto = self.bico(bicos_b)
                                if bico_produto:
                                    print(bico_produto)
                                    produto_preco = self.produto(
                                        bico_produto, tipo_chave)
                                    print(produto_preco)
                                    if produto_preco:
                                        troca_preco = self.troca_preco(
                                            produto_preco, bicos_b)
                                        print(troca_preco)
                                        resposta = f"""U{bicos_b} preco = {produto_preco} trocado? {troca_preco}"""                                                   
                                        log = loggers("automacao").info(msg=resposta) 
                                        bicos_atualizados.update({bicos_b:{'preco':produto_preco,'tipo':tipo_chave}})
                                        time.sleep(self.tempo_cmd)
                        self.incrementa_identfid()
                    else:
                        print(chave)
                        log = loggers("automacao").info(msg=chave)
                        print(self.salva_cartao(chave))
                        self.incrementa_identfid()
                if comando != "0":
                    print(comando)
            except:
                print('erro na identificacao do chip')  
                log = loggers("automacao").info(msg='erro na identificacao do chip')             
                
            try:
                tipo_chave = self.tipo_default
                status = self.status()[1:33]
                for i, c in enumerate(status):
                    if c == "A" and estado_rel[i] != "G":
                        estado_rel[i] = "G"
                        bicos = self.montaHexLado(i)
                        abast = self.ver_abast()
                        if len(abast) >= 18:
                            qtd = len(abast)/18           
                            for x in range(int(qtd)):
                                abast_andamento = abast[(x*18):((x*18)+18)]
                                bico_andamento = abast_andamento[0:2]
                                frentista = abast_andamento[2:18]                            
                                for bicos_b in bicos:
                                    if bicos_b == bico_andamento:
                                        encerrante = self.encerrante(bicos_b)
                                        if bicos_b in encerrantes:
                                            encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                        else:
                                            encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                        bicos_abastecendo.append(bicos_b)
                                        print(encerrante)   
                    elif c == "B" and estado_rel[i] == "G":
                        estado_rel[i] = "B"
                        bico = self.montaHexLado(i)
                        print(bicos_abastecendo)
                        for t, bicos in enumerate(bicos_abastecendo):
                            print(bicos)
                            if bicos in bico :
                                encerrante = int(self.encerrante(bicos))/100
                                enc_ant = int(encerrantes[bicos]['encerrante'])/100
                                frentista = encerrantes[bicos]['frentista']
                                qtd = encerrante - enc_ant
                                preco = 0
                                produto = ""                            
                                if qtd > 0.01:
                                    bico_banco = Bicos.objects.filter(bico=bicos)
                                    ultimo_enc = bico_banco[0].encerrante
                                    bico_produto = self.bico(bicos)
                                    produto = bico_produto
                                    print(bicos_atualizados)
                                    if bicos in bicos_atualizados:                                
                                        preco = (int(bicos_atualizados[bicos]['preco']))/1000
                                        tipo_chave = bicos_atualizados[bicos]['tipo']
                                        for x in bico:
                                            print(x)
                                            if x in bicos_atualizados:
                                                bicos_atualizados.pop(x)
                                    else:
                                        produto_preco = self.produto(bico_produto, tipo_chave)
                                        preco = (int(produto_preco))/1000
                                    
                                    if ultimo_enc == 0.00:
                                        bico_banco.update(encerrante=encerrante)
                                    elif ultimo_enc < enc_ant:
                                        dif = int(enc_ant) - int(ultimo_enc)
                                        if dif > 0.1:
                                            produto_preco = self.produto(bico_produto, self.tipo_default)
                                            preco_padrao = (int(produto_preco))/1000
                                            total_padrao = dif * preco_padrao
                                            abastecimento = Abast.objects.create(bico=bicos,cartao="Nao Identificado",produto=produto,valor=preco_padrao,enc_ini=ultimo_enc,enc_fim=enc_ant,quantidade=dif,total=total_padrao,tipo = self.tipo_default) 
                                            bico_banco.update(encerrante=enc_ant)
                                            print(f" abast nao identificado bico {bicos} quantidade {dif}  preco {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}")                                                   
                                            log = loggers("automacao").info(msg=f" abast nao identificado bico {bicos} quantidade {dif}  preco {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}")
                                    total = qtd * preco
                                    abastecimento = Abast.objects.create(bico=bicos,cartao=frentista,produto=produto,valor=preco,enc_ini=enc_ant,enc_fim=encerrante,quantidade=qtd,total=total,tipo = tipo_chave)
                                    bico_banco.update(encerrante=encerrante)
                                    print(f"bico {bicos} quantidade {qtd}  preco {preco} valor abastecido {total}  frentista {frentista}")                                      
                                    log = loggers("automacao").info(msg=f"bico {bicos} quantidade {qtd}  preco {preco} valor abastecido {total}  frentista {frentista}")
                                else:
                                    print('abastecimento zerado')                                    
                                    log = loggers("automacao").info(msg='abastecimento zerado')
                                bicos_abastecendo.pop(t)
            except:
                print('erro ao gravar no banco de dados o abastecimento')  
                log = loggers("automacao").info(msg='erro ao gravar no banco de dados o abastecimento')
                
            try:
                tipo_chave = self.tipo_default
                if tipo_chave > 0:
                    status = self.status()[1:33]
                    state_cbc = self.state_chave_preco
                    if status != state_cbc:
                        if state_cbc:
                            for i, c in enumerate(status):
                                if c != state_cbc[i] and c == 'B':
                                    codigos = self.montaHexLado(i)
                                    for a in codigos:
                                        if a in self.bicos:
                                            bico_produto = self.bico(a)
                                            if bico_produto:
                                                produto_preco = self.produto(
                                                    bico_produto, tipo_chave)
                                                if produto_preco:
                                                    troca_preco = self.troca_preco(
                                                        produto_preco, a)
                                                    resposta = f"""U{a} preco = {produto_preco} trocado? {troca_preco}"""                                                      
                                                    log = loggers("automacao").info(msg=resposta)                                         
                                                    time.sleep(self.tempo_cmd)
                                                print('Preco padrao setado')
                                                log = loggers("automacao").info(msg='Preco padrao setado')
                                                
                        else:
                            for i, c in enumerate(status):
                                if c == 'B':
                                    codigos = self.montaHexLado(i)
                                    for a in codigos:
                                        if a in self.bicos:
                                            bico_produto = self.bico(a)
                                            if bico_produto:
                                                produto_preco = self.produto(
                                                    bico_produto, tipo_chave)
                                                if produto_preco:
                                                    troca_preco = self.troca_preco(
                                                        produto_preco, a)
                                                    resposta = f"""U{a} preco = {produto_preco} trocado? {troca_preco}"""                                                       
                                                    log = loggers("automacao").info(msg=resposta)                   
                                                    time.sleep(self.tempo_cmd)
                                                print('Preco padrao setado')
                                                log = loggers("automacao").info(msg='Preco padrao setado')
                        self.state_chave_preco = status
            except:
                print('erro ao setar o preco padrao')
                log = loggers("automacao").info(msg='erro ao setar o preco padrao')
            time.sleep(self.tempo_cmd)
