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
        self.config = Config.objects.all().first()
        self.tempo_cmd = float(self.config.tempo_cmd)        
        self.bicos_atualizados = {}
        self.bicos_abastecendo = []
        self.estado_rel = []    
        self.encerrantes = {}  
        log = loggers("automacao").info(msg=f" bicos {bicos}",prefix="[Gravando]")
        log = loggers("automacao").info(msg=f" produtos {produtos}",prefix="[Gravando]")
        log = loggers("automacao").info(msg=f" chaves {chaves}",prefix="[Gravando]")
        log = loggers("automacao").info(msg=f" tipos {tipos}",prefix="[Gravando]")
        
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
        log = loggers("automacao").info(msg=f'comando = {string} resposta = {comando}',prefix="[TROCA_PRECO]")
        if comando == f"""U{bico}""":
            return True
        else:
            comando = self.comando(string)
            print(comando)
            log = loggers("automacao").info(msg=f'comando = {string} resposta = {comando}',prefix="[TROCA_PRECO]")
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
        
    
    def ver_abast(self):
        comando = self.comando('(?V95)', check=False)
        return comando
    

    def tem_numeros(self,string):
        return any(char.isdigit() for char in string)


    def encerrante(self,bico):
        comando = self.comando(f'&T{bico}l')
        log = loggers("automacao").info(msg=f'comando = &T{bico}l resposta = {comando}',prefix="[ENCERRANTE]")
        if len(comando) == 16:
            comando  = comando[4:14]
            log = loggers("automacao").info(msg=f'encerrante =  {comando}',prefix="[ENCERRANTE]")
        else:
            comando = self.comando(f'&T{bico}l')
            log = loggers("automacao").info(msg=f'comando = &T{bico}l resposta = {comando}',prefix="[ENCERRANTE]")
            if len(comando) == 16:
                comando  = comando[4:14]
                log = loggers("automacao").info(msg=f'encerrante =  {comando}',prefix="[ENCERRANTE]")
            else:
                comando = 0
        return comando

    def verificaChave(self):
        try:
            comando = self.comando('?A')
            if len(comando) == 35:
                log = loggers("automacao").info(msg=f" resposta comando {comando}",prefix="[chave]")
                chave = comando[1:17]
                log = loggers("automacao").info(msg=f" chave {chave}",prefix="[chave]")
                bico = comando[17:19]
                log = loggers("automacao").info(msg=f" bico {bico}",prefix="[chave]")
                bicos = self.montaHexPerso(int(bico, 16))
                log = loggers("automacao").info(msg=f" bicos {bicos}",prefix="[chave]")
                ver_chave = self.chave_preco(chave)
                if ver_chave:
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
                                    log = loggers("automacao").info(msg=resposta,prefix="[Chave]") 
                                    self.bicos_atualizados.update({bicos_b:{'preco':produto_preco,'tipo':tipo_chave}})
                        time.sleep(self.tempo_cmd)
                    self.incrementa_identfid()
                else:
                    print(chave)
                    log = loggers("automacao").info(msg=chave,prefix="[Chave]")
                    bico_cartao = comando[17:19]
                    log = loggers("automacao").info(msg=f" bico cartao {bico_cartao}",prefix="[chave]")
                    print(self.salva_cartao(chave,bico_cartao))
                    self.incrementa_identfid()
            elif comando != "0":
                print(comando)
                log = loggers("automacao").info(msg=f" Resposta {comando}   rejeitada",prefix="[chave]")
                self.tcp.close()
        except Exception as e:
            track = traceback.format_exc()
            log = loggers("automacao").info(msg=track,prefix="[Chave]") 
            print(e)
            print('erro na identificacao do chip')
            log = loggers("automacao").info(msg='erro na identificacao do chip',prefix="[Chave]") 
            log = loggers("automacao").info(msg=e,prefix="[Chave]") 
                    
    def gravaAbastecimento(self):
        try:
            tipo_chave = self.tipo_default

            status = self.status()
            tipo_status = self.tem_numeros(status)
            if tipo_status:
                tamanho = 32
                status = status[1:33]
            else:
                tamanho = 48
                status = status[1::]

            if len(status) == tamanho:                
                for i, c in enumerate(status):
                    if c == "A" and self.estado_rel[i] != "G":
                        self.estado_rel[i] = "G"
                        bicos = self.montaHexLado(i)
                        log = loggers("automacao").info(msg=f" bicos = {bicos}",prefix="[Gravando]") 
                        abast = self.ver_abast()
                        log = loggers("automacao").info(msg=f" abast comando = {abast} tamanho comando {len(abast)}",prefix="[Gravando]") 
                        if len(abast) >= 18:
                            qtd = len(abast)/18    
                            log = loggers("automacao").info(msg=f" quantidade de abastecimentos = {qtd}",prefix="[Gravando]")        
                            for x in range(int(qtd)):
                                abast_andamento = abast[(x*18):((x*18)+18)]
                                log = loggers("automacao").info(msg=f" abastecimento em andamento = {abast_andamento}",prefix="[Gravando]")
                                bico_andamento = abast_andamento[0:2]
                                frentista = abast_andamento[2:18]                            
                                for bicos_b in bicos:
                                    if bicos_b in self.bicos:
                                        if bicos_b == bico_andamento:
                                            encerrante = self.encerrante(bicos_b)
                                            log = loggers("automacao").info(msg=f" atualizando encerrante = {encerrante}  do bico {bicos_b}",prefix="[Gravando]")
                                            if bicos_b in self.encerrantes:
                                                self.encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                            else:
                                                self.encerrantes.update({bicos_b:{'encerrante':encerrante,'frentista':frentista}})
                                            self.bicos_abastecendo.append(bicos_b)
                                            log = loggers("automacao").info(msg=f" bicos_abastecendo = {self.bicos_abastecendo}",prefix="[Gravando]")
                                            print(encerrante)  
                                    else:
                                        log = loggers("automacao").info(msg=f" bicos nao configurado = {bicos_b}",prefix="[Gravando]")
                    elif c == "B" and self.estado_rel[i] == "G":
                        self.estado_rel[i] = "B"
                        bico = self.montaHexLado(i)
                        print(self.bicos_abastecendo)
                        for t, bicos in enumerate(self.bicos_abastecendo):
                            print(bicos)
                            if bicos in bico :
                                log = loggers("automacao").info(msg=f" bico = {bicos}",prefix="[Gravando]") 
                                log = loggers("automacao").info(msg=f" encerrante ** = {self.encerrante(bicos)}",prefix="[Gravando]") 
                                log = loggers("automacao").info(msg=f" enc_ant ** = {self.encerrantes[bicos]['encerrante']}",prefix="[Gravando]") 
                                encerrante = int(self.encerrante(bicos))/100
                                enc_ant = int(self.encerrantes[bicos]['encerrante'])/100
                                frentista = self.encerrantes[bicos]['frentista']
                                qtd = encerrante - enc_ant
                                preco = 0
                                produto = ""       
                                log = loggers("automacao").info(msg=f" encerrante = {encerrante}",prefix="[Gravando]")                     
                                log = loggers("automacao").info(msg=f" encerrante anterior= {enc_ant}",prefix="[Gravando]")                     
                                log = loggers("automacao").info(msg=f" frentista = {frentista}",prefix="[Gravando]")                     
                                log = loggers("automacao").info(msg=f" quantidade = {qtd}",prefix="[Gravando]")                     
                                if qtd > 0.01:
                                    bico_banco = Bicos.objects.filter(bico=bicos)
                                    ultimo_enc = bico_banco[0].encerrante
                                    bico_produto = self.bico(bicos)
                                    produto = bico_produto
                                    log = loggers("automacao").info(msg=f" produto = {produto}",prefix="[Gravando]")
                                    print(self.bicos_atualizados)
                                    log = loggers("automacao").info(msg=f" bicos_atualizados = {self.bicos_atualizados}",prefix="[Gravando]")
                                    if bicos in self.bicos_atualizados:                                
                                        log = loggers("automacao").info(msg=f" bicos_atualizados  preco = {self.bicos_atualizados[bicos]['preco']}",prefix="[Gravando]")
                                        preco = (int(self.bicos_atualizados[bicos]['preco']))/1000
                                        tipo_chave = self.bicos_atualizados[bicos]['tipo']
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
            track = traceback.format_exc()
            print(e)
            print('erro ao gravar no banco de dados o abastecimento')
            log = loggers("automacao").info(msg=e,prefix="[Gravando]")
            log = loggers("automacao").info(msg=track,prefix="[Gravando]")
            log = loggers("automacao").info(msg='erro ao gravar no banco de dados o abastecimento',prefix="[Gravando]")
            
            
    def setDefault(self):
        try:
            tipo_chave = self.tipo_default
            if tipo_chave > 0:
                status = self.status()
                state_cbc = self.state_chave_preco
                tipo_status = self.tem_numeros(status)
                if tipo_status:
                    tamanho = 32
                    status = status[1:33]
                else:
                    tamanho = 48
                    status = status[1::]
                    
                if len(status) == tamanho and status != state_cbc and (len(state_cbc) == tamanho or state_cbc == ''):        
                    log = loggers("automacao").info(msg=f" tipo chave padrao = {tipo_chave}",prefix="[Default]")
                    print("////////")
                    print(status)
                    log = loggers("automacao").info(msg=status,prefix="[Default]")
                    print(state_cbc)
                    log = loggers("automacao").info(msg=state_cbc,prefix="[Default]")
                    print("////////")
                    if state_cbc:
                        for i, c in enumerate(status):
                            if c != state_cbc[i] and c == 'B':
                                codigos = self.montaHexLado(i)
                                for a in codigos:

                                    status_troca = status
                                    if len(status_troca) > tamanho:
                                        status_troca =status  
                                    else:
                                        status_troca = False
                                        
                                    if a in self.bicos:
                                        bico_produto = self.bico(a)
                                        if bico_produto:
                                            produto_preco = self.produto(
                                                bico_produto, tipo_chave)
                                            if produto_preco and status_troca:
                                                if status_troca[1] == "B":
                                                    troca_preco = self.troca_preco(
                                                        produto_preco, a)
                                                    resposta = f"""U{a} preco = {produto_preco} trocado? {troca_preco}"""    
                                                    
                                                    log = loggers("automacao").info(msg=resposta,prefix="[Default]")
                                                else:
                                                    print("status diferente")
                                                    print(status_troca[i])                                            
                                                time.sleep(self.tempo_cmd)
                                            elif produto_preco:
                                                troca_preco = self.troca_preco(
                                                        produto_preco, a)
                                                resposta = f"""U{a} preco = {produto_preco} trocado? {troca_preco}"""  
                                                log = loggers("automacao").info(msg=resposta,prefix="[Default]")
                                                time.sleep(self.tempo_cmd)
                                            print('Preco padrao setado')
                                            log = loggers("automacao").info(msg='Preco padrao setado',prefix="[Default]")
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
                                                log = loggers("automacao").info(msg=resposta,prefix="[Default]")                   
                                                time.sleep(self.tempo_cmd)
                                            print('Preco padrao setado')
                                            log = loggers("automacao").info(msg='Preco padrao setado',prefix="[Default]")

                    self.state_chave_preco = status
        except Exception as e:
            print(e)
            track = traceback.format_exc()
            print('erro ao setar o preco padrao') 
            log = loggers("automacao").info(msg=track,prefix="[Default]")         
            log = loggers("automacao").info(msg=e,prefix="[Default]")  
            log = loggers("automacao").info(msg='erro ao setar o preco padrao',prefix="[Default]")
            
            
            
        
    def ler_identificador(self):  
        status = self.status()
        tipo_status = self.tem_numeros(status)
        if tipo_status:
            status = status[1:33]
        else:
            status = status[1::]       
        for c in status:
            self.estado_rel.append(c)
        
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
                self.tcp.close()
                break
