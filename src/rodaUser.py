import mysql.connector
import mercadopago
import secrets
from .mail import EMAIL
from datetime import datetime, timedelta

class EnviaMail():

    def GeraTicketPix(self,email, idEvento, qtd ):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        hash_ticket = str(secrets.token_hex(5)).upper()
        idUser =  self.GetId(email)
        idTransaction = self.saveTransaction(idUser,0,idEvento, qtd,159.9)
        script = 'INSERT INTO `TICKPASS`.`TICKET` (`idEvento`, `hash_ticket`, `qtdComprado`, `idUser`, `idTransactions`) VALUES (%s, %s, %s, %s,%s);'
        val = (idEvento,hash_ticket,qtd, idUser, idTransaction)

        if idUser > 0:
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script, val)
                    connectionDB.commit()
                doc_email = EMAIL()
                doc_email.SendTicket(email, hash_ticket)

                self.consomeTicket(idEvento, qtd)
                

                connectionDB.close()
                return (['OK', idEvento,hash_ticket])

            except mysql.connector.Error as err:
                return([str(err), idEvento, hash_ticket ])

        else: 
            return (['Erro', idEvento,hash_ticket])

    def consomeTicket(self, idEvento,qtd):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"UPDATE EVENTOS SET `QtdDisp` = `QtdDisp` - {qtd} WHERE id = {idEvento}"
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
            return ('OK')
        except mysql.connector.Error as err:
            return(str(err))

    def GetId(self,email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT id FROM USUARIOS WHERE email = '{email}'"
        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
        connectionDB.close()
        return row[0]

    def saveTransaction(self,  User, cupom, idEvento, qtd,preco_unitario):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        dataSol = str(datetime.utcnow())
        preference = 'PIX'
        if cupom > 0:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idCupom`, `idEvento`, `qtd`, `valor`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            val = (User, preference, dataSol, "N", cupom, idEvento, qtd, (preco_unitario*qtd))
        else:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idEvento`, `qtd`, `valor`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            val = (User, preference, dataSol, "N", idEvento, qtd, (preco_unitario*qtd))

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()
                script = f"SELECT LAST_INSERT_ID() AS novo_id;"

                cursor.execute(script)
                row = cursor.fetchone()
            connectionDB.close()
            return row[0]

        except mysql.connector.Error as err:
            return str(err)