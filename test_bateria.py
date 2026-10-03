

from bateria import dimensionar_baterias


def test_caso_de_uso_300kwh_12h_lifepo4():
    r = dimensionar_baterias(consumo_mensal_kwh=300, horas_autonomia=12, utiliza_baterias=True)

    assert r["energia_diaria_kwh"] == 10          # 300 / 30
    assert r["energia_autonomia_kwh"] == 5        # 10 x 12/24
    assert r["capacidade_nominal_kwh"] == 6.25    # 5 / 0.8
    assert r["bateria"]["tecnologia"] == "LiFePO4"
    assert r["bateria"]["tensao_nominal_v"] == 48
    assert r["quantidade"] == 2                   # ceil(5 / 3.84)
    assert round(r["custo_total_brl"], 2) == 11487.10  # 2x Unipower 48V


def test_sem_bateria_custo_zero():
    r = dimensionar_baterias(consumo_mensal_kwh=300, horas_autonomia=12, utiliza_baterias=False)

    assert r["custo_total_brl"] == 0
    assert "quantidade" not in r  # cálculo foi pulado


if __name__ == "__main__":
    test_caso_de_uso_300kwh_12h_lifepo4()
    test_sem_bateria_custo_zero()
    print("Todos os testes da PB20 passaram.")
