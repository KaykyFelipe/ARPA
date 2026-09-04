import csv
import pyodbc
import datetime

# https://learn.microsoft.com/en-us/sql/connect/python/pyodbc/step-3-proof-of-concept-connecting-to-sql-using-pyodbc?view=sql-server-ver16

SERVER = '10.117.41.2,54300\\PROTHEUS'  # 'localhost,1433\\PROTHEUS'
DATABASE = 'PROTHEUS_PROD_ATIVA'
DATABASE_HOMOL = 'PROTHEUS_HML_ATIVA'
DATABASE_HOMOLFIS = 'PROTHEUS_HOMOL_FIS_ATIVA'
USERNAME = 'api.ativa'  # 'sa'
PASSWORD = 'wVQECaWtEuUoobqpiXWosk9OfG8MpWOP'
#PASSWORD = input('senha:')

class DataBase():
    def __init__(self, ambiente):
        self.conn = None
        self.cur = None
        self.ambiente = ambiente
        self.connect()

    def connect(self):
        try:
            database = DATABASE if self.ambiente == 'produção' else DATABASE_HOMOL
            connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={database};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes;'
            self.conn = pyodbc.connect(connectionString)
            # print("Conectado no banco de dados com sucesso!")
            self.cur = self.conn.cursor()
        except Exception:
            # print("Erro ao conectar no banco de dados MS SQL Server.")
            self.cur = None
            self.conn = None
            raise

    def commit_close(self):
        self.conn.commit()

    def rollback_close(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()
        self.cur = None
        self.conn = None

    def __del__(self):
        self.rollback_close()


if __name__ == '__main__':
    db = DataBase('!produção')

    # db.cur.execute("update fwp010 set fwp_txtass = ? where fwp_txtass like '%vencimento%'",
    #                [b'Ativa Loca\xe7\xe3o | Informativo de vencimento pr\xf3ximo'])
    # db.cur.execute("update fwp010 set fwp_txtass = ? where fwp_txtass like '%vencido%'",
    #                [b'Ativa Loca\xe7\xe3o | Informativo de t\xedtulo vencido'])
    # db.conn.commit()
    # db.cur.execute("select fwp_txtass from fwp010")
    # print(db.cur.fetchall())
    # vaca

    with open('titulos.csv') as titulos_csv:
        dialect = 'excel-tab'
        titulos_csv.seek(0)
        titulos = csv.reader(titulos_csv, dialect)
        for n, titulo in enumerate(titulos, 1):
            titulo = [campo.strip() for campo in titulo]
            db.cur.execute(
                "select se2.e2_baixa as data_baixa, se2.e2_saldo as saldo\n"
                "from se2010 se2\n"
                "where se2.d_e_l_e_t_ <> '*'\n"
                "and trim(se2.e2_prefixo) = ?\n"
                "and trim(se2.e2_num) = ?\n"
                "and trim(se2.e2_parcela) = ?\n"
                "and trim(se2.e2_tipo) = ?\n"
                "and trim(se2.e2_fornece) = ?\n"
                "and trim(se2.e2_loja) = ?\n"
                "and se2.e2_saldo = 0\n"  # = ?\n"
                "and se2.e2_valor = ?\n"
                ,
                titulo[2], titulo[3], titulo[4], titulo[5], titulo[0], titulo[1], float(titulo[7]),  # float(titulo[6]), float(titulo[7]),
            )
            dados = db.cur.fetchall()
            qtd = len(dados)
            if qtd != 0:
                print('.', end='', flush=True)
            else:
                print()
                print("{n}\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}".format(*titulo, dados, qtd, n=n))
