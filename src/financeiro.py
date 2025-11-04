import mysql.connector
from datetime import datetime, timedelta

class Financeiro():

    def Total(self, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT 
                        count(TI.qtdComprado),
                        TA.valor
                    FROM TICKET AS TI
                        LEFT JOIN TRANSACTIONS AS TA
                            ON TA.id = TI.idTransactions
                        LEFT JOIN USUARIOS AS USER 
                            ON USER.id = TI.idUser
                        LEFT JOIN CUPOMDESCONTO AS CP
                            ON CP.id = TI.idCupom
                    WHERE 
                        TI.idEvento = {idEvento}
                    GROUP BY TA.valor'''
        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            total = 0
            row = cursor.fetchone()
            while row:
                total += (row[0] * row[1])
                row = cursor.fetchone()
        
        connectionDB.close()
        return total


    def Resgatado(self, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT 
                        valor
                    FROM SOLICITACOES
                    WHERE 
                        idEvento = {idEvento}
                        AND pag_status = 'S' '''
        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            total = 0
            row = cursor.fetchone()
            while row:
                total += (row[0])
                row = cursor.fetchone()
        
        connectionDB.close()
        return total

    def Pendente(self, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT 
                        valor
                    FROM SOLICITACOES
                    WHERE 
                        idEvento = {idEvento}
                        AND pag_status = 'N' '''
        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            total = 0
            row = cursor.fetchone()
            while row:
                total += (row[0])
                row = cursor.fetchone()
        
        connectionDB.close()
        return total

    def Solicitacoes(self, idEvento):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f'''SELECT 
                        id,
                        dtSolicitacao,
                        valor,
                        dtRecebido,
                        pag_status,
                        comprovante
                    FROM SOLICITACOES
                    WHERE 
                        idEvento = {idEvento}'''
        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            linha = []
            row = cursor.fetchone()
            while row:
                linha.append({'id' : row[0],
                            'dtSolicitacao' : (row[1]),
                            'valor' : row[2],
                            'dtRecebido' : row[3],
                            'pag_status' : row[4],
                            'comprovante' : row[5]})
                row = cursor.fetchone()
        
        connectionDB.close()
        return linha