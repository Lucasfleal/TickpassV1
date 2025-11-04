from src import (
    EventosRepo,
    LinkPagamento,
    Usuarios,
    Cupom,
    Ticket,
    EMAIL,
    EnviaMail,
    testePag,
    Bilheteria,
    InsertEvento,
)
from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS, cross_origin
from flask_caching import Cache
from functools import wraps
from datetime import datetime, timedelta
from healthcheck import HealthCheck, EnvironmentDump
import mysql.connector
import redis
import jwt
import bcrypt
import sys


app = Flask(__name__)
health = HealthCheck()
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config["SECRET_KEY"] = "4f2375c069cd44029bcfc4cb896e35e3"
cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": "meu-redis",
        "CACHE_REDIS_PORT": 6379,
    }
)
cache.init_app(app)
sys.setrecursionlimit(1000)

app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"Alert!": "Token is missing!"})
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
        except:
            return jsonify({"Alert!": "Invalid Token!"})
        return func(*args, **kwargs)

    return decorated


@app.route("/", methods=["GET"])
def home():
    # mail = Cupom()
    # teste = mail.teste()
    # mail = EMAIL()
    # teste = mail.SendCad("lucasfleal159@gmail.com", "teste123")

    return "EAEEE"


@app.route("/eventos", methods=["GET", "POST"])
@cross_origin()
@cache.cached(timeout=5)
def eventos():
    if request.method == "GET":
        body = ""
    else:
        body = request.json
    eventosRepo = EventosRepo()
    data = eventosRepo.select_all(body)
    return jsonify({"resultado": data})


