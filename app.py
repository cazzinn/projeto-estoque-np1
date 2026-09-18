import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


PASTA = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(PASTA, "estoque.db")


def conectar():
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    with conectar() as conexao:
        with open(os.path.join(PASTA, "database.sql"), encoding="utf-8") as arquivo:
            conexao.executescript(arquivo.read())


class Servidor(BaseHTTPRequestHandler):
    def responder_json(self, dados, status=200):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def ler_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(tamanho).decode("utf-8"))

    def servir_arquivo(self, nome, tipo):
        caminho = os.path.join(PASTA, nome)
        try:
            with open(caminho, "rb") as arquivo:
                corpo = arquivo.read()
            self.send_response(200)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
        except FileNotFoundError:
            self.responder_json({"erro": "Arquivo não encontrado"}, 404)

    def do_GET(self):
        rota = urlparse(self.path).path
        if rota == "/":
            return self.servir_arquivo("index.html", "text/html; charset=utf-8")
        if rota == "/style.css":
            return self.servir_arquivo("style.css", "text/css; charset=utf-8")
        if rota == "/script.js":
            return self.servir_arquivo("script.js", "text/javascript; charset=utf-8")
        if rota == "/api/categorias":
            with conectar() as conexao:
                dados = conexao.execute("SELECT Id, Nome FROM Categorias ORDER BY Nome").fetchall()
            return self.responder_json([dict(item) for item in dados])
        if rota == "/api/produtos":
            with conectar() as conexao:
                dados = conexao.execute("""
                    SELECT p.Id, p.Nome, p.Quantidade, p.Preco, p.CategoriaId,
                           c.Nome AS Categoria
                    FROM Produtos p
                    INNER JOIN Categorias c ON c.Id = p.CategoriaId
                    ORDER BY p.Id DESC
                """).fetchall()
            return self.responder_json([dict(item) for item in dados])
        self.responder_json({"erro": "Rota não encontrada"}, 404)

    def do_POST(self):
        if urlparse(self.path).path != "/api/produtos":
            return self.responder_json({"erro": "Rota não encontrada"}, 404)
        try:
            dados = self.ler_json()
            nome = dados.get("nome", "").strip()
            quantidade = int(dados.get("quantidade", 0))
            preco = float(dados.get("preco", 0))
            categoria_id = int(dados.get("categoriaId", 0))
            if not nome or quantidade < 0 or preco < 0 or categoria_id <= 0:
                return self.responder_json({"erro": "Preencha os campos corretamente"}, 400)
            with conectar() as conexao:
                cursor = conexao.execute(
                    "INSERT INTO Produtos (Nome, Quantidade, Preco, CategoriaId) VALUES (?, ?, ?, ?)",
                    (nome, quantidade, preco, categoria_id),
                )
            self.responder_json({"mensagem": "Produto cadastrado", "id": cursor.lastrowid}, 201)
        except (ValueError, json.JSONDecodeError, sqlite3.Error) as erro:
            self.responder_json({"erro": str(erro)}, 400)

    def do_PUT(self):
        partes = urlparse(self.path).path.strip("/").split("/")
        if len(partes) != 3 or partes[:2] != ["api", "produtos"]:
            return self.responder_json({"erro": "Rota não encontrada"}, 404)
        try:
            produto_id = int(partes[2])
            dados = self.ler_json()
            nome = dados.get("nome", "").strip()
            quantidade = int(dados.get("quantidade", 0))
            preco = float(dados.get("preco", 0))
            categoria_id = int(dados.get("categoriaId", 0))
            if not nome or quantidade < 0 or preco < 0 or categoria_id <= 0:
                return self.responder_json({"erro": "Preencha os campos corretamente"}, 400)
            with conectar() as conexao:
                cursor = conexao.execute("""
                    UPDATE Produtos SET Nome = ?, Quantidade = ?, Preco = ?, CategoriaId = ?
                    WHERE Id = ?
                """, (nome, quantidade, preco, categoria_id, produto_id))
            if cursor.rowcount == 0:
                return self.responder_json({"erro": "Produto não encontrado"}, 404)
            self.responder_json({"mensagem": "Produto atualizado"})
        except (ValueError, json.JSONDecodeError, sqlite3.Error) as erro:
            self.responder_json({"erro": str(erro)}, 400)

    def do_DELETE(self):
        partes = urlparse(self.path).path.strip("/").split("/")
        if len(partes) != 3 or partes[:2] != ["api", "produtos"]:
            return self.responder_json({"erro": "Rota não encontrada"}, 404)
        try:
            produto_id = int(partes[2])
            with conectar() as conexao:
                cursor = conexao.execute("DELETE FROM Produtos WHERE Id = ?", (produto_id,))
            if cursor.rowcount == 0:
                return self.responder_json({"erro": "Produto não encontrado"}, 404)
            self.responder_json({"mensagem": "Produto excluído"})
        except (ValueError, sqlite3.Error) as erro:
            self.responder_json({"erro": str(erro)}, 400)


if __name__ == "__main__":
    criar_banco()
    servidor = HTTPServer(("localhost", 8000), Servidor)
    print("Sistema disponível em http://localhost:8000")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        servidor.server_close()

