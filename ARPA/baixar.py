import csv
from arpa import ARPA

class BaixarTituloRPA(ARPA):
    def trabalhar(self):
        if self.coletando:
            print("--- COLETA INICIAL DOS STATUS ---")
            print("Deixe os status visíveis na tela para recortar o Verde, Vermelho e Cinza.")
            self.clicar("Status Verde", 1, esperar_pixel=lambda p: p[1] > p[0] + 30 and p[1] > p[2] + 30 and p[1] > 100)
            self.clicar("Status Vermelho", 1, esperar_pixel=lambda p: p[0] > p[1] + 30 and p[0] > p[2] + 30 and p[0] > 100)
            self.clicar("Status Cinza", 1)
            print("--- COLETA DOS STATUS CONCLUÍDA ---")

        with open("titulos2026.csv", "r", encoding="utf-8") as fd:
            linhas = list(csv.reader(fd))
            
        for n, campos in enumerate(linhas, 1):
            if not campos or campos[0] in ('X', 'P', 'B'):
                print(f"Linha {n} já processada (marcada com {campos[0]}). Pulando...")
                continue
                
            print(n, campos)

            # if n not in (71, 1620, 1736):
            #     continue

            self.clicar("Filtrar", 5)
            self.clicar("Excluir", 8)
            self.clicar("Criar Filtro", 5)
            self.clicar("Nome do filtro", 5)
            self.escrever(f"Filtro do RPA [ {n} ]", 5)
            self.clicar("Expressão", 5)
            self.clicar("Expressão de filtro", 5)

            self.escrever(
                f'E1_FILIAL== "{campos[0]}"'
                # f' .AND. E1_LOJA == "{campos[9]}"'
                f' .AND. E1_PREFIXO == "{campos[2]}"'
                f' .AND. alltrim(E1_NUM) == "{campos[3]}"'
                f' .AND. alltrim(E1_TIPO) == "{campos[5]}"'
                f' .AND. E1_VALOR == {campos[18].replace(",", "").strip()}'
                , .5)

                #001002" .AND. E1_NUM== "000076195" .AND. E1_VALOR == 820.49 .AND. E1_TIPO== "NF "

            self.clicar("Adicionar filtro", 4)
            self.clicar("Salvar filtro", 5)
            self.clicar('Clique na Barra', 5)
            self.teclar('end', 1)
            self.clicar('Marcar Filtro', 5)
            self.clicar("Aplicar filtro", 10)

            # Verifica se o título ficou com o status Verde
            # Se estiver coletando, pula essa checagem para não pedir o recorte de novo
            if self.coletando:
                status_verde = True
            else:
                status_verde = self.clicar(
                    "Status Verde", 3, 
                    esperar_pixel=lambda p: p[1] > p[0] + 30 and p[1] > p[2] + 30 and p[1] > 100
                )
            
            if not status_verde:
                # Verifica se o título ficou com o status Vermelho
                status_vermelho = self.clicar(
                    "Status Vermelho", 1, 
                    esperar_pixel=lambda p: p[0] > p[1] + 30 and p[0] > p[2] + 30 and p[0] > 100
                )
                
                if status_vermelho:
                    campos.insert(0, 'B')
                else:
                    # Verifica se ficou Cinza
                    status_cinza = self.clicar("Status Cinza", 1)
                    if status_cinza:
                        campos.insert(0, 'C') # Letra para cinza
                    else:
                        # Se NÃO for verde, nem vermelho, nem cinza, marca com 'P'
                        campos.insert(0, 'P')
                    
                with open("titulos2026.csv", "w", encoding="utf-8", newline='') as fd_out:
                    csv.writer(fd_out, quoting=csv.QUOTE_ALL).writerows(linhas)
                self.recoletar()
                continue

            self.clicar("Outras Acoes", 5)
            self.clicar("Baixa Manual", 5)

            # self.clicar("Cancelar baixa", 5)
            # self.clicar("Confirmar", .5)

            self.clicar("Baixar", 2)

            self.clicar("Clicar Mot Baixa", 5)
            self.clicar("Selecionar PERDA CLI", 5)
            self.clicar("Hist Baixa", 5)
            self.escrever('PERDA CLIENTE 2026', 5)
            self.clicar("Salvar Baixa", 6)

            self.recoletar()

            # Marca a linha com 'X' na primeira coluna
            campos.insert(0, 'X')

            # Salva o progresso no próprio arquivo CSV
            with open("titulos2026.csv", "w", encoding="utf-8", newline='') as fd_out:
                csv.writer(fd_out, quoting=csv.QUOTE_ALL).writerows(linhas)

if __name__ == '__main__':
    rpa = BaixarTituloRPA()
    rpa.iniciar()
