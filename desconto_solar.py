
# PB16 - Parâmetros do sistema solar


# T03 - Validar os dados do sistema solar
def ler_numero(texto, minimo, maximo):

    while True:
        resposta = input(texto).strip().replace(",", ".")  # Correção de input em caso de virgula

        try:
            numero = float(resposta)
        except ValueError:
            print("Erro: digite apenas números (ex: 4.5).")
            continue

        if not (minimo <= numero <= maximo):
            print(f"Erro: digite um valor entre {minimo} e {maximo}.")
            continue

        return numero


# T02 - Perguntar sobre baterias
def pedir_baterias():
    while True:
        resposta = input("Deseja baterias? (s/n): ").strip().lower()

        if resposta == "s":
            return ler_numero("Autonomia desejada em horas: ", 1, 72)
        if resposta == "n":
            return 0

        print("Erro: responda com 's' ou 'n'.")


# T01 - Receber sol disponível e consumo alvo
def pedir_dados_solares():
    print("=== Parâmetros do Sistema Solar ===")
    horas_sol = ler_numero("Horas de sol pleno por dia (HSP): ", 1, 12)
    porcentagem = ler_numero("Quantos % do consumo quer abater? (1-100): ", 1, 100)
    autonomia = pedir_baterias()

    return {
        "horas_sol": horas_sol,
        "porcentagem": porcentagem,
        "autonomia_horas": autonomia,
    }


# T04 - Ligar os dados solares ao consumo do imóvel
def calcular_consumo_alvo(consumo_mensal, porcentagem):
    return consumo_mensal * porcentagem / 100


def montar_parametros_solares(consumo_mensal):
    
    parametros = pedir_dados_solares()
    parametros["consumo_mensal"] = consumo_mensal
    parametros["consumo_alvo"] = calcular_consumo_alvo(
        consumo_mensal, parametros["porcentagem"]
    )
    return parametros


# Teste 
if __name__ == "__main__":
    resultado = montar_parametros_solares(300) 
    print(resultado)