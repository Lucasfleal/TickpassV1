import mysql.connector
from datetime import datetime, timedelta


class InsertEvento:
    def Insert(self, body, idUser):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        script = """INSERT INTO `TICKPASS`.`EVENTOS` (NomeEvento, Descricao, QtdDisp, QtdTicket, DateEvent, site_banner, site_logo, dt_fim, habilitado ,insta, youtube, idUser)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        val = (
            body["name"],
            body["descricao"],
            body["qtdTicket"],
            body["qtdTicket"],
            body["dataInicio"],
            body["banner"],
            body["logo"],
            body["dataFim"],
            "S",
            body["insta"],
            body["youtube"],
            idUser,
        )
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()

                script = f"SELECT LAST_INSERT_ID() AS novo_id;"

                cursor.execute(script)
                row = cursor.fetchone()
            connectionDB.close()
            setor = self.InsertSetor(body["setor"], row[0], body["typeLote"])
            if setor != "OK":
                return setor
            return "OK"
        except mysql.connector.Error as err:
            connectionDB.close()
            return str(err)

    def InsertGuest(self, guests, idEvento):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        script = """INSERT INTO `TICKPASS`.`GUESTS` (idEvento, NomeGuest, InstaGuest)
                    VALUES (%s, %s, %s);"""
        for guest in guests:
            val = (
                idEvento,
                guest["nome"],
                guest["insta"],
            )
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script, val)
                    connectionDB.commit()
            except mysql.connector.Error as err:
                connectionDB.close()
                return str(err)

        connectionDB.close()
        return "OK"

    def InsertLotes(self, lotes, idEvento, typeLote, idSetor):
        order = 0
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        script = """INSERT INTO `TICKPASS`.`LOTESEVENTOS` (idEvento, NomeLote, price, DispQtd, OrderLote, dtFim, typeLote, idSetor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        for lote in lotes:
            order += 1
            val = (
                idEvento,
                f"Lote {order}",
                lote["price"],
                lote["qtd"],
                order,
                lote["date"],
                typeLote,
                idSetor,
            )
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script, val)
                    connectionDB.commit()
            except mysql.connector.Error as err:
                connectionDB.close()
                return str(err) + "LOTES"

        connectionDB.close()
        return "OK"

    def InsertSetor(self, setores, idEvento, typeLote):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        try:
            for setor in setores:
                script = """INSERT INTO `TICKPASS`.`SETOR` (idEvento, NomeSetor)
                            VALUES (%s, %s);"""
                val = (idEvento, setor["NomeSetor"])
                print(setor)
                try:
                    with connectionDB.cursor() as cursor:
                        cursor.execute(script, val)
                        connectionDB.commit()

                        script = "SELECT LAST_INSERT_ID() AS novo_id;"
                        cursor.execute(script)
                        row = cursor.fetchone()

                except mysql.connector.Error as err:
                    return str(err) + " SETOR"

                lote = self.InsertLotes(setor["lotes"], idEvento, typeLote, row[0])
                if lote != "OK":
                    return lote

        finally:
            connectionDB.close()

        return "OK"
