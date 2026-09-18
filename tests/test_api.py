"""Testes reais da API. Defina PB14_TEST_URL e PB14_TEST_TOKEN para executar.

Use o emulador local; estes testes criam registros de teste identificados por UUID.
"""
import json
import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


@unittest.skipUnless(os.getenv("PB14_TEST_URL"), "Requer API de teste em execução")
class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.environ["PB14_TEST_URL"]
        cls.token = os.environ["PB14_TEST_TOKEN"]

    def rpc(self, operacao, dados=None, token=None):
        request = Request(
            self.url + "/rpc/" + operacao,
            data=json.dumps(dados or {}).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + (self.token if token is None else token)},
        )
        try:
            with urlopen(request, timeout=20) as response:
                return response.status, json.load(response)
        except HTTPError as erro:
            with erro:
                return erro.code, json.load(erro)

    def criar(self, operacao, **dados):
        status, resposta = self.rpc(operacao, dados)
        self.assertEqual(status, 200, resposta)
        return resposta["resultado"]

    def test_acesso_sem_chave_valida(self):
        self.assertEqual(self.rpc("verificar_conexao", token="")[0], 401)
        self.assertEqual(self.rpc("verificar_conexao", token="errada")[0], 401)

    def test_fluxo_completo_e_integridade(self):
        email = f"qa-{uuid4().hex}@example.test"
        usuario = self.criar("salvar_usuario", nome="Teste PB14", email=email, senha_hash="hash-sintetico-de-teste")
        outro = self.criar("salvar_usuario", nome="Outro", email="outro-" + email, senha_hash="hash-sintetico")
        imovel = self.criar("salvar_imovel", usuario_id=usuario, identificacao="Casa", localidade="São Paulo", tipo="Casa")
        self.assertEqual(self.rpc("salvar_usuario", {"nome": "Duplicado", "email": email.upper(), "senha_hash": "teste"})[0], 409)
        self.criar("atualizar_imovel", usuario_id=usuario, imovel_id=imovel, identificacao="Casa editada", localidade="Santos", tipo="Casa")
        self.assertEqual(self.criar("buscar_imovel", usuario_id=usuario, imovel_id=imovel)["identificacao"], "Casa editada")
        for operacao in ("buscar_imovel", "excluir_imovel", "listar_consumos"):
            self.assertEqual(self.rpc(operacao, {"usuario_id": outro, "imovel_id": imovel})[0], 404)
        self.assertEqual(self.criar("listar_imoveis", usuario_id=outro), [])
        dados = dict(usuario_id=usuario, imovel_id=imovel, ano=2026, mes=2, consumo_kwh=0)
        self.criar("salvar_consumo", **dados)
        self.assertEqual(self.rpc("salvar_consumo", dados)[0], 409)
        self.criar("salvar_consumo", **{**dados, "ano": 2025, "mes": 12, "consumo_kwh": 320.5})
        historico = self.criar("listar_consumos", usuario_id=usuario, imovel_id=imovel)
        self.assertEqual([(r["ano"], r["mes"]) for r in historico], [(2025, 12), (2026, 2)])
        self.assertEqual(historico[0]["consumo_kwh"], 320.5)
        self.assertEqual(self.rpc("excluir_imovel", {"usuario_id": usuario, "imovel_id": imovel})[0], 409)
        for alteracao in ({"mes": 13}, {"consumo_kwh": -1}, {"consumo_kwh": "320"}, {"usuario_id": True}):
            self.assertEqual(self.rpc("salvar_consumo", {**dados, **alteracao})[0], 400)
        self.assertEqual(self.rpc("salvar_consumo", {**dados, "usuario_id": outro})[0], 404)
        self.assertEqual(len(self.criar("listar_consumos", usuario_id=usuario, imovel_id=imovel)), 2)
        vazio = self.criar("salvar_imovel", usuario_id=usuario, identificacao="Vazio", localidade="SP", tipo="Casa")
        self.criar("excluir_imovel", usuario_id=usuario, imovel_id=vazio)
        self.assertEqual(self.rpc("buscar_imovel", {"usuario_id": usuario, "imovel_id": vazio})[0], 404)

    def test_rejeita_corpo_excessivo_e_operacao_desconhecida(self):
        self.assertEqual(self.rpc("verificar_conexao", {"excesso": "a" * 9000})[0], 413)
        self.assertEqual(self.rpc("sql_livre", {"sql": "DROP TABLE usuarios"})[0], 404)


if __name__ == "__main__":
    unittest.main()
