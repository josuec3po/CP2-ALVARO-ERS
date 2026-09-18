import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from persistencia import BancoDados, ErroConexao, RegistroNaoEncontrado


class ClienteTests(unittest.TestCase):
    def setUp(self):
        self.banco = BancoDados(url="https://teste.example", token="chave-sintetica")

    def test_nao_envia_chave_por_http(self):
        with self.assertRaises(ErroConexao):
            BancoDados(url="http://teste.example", token="chave-sintetica")

    def test_envia_dados_e_retorna_resultado(self):
        with patch.object(self.banco._http, "open", return_value=io.BytesIO(b'{"resultado": 7}')) as abrir:
            self.assertEqual(self.banco.salvar_imovel(2, "Casa", "SP", "Casa"), 7)
            request = abrir.call_args.args[0]
            self.assertEqual(request.full_url, "https://teste.example/rpc/salvar_imovel")
            self.assertEqual(request.get_header("Authorization"), "Bearer chave-sintetica")
            self.assertEqual(request.get_header("User-agent"), "CP2-PB14/1.0")

    def test_erros_http_sem_expor_credenciais(self):
        for status, classe in [(401, ErroConexao), (404, RegistroNaoEncontrado), (500, ErroConexao)]:
            erro = HTTPError("https://teste.example", status, "falha", {}, None)
            with self.subTest(status=status), patch.object(self.banco._http, "open", side_effect=erro):
                with self.assertRaises(classe) as contexto:
                    self.banco.inicializar()
                self.assertNotIn("chave-sintetica", str(contexto.exception))

    def test_falha_de_rede_nao_cria_banco_local(self):
        with patch.object(self.banco._http, "open", side_effect=URLError("offline")):
            with self.assertRaises(ErroConexao):
                self.banco.inicializar()


if __name__ == "__main__":
    unittest.main()
