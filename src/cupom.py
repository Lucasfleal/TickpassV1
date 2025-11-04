import mysql.connector
from datetime import datetime, timedelta
import secrets

class Cupom:
    
    def validaCupom(self, idEvento, CodCupom):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")

        script = f"SELECT qtdDip, id, porcentagem FROM CUPOMDESCONTO where idEvento = {idEvento} and codigo = '{CodCupom}'"

        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            if cursor.rowcount > 0:
                row = cursor.fetchone()
                while row:
                    qtdDisp = row[0]
                    idCupom = row[1]
                    porcentagem = row[2]
                    row = cursor.fetchone()
            else: 
                return ('Não existe!') 
        connectionDB.close()
        pendente = self.getPendente(idEvento,idCupom)
        if (qtdDisp - pendente) > 0:
            return (['Valido', porcentagem])
        else:
            return ('Já utilizado!')



    def getPendente(self, idEvento, idCupom):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")

        dataAnt = str(datetime.utcnow() - timedelta(minutes=20))
        script = f"SELECT COUNT(*) FROM TRANSACTIONS where idEvento = {idEvento} and idCupom = {idCupom} and dateTransaction >= '{dataAnt}'"

        with connectionDB.cursor() as cursor:
            cursor.execute(script)
            result =cursor.fetchone()
            count = result[0]
        connectionDB.close()
        return count

    def teste(self):
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        connectionDB.set_charset_collation('utf8')
        nome = '''<b>Sobre a Conferência MQMA</b></br>
        A Conferência Mulheres Que Muito Amam nasceu para levantar mulheres para cumprirem o IDE do Senhor. Estamos na 2ª edição e temos convicção de que é apenas o início para as mulheres de Paulínia-SP e Região. Cremos que basta apenas um encontro com Jesus para tudo mudar. De improváveis e pecadoras, para filhas remidas, amadas e perdoadas. A mulher posicionada em Deus provoca uma mudança poderosa através de sua atitude de louvor e generosidade em sua entrega. Cumprem o propósito de levar esse amor aonde for! Seja essa mulher, seja você e faça parte desse exército que se levanta hoje para exalar o bom perfume de Cristo. Inscreva-se e tenha sua vida transformada!</br>
        </br>
        <b>Garanta sua vaga</b></br>
        As vagas são limitadas em função do espaço. Corra e garanta já sua vaga, pois a próxima edição será apenas em 2025.</br>
        </br>
        <b>Sobre a Organizadora</b>
        Pra Rafaela Marques ao lado do seu marido Pr André Marques são pastores da Igreja Batista da Lagoinha Paulínia e sub-regional do Estado de SP, onde dezenas de igrejas estão aos seus cuidados.</br>
        Uma mulher de fé, convicção do seu chamado e fiel aos princípios Bíblicos, tem levantando centenas de mulheres, através do ensino, discipulado e projetos onde são mentoreadas, cuidadas, curadas e levantadas para cumprir o IDE do Senhor. Não apenas na igreja local, mas mulheres do país todo.</br>
        Com o intuito de levar cada coração ao temor do Senhor, alinhamento de corações, um viver de adoração e entrega absoluta, crê, pois é testemunho vivo, no poder que há quando Ele chama cada mulher improvável para um posicionamento de viver de forma inteira para Cristo. Milagres, transformação e restauração acontecem não apenas em cada mulher mas em cada um a sua volta. Diversos testemunhos já foram presenciados e ainda veremos o que o Senhor fará neste ajuntamento preparado pelo Senhor.</br>
        </br>
        </br>
        Lagoinha Paulínia – Novo Espaço - Av. Prefeito José Lozano Araújo 4545 - Paulínia -  CEP: 13141-901'''

        script = f"UPDATE EVENTOS SET info = '{nome}'"

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
                connectionDB.close()
            return 'ok'
        except mysql.connector.Error as err:
            return(str(err))
        