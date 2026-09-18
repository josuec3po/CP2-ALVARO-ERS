from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from imoveis import executar_menu_imoveis
from persistencia import ErroConexao
from tests.banco_local import BancoDados


class ImoveisTests(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.caminho = Path(temporario.name) / "teste.db"
        self.banco = BancoDados(self.caminho)
        self.banco.inicializar()
        self.usuario = self.banco.salvar_usuario("Ana", "ana@example.test", "hash-sintetico")
        self.outro = self.banco.salvar_usuario("Bia", "bia@example.test", "hash-sintetico")

    def menu(self, respostas, usuario=None):
        respostas = iter(respostas)
        mensagens = []

        def entrada(prompt):
            return next(respostas)

        executar_menu_imoveis(self.usuario if usuario is None else usuario, self.banco,
                             entrada=entrada, saida=mensagens.append)
        return "\n".join(mensagens)

    def criar(self):
        return self.banco.salvar_imovel(self.usuario, "Casa", "São Paulo", "Casa")

    def test_cadastro_rejeita_vazios_e_persiste_com_vinculo(self):
        saida = self.menu(["1", "  ", " Minha casa ", "", " São Paulo ", "", "Casa", "0"])
        registro = BancoDados(self.caminho).listar_imoveis(self.usuario)[0]
        self.assertEqual(registro["identificacao"], "Minha casa")
        self.assertEqual(registro["localidade"], "São Paulo")
        self.assertEqual(registro["tipo"], "Casa")
        self.assertEqual(registro["usuario_id"], self.usuario)
        self.assertEqual(saida.count("é obrigatório"), 3)
        self.assertIn("cadastrado com sucesso", saida)

    def test_campo_longo_e_cancelamento_nao_gravam(self):
        saida = self.menu(["1", "x" * 2001, "Casa", ":cancelar", "0"])
        self.assertIn("2.000", saida)
        self.assertEqual(self.banco.listar_imoveis(self.usuario), [])

    def test_edicao_preserva_campos_com_enter(self):
        imovel = self.criar()
        saida = self.menu(["3", "1", "Casa nova", "", "", "0"])
        registro = BancoDados(self.caminho).buscar_imovel(self.usuario, imovel)
        self.assertEqual(registro["identificacao"], "Casa nova")
        self.assertEqual(registro["localidade"], "São Paulo")
        self.assertEqual(registro["tipo"], "Casa")
        self.assertIn("atualizado com sucesso", saida)

    def test_edicao_cancelada_descarta_todos_os_campos(self):
        imovel = self.criar()
        saida = self.menu(["3", "1", "Nome novo", ":cancelar", "0"])
        self.assertEqual(self.banco.buscar_imovel(self.usuario, imovel)["identificacao"], "Casa")
        self.assertIn("cancelada", saida)

    def test_sem_alteracao_nao_envia_gravacao(self):
        self.criar()
        with patch.object(self.banco, "atualizar_imovel") as gravar:
            saida = self.menu(["3", "1", "", "", "", "0"])
        gravar.assert_not_called()
        self.assertIn("Nenhuma alteração", saida)

    def test_exclusao_precisa_de_confirmacao_explicita(self):
        self.criar()
        for resposta in ("", "n", "sim", "qualquer coisa"):
            with self.subTest(resposta=resposta):
                saida = self.menu(["4", "1", resposta, "0"])
                self.assertEqual(len(self.banco.listar_imoveis(self.usuario)), 1)
                self.assertIn("cancelada", saida)
                self.assertNotIn("excluído com sucesso", saida)

    def test_exclusao_confirmada_persiste(self):
        self.criar()
        saida = self.menu(["4", "1", "EXCLUIR", "0"])
        self.assertEqual(BancoDados(self.caminho).listar_imoveis(self.usuario), [])
        self.assertIn("excluído com sucesso", saida)

    def test_exclusao_com_consumo_preserva_historico(self):
        imovel = self.criar()
        self.banco.salvar_consumo(self.usuario, imovel, 2026, 1, 100)
        saida = self.menu(["4", "1", "EXCLUIR", "0"])
        self.assertIn("Exclusão bloqueada", saida)
        self.assertEqual(len(self.banco.listar_consumos(self.usuario, imovel)), 1)
        self.assertEqual(len(self.banco.listar_imoveis(self.usuario)), 1)

    def test_listagem_e_selecao_nao_expoem_outro_usuario(self):
        self.banco.salvar_imovel(self.outro, "Imóvel privado", "Outra cidade", "Casa")
        imovel = self.criar()
        saida = self.menu(["3", "texto", "-1", "99", "1", "Novo", "", "", "0"])
        self.assertNotIn("Imóvel privado", saida)
        self.assertEqual(self.banco.buscar_imovel(self.usuario, imovel)["identificacao"], "Novo")
        self.assertEqual(self.banco.listar_imoveis(self.outro)[0]["identificacao"], "Imóvel privado")

    def test_menu_vazio_opcao_invalida_e_cancelar_selecao(self):
        saida = self.menu(["abc", "2", "3", "4", "0"])
        self.assertIn("Opção inválida", saida)
        self.assertEqual(saida.count("ainda não tem imóveis"), 3)
        self.criar()
        self.assertIn("cancelada", self.menu(["4", "0", "0"]))

    def test_falha_de_rede_nao_confirma_sucesso(self):
        with patch.object(self.banco, "salvar_imovel", side_effect=ErroConexao("offline")):
            saida = self.menu(["1", "Casa", "SP", "Casa", "0"])
        self.assertIn("Não foi possível confirmar", saida)
        self.assertNotIn("cadastrado com sucesso", saida)

    def test_sessao_invalida_nao_abre_menu(self):
        for usuario in (None, True, 0, -1, "1"):
            with self.subTest(usuario=usuario), self.assertRaises(ValueError):
                executar_menu_imoveis(usuario, self.banco)

    def test_interrupcao_antes_de_confirmar_nao_exclui(self):
        self.criar()
        entradas = iter(["4", "1"])

        def entrada(prompt):
            try:
                return next(entradas)
            except StopIteration:
                raise EOFError()

        executar_menu_imoveis(self.usuario, self.banco, entrada=entrada, saida=lambda _: None)
        self.assertEqual(len(self.banco.listar_imoveis(self.usuario)), 1)


if __name__ == "__main__":
    unittest.main()