@app.route("/testePag", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def meuteste():
    mydate = request.json["date"]
    pagamento = testePag()
    retorno = pagamento.GeraPix(mydate)
    return jsonify({"status": retorno})


@app.route("/eventos/create", methods=["POST"])
@token_required
@cross_origin()
def createEvent():
    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")

    body = body = request.json
    create = InsertEvento()

    return jsonify("retorno",create.Insert(body, token_data["id"]))


############################  USUARIOS  ##########################################


@app.route("/login", methods=["POST"])
@cross_origin()
def login():
    usuario = Usuarios()
    password = bcrypt.hashpw(
        bytes(request.json["password"], encoding="utf8"),
        bytes(usuario.salt, encoding="utf8"),
    )
    email = request.json["email"]

    if email:
        cryptPass = usuario.consultaPass(email)

        if cryptPass:
            if str(password, "utf-8") == cryptPass:
                session["logged_in"] = True
                dados_user = usuario.consultaUser(email)
                token = jwt.encode(
                    {
                        "id": dados_user["id"],
                        "name": dados_user["name"],
                        "email": dados_user["email"],
                        "picture": dados_user["picture"],
                        "tel": dados_user["tel"],
                        "cpf": dados_user["cpf"],
                        "expiration": str(datetime.utcnow() + timedelta(minutes=20)),
                    },
                    app.config["SECRET_KEY"],
                    algorithm="HS256",
                )
                return jsonify({"token": token})
            else:
                return jsonify({"Erro": "Senha Incorreta!"})
        else:
            return jsonify({"Erro": "E-mail não cadastrado!"})
    return jsonify({"Erro": "E-mail não digitado!"})


@app.route("/trocasenha", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def trocasenha():
    user = Usuarios()
    body = request.json
    retorno = user.TrocaSenha(body["idUser"], body["pass"])

    return jsonify({"resultado": retorno})


@app.route("/upuser", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
@token_required
def myuser():
    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")

    body = request.json
    user = Usuarios()
    retorno = user.updateUser(token_data["id"], body)

    if retorno[0] != "OK":
        return jsonify({"Erro": retorno}), 400

    dados_user = user.consultaUser(retorno[1])
    token = jwt.encode(
        {
            "id": dados_user["id"],
            "name": dados_user["name"],
            "email": dados_user["email"],
            "picture": dados_user["picture"],
            "tel": dados_user["tel"],
            "cpf": dados_user["cpf"],
            "expiration": str(datetime.utcnow() + timedelta(minutes=20)),
        },
        app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    return jsonify({"token": token})


@app.route("/myticket", methods=["GET"])
@cross_origin()
@cache.cached(timeout=5)
@token_required
def myTicket():
    token = request.headers.get("Authorization")
    ticket = Ticket()
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
    data = ticket.myTickets(token_data["id"])
    transacoes = ticket.myTransactions(token_data["id"])

    return jsonify({"resultado": data, "transacoes": transacoes})


@app.route("/caduser", methods=["POST"])
@cross_origin()
def cadUser():
    usuario = Usuarios()
    body = request.json
    ret = usuario.CriaUsuario(body)
    if ret[0] == "OK":
        mail = EMAIL()
        teste = mail.SendCad(ret[1], ret[2])
        return jsonify({"status": ret})

    return jsonify({"status": ret}), 400


###########################  PAGAMENTO  ##########################################


@app.route("/getlink", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
@token_required
def getlink():
    linkPag = LinkPagamento()
    body = request.json
    site = linkPag.GeraLink(
        body["id"], body["qtd"], body["User"], body["cupom"], body["participantes"],body["isBrothers"]
    )
    print(site)
    if site[0] == "OK":
        return jsonify({"resultado": site[1]})
    return jsonify({"resultado": site[0]}), 400


@app.route("/validacupom", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def validaCupom():
    cupom = Cupom()
    body = request.json
    codCupom = body["codCupom"]
    idEvento = body["idEvento"]

    status = cupom.validaCupom(idEvento, codCupom)
    if status[0] == "Valido":
        return jsonify({"Status": status[0], "porcentagem": status[1]})
    else:
        return jsonify({"Status": status[0], "porcentagem": status[1]}), 400


#############################  TICKET  ###########################################


@app.route("/saveTicket", methods=["POST"])
@cross_origin()
@token_required
@cache.cached(timeout=5)
def saveTicket():
    body = request.json
    pagamento = LinkPagamento()
    retorno = pagamento.saveTicket(body["preference_id"])
    return jsonify({"status": retorno[0], "idEvento": retorno[1], "ticket": retorno[2]})


@app.route("/setpending", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def setpending():
    body = request.json
    pagamento = LinkPagamento()
    retorno = pagamento.SetCancel(body["preferences"])

    return jsonify({"resultado": retorno})


@app.route("/freeticket", methods=["POST"])
@cross_origin()
@cache.cached(timeout=1)
@token_required
def ticketFree():
    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
    ticket = Ticket()
    retorno = ticket.saveTicketFree(token_data["id"], request.json)

    return jsonify({"status": retorno[0], "idEvento": retorno[1], "ticket": retorno[2]})


@app.route("/resendmail", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def resendmail():
    body = request.json
    email = EMAIL()
    retorno = email.ResendTicket(body["email"], body["codigo"])

    return jsonify({"resultado": retorno})


############################  VENDEDOR  ##########################################


@app.route("/loginVendedor", methods=["POST"])
@cross_origin()
def loginVendedor():
    usuario = Usuarios()
    password = bcrypt.hashpw(
        bytes(request.json["password"], encoding="utf8"),
        bytes(usuario.salt, encoding="utf8"),
    )
    email = request.json["email"]

    if email:
        cryptPass = usuario.consultaPassVend(email)

        if cryptPass:
            if str(password, "utf-8") == cryptPass:
                session["logged_in"] = True
                dados_user = usuario.consultaVend(email)
                token = jwt.encode(
                    {
                        "id": dados_user["id"],
                        "name": dados_user["name"],
                        "email": dados_user["email"],
                        "picture": dados_user["picture"],
                        "tel": dados_user["tel"],
                        "cnpj": dados_user["cnpj"],
                        "expiration": str(datetime.utcnow() + timedelta(minutes=20)),
                    },
                    app.config["SECRET_KEY"],
                    algorithm="HS256",
                )
                return jsonify({"token": token})
            else:
                return jsonify({"Erro": "Senha Incorreta!"})
        else:
            return jsonify({"Erro": "E-mail não cadastrado!"})
    else:
        return jsonify({"Erro": "E-mail não digitado!"})


@app.route("/myeventos", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
@token_required
def myeventos():
    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")
    evento = EventosRepo()

    retorno = evento.select_mine(token_data["id"])

    return jsonify({"resultado": retorno})


###########################  BILHETERIA  #########################################


@app.route("/loginbilheteria", methods=["POST"])
@cross_origin()
@cache.cached(timeout=5)
def loginbilheteria():
    bilheteria = Bilheteria()
    body = request.json

    login = bilheteria.login(body)
    if login[1] == 200:
        token = jwt.encode(
            {
                "idEvento": body["evento"],
                "expiration": str(datetime.utcnow() + timedelta(minutes=20)),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return jsonify({"token": token})
    return jsonify({"status": login[0]}), login[1]


@app.route("/checkticket", methods=["POST"])
@cross_origin()
@token_required
@cache.cached(timeout=1)
def checkticket():
    bilheteria = Bilheteria()
    body = request.json

    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")

    codigo = body["codigo"]
    idEvento = token_data["idEvento"]

    status = bilheteria.ticket(codigo, idEvento)
    if status[0] == "Valido":
        return jsonify({"Status": status[0], "porcentagem": status[1]})
    else:
        return jsonify({"Status": status[0]}), 400


@app.route("/pesquisa", methods=["POST"])
@cross_origin()
@token_required
@cache.cached(timeout=1)
def pesquisa():
    bilheteria = Bilheteria()

    body = request.json
    token = request.headers.get("Authorization")
    token_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")

    cpf = body["cpf"]
    idEvento = token_data["idEvento"]

    status = bilheteria.pesquisa(cpf, idEvento)
    if status[0] == "Valido":
        return jsonify({"tickets": status[1]})
    else:
        return jsonify({"Status": status[0]}), 400


##############3 TESTE #############################


@app.route("/rodascript", methods=["POST"])
@cross_origin()
@token_required
@cache.cached(timeout=1)
def rodascript():
    teste = testePag()

    body = request.json

    status = teste.rodaScript(body)
    if status[0] == "OK":
        return jsonify({"tickets": "OK"})
    else:
        return jsonify({"Status": status}), 400
