

import csv
from pathlib import Path

CAMINHO_CSV = Path(__file__).parent / "fornecedores" / "inversores.csv"


RAZAO_DC_AC_MAX = 1.3


def carregar_inversores(caminho=CAMINHO_CSV):
    """Lê o CSV e devolve uma lista de dicionários com os números já convertidos."""
    inversores = []

    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for linha in leitor:

            inversores.append({
                "id": int(linha["id"]),
                "fabricante": linha["fabricante"],
                "modelo": linha["modelo"],
                "tipo": linha["tipo"],
                "potencia_nominal_w": int(linha["potencia_nominal_w"]),
                "potencia_max_fv_w": int(linha["potencia_max_fv_w"]),
                "compativel_bateria": linha["compativel_bateria"].strip().lower() == "sim",
                "preco_brl": float(linha["preco_brl"]),
                "fornecedor": linha["fornecedor"],
            })

    return inversores



def eh_compativel(inversor, potencia_modulos_w, utiliza_baterias=False):
    """Retorna (True, "") se o inversor serve, ou (False, motivo) se não serve."""


    if potencia_modulos_w > inversor["potencia_max_fv_w"]:
        return False, "painéis acima do máximo FV suportado"

    if potencia_modulos_w / inversor["potencia_nominal_w"] > RAZAO_DC_AC_MAX:
        return False, "inversor subdimensionado"

    if utiliza_baterias and not inversor["compativel_bateria"]:
        return False, "não aceita bateria"

    return True, ""


def buscar_inversores_compativeis(inversores, potencia_modulos_w, utiliza_baterias=False):
  
    compativeis = []

    for inversor in inversores:
        ok, _motivo = eh_compativel(inversor, potencia_modulos_w, utiliza_baterias)
        if ok:
            compativeis.append(inversor)

    return compativeis


def selecionar_inversor(compativeis):

    if not compativeis:
        return None

    ordenados = sorted(compativeis, key=lambda inv: inv["preco_brl"])
    return ordenados[0]


def dimensionar_inversor(potencia_modulos_w, utiliza_baterias=False):
 
    inversores = carregar_inversores()
    compativeis = buscar_inversores_compativeis(inversores, potencia_modulos_w, utiliza_baterias)
    inversor_selecionado = selecionar_inversor(compativeis)  # variável final do relatório
    return inversor_selecionado


if __name__ == "__main__":
    potencia = float(input("Potência dos módulos (kWp): ")) * 1000
    bateria = input("Vai usar bateria? (s/n): ").strip().lower() == "s"

    escolhido = dimensionar_inversor(potencia, bateria)

    if escolhido is None:
        print("Nenhum inversor do catálogo atende essa configuração.")
    else:
        print(f"Inversor: {escolhido['fabricante']} {escolhido['modelo']} "
              f"({escolhido['potencia_nominal_w'] / 1000:.1f} kW) - R$ {escolhido['preco_brl']:.2f}")
