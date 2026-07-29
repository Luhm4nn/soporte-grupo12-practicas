import os
import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class PatenteRequest(BaseModel):
    patente: str


def verificar(patente):
    _DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patentes.db")
    conn = sqlite3.connect(_DB)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM autorizadas WHERE patente = ?", (patente,))
    existe = cur.fetchone() is not None
    conn.close()
    return existe


@app.post("/verificar")
def verificar_patente(data: PatenteRequest):
    existe = verificar(data.patente.upper())
    return {"patente": data.patente.upper(), "autorizado": existe}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
