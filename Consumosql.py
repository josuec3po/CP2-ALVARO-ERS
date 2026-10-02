

"""Módulo de dimensionamento e estimativa de consumo energético.

A versão original mantinha imóveis/equipamentos em listas em memória.
Nesta versão, essas informações são lidas e persistidas no banco MySQL
através das funções de CRUD do projeto.
"""

from datetime import datetime

from crud import (
    adicionar_eletrodomestico_comodo,
    atualizar_eletrodomestico_comodo,
    buscar_usuario,
    listar_comodos,
    listar_eletrodomesticos,
    listar_eletrodomesticos_comodo,
    listar_imoveis,
    remover_eletrodomestico_comodo,
)

DIAS_NO_MES = 30

DIAS_DOS_MESES = {
    "Janeiro": 31,
    "Fevereiro": 28,
    "Março": 31,
    "Abril": 30,
    "Maio": 31,
    "Junho": 30,
    "Julho": 31,
    "Agosto": 31,
    "Setembro": 30,
    "Outubro": 31,
    "Novembro": 30,
    "Dezembro": 31,
}


def ler_quantidade(atual=None):
    """Lê uma quantidade inteira positiva.

    Quando ``atual`` é informado, Enter mantém o valor atual.
    """
    while True:
        texto = input("Quantidade: ").strip()
        if texto == "" and atual is not None:
            return atual

        try:
            quantidade = int(texto)
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue

        if quantidade <= 0:
            print("Erro: a quantidade deve ser maior que zero.")
            continue

        return quantidade


def ler_horas(atual=None):
    """Lê horas de uso diário entre 0 e 24.

    Quando ``atual`` é informado, Enter mantém o valor atual.
    """
    while True:
        texto = input("Horas de uso por dia (0 a 24): ").strip()
        if texto == "" and atual is not None:
            return atual

        try:
            horas = float(texto.replace(",", "."))
        except ValueError:
            print("Erro: digite um número.")
            continue

        if horas < 0 or horas > 24:
            print("Erro: o tempo deve estar entre 0 e 24 horas.")
            continue

        return horas


def calcular_consumo_diario(potencia_w, quantidade, horas):
    """Calcula o consumo diário estimado em kWh."""
    return potencia_w * quantidade * horas / 1000


def calcular_consumo_mensal(potencia_w, quantidade, horas):
    """Calcula o consumo mensal estimado em kWh, usando 30 dias."""
    return calcular_consumo_diario(potencia_w, quantidade, horas) * DIAS_NO_MES


