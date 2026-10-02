
import csv
import math
from pathlib import Path

CAMINHO_CSV = Path(__file__).parent / "fornecedores" / "baterias.csv"

DIAS_NO_MES = 30

TENSAO_BANCO_V = 48

def carregar_baterias(caminho=CAMINHO_CSV):
    """Lê o CSV e devolve uma lista de dicionários com os números convertidos."""
    baterias = []

    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        for linha in leitor:
            baterias.append({
                "id": int(linha["id"]),
                "fabricante": linha["fabricante"],
                "modelo": linha["modelo"],
                "tecnologia": linha["tecnologia"],
                "tensao_nominal_v": float(linha["tensao_nominal_v"]),
                "capacidade_kwh": float(linha["capacidade_kwh"]),
                "dod": float(linha["dod_pct"]) / 100,  # 80 -> 0.8
                "preco_brl": float(linha["preco_brl"]),
            })

    return baterias

def calcular_energia_diaria(consumo_mensal_kwh):
    """kWh/mês -> kWh/dia."""
    return consumo_mensal_kwh / DIAS_NO_MES


def calcular_energia_autonomia(energia_diaria_kwh, horas_autonomia):
    """Quanto de energia a bateria precisa entregar durante a autonomia.
    Simplificação: assume consumo uniforme ao longo das 24h."""
    return energia_diaria_kwh * (horas_autonomia / 24)


def calcular_capacidade_nominal(energia_autonomia_kwh, dod):
    """A bateria não pode ser descarregada 100%. Se só 80% é utilizável,
    o banco precisa ser maior: 5 kWh / 0.8 = 6.25 kWh."""
    return energia_autonomia_kwh / dod


def calcular_capacidade_util(bateria):
    """Quanto de cada bateria dá para usar de fato: 4.8 kWh x 0.8 = 3.84 kWh."""
    return bateria["capacidade_kwh"] * bateria["dod"]


def selecionar_bateria(baterias, energia_autonomia_kwh, tecnologia="LiFePO4"):
    """Filtra por tecnologia e tensão, e escolhe a que dá o MENOR CUSTO TOTAL
    (não a mais barata por unidade: uma bateria barata e pequena pode
    exigir tantas unidades que sai mais caro no fim)."""
    candidatas = [
        b for b in baterias
        if b["tecnologia"] == tecnologia and b["tensao_nominal_v"] == TENSAO_BANCO_V
    ]

    if not candidatas:
        return None

    def custo_total(bateria):
        return calcular_quantidade(energia_autonomia_kwh, bateria) * bateria["preco_brl"]

    return min(candidatas, key=custo_total)


def calcular_quantidade(energia_autonomia_kwh, bateria):
    """Energia necessária / capacidade útil de cada uma, arredondando PRA CIMA
    (1.3 bateria não existe: precisa de 2).
    Atenção: o DoD entra só uma vez aqui, via capacidade útil."""
    return math.ceil(energia_autonomia_kwh / calcular_capacidade_util(bateria))


def dimensionar_baterias(consumo_mensal_kwh, horas_autonomia, utiliza_baterias):
    """Retorna um dicionário com o resultado para o relatório."""

    if not utiliza_baterias:
        return {"utiliza_baterias": False, "custo_total_brl": 0.0}

    energia_diaria = calcular_energia_diaria(consumo_mensal_kwh)
    energia_autonomia = calcular_energia_autonomia(energia_diaria, horas_autonomia)

    baterias = carregar_baterias()
    bateria = selecionar_bateria(baterias, energia_autonomia)

    if bateria is None:
        return {"utiliza_baterias": True, "erro": "nenhuma bateria compatível no catálogo",
                "custo_total_brl": 0.0}

    quantidade = calcular_quantidade(energia_autonomia, bateria)

    return {
        "utiliza_baterias": True,
        "energia_diaria_kwh": energia_diaria,
        "energia_autonomia_kwh": energia_autonomia,
        "capacidade_nominal_kwh": calcular_capacidade_nominal(energia_autonomia, bateria["dod"]),
        "bateria": bateria,
        "capacidade_util_kwh": calcular_capacidade_util(bateria),
        "quantidade": quantidade,
        "custo_total_brl": quantidade * bateria["preco_brl"],
    }


if __name__ == "__main__":
    consumo = float(input("Consumo mensal (kWh/mês): "))
    usa = input("Vai usar bateria? (s/n): ").strip().lower() == "s"
    horas = float(input("Horas de autonomia: ")) if usa else 0

    r = dimensionar_baterias(consumo, horas, usa)

    if not r["utiliza_baterias"]:
        print("Sem baterias. Custo: R$ 0,00")
    elif "erro" in r:
        print(r["erro"])
    else:
        b = r["bateria"]
        print(f"Energia diária:      {r['energia_diaria_kwh']:.2f} kWh")
        print(f"Energia autonomia:   {r['energia_autonomia_kwh']:.2f} kWh")
        print(f"Capacidade nominal:  {r['capacidade_nominal_kwh']:.2f} kWh")
        print(f"Bateria:             {b['fabricante']} {b['modelo']} ({b['capacidade_kwh']} kWh)")
        print(f"Capacidade útil:     {r['capacidade_util_kwh']:.2f} kWh por unidade")
        print(f"Quantidade:          {r['quantidade']}")
        print(f"Custo total:         R$ {r['custo_total_brl']:.2f}")
