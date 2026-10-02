"""PB21: orçamento e resumo de um sistema já dimensionado pelas PB18-20."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def numero(valor, campo, minimo=0, maximo=None):
    """Aceita números finitos e vírgula decimal; rejeita campos inválidos."""
    try:
        if isinstance(valor, bool):
            raise ValueError
        resultado = Decimal(str(valor).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{campo}: informe um número válido.") from None
    if not resultado.is_finite() or resultado < minimo:
        raise ValueError(f"{campo}: informe um número finito maior ou igual a {minimo}.")
    if maximo is not None and resultado > maximo:
        raise ValueError(f"{campo}: o máximo permitido é {maximo}.")
    return resultado


def quantidade(valor, campo):
    resultado = numero(valor, campo, 1)
    if resultado != resultado.to_integral_value():
        raise ValueError(f"{campo}: informe uma quantidade inteira.")
    return int(resultado)


def produto(dados, campo):
    if not isinstance(dados, dict):
        raise ValueError(f"{campo}: informe os dados do equipamento selecionado.")
    copia = dict(dados)
    for chave in ("fabricante", "modelo"):
        if not isinstance(copia.get(chave), str) or not copia[chave].strip():
            raise ValueError(f"{campo}: {chave} é obrigatório.")
        copia[chave] = copia[chave].strip()
    copia["preco_brl"] = numero(copia.get("preco_brl"), f"Preço de {campo}")
    return copia


def centavos(valor):
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def gerar_proposta(consumo_referencia_kwh, percentual_atendido, hsp,
                   potencia_calculada_kwp, modulo, quantidade_modulos, inversor,
                   bateria=None, quantidade_baterias=0, percentual_adicionais=20):
    """Recebe as seleções anteriores; não escolhe nem valida compatibilidade elétrica.

    Os produtos usam as chaves dos CSVs da PB17. Consumo em kWh/mês,
    HSP em h/dia, potência em kWp e percentuais entre 0 e 100.
    """
    consumo = numero(consumo_referencia_kwh, "Consumo de referência", Decimal("0.000001"))
    percentual = numero(percentual_atendido, "Percentual atendido", Decimal("0.000001"), 100)
    horas = numero(hsp, "HSP", Decimal("0.000001"), 24)
    potencia = numero(potencia_calculada_kwp, "Potência calculada", Decimal("0.000001"))
    adicionais = numero(percentual_adicionais, "Percentual de custos adicionais", 0, 100)
    painel = produto(modulo, "módulo")
    qtd_modulos = quantidade(quantidade_modulos, "Quantidade de módulos")
    painel["potencia_wp"] = numero(painel.get("potencia_wp"), "Potência do módulo", Decimal("0.000001"))
    instalado = painel["potencia_wp"] * qtd_modulos / 1000
    if instalado < potencia:
        raise ValueError("A potência instalada deve atender à potência calculada; revise a PB18.")
    inversor_selecionado = produto(inversor, "inversor")
    custo_modulos = centavos(painel["preco_brl"] * qtd_modulos)
    custo_inversor = centavos(inversor_selecionado["preco_brl"])
    custo_baterias = Decimal("0.00")
    capacidade_nominal = Decimal("0")
    capacidade_util = Decimal("0")
    qtd_baterias = 0
    bateria_selecionada = None
    if bateria is None:
        if numero(quantidade_baterias, "Quantidade de baterias") != 0:
            raise ValueError("Quantidade de baterias exige um modelo selecionado.")
    else:
        bateria_selecionada = produto(bateria, "bateria")
        qtd_baterias = quantidade(quantidade_baterias, "Quantidade de baterias")
        capacidade = numero(bateria_selecionada.get("capacidade_kwh"), "Capacidade da bateria", Decimal("0.000001"))
        dod = numero(bateria_selecionada.get("dod_pct"), "DoD", Decimal("0.000001"), 100)
        capacidade_nominal = capacidade * qtd_baterias
        capacidade_util = capacidade_nominal * dod / 100
        custo_baterias = centavos(bateria_selecionada["preco_brl"] * qtd_baterias)
    equipamentos = custo_modulos + custo_inversor + custo_baterias
    custo_demais = centavos(equipamentos * adicionais / 100)
    return {
        "consumo_referencia_kwh": consumo, "percentual_atendido": percentual,
        "hsp": horas, "potencia_calculada_kwp": potencia,
        "potencia_instalada_kwp": instalado, "modulo": painel,
        "quantidade_modulos": qtd_modulos, "inversor": inversor_selecionado,
        "bateria": bateria_selecionada, "quantidade_baterias": qtd_baterias,
        "capacidade_nominal_kwh": capacidade_nominal,
        "capacidade_util_kwh": capacidade_util,
        "custo_modulos": custo_modulos, "custo_inversor": custo_inversor,
        "custo_baterias": custo_baterias, "custo_equipamentos": equipamentos,
        "percentual_adicionais": adicionais, "custo_demais": custo_demais,
        "custo_total": equipamentos + custo_demais,
    }


def formatar_numero(valor, casas=2):
    return f"{valor:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def moeda(valor):
    return "R$ " + formatar_numero(centavos(valor))


def resumo_proposta(proposta):
    painel = proposta["modulo"]
    inversor = proposta["inversor"]
    linhas = [
        "\n=== PB21 - RESUMO TÉCNICO ===",
        f"Consumo de referência: {formatar_numero(proposta['consumo_referencia_kwh'])} kWh/mês",
        f"Percentual atendido: {formatar_numero(proposta['percentual_atendido'])}%",
        f"HSP: {formatar_numero(proposta['hsp'])} h/dia",
        f"Potência calculada: {formatar_numero(proposta['potencia_calculada_kwp'], 3)} kWp",
        f"Potência instalada: {formatar_numero(proposta['potencia_instalada_kwp'], 3)} kWp",
        f"Módulos: {proposta['quantidade_modulos']} x {painel['fabricante']} - {painel['modelo']}",
        f"Inversor: 1 x {inversor['fabricante']} - {inversor['modelo']}",
    ]
    if proposta["bateria"] is None:
        linhas.append("Baterias: não incluídas (sem armazenamento).")
    else:
        bateria = proposta["bateria"]
        linhas.extend([
            f"Baterias: {proposta['quantidade_baterias']} x {bateria['fabricante']} - {bateria['modelo']}",
            f"Armazenamento nominal: {formatar_numero(proposta['capacidade_nominal_kwh'])} kWh",
            f"Armazenamento útil (DoD): {formatar_numero(proposta['capacidade_util_kwh'])} kWh",
        ])
    linhas.extend([
        "\n=== PB21 - ORÇAMENTO ESTIMADO ===",
        f"Módulos: {moeda(proposta['custo_modulos'])}",
        f"Inversor: {moeda(proposta['custo_inversor'])}",
        f"Baterias: {moeda(proposta['custo_baterias'])}",
        f"Subtotal dos equipamentos: {moeda(proposta['custo_equipamentos'])}",
        f"Cabos, estruturas e instalação ({formatar_numero(proposta['percentual_adicionais'])}%): {moeda(proposta['custo_demais'])}",
        f"CUSTO TOTAL ESTIMADO: {moeda(proposta['custo_total'])}",
        "Proposta preliminar baseada nos equipamentos já dimensionados.",
    ])
    return "\n".join(linhas)


def ler_numero(mensagem, minimo=0, maximo=None, inteiro=False):
    while True:
        try:
            entrada = input(mensagem)
            if inteiro:
                return quantidade(entrada, mensagem)
            return numero(entrada, mensagem, minimo, maximo)
        except ValueError as erro:
            print(erro)


def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Este campo é obrigatório.")


def ler_produto(tipo):
    print(f"\nDados do {tipo} já selecionado:")
    return {"fabricante": ler_texto("Fabricante: "),
            "modelo": ler_texto("Modelo: "),
            "preco_brl": ler_numero("Preço unitário (R$): ")}


def executar_orcamento(consumo_referencia_kwh=None):
    print("\n=== PROPOSTA SOLAR - PB21 ===")
    print("Informe os resultados das PB18, PB19 e PB20 para compor a proposta.")
    if consumo_referencia_kwh is None:
        consumo_referencia_kwh = ler_numero("Consumo de referência (kWh/mês): ", Decimal("0.000001"))
    percentual = ler_numero("Percentual atendido (%): ", Decimal("0.000001"), 100)
    hsp = ler_numero("HSP (h/dia): ", Decimal("0.000001"), 24)
    potencia = ler_numero("Potência calculada na PB18 (kWp): ", Decimal("0.000001"))
    painel = ler_produto("módulo")
    painel["potencia_wp"] = ler_numero("Potência unitária (Wp): ", Decimal("0.000001"))
    qtd_modulos = ler_numero("Quantidade de módulos: ", inteiro=True)
    while painel["potencia_wp"] * qtd_modulos / 1000 < potencia:
        print("A potência instalada não atende à calculada. Revise a quantidade da PB18.")
        qtd_modulos = ler_numero("Quantidade de módulos: ", inteiro=True)
    inversor = ler_produto("inversor")
    bateria = None
    qtd_baterias = 0
    while True:
        resposta = input("Incluir baterias selecionadas na PB20? (s/n): ").strip().lower()
        if resposta in ("s", "n"):
            break
        print("Digite s ou n.")
    if resposta == "s":
        bateria = ler_produto("bateria")
        bateria["capacidade_kwh"] = ler_numero("Capacidade nominal unitária (kWh): ", Decimal("0.000001"))
        bateria["dod_pct"] = ler_numero("DoD (%): ", Decimal("0.000001"), 100)
        qtd_baterias = ler_numero("Quantidade de baterias: ", inteiro=True)
    while True:
        entrada = input("Custos adicionais (%) [Enter = 20]: ").strip()
        try:
            adicionais = numero(entrada or 20, "Custos adicionais", 0, 100)
            break
        except ValueError as erro:
            print(erro)
    proposta = gerar_proposta(consumo_referencia_kwh, percentual, hsp, potencia,
                             painel, qtd_modulos, inversor, bateria, qtd_baterias, adicionais)
    print(resumo_proposta(proposta))
    return proposta
