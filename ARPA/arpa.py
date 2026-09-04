import pyautogui
import pymsgbox
import time
import json
import sys


class ARPA():
    ''' Ativa Robot Processing Automate '''
    coletando = False
    posicoes = {}

    def clicar(self, local, segundos_apos, esperar_pixel=None):
        while self.coletando or local not in self.posicoes:
            resp = pymsgbox.confirm(
                f"Posicione o mouse em `{local}´ para clique automático em 3 segundos após clicar em ok...",
                buttons=['Ok', 'Cancelar'])
            if resp == 'Ok':
                time.sleep(3)
                p = pyautogui.position()
                self.posicoes[local] = p
                if not self.coletando:
                    self.gravar_cliques(perguntar=False)
                break
            elif local in self.posicoes:
                time.sleep(2)
                break

        p = self.posicoes[local]
        for i in (1, 2):
            pixel = tuple(pyautogui.pixel(*p))
            print(f'"{local}": {p} [{pixel} == {esperar_pixel}]')
            if not esperar_pixel:
                break
            if callable(esperar_pixel) and esperar_pixel(pixel):
                break
            if not callable(esperar_pixel) and pixel == esperar_pixel:
                break
            time.sleep(1)

        if esperar_pixel:
            if callable(esperar_pixel) and not esperar_pixel(pixel):
                return False
            if not callable(esperar_pixel) and pixel != esperar_pixel:
                return False

        pyautogui.click(p)
        self.esperar(segundos_apos)

        return True

    def gravar_cliques(self, perguntar=True):
        if perguntar:
            resp = pymsgbox.confirm("Você quer gravar os cliques?", title="Esperando resposta...", buttons=['Sim', 'Não'])
        if not perguntar or resp == 'Sim':
            with open("cliques.json", "w") as fd:
                json.dump(self.posicoes, fd, indent=4)

    def carregar_cliques(self):
        try:
            with open("cliques.json", "r") as fd:
                self.posicoes = json.load(fd)
        except Exception as e:
            print(e)
            pymsgbox.alert(f"Cliques não carregados!\n\n{e}", title="Problema!")


    def perguntar_se_quer_parar(self):
        resp = pymsgbox.confirm("Você quer parar?", title="Esperando resposta...", buttons=['Sim', 'Não'])
        if resp == 'Sim':
            sys.exit(0)

    def perguntar_se_quer_reprogramar_cliques(self):
        resp = pymsgbox.confirm("Você quer reprogramar os cliques?", title="Reprogramação de cliques", buttons=['Sim', 'Não'])
        self.coletando = resp == 'Sim'
        self.esperar(2)

    def esperar(self, segundos):
        while segundos > 0:
            p = pyautogui.position()
            if p[0] < 10:
                self.perguntar_se_quer_parar()
            else:
                time.sleep(.25)
                segundos -= .25

    def escrever(self, texto, segundos):
        print(f'Escrever: "{texto}"')
        pyautogui.write(texto, interval=0.05)
        self.esperar(segundos)

    def teclar(self, tecla, segundos):
        print(f'Teclar: "{tecla}"')
        pyautogui.press(tecla)
        self.esperar(segundos)

    def iniciar(self):
        self.carregar_cliques()
        self.perguntar_se_quer_reprogramar_cliques()
        self.trabalhar()
        pymsgbox.alert("Trabalho do RPA realizado!", title="Sucesso!")

    def recoletar(self):
        if self.coletando:
            self.gravar_cliques()
            self.perguntar_se_quer_parar()
            self.perguntar_se_quer_reprogramar_cliques()

    def trabalhar(self):
        pymsgbox.alert("Trabalho do RPA não implementado!", title="Problema!")
