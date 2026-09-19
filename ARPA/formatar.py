''' Converte a planilha exportada (do Protheus / Excel) para o formato que o robô lê:

      - separador vírgula, todos os campos entre aspas (as colunas vazias viram "")
      - números no formato americano:  2.306,67  ->  2,306.67
      - codificação UTF-8

    Uso:  python formatar.py "planilha exportada.csv" [saida.csv]

    Sem o segundo parâmetro, grava em titulos_formatados.csv.
'''
import csv
import re
import sys

SAIDA_PADRAO = "titulos_formatados.csv"
COLUNAS_ESPERADAS = 35
MARCAS = ('X', 'P', 'B')   # linhas que o robô já processou ganham uma coluna a mais

NUMERO_BR = re.compile(r"^-?\d{1,3}(?:\.\d{3})+(?:,\d+)?$|^-?\d+,\d+$")
TRACO = re.compile(r"^-\s*$")

# Para descobrir se a planilha já veio no formato americano (e não mexer nela).
# "2.306,67" só existe em BR; "2,306.67" e "800.00" só existem nos EUA.
# "2,076" é ambíguo (2076 em US, 2,076 em BR), por isso não conta para nenhum lado.
SO_BR = re.compile(r"^-?\d{1,3}(?:\.\d{3})+,\d+$|^-?\d+,\d{1,2}$|^-?\d+,\d{4,}$")
SO_US = re.compile(r"^-?\d{1,3}(?:,\d{3})+\.\d+$|^-?\d+\.\d{1,2}$|^-?\d+\.\d{4,}$")


def ler(caminho):
    ''' Lê o arquivo descobrindo sozinho a codificação e o separador. '''
    for codificacao in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(caminho, "r", encoding=codificacao, newline='') as fd:
                texto = fd.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise SystemExit(f"Não consegui ler {caminho} com nenhuma codificação conhecida.")

    linhas_cruas = [l for l in texto.splitlines() if l.strip()]
    if not linhas_cruas:
        raise SystemExit(f"{caminho} está vazio.")

    fora_de_aspas = re.sub(r'"[^"]*"', "", linhas_cruas[0])
    separador = ";" if fora_de_aspas.count(";") > fora_de_aspas.count(",") else ","

    # Uma linha física = um título, para os números baterem com os da planilha
    linhas = [next(csv.reader([l], delimiter=separador)) for l in linhas_cruas]

    return linhas, linhas_cruas, codificacao, separador


def detectar_estilo(linhas):
    ''' Descobre se os números da planilha estão em formato BR ou americano. '''
    br = us = 0
    for linha in linhas:
        for campo in linha:
            campo = campo.strip()
            if SO_BR.match(campo):
                br += 1
            elif SO_US.match(campo):
                us += 1

    return "us" if us > br else "br"


def converter(campo, estilo):
    ''' Número no formato brasileiro vira americano; o resto passa intacto. '''
    nu = campo.strip()

    if TRACO.match(nu):            # " -   " do Excel quer dizer zero
        return "0"

    if estilo == "us":             # já está formatada: não mexe nos números
        return campo

    if not NUMERO_BR.match(nu):    # datas, CNPJ, número do título, texto: não mexe
        return campo

    negativo = nu.startswith("-")
    inteiro, _, decimais = nu.lstrip("-").partition(",")
    inteiro = f"{int(inteiro.replace('.', '')):,}"
    americano = f"{inteiro}.{decimais}" if decimais else inteiro

    return f"  {'-' if negativo else ''}{americano} "


def conferir_colunas(linhas):
    ''' O erro mais comum: apagar as colunas vazias da planilha. '''
    erradas = []
    for n, campos in enumerate(linhas, 1):
        esperado = COLUNAS_ESPERADAS + (1 if campos and campos[0] in MARCAS else 0)
        if len(campos) != esperado:
            erradas.append((n, len(campos), esperado))

    if erradas:
        print(f"\n!! {len(erradas)} linha(s) com número de colunas errado:\n")
        for n, achou, esperado in erradas[:10]:
            print(f"   linha {n}: {achou} colunas (esperado {esperado})")
        if len(erradas) > 10:
            print(f"   ... e mais {len(erradas) - 10}")
        print("\n   Quase sempre é porque as colunas vazias foram apagadas na planilha.")
        print("   Exporte de novo SEM apagar nenhuma coluna e rode este script outra vez.")
        raise SystemExit(1)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)

    entrada = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else SAIDA_PADRAO

    linhas, linhas_cruas, codificacao, separador = ler(entrada)
    print(f"Lendo {entrada}")
    print(f"   codificação: {codificacao} | separador: {separador!r} | linhas: {len(linhas)}")

    abertas = [n for n, l in enumerate(linhas_cruas, 1) if l.count('"') % 2]
    if abertas:
        print(f"\n!! Aspas não fechadas na(s) linha(s): {abertas[:10]}")
        print("   Reexporte a planilha; o arquivo está corrompido.")
        raise SystemExit(1)

    conferir_colunas(linhas)

    estilo = detectar_estilo(linhas)
    print(f"   números: formato {'americano (já formatada)' if estilo == 'us' else 'brasileiro'}")

    formatadas = [[converter(campo, estilo) for campo in linha] for linha in linhas]
    convertidos = sum(1 for a, b in zip(linhas, formatadas)
                      for x, y in zip(a, b) if x != y)

    with open(saida, "w", encoding="utf-8", newline='') as fd:
        csv.writer(fd, quoting=csv.QUOTE_ALL).writerows(formatadas)

    print(f"\nOK: {len(formatadas)} linhas gravadas em {saida}")
    print(f"    {convertidos} número(s) convertido(s) para o formato americano")
    print(f"\nConfira agora com:  python test.py {saida}")


if __name__ == '__main__':
    main()
