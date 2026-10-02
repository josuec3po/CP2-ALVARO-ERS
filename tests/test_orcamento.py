import unittest
from decimal import Decimal

from orcamento import gerar_proposta, moeda, resumo_proposta


class TestOrcamento(unittest.TestCase):
    def setUp(self):
        self.modulo = {"fabricante": "Painel Teste", "modelo": "P550",
                       "preco_brl": "589.00", "potencia_wp": "550"}
        self.inversor = {"fabricante": "Inversor Teste", "modelo": "I5000",
                         "preco_brl": "2599.00"}
        self.bateria = {"fabricante": "Bateria Teste", "modelo": "B4800",
                        "preco_brl": "5743.55", "capacidade_kwh": "4.8", "dod_pct": "80"}

    def proposta(self, **alteracoes):
        dados = dict(consumo_referencia_kwh=410, percentual_atendido=100,
                     hsp=5, potencia_calculada_kwp=3.42, modulo=self.modulo,
                     quantidade_modulos=7, inversor=self.inversor)
        dados.update(alteracoes)
        return gerar_proposta(**dados)

    def test_sem_baterias(self):
        p = self.proposta()
        self.assertEqual(p["custo_modulos"], Decimal("4123.00"))
        self.assertEqual(p["custo_inversor"], Decimal("2599.00"))
        self.assertEqual(p["custo_baterias"], Decimal("0.00"))
        self.assertEqual(p["custo_equipamentos"], Decimal("6722.00"))
        self.assertEqual(p["custo_demais"], Decimal("1344.40"))
        self.assertEqual(p["custo_total"], Decimal("8066.40"))
        self.assertEqual(p["potencia_instalada_kwp"], Decimal("3.85"))
        self.assertIn("não incluídas", resumo_proposta(p))

    def test_com_baterias(self):
        p = self.proposta(bateria=self.bateria, quantidade_baterias=2)
        self.assertEqual(p["custo_baterias"], Decimal("11487.10"))
        self.assertEqual(p["capacidade_nominal_kwh"], Decimal("9.6"))
        self.assertEqual(p["capacidade_util_kwh"], Decimal("7.68"))
        self.assertEqual(p["custo_demais"], Decimal("3641.82"))
        self.assertEqual(p["custo_total"], Decimal("21850.92"))
        resumo = resumo_proposta(p)
        for texto in ("2 x Bateria Teste - B4800", "9,60 kWh", "7,68 kWh", "R$ 21.850,92"):
            self.assertIn(texto, resumo)

    def test_adicionais_configuraveis(self):
        self.assertEqual(self.proposta(percentual_adicionais=0)["custo_total"], Decimal("6722.00"))
        self.assertEqual(self.proposta(percentual_adicionais="12,5")["custo_demais"], Decimal("840.25"))

    def test_arredondamento_monetario(self):
        modulo = dict(self.modulo, preco_brl="0.005")
        inversor = dict(self.inversor, preco_brl="0.005")
        p = self.proposta(modulo=modulo, inversor=inversor, quantidade_modulos=7)
        self.assertEqual(p["custo_modulos"], Decimal("0.04"))
        self.assertEqual(p["custo_inversor"], Decimal("0.01"))
        self.assertEqual(p["custo_total"], Decimal("0.06"))
        self.assertEqual(p["custo_total"], p["custo_equipamentos"] + p["custo_demais"])

    def test_numeros_invalidos(self):
        for campo in ("consumo_referencia_kwh", "percentual_atendido", "hsp",
                      "potencia_calculada_kwp", "percentual_adicionais"):
            for valor in ("", "abc", -1, "NaN", "Infinity", True, None):
                with self.subTest(campo=campo, valor=valor), self.assertRaises(ValueError):
                    self.proposta(**{campo: valor})
        for campo, valor in (("percentual_atendido", 101), ("hsp", 25),
                             ("percentual_adicionais", 101), ("hsp", 0)):
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                self.proposta(**{campo: valor})

    def test_quantidades_invalidas(self):
        for valor in (0, -1, "1.5", "NaN", True):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                self.proposta(quantidade_modulos=valor)
            with self.subTest(baterias=valor), self.assertRaises(ValueError):
                self.proposta(bateria=self.bateria, quantidade_baterias=valor)

    def test_dados_produto_invalidos(self):
        for alteracao in ({"fabricante": " "}, {"modelo": ""}, {"preco_brl": -1},
                          {"preco_brl": "NaN"}, {"potencia_wp": 0}):
            with self.subTest(alteracao=alteracao), self.assertRaises(ValueError):
                self.proposta(modulo=dict(self.modulo, **alteracao))
        for alteracao in ({"capacidade_kwh": 0}, {"dod_pct": 0}, {"dod_pct": 101}):
            with self.subTest(alteracao=alteracao), self.assertRaises(ValueError):
                self.proposta(bateria=dict(self.bateria, **alteracao), quantidade_baterias=1)

    def test_inconsistencia_dimensionamento(self):
        with self.assertRaises(ValueError):
            self.proposta(quantidade_modulos=1)
        with self.assertRaises(ValueError):
            self.proposta(quantidade_baterias=2)

    def test_preserva_produtos_originais(self):
        self.proposta(bateria=self.bateria, quantidade_baterias=2)
        self.assertEqual(self.modulo["preco_brl"], "589.00")
        self.assertEqual(self.bateria["capacidade_kwh"], "4.8")

    def test_formato_e_cobertura_resumo(self):
        self.assertEqual(moeda(Decimal("1234567.89")), "R$ 1.234.567,89")
        resumo = resumo_proposta(self.proposta())
        for texto in ("410,00 kWh/mês", "100,00%", "5,00 h/dia", "3,420 kWp",
                      "3,850 kWp", "7 x Painel Teste - P550", "1 x Inversor Teste - I5000",
                      "Subtotal dos equipamentos", "Cabos, estruturas e instalação",
                      "R$ 8.066,40"):
            self.assertIn(texto, resumo)
