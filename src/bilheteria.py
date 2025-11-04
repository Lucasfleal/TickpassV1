import bcrypt
import mysql.connector
import secrets
from datetime import datetime, timedelta

class Bilheteria():
    def login(self,body):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT senha FROM USER_BILHETERIA where evento = {body['evento']}"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            if cursor.rowcount > 0:
                row = cursor.fetchone()
                if body["senha"] == row[0]:
                    connectionDB.close()
                    return ["OK", 200]
                connectionDB.close()    
                return ['Senha Incorreta', 400]
            
            connectionDB.close()
            return ['Evento Incorret0', 404]


    def ticket(self, codigo, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")

        script = f'''SELECT 
                        TI.qtdComprado,
                        TI.hash_ticket,
                        USER.nome,
                        RD.datePass,
                        USER.cpf,
                        TI.id
                    FROM TICKET AS TI 
                        LEFT JOIN USUARIOS AS USER 
                            ON USER.id = TI.idUser
                        LEFT JOIN TICKET_READED AS RD 
                            ON RD.idTicket = TI.id
                    WHERE 
                        TI.hash_ticket = '{codigo}' 
                        AND TI.idEvento = {idEvento}  '''

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)

            if cursor.rowcount > 0:
                row = cursor.fetchone()
                qtd = row[0]
                codigo = row[1]
                nome = row[2]
                datePass = row[3]
                cpf = row[4]
                qtdLido = self.qtdLido(row[5])
            else: 
                connectionDB.close()
                return (['Não existe!']) 
        connectionDB.close()
        if qtdLido == qtd:
            return (['Já utilizado!', {"qtd": qtd,"codigo": codigo,"nome":nome,"leitura":datePass,"cpf":cpf}])
        else:
            self.savePass(row[5])
            return (['Valido', {"qtd": qtd,"codigo": codigo,"nome":nome,"leitura":datePass,"cpf":cpf}])
        
    def qtdLido(self,idTicket):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT * FROM TICKET_READED where idTicket = {idTicket}"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            result = cursor.rowcount
        connectionDB.close()
        return result

    def savePass(self, idTicket):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        dataSol = str(datetime.now())

        script = "INSERT INTO `TICKPASS`.`TICKET_READED` (`idTicket`, `datePass`) VALUES (%s, %s);"
        val = (idTicket, dataSol)

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()
            connectionDB.close()
            return "OK"

        except mysql.connector.Error as err:
            return str(err)

    def pesquisa(self, cpf, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT 
                        TI.qtdComprado,
                        TI.hash_ticket,
                        USER.nome,
                        USER.cpf,
                        TI.id
                    FROM TICKET AS TI 
                        LEFT JOIN USUARIOS AS USER 
                            ON USER.id = TI.idUser
                    WHERE 
                        USER.cpf = '{cpf}' 
                        AND TI.idEvento = {idEvento}'''

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)

            if cursor.rowcount > 0:
                linha = []
                row = cursor.fetchone()
                while row:
                    linha.append({"qtd": row[0],
                        "codigo": row[1],
                        "nome": row[2],
                        "cpf": row[3],
                        "qtdLido": self.qtdLido(row[4])
                    })
                    row = cursor.fetchone()
                
            else: 
                connectionDB.close()
                return (['Não existe!']) 
        connectionDB.close()
        return (['Valido', linha])