from arpa import ARPA
from datetime import date, timedelta, datetime
import time


class EncerrarOSRPA(ARPA):

    def trabalhar(self):
        while True:

                # self.clicar("Filtrar", 1)
                # self.clicar("Excluir", 1)
                # self.clicar("Criar Filtro", 1)
                # self.clicar("Nome do filtro", .5)
                # self.escrever("Data", .5)
                # self.clicar("Expressão", .5)yde
                # self.clicar("Expressão de filtro", .5)

                # # self.escrever(
                # #     f'TJ_DTMPINI > ctod("{(datetime.date.today() - timedelta(days=1)).strftime('%Y%m%d')}") '
                # #     f' .AND. TJ_SERVICO = "000018"'
                # #     , .5)

                # self.clicar("Adicionar filtro", .5)
                # self.clicar("Salvar filtro", 1)
                # self.teclar('up', .5)
                # self.teclar('space', 1)
                # self.clicar("Aplicar Filtro", 1)

                # while True:

                #     if self.clicar("Clicar amarelo", 1, (255, 253, 220)):
                #         print(f"Trabalho finalizado ")
                #         break

                    self.clicar("Outras opções", 2)
                    self.clicar("Cancelar", 2)
                    self.clicar("Confirmar Cancelamento", 3)
                    self.escrever("Cancelar", 3)
                    self.clicar("Confirmar", 1)
                    self.clicar("Confirmar", 5)
                    self.recoletar()

        # agora = datetime.now()
        # hora_alvo = datetime.now().replace(hour=2, minute=0)+ timedelta(days=1)
        # segundos_espera = (hora_alvo - agora).total_seconds()
        # print(f"Aguardando até {hora_alvo.strftime('%Y-%m-%d %H:%M:%S')} para reiniciar o processo.")
        # time.sleep(segundos_espera)
        # print("Executando o RPA...")


if __name__ == '__main__':

        rpa = EncerrarOSRPA()
        rpa.iniciar()








