

from inversor import carregar_inversores, buscar_inversores_compativeis, selecionar_inversor


def test_sistema_10kwp_ignora_inversores_pequenos():
    inversores = carregar_inversores()
    compativeis = buscar_inversores_compativeis(inversores, 10_000)


    for inv in compativeis:
        assert inv["potencia_nominal_w"] > 6000, f"{inv['modelo']} deveria ter sido ignorado"

    escolhido = selecionar_inversor(compativeis)
    assert escolhido["modelo"] == "S6-GR1P8K2"  


def test_seleciona_o_mais_barato():
    inversores = carregar_inversores()
    compativeis = buscar_inversores_compativeis(inversores, 5_000)
    escolhido = selecionar_inversor(compativeis)

    assert escolhido["preco_brl"] == min(inv["preco_brl"] for inv in compativeis)


def test_com_bateria_so_aceita_hibrido():
    inversores = carregar_inversores()
    compativeis = buscar_inversores_compativeis(inversores, 5_000, utiliza_baterias=True)

    assert compativeis, "deveria achar pelo menos um híbrido"
    assert all(inv["compativel_bateria"] for inv in compativeis)


def test_sem_inversor_compativel_retorna_none():
    inversores = carregar_inversores()
    compativeis = buscar_inversores_compativeis(inversores, 20_000)
    assert selecionar_inversor(compativeis) is None


if __name__ == "__main__":
    test_sistema_10kwp_ignora_inversores_pequenos()
    test_seleciona_o_mais_barato()
    test_com_bateria_so_aceita_hibrido()
    test_sem_inversor_compativel_retorna_none()
    print("Todos os testes da PB19 passaram.")
