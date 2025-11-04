import mysql.connector
from datetime import datetime, timedelta
from .financeiro import Financeiro


class EventosRepo:
    qtdLoteVen = 0

    def select_all(self, body):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = "SELECT * FROM EVENTOS"
        if body:
            script += f" WHERE id = {body['idEvento']}"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            linha = []

            while row:
                guests = self.select_guest(row[0])
                pendente = self.getPendente(row[0])
                LoteAtual = self.LoteAtual(row[0], ((row[4] - row[3]) + pendente))

                linha.append(
                    {
                        "id": row[0],
                        "Title": (row[1]),
                        "desc": row[2],
                        "info": row[12],
                        "QtdDisp": (row[3] - pendente),
                        "QtdTicket": row[4],
                        "DateEvent": row[5],
                        "DateFim": row[10],
                        "price": LoteAtual[1],
                        "banner": row[6],
                        "logo": row[7],
                        "instagram": row[8],
                        "youtube": row[9],
                        "guests": guests,
                        "Lote_Atual": LoteAtual[0],
                        "status": row[13],
                    }
                )
                row = cursor.fetchone()

        connectionDB.close()
        return linha

    def select_guest(self, id):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT NomeGuest, InstaGuest FROM GUESTS WHERE idEvento = {id}"
        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            linha = []

            while row:
                linha.append({"name": row[0], "instagram": (row[1])})
                row = cursor.fetchone()
        connectionDB.close()
        return linha

    def LoteAtual(self, idEvento, qtdVendida):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT NomeLote, price, DispQtd FROM LOTESEVENTOS WHERE idEvento = {idEvento} ORDER by OrderLote"
        with connectionDB.cursor(buffered=True) as cursor:
            linha = []
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                if row[2] >= qtdVendida:
                    connectionDB.close()
                    self.qtdLoteVen = qtdVendida
                    return row
                else:
                    qtdVendida -= row[2]
                    row = cursor.fetchone()
            return ["Esgotado", 0]

    def getPendente(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        dataAnt = datetime.now() - timedelta(minutes=20)
        script = f"SELECT COUNT(*) FROM TRANSACTIONS where idEvento = {idEvento} and ((dateTransaction >= '{dataAnt}' and status_pag = 'N') or status_pag = 'P')"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            result = cursor.fetchone()
            count = result[0]
        connectionDB.close()
        return count

    def select_mine(self, idUser):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT * FROM EVENTOS WHERE idUser = {idUser}"
        financeiro = Financeiro()

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            linha = []

            while row:
                guests = self.select_guest(row[0])
                pendente = self.getPendente(row[0])
                Vend_ComCupom = self.VendCupom(row[0])
                Vend_SemCupom = self.VendSemCupom(row[0])
                Lotes = self.LotesEvento(row[0])
                LoteAtual = self.LoteAtual(row[0], ((row[4] - row[3]) + pendente))
                tickets = self.GetTicket(row[0])
                ValTotal = financeiro.Total(row[0])
                ValResgatado = financeiro.Resgatado(row[0])
                ValPendente = financeiro.Pendente(row[0])
                Solicitacoes = financeiro.Solicitacoes(row[0])

                if Vend_ComCupom == None:
                    Vend_ComCupom = 0

                if Vend_SemCupom == None:
                    Vend_SemCupom = 0

                linha.append(
                    {
                        "id": row[0],
                        "Title": (row[1]),
                        "desc": row[2],
                        "info": row[12],
                        "QtdDisp": (row[3] - pendente),
                        "QtdTicket": row[4],
                        "DateEvent": row[5],
                        "DateFim": row[10],
                        "banner": row[6],
                        "logo": row[7],
                        "instagram": row[8],
                        "youtube": row[9],
                        "guests": guests,
                        "lotes": Lotes,
                        "qtdDisLote": (LoteAtual[2] - self.qtdLoteVen),
                        "loteAtual": LoteAtual,
                        "SemCupom": int(Vend_SemCupom),
                        "ComCupom": int(Vend_ComCupom),
                        "tickets": tickets,
                        "financeiro": {
                            "total": ValTotal,
                            "resgatado": ValResgatado,
                            "pendente": ValResgatado,
                            "liberado": (
                                float(ValTotal) - float(ValPendente + ValResgatado)
                            ),
                            "solicitacoes": Solicitacoes,
                        },
                        "privado": row[13],
                        "teste": {"Self": self.qtdLoteVen, "lote": LoteAtual[2]},
                    }
                )
                row = cursor.fetchone()

        connectionDB.close()
        return linha

    def LotesEvento(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT NomeLote, price, DispQtd FROM LOTESEVENTOS WHERE idEvento = {idEvento} ORDER by OrderLote"
        with connectionDB.cursor(buffered=True) as cursor:
            linha = []
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                linha.append({"NomeLote": row[0], "price": (row[1]), "DispQtd": row[2]})
                row = cursor.fetchone()

        connectionDB.close()
        return linha

    def VendCupom(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT sum(qtdComprado) FROM TICKET WHERE idEvento = {idEvento} AND idCupom is not null"
        with connectionDB.cursor(buffered=True) as cursor:
            linha = []
            cursor.execute(script)
            row = cursor.fetchone()
        connectionDB.close()
        return row[0]

    def VendSemCupom(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT sum(qtdComprado) FROM TICKET WHERE idEvento = {idEvento} AND idCupom is null"
        with connectionDB.cursor(buffered=True) as cursor:
            linha = []
            cursor.execute(script)
            row = cursor.fetchone()

        connectionDB.close()
        return row[0]

    def GetTicket(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"""SELECT 
                        TI.hash_ticket,
                        USER.nome,
                        CP.codigo,
                        TI.qtdComprado,
                        TA.valor,
                        USER.tel
                    FROM TICKET AS TI
                        LEFT JOIN TRANSACTIONS AS TA
                            ON TA.id = TI.idTransactions
                        LEFT JOIN USUARIOS AS USER 
                            ON USER.id = TI.idUser
                        LEFT JOIN CUPOMDESCONTO AS CP
                            ON CP.id = TI.idCupom
                    WHERE 
                        TI.idEvento = {idEvento}"""
        with connectionDB.cursor(buffered=True) as cursor:
            linha = []
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                linha.append(
                    {
                        "ticket": row[0],
                        "nome": (row[1]),
                        "cupom": row[2],
                        "qtd": row[3],
                        "valor": row[4],
                        "telefone": row[5],
                    }
                )
                row = cursor.fetchone()

        connectionDB.close()
        return linha

    def update(self, body, idUser):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"""UPDATE `EVENTOS`
                    SET
                        NomeEvento = '{body["NomeEvento"]}',
                        Descricao = '{body["Descricao"]}',
                        QtdDisp = {body["QtdDisp"]},
                        QtdTicket = {body["QtdTicket"]},
                        DateEvent = '{body["DateEvent"]}',
                        Price = {body["Price"]},
                        site_banner = '{body["site_banner"]}',
                        site_logo = '{body["site_logo"]}',
                        dt_fim = '{body["dt_fim"]}',
                        habilitado = '{body["habilitado"]}'
                    WHERE
                            id = {body["evento"]}
                            AND idUser = {idUser}"""
