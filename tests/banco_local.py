"""Adaptador SQLite exclusivo dos testes automatizados."""

from contextlib import contextmanager
import math
from pathlib import Path
import sqlite3


RAIZ = Path(__file__).resolve().parents[1]


class RegistroNaoEncontrado(ValueError):
    """O registro não existe ou não pertence ao usuário informado."""


def _texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} deve ser um texto não vazio.")
    return valor.strip()


class BancoDados:
    """Uma conexão por operação; gravações confirmadas ou revertidas por inteiro.

    usuario_id deve vir da sessão autenticada, nunca de uma escolha livre na UI.
    O arquivo deve ser local; não usar :memory: ou compartilhar via pasta de rede.
    """

    def __init__(self, caminho):
        if str(caminho) == ":memory:":
            raise ValueError("Informe um arquivo para garantir persistência.")
        self.caminho = Path(caminho).resolve()

    @contextmanager
    def _conexao(self):
        conexao = sqlite3.connect(self.caminho, timeout=10)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        try:
            with conexao:
                yield conexao
        finally:
            conexao.close()

    def inicializar(self):
        """Cria a estrutura se necessário, sem apagar registros existentes."""
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        with self._conexao() as conexao:
            conexao.executescript((RAIZ / "database" / "schema.sql").read_text(encoding="utf-8"))

    def salvar_usuario(self, nome, email, senha_hash):
        """Persiste o hash já produzido pelo módulo de usuários; não faz login.

        O chamador deve gerar um hash de senha apropriado, nunca passar a senha
        em texto puro. Validação de e-mail e política de senha pertencem a PB01.
        """
        dados = (_texto(nome, "nome"), _texto(email, "email").lower(),
                 _texto(senha_hash, "senha_hash"))
        with self._conexao() as conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)", dados
            )
            return cursor.lastrowid

    def buscar_usuario_por_email(self, email):
        """Uso interno de PB02: inclui senha_hash para verificar credenciais."""
        with self._conexao() as conexao:
            linha = conexao.execute(
                "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
                (_texto(email, "email").lower(),),
            ).fetchone()
            return dict(linha) if linha else None

    @staticmethod
    def _exigir_imovel(conexao, usuario_id, imovel_id):
        linha = conexao.execute(
            "SELECT * FROM imoveis WHERE id = ? AND usuario_id = ?",
            (imovel_id, usuario_id),
        ).fetchone()
        if linha is None:
            raise RegistroNaoEncontrado("Imóvel não encontrado para este usuário.")
        return dict(linha)

    def salvar_imovel(self, usuario_id, identificacao, localidade, tipo):
        dados = (usuario_id, _texto(identificacao, "identificacao"),
                 _texto(localidade, "localidade"), _texto(tipo, "tipo"))
        with self._conexao() as conexao:
            cursor = conexao.execute(
                "INSERT INTO imoveis (usuario_id, identificacao, localidade, tipo) "
                "VALUES (?, ?, ?, ?)", dados,
            )
            return cursor.lastrowid

    def listar_imoveis(self, usuario_id):
        with self._conexao() as conexao:
            return [dict(linha) for linha in conexao.execute(
                "SELECT * FROM imoveis WHERE usuario_id = ? ORDER BY id", (usuario_id,)
            )]

    def buscar_imovel(self, usuario_id, imovel_id):
        with self._conexao() as conexao:
            return self._exigir_imovel(conexao, usuario_id, imovel_id)

    def atualizar_imovel(self, usuario_id, imovel_id, identificacao, localidade, tipo):
        dados = (_texto(identificacao, "identificacao"), _texto(localidade, "localidade"),
                 _texto(tipo, "tipo"), imovel_id, usuario_id)
        with self._conexao() as conexao:
            self._exigir_imovel(conexao, usuario_id, imovel_id)
            conexao.execute(
                "UPDATE imoveis SET identificacao = ?, localidade = ?, tipo = ? "
                "WHERE id = ? AND usuario_id = ?", dados,
            )

    def excluir_imovel(self, usuario_id, imovel_id):
        """PB04 deve pedir confirmação antes de chamar. Histórico bloqueia exclusão."""
        with self._conexao() as conexao:
            self._exigir_imovel(conexao, usuario_id, imovel_id)
            conexao.execute(
                "DELETE FROM imoveis WHERE id = ? AND usuario_id = ?", (imovel_id, usuario_id)
            )

    def salvar_consumo(self, usuario_id, imovel_id, ano, mes, consumo_kwh):
        if type(ano) is not int or not 1 <= ano <= 9999:
            raise ValueError("ano deve ser um inteiro entre 1 e 9999.")
        if type(mes) is not int or not 1 <= mes <= 12:
            raise ValueError("mes deve ser um inteiro entre 1 e 12.")
        if (type(consumo_kwh) not in (int, float)
                or not math.isfinite(consumo_kwh) or consumo_kwh < 0):
            raise ValueError("consumo_kwh deve ser um número finito não negativo.")
        with self._conexao() as conexao:
            self._exigir_imovel(conexao, usuario_id, imovel_id)
            cursor = conexao.execute(
                "INSERT INTO consumos (imovel_id, ano, mes, consumo_kwh) VALUES (?, ?, ?, ?)",
                (imovel_id, ano, mes, consumo_kwh),
            )
            return cursor.lastrowid

    def listar_consumos(self, usuario_id, imovel_id):
        with self._conexao() as conexao:
            self._exigir_imovel(conexao, usuario_id, imovel_id)
            return [dict(linha) for linha in conexao.execute(
                "SELECT id, imovel_id, ano, mes, consumo_kwh FROM consumos "
                "WHERE imovel_id = ? ORDER BY ano, mes", (imovel_id,),
            )]
