import mercadopago
import mysql.connector
import requests
import json
import time
from datetime import datetime, timedelta


def GetPreference():
    date_Transacao = str(datetime.now() - timedelta(hours=2))
    connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
    script = f'''SELECT 
                    preference_MP
                FROM TRANSACTIONS
                WHERE 
                    (dateTransaction >= '{date_Transacao}'
                    AND status_pag = 'N')
                    or status_pag = 'P' '''

    with connectionDB.cursor(buffered=True) as cursor:
        cursor.execute(script)
        linha = []
        row = cursor.fetchone()
        while row:
            linha.append(row[0])
            row = cursor.fetchone()
    connectionDB.close()
    return linha

def CheckPreferences(preferences):
    returno = []
    SetPending = []
    SetCancel = []
    header = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Basic c2tfOWEyN2U1NmMyMDMxNDU5MjhlZGVkNmIzODRmMDgwMTM6",
        }
    for preference in preferences:
        request = requests.get("https://api.pagar.me/core/v5/orders/" + preference, headers=header)
        content = json.loads(request.content)
        # if content["elements"]:
        #     elements = ''
        #     for element in content["elements"]:
        #         if element["status"] == "closed":
        #             status = element["order_status"]
        #             if status == "paid":
        #                 payment = element["payments"]
        #                 for pag in payment:
        #                     returno.append(preference)
        #             else:
        #                 SetPending.append(preference)
        #                 print(preference)
        #         elif element["status"] == "expired":
        #             SetCancel.append(preference)

        if content["status"] == "paid":
            returno.append(preference)
        if content["status"] == "canceled":
            SetCancel.append(preference)
        if content["status"] == "pending":
            SetPending.append(preference)

    if SetPending:
        header = {'content-type': 'application/json', 'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OSwibmFtZSI6IlIgQSBNIFBST0RVQ09FUyBFIEVWRU5UT1MgTFREQSIsImVtYWlsIjoidGVzdGUxMjNAdGVzLmNvbS5iciIsInBpY3R1cmUiOiIiLCJ0ZWwiOiIxOTk5NjQyMjU0NSIsImNucGoiOiI1MDcyNjgwNzAwMDE4NCIsImV4cGlyYXRpb24iOiIyMDI0LTA1LTExIDIwOjQ1OjU3LjIzNzY2NCJ9.0mfJ6DTkDF5dYuhLqPKq4ZRyh9OKR1x2Egx9s1dc9u4'}

        for preference in SetPending:
            data = {
                "preferences": SetPending
            }
            request = requests.post(url="https://api.tickpass.com.br/setpending",  data=json.dumps(data), headers=header )

    if SetCancel:
        connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
        for change in SetCancel:
            script = f'''UPDATE `TICKPASS`.`TRANSACTIONS`
                        SET status_pag = 'X'
                        WHERE preference_MP = '{change}' '''
            try:
                with connectionDB.cursor() as cursor:
                    cursor.execute(script)
                    connectionDB.commit()
                connectionDB.close()
            except mysql.connector.Error as err:
                connectionDB.close()

    connectionDB = mysql.connector.connect(host='mysqldb', database = 'TICKPASS', port='3306', user = 'root', password ="Yig9VEUiVwC_uPl")
    for change in returno:
        script = f'''UPDATE `TICKPASS`.`TRANSACTIONS`
                    SET status_pag = 'P'
                    WHERE preference_MP = '{change}' '''
        try:
            with connectionDB.cursor() as cursor:
                cursor.execute(script)
                connectionDB.commit()
            connectionDB.close()
        except mysql.connector.Error as err:
            connectionDB.close()

    return returno


while True:
    AllPreferences = GetPreference()
    preferences = CheckPreferences(AllPreferences)
    header = {'content-type': 'application/json', 'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6OSwibmFtZSI6IlIgQSBNIFBST0RVQ09FUyBFIEVWRU5UT1MgTFREQSIsImVtYWlsIjoidGVzdGUxMjNAdGVzLmNvbS5iciIsInBpY3R1cmUiOiIiLCJ0ZWwiOiIxOTk5NjQyMjU0NSIsImNucGoiOiI1MDcyNjgwNzAwMDE4NCIsImV4cGlyYXRpb24iOiIyMDI0LTA1LTExIDIwOjQ1OjU3LjIzNzY2NCJ9.0mfJ6DTkDF5dYuhLqPKq4ZRyh9OKR1x2Egx9s1dc9u4'}

    for preference in preferences:
        data = {
            "preference_id": preference
        }
        request = requests.post(url="https://api.tickpass.com.br/saveTicket",  data=json.dumps(data), headers=header )

    time.sleep(10)