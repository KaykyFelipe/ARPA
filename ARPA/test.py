''' Validação da planilha: monta a expressão do filtro e imprime, sem abrir o Protheus
    nem pedir a coleta de cliques.

    Uso:  python test.py [arquivo.csv] [quantidade de linhas]
'''
import csv
import re
import sys

ARQUIVO_PADRAO = "103baixas.csv"
COLUNAS_ESPERADAS = 35

# Índices das colunas usadas no filtro (mesmos do baixar.py)
FILIAL, PREFIXO, NUM, TIPO, VALOR = 0, 2, 3, 5, 18

NUMERO = re.compile(r"^-?\d+(?:[.,]\d+)*$")


def detectar_formato(caminho):
    ''' Descobre a codificação e o separador (`,´ ou `;´) do CSV. '''
    for codificacao in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(caminho, "r", encoding=codificacao, newline='') as fd:
                texto = fd.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"Não consegui ler {caminho} com nenhuma codificação conhecida.")

    primeira = texto.splitlines()[0] if texto.splitlines() else ""
    fora_de_aspas = re.sub(r'"[^"]*"', "", primeira)
    separador = ";" if fora_de_aspas.count(";") > fora_de_aspas.count(",") else ","

    return texto, codificacao, separador


def normalizar_valor(texto):
    ''' " 2.306,67 " (BR) ou " 2,306.67 " (EUA) -> "2306.67". Devolve None se não for número. '''
    nu = texto.strip().replace("\xa0", "").replace(" ", "")
    if nu in ("", "-", "0"):
        return "0"

    negativo = nu.startswith("-")
    nu = nu.lstrip("+-")

    if not NUMERO.match(nu):
        return None

    if "." in nu and "," in nu:
        # O separador que aparece por último é o decimal
        decimal = "." if nu.rfind(".") > nu.rfind(",") else ","
        nu = nu.replace("," if decimal == "." else ".", "").replace(decimal, ".")
    elif "." in nu or "," in nu:
        separador = "." if "." in nu else ","
        casas = len(nu.rsplit(separador, 1)[1])
        # 3 casas depois do separador = milhar (1,653 / 1.653); o resto é decimal
        if nu.count(separador) > 1 or casas == 3:
            nu = nu.replace(separador, "")
        else:
            nu = nu.replace(separador, ".")

    return f"-{nu}" if negativo else nu


def montar_expressao(campos):
    ''' Mesma expressão que o baixar.py digita no filtro. '''
    return (
        f'E1_FILIAL== "{campos[FILIAL]}"'
        f' .AND. E1_PREFIXO == "{campos[PREFIXO]}"'
        f' .AND. alltrim(E1_NUM) == "{campos[NUM]}"'
        f' .AND. alltrim(E1_TIPO) == "{campos[TIPO]}"'
        f' .AND. E1_VALOR == {normalizar_valor(campos[VALOR])}'
    )


def conferir(campos, linha_crua):
    ''' Lista os problemas encontrados na linha. '''
    problemas = []

    if linha_crua.count('"') % 2:
        problemas.append("aspas não fechadas (o CSV vai juntar esta linha com a próxima)")

    if len(campos) != COLUNAS_ESPERADAS:
        problemas.append(f"{len(campos)} colunas, esperado {COLUNAS_ESPERADAS} "
                         "(colunas vazias removidas? os índices saem trocados)")

    if len(campos) <= max(FILIAL, PREFIXO, NUM, TIPO, VALOR):
        problemas.append("linha curta demais para montar o filtro")
        return problemas

    if not re.fullmatch(r"\d{4,6}", campos[FILIAL].strip()):
        problemas.append(f"FILIAL suspeita: {campos[FILIAL]!r}")

    if not re.fullmatch(r"[A-Z]{2,3}", campos[TIPO].strip()):
        problemas.append(f"TIPO suspeito: {campos[TIPO]!r} (esperado NF, FT, TF, CC...)")

    if normalizar_valor(campos[VALOR]) is None:
        problemas.append(f"VALOR não é número: {campos[VALOR]!r}")

    return problemas


def main():
    arquivo = sys.argv[1] if len(sys.argv) > 1 else ARQUIVO_PADRAO
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else None

    texto, codificacao, separador = detectar_formato(arquivo)
    print(f'Arquivo: {arquivo} | codificação: {codificacao} | separador: {separador!r}\n')

    # Uma linha física = um registro, para os números baterem com os da planilha
    linhas_cruas = texto.splitlines()
    ok = com_problema = 0

    for n, linha_crua in enumerate(linhas_cruas, 1):
        if limite and n > limite:
            break
        if not linha_crua.strip():
            continue

        campos = next(csv.reader([linha_crua], delimiter=separador))

        if campos and campos[0] in ('X', 'P', 'B'):
            print(f"[{n:4}] já processada ({campos[0]}) — pulando")
            continue

        problemas = conferir(campos, linha_crua)

        print(f"[{n:4}] {len(campos)} colunas")
        if len(campos) > max(FILIAL, PREFIXO, NUM, TIPO, VALOR):
            print(f"       filial={campos[FILIAL]!r} prefixo={campos[PREFIXO]!r} "
                  f"num={campos[NUM]!r} tipo={campos[TIPO]!r} valor={campos[VALOR]!r}")
            print(f"       {montar_expressao(campos)}")

        if problemas:
            com_problema += 1
            for problema in problemas:
                print(f"       !! {problema}")
        else:
            ok += 1
        print()

    print(f"--- {ok} linha(s) OK, {com_problema} com problema ---")


if __name__ == '__main__':
    main()
