import os

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tareas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Tarea {self.titulo}>"


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    tareas = Tarea.query.order_by(Tarea.id.desc()).all()
    return render_template("index.html", tareas=tareas)


@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if titulo:
            tarea = Tarea(titulo=titulo, descripcion=descripcion or None)
            db.session.add(tarea)
            db.session.commit()

        return redirect(url_for("index"))

    return render_template("form.html", tarea=None, accion="Nueva tarea")


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    tarea = db.session.get(Tarea, id)
    if tarea is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        if titulo:
            tarea.titulo = titulo
            tarea.descripcion = descripcion or None
            db.session.commit()

        return redirect(url_for("index"))

    return render_template("form.html", tarea=tarea, accion="Editar tarea")


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    tarea = db.session.get(Tarea, id)
    if tarea is not None:
        db.session.delete(tarea)
        db.session.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
