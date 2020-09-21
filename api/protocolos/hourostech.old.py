import os
import re
import socket
import time
from collections import namedtuple
from datetime import date, datetime
from api.services.thread import threads
from api.loggers.logs import loggers
from api.models import Cartao_nao_cadastrado, Config, Abast, Bicos

class protocoloHouros():

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
        self.config = Config.objects.all().first()
        self.tempo_cmd = float(self.config.tempo_cmd)        
        self.bicos_atualizados = {}
        self.bicos_abastecendo = []
        self.estado_rel = []    
        self.encerrantes = {}  
        self.start_default = 0

    def seta_tipo_default(self):
        for a in self.tipo:
            if self.tipo[a]['padrao']:
                self.tipo_default = int(self.tipo[a]['codigo'])

    def checkSum(self, comando):
        soma = 0
        comando = comando.replace(">", '')
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

    def tam_data(self, tamanho):
        tamanho = hex(tamanho).replace('x', '0')
        return str(tamanho).zfill(4)

    def comando(self, comando, check=True):
        msg_data = comando.replace(">", '')
        tam_datas = self.tam_data(len(msg_data))
        msg = f""">?{tam_datas}{msg_data}"""
        if check:
            check = self.checkSum(msg)
        else:
            check = ''
        msg = f""">?{tam_datas}{msg_data}{check}"""
        self.tcp.send(msg.encode())
        try:
            status = self.tcp.recv(100).decode('utf-8')
            status = status.replace('>', '')
        except socket.timeout:
            status = "(404)"
        except:
            status = "(404)"
        return status

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
        comando = self.comando('01')
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
        string = f"""07{bico}{preco}"""
        comando = self.comando(string)
        status = str(comando[7:9])
        print(comando)
        if status == "00":
            return True
        else:
            return False

    def modo_operacao(self, bico, modo):
        comando = self.comando(f"""&M{bico}{modo}""")
        return comando

    def ativa_identfid(self, bico):
        return self.comando('?CI010120FE')

    def incrementa_identfid(self):
        comando = self.comando('18')
        return comando

    def salva_cartao(self, cartao):        
        try:
            cartao_nao_cadastrado = Cartao_nao_cadastrado.objects.create(cartao=cartao)
            cartao_nao_cadastrado.save()
        except Exception as erro:
            print(erro)
            return({'message':'Error interno!'}, 500)
        
        return ({str(cartao_nao_cadastrado.cartao): {
            'cartao': cartao_nao_cadastrado.cartao
        }})
    
    def comandoCBC(self, comando, check=True):
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
    
    
    def verificaChave(self):
        try:
            comando = self.comando('0C')
            if len(comando) > 10:
                bicos = [str(comando[13:15]),str(comando[15:17]),str(comando[17:19]),str(comando[19:21])]
                chave = comando[21:37]
                ver_chave = self.chave_preco(chave)
                status = self.status()
                status = status[7:(len(status)-3)]           
                if ver_chave:
                    print(bicos)
                    for bicos_b in bicos:
                        if bicos_b != '00':
                            print(bicos_b)
                            if status[int(bicos_b)-1] == 'E': 
                                self.bicos_atualizados.append(bicos_b)                                                        
                                tipo_chave = self.chave_preco(chave)['tipo']
                                bico_produto = self.bico(bicos_b)    
                                if bico_produto:
                                    print(bico_produto)
                                    produto_preco = self.produto(bico_produto, tipo_chave)
                                    print(produto_preco)
                                    if produto_preco:  
                                        print(produto_preco)                                     
                                        troca_preco = self.troca_preco(
                                        produto_preco, bicos_b)
                                        resposta = f"""U{bicos_b} preco = {produto_preco} trocado? {troca_preco}"""                                       
                                        log = loggers("automacao").info(msg=resposta,prefix="[Chave]") 
                                        self.bicos_atualizados.update({bicos_b:{'preco':produto_preco,'tipo':tipo_chave}})
                        time.sleep(self.tempo_cmd)          
                    self.incrementa_identfid()                     
                else:
                    print(chave)
                    log = loggers("automacao").info(msg=chave,prefix="[Chave]")
                    bico_cartao = bicos[0]
                    print(self.salva_cartao(chave,bico_cartao))
                    self.incrementa_identfid()
        except Exception as e:
            print(e)
            print('erro na identificacao do chip')
            log = loggers("automacao").info(msg='erro na identificacao do chip',prefix="[Chave]") 
            log = loggers("automacao").info(msg=e,prefix="[Chave]") 
                    
    def gravaAbastecimento(self):
        try:
            tipo_chave = self.tipo_default
            status = self.status()
            status = status[7:(len(status)-3)]
            if len(status) == 32:
                for i, c in enumerate(status):
                    if c == "A" and self.estado_rel[i] != "G":
                        self.estado_rel[i] = "G"
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
                                        if bicos_b in self.encerrantes:
                                            self.encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                        else:
                                            self.encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                        self.bicos_abastecendo.append(bicos_b)
                                        print(encerrante)   
                    elif c == "B" and self.estado_rel[i] == "G":
                        self.estado_rel[i] = "B"
                        bico = self.montaHexLado(i)
                        print(self.bicos_abastecendo)
                        for t, bicos in enumerate(self.bicos_abastecendo):
                            print(bicos)
                            if bicos in bico :
                                encerrante = int(self.encerrante(bicos))/100
                                enc_ant = int(self.encerrantes[bicos]['encerrante'])/100
                                frentista = self.encerrantes[bicos]['frentista']
                                qtd = encerrante - enc_ant
                                preco = 0
                                produto = ""                            
                                if qtd > 0.01:
                                    bico_banco = Bicos.objects.filter(bico=bicos)
                                    ultimo_enc = bico_banco[0].encerrante
                                    bico_produto = self.bico(bicos)
                                    produto = bico_produto
                                    print(self.bicos_atualizados)
                                    if bicos in self.bicos_atualizados:                                
                                        preco = (int(self.bicos_atualizados[bicos]['preco']))/1000
                                        tipo_chave = self.bicos_atualizados[bicos]['tipo']
                                        for x in bico:
                                            print(x)
                                            if x in self.bicos_atualizados:
                                                self.bicos_atualizados.pop(x)
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
                                            print(f" abast nao identificado bico {bicos} quantidade {dif}  preço {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}")
                                            log = loggers("automacao").info(msg=f" abast nao identificado bico {bicos} quantidade {dif}  preço {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}",prefix="[Gravando]")
                                    total = qtd * preco
                                    abastecimento = Abast.objects.create(bico=bicos,cartao=frentista,produto=produto,valor=preco,enc_ini=enc_ant,enc_fim=encerrante,quantidade=qtd,total=total,tipo = tipo_chave)
                                    bico_banco.update(encerrante=encerrante)
                                    print(f"bico {bicos} quantidade {qtd}  preço {preco} valor abastecido {total}  frentista {frentista}")
                                    log = loggers("automacao").info(msg=f"bico {bicos} quantidade {qtd}  preço {preco} valor abastecido {total}  frentista {frentista}",prefix="[Gravando]")
                                else:
                                    print('abastecimento zerado')
                                    log = loggers("automacao").info(msg='abastecimento zerado',prefix="[Gravando]")
                                self.bicos_abastecendo.pop(t)
        except Exception as e:
            print(e)
            print('erro ao gravar no banco de dados o abastecimento')
            log = loggers("automacao").info(msg=e,prefix="[Gravando]")
            log = loggers("automacao").info(msg='erro ao gravar no banco de dados o abastecimento',prefix="[Gravando]")
            
            
    def setDefault(self):
        try:
            tipo_chave = self.tipo_default
            if tipo_chave > 0:
                if len(self.bicos_atualizados) > 0:
                        codigo = self.bicos_atualizados[0]
                        status = self.status()
                        status = status[7:(len(status)-3)] 
                        if status[int(codigo)-1] == 'B': 
                            bico_produto = self.bico(codigo)      
                            print(bico_produto)       
                            if bico_produto:                        
                                produto_preco = self.produto(bico_produto, tipo_chave)
                                if produto_preco:
                                    print(codigo)
                                    print(produto_preco)
                                    troca_preco = self.troca_preco(
                                        produto_preco, codigo) 
                                    resposta = f"""U{codigo} preco = {produto_preco} trocado? {troca_preco}"""                                                       
                                    log = loggers("automacao").info(msg=resposta,prefix="[Default]")                   
                                    time.sleep(self.tempo_cmd) 
                                log = loggers("automacao").info(msg='Preco padrao setado',prefix="[Default]")   
                                
                            self.bicos_atualizados.pop(0)
                elif self.start_default == 0:
                    for a in self.bicos:
                        bico_produto = self.bico(a)
                        if bico_produto:
                            produto_preco = self.produto(
                                bico_produto, tipo_chave)
                            if produto_preco:
                                troca_preco = self.troca_preco(
                                    produto_preco, a)
                                resposta = f"""U{a} preco = {produto_preco} trocado? {troca_preco}"""                                                       
                                log = loggers("automacao").info(msg=resposta,prefix="[Default]")                   
                                time.sleep(self.tempo_cmd)
                            print('Preco padrao setado')
                            log = loggers("automacao").info(msg='Preco padrao setado',prefix="[Default]")

                    self.start_default = 1                    
        except Exception as e:
            print(e)
            print('erro ao setar o preco padrao')        
            log = loggers("automacao").info(msg=e,prefix="[Default]")  
            log = loggers("automacao").info(msg='erro ao setar o preco padrao',prefix="[Default]")
            
            

    def ler_identificador(self):
        self.bicos_atualizados = []
        while True:
            comando = self.comando('0C')
            if len(comando) > 10:
                bicos = [str(comando[13:15]),str(comando[15:17]),str(comando[17:19]),str(comando[19:21])]
                chave = comando[21:37]
                ver_chave = self.chave_preco(chave)
                status = self.status()
                status = status[7:(len(status)-3)]           
                if ver_chave:
                    print(bicos)
                    for bicos_b in bicos:
                        if bicos_b != '00':
                            print(bicos_b)
                            if status[int(bicos_b)-1] == 'E': 
                                self.bicos_atualizados.append(bicos_b)                                                        
                                tipo_chave = self.chave_preco(chave)['tipo']
                                bico_produto = self.bico(bicos_b)    
                                if bico_produto:
                                    print(bico_produto)
                                    produto_preco = self.produto(bico_produto, tipo_chave)
                                    print(produto_preco)
                                    if produto_preco:  
                                        print(produto_preco)                                     
                                        troca_preco = self.troca_preco(
                                        produto_preco, bicos_b)          
                    self.incrementa_identfid()                     
                else:
                    ...
                    print(chave)
                    print(self.salva_cartao(chave))
                    self.incrementa_identfid()
            # preco padrao
                tipo_chave = self.tipo_default
                if tipo_chave > 0:
                    if len(self.bicos_atualizados) > 0:
                        codigo = self.bicos_atualizados[0]
                        status = self.status()
                        status = status[7:(len(status)-3)] 
                        if status[int(codigo)-1] == 'B': 
                            bico_produto = self.bico(codigo)      
                            print(bico_produto)       
                            if bico_produto:                        
                                produto_preco = self.produto(bico_produto, tipo_chave)
                                if produto_preco:
                                    print(codigo)
                                    print(produto_preco)
                                    troca_preco = self.troca_preco(
                                        produto_preco, codigo)     
                                
                            self.bicos_atualizados.pop(0)
                else :
                    self.bicos_atualizados.clear()
            time.sleep(0.5)