def escolher_imovel():
    """Exibe os imóveis cadastrados e retorna o registro escolhido."""
    imoveis = listar_imoveis()

    if not imoveis:
        print("Nenhum imóvel cadastrado no banco de dados.")
        return None

    print("\nImóveis cadastrados:")
    for imovel in imoveis:
        usuario = buscar_usuario(imovel["proprietario"])
        proprietario = usuario["nome"] if usuario else f"ID {imovel['proprietario']}"
        endereco = imovel.get("endereco") or "Sem endereço informado"
        print(f"  {imovel['id']} - {endereco} | Proprietário: {proprietario}")

    while True:
        try:
            escolha = int(input("Digite o ID do imóvel: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue

        for imovel in imoveis:
            if imovel["id"] == escolha:
                return imovel

        print("Erro: ID de imóvel não existe.")


def escolher_comodo(imovel_id):
    """Exibe os cômodos do imóvel e retorna o ID selecionado."""
    comodos = listar_comodos(imovel_id)

    if not comodos:
        print("Nenhum cômodo cadastrado neste imóvel.")
        return None

    print("\nCômodos:")
    for comodo in comodos:
        print(f"  {comodo['id']} - {comodo['nome']}")

    while True:
        try:
            escolha = int(input("Digite o ID do cômodo: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue

        for comodo in comodos:
            if comodo["id"] == escolha:
                return escolha

        print("Erro: ID de cômodo não existe neste imóvel.")


def escolher_eletrodomestico():
    """Exibe o catálogo do banco e retorna o eletrodoméstico escolhido."""
    equipamentos = listar_eletrodomesticos()

    if not equipamentos:
        print("Nenhum eletrodoméstico cadastrado no catálogo.")
        return None

    print("\nEquipamentos disponíveis:")
    for equipamento in equipamentos:
        print(
            f"  {equipamento['id']} - {equipamento['nome']} "
            f"({equipamento['potencia']} W)"
        )

    while True:
        try:
            escolha = int(input("Digite o ID do equipamento: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue

        for equipamento in equipamentos:
            if equipamento["id"] == escolha:
                return equipamento

        print("Erro: ID de equipamento não existe.")


def consultar_equipamentos(comodo_id):
    """Consulta os equipamentos do cômodo e adiciona os cálculos de consumo."""
    registros = listar_eletrodomesticos_comodo(comodo_id)
    resultado = []

    for registro in registros:
        quantidade = registro.get("quantidade", 1)
        horas = float(registro["tempo_uso"])
        potencia = registro["potencia"]
        kwh_dia = calcular_consumo_diario(potencia, quantidade, horas)

        resultado.append(
            {
                "id": registro["id"],
                "id_equipamento": registro["eletrodomestico_id"],
                "nome": registro["nome"],
                "potencia": potencia,
                "quantidade": quantidade,
                "horas": horas,
                "kwh_dia": kwh_dia,
                "kwh_mes": kwh_dia * DIAS_NO_MES,
            }
        )

    return resultado


def mostrar_equipamentos(comodo_id, com_consumo=False):
    """Mostra os equipamentos de um cômodo."""
    lista = consultar_equipamentos(comodo_id)

    if not lista:
        print("Nenhum equipamento vinculado a este cômodo.")
        return lista

    for i, item in enumerate(lista, start=1):
        print(
            f"{i}) {item['nome']} | qtd: {item['quantidade']} | "
            f"{item['horas']:.2f} h/dia | {item['potencia']} W"
        )
        if com_consumo:
            print(
                f"   Consumo: {item['kwh_dia']:.2f} kWh/dia | "
                f"{item['kwh_mes']:.2f} kWh/mês"
            )

    return lista


def obter_registros_imovel(imovel_id):
    """Retorna todos os equipamentos associados ao imóvel, por cômodo."""
    resultado = []

    for comodo in listar_comodos(imovel_id):
        equipamentos = consultar_equipamentos(comodo["id"])
        for equipamento in equipamentos:
            item = dict(equipamento)
            item["comodo_id"] = comodo["id"]
            item["comodo_nome"] = comodo["nome"]
            resultado.append(item)

    return resultado


def montar_tabela_anual(lista):
    """Monta a tabela anual a partir do consumo diário estimado."""
    total_dia = sum(item["kwh_dia"] for item in lista)
    kwh_hora = total_dia / 24

    tabela = []
    for mes, dias in DIAS_DOS_MESES.items():
        tabela.append([mes, kwh_hora, total_dia, total_dia * dias])

    return tabela


def mostrar_tabela_anual(lista):
    """Exibe consumo estimado por mês e máximo/média anual."""
    tabela = montar_tabela_anual(lista)

    print(f"{'Mês':<12}{'kWh/hora':>10}{'kWh/dia':>10}{'kWh/mês':>12}")
    print("-" * 44)
    for linha in tabela:
        print(
            f"{linha[0]:<12}{linha[1]:>10.3f}"
            f"{linha[2]:>10.2f}{linha[3]:>12.2f}"
        )
    print("-" * 44)

    valores_mes = [linha[3] for linha in tabela]
    maximo = max(valores_mes)
    media = sum(valores_mes) / len(valores_mes)

    print(f"Consumo máximo: {maximo:.2f} kWh/mês")
    print(f"Consumo médio dos {len(valores_mes)} meses: {media:.2f} kWh/mês")


def selecionar_registro(imovel_id):
    """Seleciona um equipamento associado ao imóvel."""
    registros = obter_registros_imovel(imovel_id)

    if not registros:
        print("Nenhum equipamento vinculado a este imóvel.")
        return None

    print("\nEquipamentos vinculados:")
    for i, item in enumerate(registros, start=1):
        print(
            f"  {i} - {item['comodo_nome']} | {item['nome']} | "
            f"qtd: {item['quantidade']} | {item['horas']:.2f} h/dia"
        )

    while True:
        try:
            numero = int(input("Número do registro: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue

        if 1 <= numero <= len(registros):
            return registros[numero - 1]

        print("Erro: número fora da lista.")


def cadastrar():
    """PB08: cadastra equipamento em um cômodo do imóvel."""
    imovel = escolher_imovel()
    if imovel is None:
        return

    comodo_id = escolher_comodo(imovel["id"])
    if comodo_id is None:
        return

    equipamento = escolher_eletrodomestico()
    if equipamento is None:
        return

    existentes = listar_eletrodomesticos_comodo(comodo_id)
    if any(
        registro["eletrodomestico_id"] == equipamento["id"]
        for registro in existentes
    ):
        print("Esse equipamento já está no cômodo. Use a opção Editar.")
        return

    quantidade = ler_quantidade()
    horas = ler_horas()

    registro_id = adicionar_eletrodomestico_comodo(
        comodo_id,
        equipamento["id"],
        quantidade,
        horas,
    )

    print(f"Registro salvo no banco de dados! ID: {registro_id}")


def consultar():
    """PB10: consulta os equipamentos e mostra a tabela de consumo do ano."""
    imovel = escolher_imovel()
    if imovel is None:
        return

    print(f"\nConsumo estimado de '{imovel.get('endereco') or 'imóvel'}':")

    lista_total = []
    comodos = listar_comodos(imovel["id"])

    for comodo in comodos:
        print(f"\nCômodo: {comodo['nome']}")
        lista = mostrar_equipamentos(comodo["id"], com_consumo=True)
        lista_total.extend(lista)

    if not lista_total:
        print("\nNenhum equipamento vinculado a este imóvel.")
        return

    print("\nConsumo estimado do ano:")
    mostrar_tabela_anual(lista_total)


def editar():
    """PB09 T01 e T02: seleciona e edita quantidade e tempo de uso."""
    imovel = escolher_imovel()
    if imovel is None:
        return

    registro = selecionar_registro(imovel["id"])
    if registro is None:
        return

    print("Aperte Enter para manter o valor atual.")
    print(f"Quantidade atual: {registro['quantidade']}")
    quantidade = ler_quantidade(atual=registro["quantidade"])

    print(f"Horas atuais: {registro['horas']}")
    horas = ler_horas(atual=registro["horas"])

    linhas_alteradas = atualizar_eletrodomestico_comodo(
        registro["id"],
        quantidade,
        horas,
    )

    if linhas_alteradas:
        print("Registro atualizado no banco de dados!")
    else:
        print("Nenhum registro foi alterado.")


def remover():
    """PB09 T03: remove um registro após confirmação."""
    imovel = escolher_imovel()
    if imovel is None:
        return

    registro = selecionar_registro(imovel["id"])
    if registro is None:
        return

    resposta = (
        input(
            f"Remover '{registro['nome']}' do cômodo "
            f"'{registro['comodo_nome']}'? (s/n): "
        )
        .strip()
        .lower()
    )

    if resposta != "s":
        print("Remoção cancelada. Nada foi alterado.")
        return

    linhas_excluidas = remover_eletrodomestico_comodo(registro["id"])
    if linhas_excluidas:
        print("Registro removido do banco de dados!")
    else:
        print("Nenhum registro foi removido.")


def main():
    """Menu principal do dimensionamento energético integrado ao banco."""
    print("=== Dimensionamento Energético Residencial ===")
    print("Dados de imóveis, cômodos e equipamentos são lidos do MySQL.")

    while True:
        print("\n1 - Cadastrar equipamento no imóvel")
        print("2 - Consultar equipamentos do imóvel")
        print("3 - Editar registro de uso")
        print("4 - Remover registro de uso")
        print("0 - Sair")

        opcao = input("Opção: ").strip()

        try:
            if opcao == "1":
                cadastrar()
            elif opcao == "2":
                consultar()
            elif opcao == "3":
                editar()
            elif opcao == "4":
                remover()
            elif opcao == "0":
                print("Até mais!")
                break
            else:
                print("Opção inválida.")
        except Exception as erro:
            print(f"Erro durante a operação: {erro}")
            print("Verifique a configuração do MySQL em db_connection.py.")


if __name__ == "__main__":
    main()
