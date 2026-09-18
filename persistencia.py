"""PB14: cliente HTTPS do banco central. Configure com configurar_conexao.py."""
import json
import os
from pathlib import Path
import sqlite3
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

RAIZ = Path(__file__).resolve().parent


class RegistroNaoEncontrado(ValueError):
    """Registro inexistente ou não pertencente ao usuário informado."""


class ErroConexao(RuntimeError):
    """Falha de configuração, autenticação ou comunicação com o banco central."""


class _SemRedirecionamento(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Não enviar o token para outro endereço.


class BancoDados:
    def __init__(self, url=None, token=None):
        local = RAIZ / ".pb14.local.json"
        config = json.loads(local.read_text(encoding="utf-8")) if local.exists() else {}
        servidor = json.loads((RAIZ / "database" / "servidor.json").read_text(encoding="utf-8"))
        self.url = (url or os.getenv("PB14_API_URL") or config.get("url") or servidor.get("url") or "").rstrip("/")
        self._token = token or os.getenv("PB14_API_TOKEN") or config.get("token")
        destino = urlsplit(self.url)
        if (destino.scheme != "https" or not destino.hostname or destino.username
                or destino.password or destino.query or destino.fragment):
            raise ErroConexao("Configure a URL HTTPS com python configurar_conexao.py.")
        if not isinstance(self._token, str) or not self._token.strip():
            raise ErroConexao("Configure a chave da equipe com python configurar_conexao.py.")
        self._http = build_opener(_SemRedirecionamento())

    def _chamar(self, operacao, **dados):
        requisicao = Request(
            f"{self.url}/rpc/{operacao}",
            data=json.dumps(dados, allow_nan=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json",
                     "User-Agent": "CP2-PB14/1.0"},
            method="POST",
        )
        try:
            with self._http.open(requisicao, timeout=20) as resposta:
                return json.load(resposta)["resultado"]
        except HTTPError as erro:
            status = erro.code
            erro.close()
            if status in (401, 403):
                raise ErroConexao("Chave da equipe ausente ou inválida.") from None
            if status == 404:
                raise RegistroNaoEncontrado("Registro não encontrado para este usuário.") from None
            if status == 409:
                raise sqlite3.IntegrityError("Registro duplicado, vínculo inválido ou imóvel com histórico.") from None
            if status in (400, 413):
                raise ValueError("Dados inválidos ou acima do tamanho permitido.") from None
            raise ErroConexao(f"Servidor indisponível (HTTP {status}).") from None
        except (URLError, TimeoutError, OSError):
            raise ErroConexao("Não foi possível acessar o banco central. Confira a conexão.") from None
        except (json.JSONDecodeError, KeyError):
            raise ErroConexao("O servidor retornou uma resposta inesperada.") from None

    def inicializar(self):
        """Verifica a conexão; a estrutura remota é criada pelo mantenedor."""
        return self._chamar("verificar_conexao")

    def salvar_usuario(self, nome, email, senha_hash):
        return self._chamar("salvar_usuario", nome=nome, email=email, senha_hash=senha_hash)

    def buscar_usuario_por_email(self, email):
        return self._chamar("buscar_usuario_por_email", email=email)

    def salvar_imovel(self, usuario_id, identificacao, localidade, tipo):
        return self._chamar("salvar_imovel", usuario_id=usuario_id, identificacao=identificacao,
                            localidade=localidade, tipo=tipo)

    def listar_imoveis(self, usuario_id):
        return self._chamar("listar_imoveis", usuario_id=usuario_id)

    def buscar_imovel(self, usuario_id, imovel_id):
        return self._chamar("buscar_imovel", usuario_id=usuario_id, imovel_id=imovel_id)

    def atualizar_imovel(self, usuario_id, imovel_id, identificacao, localidade, tipo):
        return self._chamar("atualizar_imovel", usuario_id=usuario_id, imovel_id=imovel_id,
                            identificacao=identificacao, localidade=localidade, tipo=tipo)

    def excluir_imovel(self, usuario_id, imovel_id):
        return self._chamar("excluir_imovel", usuario_id=usuario_id, imovel_id=imovel_id)

    def salvar_consumo(self, usuario_id, imovel_id, ano, mes, consumo_kwh):
        return self._chamar("salvar_consumo", usuario_id=usuario_id, imovel_id=imovel_id,
                            ano=ano, mes=mes, consumo_kwh=consumo_kwh)

    def listar_consumos(self, usuario_id, imovel_id):
        return self._chamar("listar_consumos", usuario_id=usuario_id, imovel_id=imovel_id)


if __name__ == "__main__":
    try:
        BancoDados().inicializar()
    except ErroConexao as erro:
        raise SystemExit(str(erro))
    print("Conexão com o banco central confirmada.")
