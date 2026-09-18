import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from tests.banco_local import BancoDados, RegistroNaoEncontrado


class PersistenciaTests(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.caminho = Path(self.temporario.name) / "energia.db"
        self.banco = BancoDados(self.caminho)
        self.banco.inicializar()
        # Sentinela de teste; autenticação e geração de hashes pertencem a PB01/02.
        self.usuario = self.banco.salvar_usuario("Ana", "ana@example.test", "hash-teste-ana")
        self.outro = self.banco.salvar_usuario("Bia", "bia@example.test", "hash-teste-bia")
        self.imovel = self.banco.salvar_imovel(self.usuario, "Casa", "São Paulo", "Casa")

    def test_dados_sobrevivem_em_outro_processo(self):
        self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 8, 320.5)
        codigo = (
            "import json, sys; from tests.banco_local import BancoDados; "
            "b = BancoDados(sys.argv[1]); b.inicializar(); "
            "print(json.dumps([b.listar_imoveis(int(sys.argv[2])), "
            "b.listar_consumos(int(sys.argv[2]), int(sys.argv[3]))]))"
        )
        resultado = subprocess.run(
            [sys.executable, "-c", codigo, str(self.caminho), str(self.usuario), str(self.imovel)],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
            check=True, timeout=15,
        )
        imoveis, consumos = json.loads(resultado.stdout)
        self.assertEqual(imoveis[0]["usuario_id"], self.usuario)
        self.assertEqual(imoveis[0]["localidade"], "São Paulo")
        self.assertEqual(consumos[0]["consumo_kwh"], 320.5)

    def test_inicializacao_repetida_preserva_dados(self):
        self.banco.inicializar()
        self.assertEqual(len(self.banco.listar_imoveis(self.usuario)), 1)

    def test_email_unico_e_normalizado(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.salvar_usuario("Ana 2", " ANA@EXAMPLE.TEST ", "hash-teste")
        usuario = self.banco.buscar_usuario_por_email("ANA@example.test")
        self.assertEqual(usuario["id"], self.usuario)
        self.assertIsNone(self.banco.buscar_usuario_por_email("ausente@example.test"))

    def test_imovel_precisa_de_usuario_existente(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.salvar_imovel(999, "Casa", "SP", "Casa")

    def test_edicao_e_exclusao_persistem(self):
        self.banco.atualizar_imovel(self.usuario, self.imovel, "Apto", "Santos", "Apartamento")
        outro_banco = BancoDados(self.caminho)
        self.assertEqual(outro_banco.buscar_imovel(self.usuario, self.imovel)["identificacao"], "Apto")
        outro_banco.excluir_imovel(self.usuario, self.imovel)
        self.assertEqual(BancoDados(self.caminho).listar_imoveis(self.usuario), [])

    def test_edicao_invalida_preserva_registro(self):
        with self.assertRaises(ValueError):
            self.banco.atualizar_imovel(self.usuario, self.imovel, " ", "SP", "Casa")
        self.assertEqual(self.banco.buscar_imovel(self.usuario, self.imovel)["identificacao"], "Casa")

    def test_operacoes_respeitam_vinculo_com_usuario(self):
        operacoes = [
            lambda: self.banco.buscar_imovel(self.outro, self.imovel),
            lambda: self.banco.atualizar_imovel(self.outro, self.imovel, "X", "X", "X"),
            lambda: self.banco.excluir_imovel(self.outro, self.imovel),
            lambda: self.banco.salvar_consumo(self.outro, self.imovel, 2026, 1, 10),
            lambda: self.banco.listar_consumos(self.outro, self.imovel),
        ]
        for operacao in operacoes:
            with self.subTest(operacao=operacao), self.assertRaises(RegistroNaoEncontrado):
                operacao()
        self.assertEqual(self.banco.listar_imoveis(self.outro), [])
        self.assertEqual(self.banco.buscar_imovel(self.usuario, self.imovel)["identificacao"], "Casa")

    def test_historico_ordenado_e_consumo_zero(self):
        self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 2, 0)
        self.banco.salvar_consumo(self.usuario, self.imovel, 2025, 12, 120)
        registros = self.banco.listar_consumos(self.usuario, self.imovel)
        self.assertEqual([(r["ano"], r["mes"]) for r in registros], [(2025, 12), (2026, 2)])
        self.assertEqual(registros[1]["consumo_kwh"], 0)

    def test_mes_duplicado_nao_sobrescreve_historico(self):
        self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 1, 320)
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 1, 500)
        self.assertEqual(self.banco.listar_consumos(self.usuario, self.imovel)[0]["consumo_kwh"], 320)
        # Uma falha não impede a próxima gravação.
        self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 2, 100)
        self.assertEqual(len(self.banco.listar_consumos(self.usuario, self.imovel)), 2)

    def test_consumos_invalidos_nao_sao_gravados(self):
        casos = [(2026, 0, 1), (2026, 13, 1), (0, 1, 1), (2026.5, 1, 1),
                 (True, 1, 1), (2026, 1, -1), (2026, 1, "320"), (2026, 1, True),
                 (2026, 1, float("nan")), (2026, 1, float("inf"))]
        for ano, mes, consumo in casos:
            with self.subTest(dados=(ano, mes, consumo)), self.assertRaises(ValueError):
                self.banco.salvar_consumo(self.usuario, self.imovel, ano, mes, consumo)
        self.assertEqual(self.banco.listar_consumos(self.usuario, self.imovel), [])

    def test_exclusao_com_historico_preserva_imovel_e_consumo(self):
        self.banco.salvar_consumo(self.usuario, self.imovel, 2026, 1, 320)
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.excluir_imovel(self.usuario, self.imovel)
        self.assertEqual(len(self.banco.listar_imoveis(self.usuario)), 1)
        self.assertEqual(len(self.banco.listar_consumos(self.usuario, self.imovel)), 1)

    def test_banco_rejeita_dados_invalidos_mesmo_por_sql_direto(self):
        with self.banco._conexao() as conexao:
            for valor in (-10, "abc", float("inf")):
                with self.subTest(valor=valor), self.assertRaises(sqlite3.IntegrityError):
                    conexao.execute(
                        "INSERT INTO consumos (imovel_id, ano, mes, consumo_kwh) VALUES (?, 2026, 1, ?)",
                        (self.imovel, valor),
                    )


if __name__ == "__main__":
    unittest.main()
