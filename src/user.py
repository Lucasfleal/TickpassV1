import bcrypt
import mysql.connector
import secrets
from datetime import datetime, timedelta
from .mail import EMAIL
from .config import salt as SaltConfig

class Usuarios():
    salt = '$2b$08$MVH34E7z1WL..h/2MrrYiu'
    
    def CriaUsuario(self, body):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        password = bcrypt.hashpw(bytes(body["password"], encoding='utf8'),bytes(self.salt, encoding='utf8'))

        script = 'INSERT INTO `TICKPASS`.`USUARIOS` (`nome`, `email`, `senha`, `picture`, `tel`, `cpf`) VALUES (%s, %s, %s, %s, %s, %s);'
        val = (body["name"],body["email"],password,body["picture"],body["tel"],body["cpf"])
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()
            connectionDB.close()
            return ('OK', body["email"],body["password"])
        except mysql.connector.Error as err:
            connectionDB.close()
            return(str(err))

    def consultaPass(self,email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT senha FROM USUARIOS where email = '{email}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                password = row[0]
                row = cursor.fetchone()
        connectionDB.close()
        return password

    def consultaUser(self, email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT id, nome, email, picture, tel, cpf FROM USUARIOS where email = '{email}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                retorno = {"id" : row[0],
                           "name" : row[1],
                           "email" : row[2],
                           "picture" : row[3],
                           "tel" : row[4],
                           "cpf" : row[5]}
                row = cursor.fetchone()
        connectionDB.close()
        return retorno

    def updateUser(self,idUser, body):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        script = f'''UPDATE `TICKPASS`.`USUARIOS`
                    SET nome = '{body["nome"]}',
                        email = '{body["email"]}',
                        picture = '{body["picture"]}',
                        tel = {body['tel']}
                    WHERE id = '{idUser}' '''

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
            return (['OK', body["email"]])
        except mysql.connector.Error as err:
            connectionDB.close()
            return(str(err))

    def consultaPassVend(self,email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT senha FROM VENDEDOR where email = '{email}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                password = row[0]
                row = cursor.fetchone()
        connectionDB.close()
        return password

    def consultaVend(self, email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        script = f"SELECT id, nome, email, picture, tel, cnpj FROM VENDEDOR where email = '{email}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            row = cursor.fetchone()
            while row:
                retorno = {"id" : row[0],
                           "name" : row[1],
                           "email" : row[2],
                           "picture" : row[3],
                           "tel" : row[4],
                           "cnpj" : row[5]}
                row = cursor.fetchone()
        connectionDB.close()
        return retorno

    def geraTrocaSenha(self, email):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        VeriCod = str(secrets.token_hex(3)).upper()
        user = self.consultaUser(email)

        script = 'INSERT INTO `TICKPASS`.`TROCASENHA` (`codigo`, `idUser`, `dtSolicitacao`) VALUES (%s, %s, %s);'
        val = (VeriCod, user["id"], str(datetime.now()))
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script, val)
                connectionDB.commit()
            connectionDB.close()
            return ('OK')
        except mysql.connector.Error as err:
            connectionDB.close()
            return(str(err))

    def validaRecCod(self, codigo):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        
        dataAnt = datetime.now() - timedelta(hours=1)
        status = 'Codigo Inexistente'
        script = f"SELECT idUser, dtSolicitacao FROM TROCASENHA where codigo = '{codigo}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            retorno = 0
            row = cursor.fetchone()
            if row[1] > dataAnt:
                retorno = row[0]
                status = 'OK'
            else:
                status = 'Codigo expirado'
        connectionDB.close()
        return {status, retorno}
    
    
    def TrocaSenha(self, idUser, newPass):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        password = str(bcrypt.hashpw(bytes(newPass, encoding='utf8'),bytes(SaltConfig, encoding='utf8')), "utf-8")
        script = f"UPDATE `TICKPASS`.`USUARIOS` SET senha = '{password}' WHERE id = {idUser}"

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
            return ('OK')   
        except mysql.connector.Error as err:
            connectionDB.close()
            return(str(err))