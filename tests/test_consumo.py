"""Testes automatizados da camada de consumo (PB05, PB06, PB07)."""
import unittest

from persistencia import BancoDados
from consumo import cadastrar_consumo, consultar_historico


class ConsumoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.banco = BancoDados()
        cls.usuario_id = cls.banco.salvar_usuario(
            "TESTE unittest", "teste.unittest.consumo@example.test", "hash-fake"
        )

    def _novo_imovel(self, nome):
        return self.banco.salvar_imovel(self.usuario_id, nome, "São Paulo", "Casa")

    # PB05 --------------------------------------------------------------

    def test_kwh_valido_e_cadastrado(self):
        imovel_id = self._novo_imovel("TESTE PB05 valido")
        sucesso, mensagem = cadastrar_consumo(self.usuario_id, imovel_id, 2026, 1, 100.0)
        self.assertTrue(sucesso)

    def test_kwh_negativo_e_rejeitado(self):
        imovel_id = self._novo_imovel("TESTE PB05 negativo")
        sucesso, mensagem = cadastrar_consumo(self.usuario_id, imovel_id, 2026, 1, -5)
        self.assertFalse(sucesso)

    def test_kwh_nao_numerico_e_rejeitado(self):
        imovel_id = self._novo_imovel("TESTE PB05 nao numerico")
        sucesso, mensagem = cadastrar_consumo(self.usuario_id, imovel_id, 2026, 1, "abc")
        self.assertFalse(sucesso)

    def test_kwh_zero_e_valido(self):
        imovel_id = self._novo_imovel("TESTE PB05 zero")
        sucesso, mensagem = cadastrar_consumo(self.usuario_id, imovel_id, 2026, 1, 0)
        self.assertTrue(sucesso)

    # PB06 --------------------------------------------------------------

    def test_multiplos_meses_distintos_ok(self):
        imovel_id = self._novo_imovel("TESTE PB06 multiplos")
        self.assertTrue(cadastrar_consumo(self.usuario_id, imovel_id, 2026, 1, 100)[0])
        self.assertTrue(cadastrar_consumo(self.usuario_id, imovel_id, 2026, 2, 110)[0])
        self.assertTrue(cadastrar_consumo(self.usuario_id, imovel_id, 2026, 3, 120)[0])

    def test_duplicata_mes_ano_e_bloqueada(self):
        imovel_id = self._novo_imovel("TESTE PB06 duplicata")
        cadastrar_consumo(self.usuario_id, imovel_id, 2026, 5, 100)
        sucesso, mensagem = cadastrar_consumo(self.usuario_id, imovel_id, 2026, 5, 999)
        self.assertFalse(sucesso)
        self.assertIn("Já existe consumo", mensagem)

    # PB07 --------------------------------------------------------------

    def test_historico_vazio(self):
        imovel_id = self._novo_imovel("TESTE PB07 vazio")
        sucesso, registros = consultar_historico(self.usuario_id, imovel_id)
        self.assertTrue(sucesso)
        self.assertEqual(registros, [])

    def test_historico_multiplos_anos_ordenado(self):
        imovel_id = self._novo_imovel("TESTE PB07 multi ano")
        cadastrar_consumo(self.usuario_id, imovel_id, 2027, 1, 50)
        cadastrar_consumo(self.usuario_id, imovel_id, 2025, 6, 80)
        cadastrar_consumo(self.usuario_id, imovel_id, 2026, 12, 60)
        sucesso, registros = consultar_historico(self.usuario_id, imovel_id)
        self.assertTrue(sucesso)
        ordem = [(r["ano"], r["mes"]) for r in registros]
        self.assertEqual(ordem, [(2025, 6), (2026, 12), (2027, 1)])


if __name__ == "__main__":
    unittest.main()