from flask import Flask, render_template, request, session
from flask_session import Session
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
ROLES = ['estudiante','profesor']

app = Flask(__name__)
dbUser = os.environ['dbUser']
dbPass = os.environ['dbPass']
client = pymongo.MongoClient(f"mongodb+srv://{dbUser}:{dbPass}@cluster0.jorut.mongodb.net/oneminute?retryWrites=true&w=majority")
db = client.oneminute


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        msgError = ""
        nuevoUsuario = {}
        print(request.form)
        if "nombres" in request.form:
            nuevoUsuario["nombres"] = request.form.get("nombres").strip()
            if not nuevoUsuario["nombres"]:
                msgError += "Debe ingresar un nombre valido. "

        if "apelliidos" in request.form:
            nuevoUsuario["apelliidos"] = request.form.get("apelliidos").strip()
            if not nuevoUsuario["apelliidos"]:
                msgError += "Debe ingresar un apelliidos valido. "

        if "correo" in request.form:
            nuevoUsuario["correo"] = request.form.get("correo").strip()
            if not nuevoUsuario["correo"]:
                msgError += "Debe ingresar un correo valido. "
            elif not EMAIL_REGEX.match(nuevoUsuario["correo"]):
                msgError += "Debe ingresar un correo valido. "
        if "rol" in request.form:
            nuevoUsuario["roles"] = [request.form.get("rol").strip()]
            if nuevoUsuario["roles"][0] not in ROLES:
                msgError += "Debe ingresar un rol valido. "
            elif nuevoUsuario["roles"][0] == ROLES[1]:
                nuevoUsuario["roles"].append(ROLES[0])
        if "clave" in request.form:
            nuevoUsuario["clave"] = request.form.get("clave")
            if not nuevoUsuario["clave"]:
                msgError += "Debe ingresar una conteseña valida. "
            else:
                if "confClave" in request.form:
                    if nuevoUsuario["clave"] != request.form.get("confClave"):
                        msgError += "Las dos contraseñas deben coincidir. "
        if msgError != "":
            return render_template("register.html", msg=msgError)
        else:
            nuevoUsuario["clave"] = generate_password_hash(nuevoUsuario["clave"])
            try:
                result = db.usuarios.insert_one(nuevoUsuario)
            except pymongo.errors.DuplicateKeyError:
                msgError += " El correro ingresado no esta disponible"
            return render_template("index.html", user = nuevoUsuario, result = result)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500)