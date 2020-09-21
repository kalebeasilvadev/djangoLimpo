import os
import re
import socket
import time
from collections import namedtuple
from datetime import date, datetime
from api.services.thread import threads
from api.loggers.logs import loggers
from api.models import Cartao_nao_cadastrado, Config, Abast, Bicos

import traceback
 

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
        self.tempo_cmd = 0.5       
        self.bicos_atualizados = {}
        self.bicos_abastecendo = {}
        self.estado_rel = []    
        self.encerrantes = {}  
        self.start_default = 0
        
    def set_status(self):
        status = self.status()
        status = status[7:(len(status)-3)]
        for c in status:
            self.estado_rel.append(c)

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
    
    def conecta(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp.settimeout(1)
        dest = (str(self.host), int(self.porta))
        self.tcp.connect(dest)


    def comando(self, comando, check=True):
        while True:
            try:
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
            except:
                log = loggers("automacao").info(msg='Perdeu Comunicação com a Automaçao',prefix="[Rede]")
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
        comando = self.comando('01')
        return comando

    def leitura_totais(self, bico, modo='01'):
        string = f"05{bico}{modo}"
        comando = self.comando(string)
        return comando

    def leitura_registro(self, registro):
        string = f"08{registro}"
        comando = self.comando(string)
        return comando
    
    def leitura_ponteiro(self):
        string = f"050006"
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

    def salva_cartao(self, cartao,bico):
        try:
            cartao_nao_cadastrado = Cartao_nao_cadastrado.objects.create(
                cartao=cartao,bico=bico)
            cartao_nao_cadastrado.save()
        except Exception as erro:
            print(erro)
            return({'message': 'Error interno!'}, 500)

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
    
    def ver_abast(self):
        comando = self.comando('28')
        comando = comando[7:(len(comando)-3)]
        return comando
    
    def verificaChave(self):
        try:
            comando = self.comando('0C')
            if len(comando) > 10:
                log = loggers("automacao").info(msg=f"comando {comando}",prefix="[Chave]")
                bicos = [str(comando[13:15]),str(comando[15:17]),str(comando[17:19]),str(comando[19:21])]
                log = loggers("automacao").info(msg=f"bicos {bicos}",prefix="[Chave]")
                chave = comando[21:37]
                log = loggers("automacao").info(msg=f"chave {chave}",prefix="[Chave]")
                ver_chave = self.chave_preco(chave)
                status = self.status()
                log = loggers("automacao").info(msg=f"status {status}",prefix="[Chave]")
                status = status[7:(len(status)-3)]  
                log = loggers("automacao").info(msg=f"status formatado {status}",prefix="[Chave]")
                if ver_chave:
                    for bicos_b in bicos:
                        if bicos_b != '00':
                            if status[int(bicos_b)-1] == 'E':                                             
                                tipo_chave = self.chave_preco(chave)['tipo']
                                log = loggers("automacao").info(msg=f"tipo chave {tipo_chave}",prefix="[Chave]")
                                bico_produto = self.bico(bicos_b)   
                                log = loggers("automacao").info(msg=f"bicos produto {bico_produto}",prefix="[Chave]")
                                log = loggers("automacao").info(msg=f"bico {bicos_b}",prefix="[Chave]")
                                if bico_produto:
                                    produto_preco = self.produto(bico_produto, tipo_chave)
                                    log = loggers("automacao").info(msg=f"preco {produto_preco}",prefix="[Chave]")
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
            
            track = traceback.format_exc()
            self.incrementa_identfid()
            print(e)
            print('erro na identificacao do chip')
            log = loggers("automacao").info(msg='erro na identificacao do chip',prefix="[Chave]") 
            log = loggers("automacao").info(msg=track,prefix="[Chave]") 
                    
    def gravaAbastecimento(self):
        try:
            tipo_chave = self.tipo_default
            status = self.status()
            status = status[7:(len(status)-3)]
            if len(status):                      
                for i, c in enumerate(status):
                    if c == "A" and self.estado_rel[i] != "G":
                        self.estado_rel[i] = "G"
                        abast = self.ver_abast()
                        if len(abast) >= 24:
                            qtd = len(abast)/24  
                            for x in range(int(qtd)):
                                abast_andamento = abast[(x*24):((x*24)+24)]
                                log = loggers("automacao").info(msg=f"abast_andamento {abast_andamento}",prefix="[Gravando]")
                                bico_andamento = abast_andamento[0:2]
                                log = loggers("automacao").info(msg=f"bico_andamento {bico_andamento}",prefix="[Gravando]")
                                frentista = abast_andamento[8:24]         
                                log = loggers("automacao").info(msg=f"frentista {frentista}",prefix="[Gravando]")
                                encerrante = self.leitura_totais(bico_andamento)[11:21]
                                log = loggers("automacao").info(msg=f"encerrante {encerrante}",prefix="[Gravando]")
                                self.encerrantes.update({bico_andamento:{'encerrante':encerrante,'frentista':frentista}})           
                                self.bicos_abastecendo.update({bico_andamento:bico_andamento})
                    elif c == "B" and self.estado_rel[i] == "G":
                        self.estado_rel[i] = "B"
                        bico = str(i+1).zfill(2)
                        print(self.bicos_abastecendo)
                        if bico in self.bicos_abastecendo:
                            log = loggers("automacao").info(msg=f"encerrante {self.leitura_totais(bico)[11:21]}",prefix="[Gravando]")
                            log = loggers("automacao").info(msg=f"encerrante anterior {self.encerrantes[bico]['encerrante']}",prefix="[Gravando]")
                            log = loggers("automacao").info(msg=f"frentista {self.encerrantes[bico]['frentista']}",prefix="[Gravando]")
                            encerrante = int(self.leitura_totais(bico)[11:21])/100
                            enc_ant = int(self.encerrantes[bico]['encerrante'])/100
                            frentista = self.encerrantes[bico]['frentista']
                            qtd = encerrante - enc_ant
                            log = loggers("automacao").info(msg=f"quantiade de abastecimento {qtd}",prefix="[Gravando]")
                            preco = 0
                            produto = ""                            
                            if qtd > -0.01:
                                bico_banco = Bicos.objects.filter(bico=bico)
                                ultimo_enc = bico_banco[0].encerrante
                                ultimo_enc = 0
                                bico_produto = self.bico(bico)
                                produto = bico_produto
                                log = loggers("automacao").info(msg=f" produto = {produto}",prefix="[Gravando]")
                                print(self.bicos_atualizados)
                                log = loggers("automacao").info(msg=f" bicos_atualizados = {self.bicos_atualizados}",prefix="[Gravando]")
                                if bico in self.bicos_atualizados:    
                                    log = loggers("automacao").info(msg=f" bicos_atualizados  preco = {self.bicos_atualizados[bicos]['preco']}",prefix="[Gravando]")                            
                                    preco = (int(self.bicos_atualizados[bico]['preco']))/1000
                                    tipo_chave = self.bicos_atualizados[bico]['tipo']
                                    log = loggers("automacao").info(msg=f" preco = {preco}",prefix="[Gravando]")
                                    log = loggers("automacao").info(msg=f" tipo de chave = {tipo_chave}",prefix="[Gravando]")
                                    for x in bico:
                                        print(x)
                                        log = loggers("automacao").info(msg=f" bico = {x}",prefix="[Gravando]")
                                        if x in self.bicos_atualizados:
                                            self.bicos_atualizados.pop(x)
                                            
                                else:
                                    produto_preco = self.produto(bico_produto, tipo_chave)
                                    log = loggers("automacao").info(msg=f" preco ** = {produto_preco}",prefix="[Gravando]")
                                    preco = (int(produto_preco))/1000
                                    log = loggers("automacao").info(msg=f" preco = {preco}",prefix="[Gravando]")

                                if ultimo_enc == 0.00:
                                    bico_banco.update(encerrante=encerrante)
                                    log = loggers("automacao").info(msg=f" gravando no banco o encerrante {encerrante}",prefix="[Gravando]")
                                elif ultimo_enc < enc_ant:
                                    log = loggers("automacao").info(msg=f" diferenca {enc_ant}  {ultimo_enc}",prefix="[Gravando]")
                                    dif = int(enc_ant) - int(ultimo_enc)
                                    if dif > 0.1:
                                        produto_preco = self.produto(bico_produto, self.tipo_default)
                                        log = loggers("automacao").info(msg=f" produto preco {produto_preco}",prefix="[Gravando]") 
                                        preco_padrao = (int(produto_preco))/1000
                                        total_padrao = dif * preco_padrao
                                        abastecimento = Abast.objects.create(bico=bicos,cartao="Nao Identificado",produto=produto,valor=preco_padrao,enc_ini=ultimo_enc,enc_fim=enc_ant,quantidade=dif,total=total_padrao,tipo = self.tipo_default) 
                                        bico_banco.update(encerrante=enc_ant)
                                        print(f" abast nao identificado bico {bico} quantidade {dif}  preço {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}")
                                        log = loggers("automacao").info(msg=f" abast nao identificado bico {bicos} quantidade {dif}  preço {preco_padrao} valor abastecido {total_padrao}  frentista {frentista}",prefix="[Gravando]")
                                total = qtd * preco
                                abastecimento = Abast.objects.create(bico=bico,cartao=frentista,produto=produto,valor=preco,enc_ini=enc_ant,enc_fim=encerrante,quantidade=qtd,total=total,tipo = tipo_chave)
                                bico_banco.update(encerrante=encerrante)
                                print(f"bico {bico} quantidade {qtd}  preço {preco} valor abastecido {total}  frentista {frentista}")
                                log = loggers("automacao").info(msg=f"bico {bico} quantidade {qtd}  preço {preco} valor abastecido {total}  frentista {frentista}",prefix="[Gravando]")
                            else:
                                print('abastecimento zerado')
                                log = loggers("automacao").info(msg='abastecimento zerado',prefix="[Gravando]")
                            self.bicos_abastecendo.pop(bico)
        except Exception as e:
            
            track = traceback.format_exc()
            print(e)
            print('erro ao gravar no banco de dados o abastecimento')
            log = loggers("automacao").info(msg=track,prefix="[Gravando]")
            log = loggers("automacao").info(msg='erro ao gravar no banco de dados o abastecimento',prefix="[Gravando]")
            
            
    def setDefault(self):
        try:
            tipo_chave = self.tipo_default
            if tipo_chave > 0:
                if len(self.bicos_atualizados) > 0:
                        codigo = ""
                        for x in self.bicos_atualizados:
                            codigo = x
                            break

                        status = self.status()
                        status = status[7:(len(status)-3)] 
                        log = loggers("automacao").info(msg=f" status = {status}",prefix="[Default]")
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
                                
                            self.bicos_atualizados.pop(codigo)
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
            track = traceback.format_exc()
            print(track)
            print(e)
            print('erro ao setar o preco padrao')        
            log = loggers("automacao").info(msg=track,prefix="[Default]")  
            log = loggers("automacao").info(msg='erro ao setar o preco padrao',prefix="[Default]")
            
            

    def ler_identificador(self):
        self.set_status()
        while True:
            config = Config.objects.all().first()
            if config.automacao_ativo:
                self.verificaChave()            
                time.sleep(self.tempo_cmd)
                
                self.gravaAbastecimento()
                time.sleep(self.tempo_cmd)
                
                self.setDefault()            
                time.sleep(self.tempo_cmd)
            else:
                break