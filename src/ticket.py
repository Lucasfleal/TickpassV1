import mysql.connector
import secrets
from .mail import EMAIL
from datetime import datetime, timedelta

class Ticket():
    
    def myTickets(self, idUser):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'SELECT id, idEvento,hash_ticket,qtdComprado FROM TICKET WHERE idUser = {idUser}'
        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            linha = []
        
            while row:
                linha.append({'id' : row[0],
                            'idEvento' : row[1],
                            'hash_ticket' : row[2],
                            'qtdComprado' : row[3]})
                row = cursor.fetchone()
        connectionDB.close()
        return linha
    
    def myTransactions(self, idUser):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT id, idEvento,dateTransaction,qtd,valor,status_pag FROM TRANSACTIONS WHERE idUser = {idUser} AND (status_pag = 'S' or status_pag = 'P' or status_pag = 'X') '''
        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            linha = []
        
            while row:
                linha.append({'id' : row[0],
                            'idEvento' : row[1],
                            'dateTransaction' : row[2],
                            'qtdComprado' : row[3],
                            'valor' : row[4],
                            'status_pag' : row[5]})
                row = cursor.fetchone()
        connectionDB.close()
        return linha
        
    def saveTicketFree(self,idUser,body):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        idEvento  = body["idEvento"]
        hash_ticket = str(secrets.token_hex(5)).upper()
        idCupom = self.GetCupom(idEvento, body["CodCupom"])
        email = self.getEmail(idUser)
        ExistTicket  = self.ExistOTicket(idUser,idCupom)

        if ExistTicket:
            return(['OK', idEvento, row[2]]) 

        idTransactions = self.saveTransaction(idUser, idCupom[1], idEvento, 1,0)
        script = 'INSERT INTO `TICKPASS`.`TICKET` (`idEvento`, `hash_ticket`, `qtdComprado`, `idCupom`, `idUser`, `idTransactions`) VALUES (%s, %s, %s, %s, %s, %s);'
        val = (idEvento,hash_ticket,1,idCupom[1], idUser, idTransactions)
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()
            doc_email = EMAIL()
            doc_email.SendTicket(email, hash_ticket)

            self.consomeTicket(idEvento)
            self.consomeCupom(idCupom[1])

            connectionDB.close()
            return (['OK', idEvento,hash_ticket])
        except mysql.connector.Error as err:
            return({str(err), idEvento})
    
    def ExistOTicket(self,idUser,idCupom):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT * FROM TICKET where idUser = {idUser} and idCupom = '{idCupom}'"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            if cursor.rowcount > 0:
                row = cursor.fetchone()
                return row
            else:
                return ""

    def GetCupom(self, idEvento, CodCupom):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT qtdDip, id, porcentagem FROM CUPOMDESCONTO where idEvento = {idEvento} and codigo = '{CodCupom}'"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            if cursor.rowcount > 0:
                row = cursor.fetchone()
                return row

    def getEmail(self, idUser):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT email FROM USUARIOS where id = {idUser}"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            return row[0]
    
    def consomeTicket(self, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"UPDATE EVENTOS SET `QtdDisp` = `QtdDisp` - 1 WHERE id = {idEvento}"
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()

            return ('OK')
        except mysql.connector.Error as err:
            return(str(err))
        
    def consomeCupom(self, idCupom):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"UPDATE CUPOMDESCONTO SET `QtdDip` = `QtdDip` - 1 WHERE id = {idCupom}"
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()

            return ('OK')
        except mysql.connector.Error as err:
            return(str(err))
    
    def saveTransaction(self,  User, cupom, idEvento, qtd,preco_unitario):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        dataSol = str(datetime.now())
        preference = 'free'
        if cupom > 0:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idCupom`, `idEvento`, `qtd`, `valor`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
            val = (User, preference, dataSol, "S", cupom, idEvento, qtd, (preco_unitario*qtd))
        else:
            script = "INSERT INTO `TICKPASS`.`TRANSACTIONS` (`idUser`, `preference_MP`, `dateTransaction`, `status_pag`, `idEvento`, `qtd`, `valor`) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            val = (User, preference, dataSol, "S", idEvento, qtd, (preco_unitario*qtd))

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