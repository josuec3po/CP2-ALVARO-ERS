# FIAP-CP-ALVARO - PB08, PB09 e PB10
# Matriz (lista de listas): cada linha é [mês, consumo em kWh/mês]

ANO = 2026  # ano mostrado junto do nome do mês (PB10 T03)


# ---------------------------------------------------------------
# PB08 T01 - Inicializar a matriz de dados
# ---------------------------------------------------------------
def ler_dados():
    """Função só para ler/criar os dados (matriz mês x consumo)."""
    matriz = [
        ["Janeiro", 310.5],
        ["Fevereiro", 280.0],
        ["Março", 295.8],
        ["Abril", 270.2],
        ["Maio", 250.0],
        ["Junho", 240.7],
        ["Julho", 265.3],
        ["Agosto", 275.0],
        ["Setembro", 290.4],
        ["Outubro", 305.9],
        ["Novembro", 330.1],
        ["Dezembro", 345.6],
    ]
    return matriz


# ---------------------------------------------------------------
# PB08 T04 - Validação dos dados
# ---------------------------------------------------------------
def validar_matriz(matriz):
    """Devolve True se a matriz pode ser usada, senão mostra o erro."""
    if len(matriz) == 0:  # matriz vazia
        print("Erro: a matriz de histórico está vazia.")
        return False
    for linha in matriz:
        if linha[1] < 0:  # consumo negativo
            print(f"Erro: consumo negativo em {linha[0]}.")
            return False
    return True


# ---------------------------------------------------------------
# PB08 T02 - Busca do maior valor
# ---------------------------------------------------------------
def buscar_maior(matriz):
    maior = matriz[0][1]  # começa com o consumo da primeira linha
    for linha in matriz:
        consumo = linha[1]  # coluna de consumo (índice 1)
        if consumo > maior:
            maior = consumo
    return maior


# ---------------------------------------------------------------
# PB08 T03 - Formatar a saída
# ---------------------------------------------------------------
def formatar_saida(valor):
    texto = f"{valor:.2f}"  # converte para string com 2 casas
    return texto + " kWh/mês"  # concatena a unidade


# ---------------------------------------------------------------
# PB09 T01 - Soma dos valores da matriz
# ---------------------------------------------------------------
def somar_consumos(matriz):
    soma = 0  # acumulador começa em zero
    for linha in matriz:
        soma = soma + linha[1]
    return soma


# ---------------------------------------------------------------
# PB09 T02 - Média
# ---------------------------------------------------------------
def calcular_media(soma, matriz):
    quantidade_meses = len(matriz)  # nº de meses = nº de linhas
    return soma / quantidade_meses


# ---------------------------------------------------------------
# PB10 T01 - Importar o valor de referência (máximo do PB08)
# ---------------------------------------------------------------
def receber_maximo(maximo):
    if maximo is None:  # dado nulo
        print("Erro: valor máximo não informado.")
        return None
    if maximo < 0:  # dado inválido
        print("Erro: valor máximo inválido.")
        return None
    valor_referencia = maximo  # guarda em variável local
    return valor_referencia


# ---------------------------------------------------------------
# PB10 T02 - Busca linear na matriz
# ---------------------------------------------------------------
def buscar_linha(matriz, valor_referencia):
    """Devolve o índice da linha cujo consumo é igual ao valor máximo."""
    indice = -1
    for i in range(len(matriz)):
        if matriz[i][1] == valor_referencia:  # correspondência exata
            indice = i
            break  # guarda a primeira linha encontrada
    return indice


# ---------------------------------------------------------------
# PB10 T03 - Exibir o nome do mês e ano
# ---------------------------------------------------------------
def mostrar_mes(matriz, indice):
    mes = matriz[indice][0]  # coluna de texto (índice 0)
    print(f"Mês de maior consumo: {mes} de {ANO}")
    return mes


# ---------------------------------------------------------------
# Função principal (junta tudo)
# ---------------------------------------------------------------
def principal(matriz):
    """Recebe a matriz, calcula e mostra os resultados.
    Devolve um dicionário com os resultados (ou None se der erro)."""
    if not validar_matriz(matriz):
        return None

    maximo = buscar_maior(matriz)
    soma = somar_consumos(matriz)
    media = calcular_media(soma, matriz)

    print("Consumo máximo:", formatar_saida(maximo))
    print("Soma dos consumos:", formatar_saida(soma))
    print("Média dos meses:", formatar_saida(media))

    referencia = receber_maximo(maximo)
    if referencia is None:
        return None
    indice = buscar_linha(matriz, referencia)
    mes = mostrar_mes(matriz, indice)

    return {"maximo": maximo, "soma": soma, "media": media, "mes_maximo": mes}


# ---------------------------------------------------------------
# PB10 T04 - Testes de integração
# ---------------------------------------------------------------
def testes():
    print("Teste 1 - matriz normal (máximo no meio)")
    r = principal([["Janeiro", 100.0], ["Fevereiro", 300.0], ["Março", 200.0]])
    assert r["mes_maximo"] == "Fevereiro"
    assert r["maximo"] == 300.0
    assert r["soma"] == 600.0
    assert r["media"] == 200.0

    print("\nTeste 2 - apenas um mês")
    r = principal([["Maio", 150.0]])
    assert r["mes_maximo"] == "Maio"
    assert r["media"] == 150.0

    print("\nTeste 3 - dois meses com o mesmo máximo")
    r = principal([["Abril", 50.0], ["Junho", 90.0], ["Julho", 90.0]])
    assert r["mes_maximo"] == "Junho"  # fica com o primeiro encontrado

    print("\nTeste 4 - matriz vazia")
    assert principal([]) is None

    print("\nTeste 5 - consumo negativo")
    assert principal([["Janeiro", 100.0], ["Fevereiro", -5.0]]) is None

    print("\nTodos os testes passaram!")


# ---------------------------------------------------------------
# Execução
# ---------------------------------------------------------------
print("=== Consumo do ano ===")
principal(ler_dados())

print("\n=== Testes de integração ===")
testes()
