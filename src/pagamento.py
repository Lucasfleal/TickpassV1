import mysql.connector
import mercadopago
import secrets
import bcrypt
import requests, json
from .user import Usuarios
from .mail import EMAIL
from datetime import datetime, timedelta


class LinkPagamento:
    connectionDB = mysql.connector.connect(
        host="mysqldb",
        database="TICKPASS",
        port="3306",
        user="root",
        password="Yig9VEUiVwC_uPl",
    )

    def GeraLink(self, idEvento, qtd, User, cupom, participantes, isBrothers):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        sdk = mercadopago.SDK(
            "APP_USR-5696291509969784-080623-e94f788df2e146254bf93b3f361507ec-1804033755"
        )

        pendente = self.getPendente(idEvento)
        script = f"SELECT NomeEvento, habilitado, QtdDisp, site_logo, QtdTicket FROM EVENTOS where id = {idEvento}"
        reference = secrets.token_hex(10).upper()

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                titulo = str(row[0])
                qtdDisp = row[2] - pendente
                QtdTicket = row[4]
                logo = row[3]
                row = cursor.fetchone()
        if qtdDisp <= 0:
            return "Esgotado!"

        preco_unitario = self.LoteAtual(idEvento, (QtdTicket - qtdDisp))
        dataCupom = [0, 0]

        if cupom:
            dataCupom = self.getCupom(idEvento, cupom)
            preco_unitario -= preco_unitario * (dataCupom[1] / 100)

        # if idEvento == 4:
        #     taxa = format((preco_unitario * 0.05), ".2f")
        #     site = "https://pay.finaliza.shop/checkout/dados?pl=9ad81ed4ef"
        # elif idEvento == 3:
        #     site = "https://pay.finaliza.shop/pl/88f0a0b17f"
        # elif idEvento == 5:
        #     site = "https://pay.finaliza.shop/pl/202231f535"
        # else:

        dadosUser = self.getUser(User)

        taxa = format((preco_unitario * 0.1), ".2f")
        url = "https://api.pagar.me/core/v5/orders"

        if isBrothers == True:
            preco_unitario = 35

        telefone = dadosUser["tel"]

        payload = {
            "customer": {
                "name": dadosUser["name"],
                "email": dadosUser["email"],
                "document": dadosUser["cpf"],
                "document_type": "CPf",
                "type": "individual",
                "phones": {
                    "mobile_phone": {
                        "country_code": "55",
                        "area_code": "19",
                        "number": dadosUser["tel"],
                    }
                },
            },
            "items": [
                {
                    "amount": int(preco_unitario * 100),
                    "description": titulo,
                    "quantity": qtd,
                    "code": idEvento,
                }
            ],
            "payments": [
                {
                    "checkout": {
                        "expires_in": 15,
                        "accepted_payment_methods": [
                            "credit_card",
                            "pix",
                            "debit_card",
                        ],
                        "Pix": {"expires_in": 900},
                    },
                    "payment_method": "checkout",
                }
            ],
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic c2tfOWEyN2U1NmMyMDMxNDU5MjhlZGVkNmIzODRmMDgwMTM6",
        }

        response = requests.post(url, json=payload, headers=headers)

        comments = json.loads(response.content)
        site = comments["checkouts"][0]["payment_url"]
        id_pagarme = comments["id"]

        print(site)

        # preference_response = sdk.preference().create(preference_data)
        # preference = preference_response["response"]
        # site = preference["init_point"]
        # print(site)

        status_Save = self.saveTransaction(
            id_pagarme,
            User,
            dataCupom[0],
            idEvento,
            qtd,
            preco_unitario,
            reference,
        )

        self.saveParticipante(participantes, status_Save[1])
        connectionDB.close()
        # if status_Save[0] != "OK":
        #     return status_Save
        return [status_Save[0], site]

    def getUser(self, idUser):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT id, nome, email, picture, tel, cpf FROM USUARIOS where id = '{idUser}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                retorno = {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "picture": row[3],
                    "tel": row[4],
                    "cpf": row[5],
                }
                row = cursor.fetchone()
        connectionDB.close()
        return retorno

    def saveTransaction(self, preference, User, cupom, idEvento, qtd, preco_unitario, reference):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")
        dataSol = str(datetime.now())
        if cupom > 0:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idCupom`, `idEvento`, `qtd`, `valor`,`reference`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            val = (
                User,
                preference,
                dataSol,
                "N",
                cupom,
                idEvento,
                qtd,
                (preco_unitario * qtd),
                reference,
            )
        else:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idEvento`, `qtd`, `valor`,`reference`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            val = (
                User,
                preference,
                dataSol,
                "N",
                idEvento,
                qtd,
                (preco_unitario * qtd),
                reference,
            )

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()

                script = "SELECT LAST_INSERT_ID() AS novo_id;"

                cursor.execute(script)
                row = cursor.fetchone()
            connectionDB.close()
            return ["OK", row[0]]
        except mysql.connector.Error as err:
            connectionDB.close()
            return str(err)

    def getCupom(self, idEvento, CodCupom):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT porcentagem, id FROM CUPOMDESCONTO where idEvento = {idEvento} and codigo = '{CodCupom}'"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)

            row = cursor.fetchone()
            idCupom = row[1]
            porcentagem = row[0]
        connectionDB.close()
        return [idCupom, porcentagem]

    def getPendente(self, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        dataAnt = datetime.utcnow() - timedelta(minutes=20)
        script = f"SELECT COUNT(*) FROM TRANSACTIONS where idEvento = {idEvento} and dateTransaction >= '{dataAnt}' and status_pag = 'N'"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            result = cursor.fetchone()
            count = result[0]
        connectionDB.close()
        return count

    def getQtdTicket(self, preference):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT id,qtd,idCupom,idEvento,idUser, status_pag FROM TRANSACTIONS where preference_MP = '{preference}'"

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                row = cursor.fetchone()
            connectionDB.close()
            return row
        except mysql.connector.Error as err:
            return str(err)

    def upTransaction(self, idTransaction):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"UPDATE TRANSACTIONS SET status_pag = 'S' WHERE id = {idTransaction}"

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
            return "OK"
        except mysql.connector.Error as err:
            return str(err)

    def saveTicket(self, preference):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")
        hash_ticket = secrets.token_hex(5).upper()
        transaction = self.getQtdTicket(preference)
        idEvento = transaction[3]
        email = self.getEmail(transaction[4])

        if transaction[5] == "S":
            hash_ticket = self.GetHash(transaction[4], idEvento)
            return ["OK", idEvento, hash_ticket]

        self.upTransaction(transaction[0])

        script = "INSERT INTO `TICKPASS`.`TICKET` (`idEvento`, `hash_ticket`, `qtdComprado`, `idCupom`, `idUser`, idTransactions) VALUES (%s, %s, %s, %s, %s, %s);"
        for n in range(transaction[1]):
            hash_ticket = secrets.token_hex(5).upper()
            val = (
                idEvento,
                hash_ticket,
                1,
                transaction[2],
                transaction[4],
                transaction[0],
            )
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script, val)
                    connectionDB.commit()
                ob_Emai = EMAIL()
                ob_Emai.SendTicket(email, hash_ticket)
                self.consomeTicket(idEvento, transaction[1])
                # return ["OK", idEvento, hash_ticket]
            except mysql.connector.Error as err:
                connectionDB.close()
                return [str(err), idEvento, "erro"]
        connectionDB.close()
        return ["OK", idEvento, hash_ticket]

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
                    return row[1]
                else:
                    qtdVendida -= row[2]
                    row = cursor.fetchone()
            return ["Esgotado", 0]

    def getEmail(self, idUser):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT email FROM USUARIOS where id = {idUser}"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
        connectionDB.close()
        return row[0]

    def consomeTicket(self, idEvento, qtd):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = (
            f"UPDATE EVENTOS SET `QtdDisp` = `QtdDisp` - {qtd} WHERE id = {idEvento}"
        )
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
            return "OK"
        except mysql.connector.Error as err:
            return str(err)

    def GetHash(self, idUser, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"SELECT hash_ticket FROM TICKET where id = {idUser} and idEvento = {idEvento}"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
        connectionDB.close()
        return row[0]

    def SetCancel(self, SetPending):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        for change in SetPending:
            script = f"""UPDATE `TICKPASS`.`TRANSACTIONS`
                        SET status_pag = 'P'
                        WHERE preference_MP = '{change}' """
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script)
                    connectionDB.commit()
                connectionDB.close()
                return "OK"
            except mysql.connector.Error as err:
                connectionDB.close()
                return str(err)

    def saveParticipante(self, body, idTransaction):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        script = "INSERT INTO `TICKPASS`.`PARTICIPANTES` (`idTransactions`, `nome`, `cpf`) VALUES (%s, %s, %s);"

        for participante in body:
            val = (idTransaction, participante["nome"], participante["cpf"])
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script, val)
                    connectionDB.commit()
            except mysql.connector.Error as err:
                connectionDB.close()
                return str(err)
        connectionDB.close()
        return "OK"
