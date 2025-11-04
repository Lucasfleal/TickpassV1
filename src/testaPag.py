import mercadopago
import mysql.connector
import requests
import json
from datetime import datetime, timedelta


class testePag:
    def GeraPix(self, mydate):
        preferences = self.GetPreference(mydate)
        retorno = self.CheckPreferences(preferences)
        return retorno

    def GetPreference(self, mydate):
        date_Transacao = mydate  # str(datetime.now() - timedelta(hours=24))
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        script = f"""SELECT 
                        preference_MP
                    FROM TRANSACTIONS
                    WHERE 
                        dateTransaction like '{date_Transacao}%'
                        AND status_pag = 'N' """
        print(script)
        with connectionDB.cursor(buffered=True) as cursor:
            cursor.execute(script)
            linha = []
            row = cursor.fetchone()
            while row:
                linha.append(row[0])
                row = cursor.fetchone()
        connectionDB.close()
        return linha

    def CheckPreferences(self, preferences):
        returno = []
        header = {
            "Authorization": "Bearer APP_USR-6997386249502271-042922-31c74023c6f12bd89eef3a10de4005cd-1391927952"
        }
        for preference in preferences:
            request = requests.get(
                "https://api.mercadopago.com/merchant_orders/search?preference_id="
                + preference,
                headers=header,
            )
            content = json.loads(request.content)
            if content["elements"]:
                for element in content["elements"]:
                    if element["status"] == "closed":
                        elements = element
                        status = elements["order_status"]
                        if status == "paid":
                            payment = elements["payments"]
                            for pag in payment:
                                returno.append([pag["id"], preference])
            return returno

    def rodaScript(self, body):
        connectionDB = mysql.connector.connect(
            host="mysqldb",
            database="TICKPASS",
            port="3306",
            user="root",
            password="Yig9VEUiVwC_uPl",
        )
        connectionDB.set_charset_collation("utf8")

        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(body["script"])
                connectionDB.commit()
            connectionDB.close()
            return "OK"
        except mysql.connector.Error as err:
            connectionDB.close()
            return str(err)
