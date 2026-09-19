
## Passo 1 — Exportar a planilha

Exporte os títulos normalmente e salve como **CSV**, do jeito que sair.

Não precisa arrumar nada à mão: não precisa trocar ponto e vírgula por vírgula, não
precisa mexer nos números, não precisa acertar acentuação. O passo 2 faz tudo isso.

Só não apague nem reordene colunas, e não apague linhas no meio.

Guarde o arquivo dentro da pasta `ARPA` do projeto.

## Passo 2 — Formatar

Abra o terminal na pasta `ARPA` e rode:

```
python formatar.py "planilha que você exportou.csv" 103baixas.csv
```

> As aspas no nome do arquivo são necessárias quando o nome tem espaços.

O script descobre sozinho a codificação e o separador (`;` ou `,`) e grava o arquivo
já no formato do robô. Você deve ver algo assim:

```
Lendo planilha que você exportou.csv
   codificação: cp1252 | separador: ';' | linhas: 103
   números: formato brasileiro

OK: 103 linhas gravadas em 103baixas.csv
    659 número(s) convertido(s) para o formato americano
```

O que ele faz:

| Antes (como sai do sistema) | Depois (como o robô precisa) |
|---|---|
| `001004;ATIVA;FAT;000047878;;NF` | `"001004","ATIVA","FAT","000047878","","NF"` |
| `2.306,67` | `2,306.67` |
| `-` (traço) | `0` |

Rodar o `formatar.py` duas vezes no mesmo arquivo não estraga nada: se ele perceber que
a planilha já está formatada, não mexe nos números.

## Passo 3 — Conferir antes de rodar o robô

**Não pule este passo.** Ele leva 2 segundos e evita dar baixa em título errado.

```
python test.py 103baixas.csv
```

O `test.py` não abre o Protheus, não mexe no mouse e não pede a coleta de cliques.
Ele só lê a planilha e mostra o filtro que o robô vai digitar em cada linha:

```
[   1] 35 colunas
       filial='001004' prefixo='FAT' num='000047878' tipo='NF' valor='  800.00 '
       E1_FILIAL== "001004" .AND. E1_PREFIXO == "FAT" .AND. alltrim(E1_NUM) == "000047878" .AND. alltrim(E1_TIPO) == "NF" .AND. E1_VALOR == 800.00

--- 103 linha(s) OK, 0 com problema ---
```

**Só continue se a última linha disser `0 com problema`.**

Confira também se faz sentido: `tipo` tem que ser `NF`, `FT`, `TF`, `CC`... e `valor`
tem que ser dinheiro, não data nem número de contrato.

Para ver só as primeiras linhas:

```
python test.py 103baixas.csv 5
```

## Passo 4 — Rodar o robô

O robô lê o arquivo cujo nome está escrito na **linha 15 do `baixar.py`**:

```python
with open("103baixas.csv", "r", encoding="utf-8") as fd:
```

O mais simples é sempre gravar a planilha formatada com esse mesmo nome
(`103baixas.csv`), como no passo 2. Se você quiser usar outro nome, precisa trocá-lo
em **três lugares** do `baixar.py`: linhas 15, 87 e 112 — senão o robô lê um arquivo e
grava o progresso em outro.

Aí é só rodar:

```
python baixar.py
```

---

## Como o robô marca o que já fez

O robô grava o progresso **na própria planilha**, escrevendo uma letra no começo da linha:

| Marca | Significa |
|---|---|
| `X` | Baixa feita com sucesso |
| `B` | Título ficou vermelho na tela (não foi baixado) |
| `P` | Título ficou cinza ou não foi encontrado (não foi baixado) |

Por isso:

- **Pode parar o robô no meio** (mouse no canto esquerdo da tela → "Você quer parar?").
  Ao rodar de novo, ele pula as linhas já marcadas e continua de onde parou.
- **Linha marcada fica com 36 colunas** em vez de 35 (a letra é uma coluna a mais).
  Isso é normal, o `test.py` entende e mostra `já processada (X) — pulando`.
- No fim, filtre a coluna A no Excel para ver o que ficou como `B` e `P` — esses
  precisam ser tratados à mão.

Como o arquivo guarda o progresso, **não formate de novo por cima dele no meio do
trabalho**: isso apaga as marcas e o robô vai tentar baixar tudo outra vez.

---

## Mensagens de erro e o que fazer

| Mensagem | O que houve | O que fazer |
|---|---|---|
| `29 colunas, esperado 35 (colunas vazias removidas?)` | Apagaram colunas vazias da planilha | Exporte de novo sem apagar coluna nenhuma |
| `aspas não fechadas` | O arquivo foi salvo/editado de um jeito que quebrou o CSV | Exporte de novo e rode o `formatar.py` |
| `TIPO suspeito: '101010001'` | As colunas estão deslocadas | Mesma coisa: colunas vazias faltando |
| `VALOR não é número: '06/05/2024 A 04/06/2024'` | As colunas estão deslocadas | Mesma coisa |
| `FILIAL suspeita` | A primeira coluna não é o código da filial | Confira se a planilha tem uma linha de cabeçalho — o robô não usa cabeçalho, apague essa linha |

---

## O que **não** fazer

- ❌ Apagar colunas vazias (é o erro nº 1).
- ❌ Abrir o CSV **já formatado** no Excel e salvar por cima: o Excel come os zeros à
  esquerda (`000047878` vira `47878`) e devolve os números para o formato brasileiro.
  Se precisar olhar o conteúdo, abra no Bloco de Notas, ou abra no Excel e **feche sem
  salvar**.
- ❌ Adicionar uma linha de cabeçalho: o robô trata a primeira linha como um título.
- ❌ Rodar o `formatar.py` por cima da planilha que o robô já começou a marcar.

---

## Referência: as colunas que o robô usa

| Coluna no Excel | Conteúdo | Exemplo |
|---|---|---|
| **A** | Filial | `001004` |
| **C** | Prefixo | `FAT` |
| **D** | Nº do título | `000047878` |
| **F** | Tipo | `NF` |
| **S** | Valor | `  800.00 ` |

As outras 30 colunas o robô não lê — mas **precisam continuar lá**, senão essas cinco
saem do lugar.
