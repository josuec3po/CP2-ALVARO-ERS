# Matriz (lista de listas) = tabela associativa imóvel-equipamento
# Cada linha da matriz: [id_imovel, id_equipamento, quantidade, horas_por_dia]
# Dicionários (id -> nome)
imoveis = {1: "Casa", 2: "Apartamento", 3: "Imóvel novo"}
equipamentos = {1: "Geladeira", 2: "Chuveiro", 3: "TV", 4: "Ar-condicionado"}
# Potência de cada equipamento em watts (id -> W). Valores aproximados.
potencias = {1: 150, 2: 5500, 3: 100, 4: 1400}
DIAS_NO_MES = 30  # usado no consumo mensal de cada equipamento

# Dias de cada mês do ano (usado na tabela anual; fevereiro com 28 dias)
dias_dos_meses = {
    "Janeiro": 31, "Fevereiro": 28, "Março": 31, "Abril": 30,
    "Maio": 31, "Junho": 30, "Julho": 31, "Agosto": 31,
    "Setembro": 30, "Outubro": 31, "Novembro": 30, "Dezembro": 31,
}

# Matriz de associação (começa vazia, nenhum imóvel tem equipamentos)
associacao = []

# PB08 - Entrada e validação de quantidade e tempo de uso

def ler_quantidade(atual=None):

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

# PB08 T04 - Persistir na associação (INSERT na matriz)

def salvar_registro(id_imovel, id_equipamento, quantidade, horas):
    associacao.append([id_imovel, id_equipamento, quantidade, horas])

# PB10 - Consulta dos equipamentos de um imóvel (o "JOIN")

def consultar_equipamentos(id_imovel):
   
    resultado = []
    for linha in associacao:
        if linha[0] == id_imovel:
          
            kwh_dia = potencias[linha[1]] * linha[2] * linha[3] / 1000
            resultado.append({
                "id_equipamento": linha[1],
                "nome": equipamentos[linha[1]],
                "quantidade": linha[2],
                "horas": linha[3],
                "kwh_dia": kwh_dia,
                "kwh_mes": kwh_dia * DIAS_NO_MES,
            })
    return resultado

def mostrar_equipamentos(id_imovel, com_consumo=False):
    
    lista = consultar_equipamentos(id_imovel)
    if len(lista) == 0:  
        print("Nenhum equipamento vinculado a este imóvel.")
        return lista
    for i, item in enumerate(lista, start=1):
        print(f"{i}) {item['nome']} | qtd: {item['quantidade']} | {item['horas']} h/dia")
        if com_consumo:
            print(f"   Consumo: {item['kwh_dia']:.2f} kWh/dia | {item['kwh_mes']:.2f} kWh/mês")
    return lista

def montar_tabela_anual(lista):
    
    total_dia = sum(item["kwh_dia"] for item in lista)  
    kwh_hora = total_dia / 24 
    tabela = []
    for mes, dias in dias_dos_meses.items():
        tabela.append([mes, kwh_hora, total_dia, total_dia * dias])
    return tabela

def mostrar_tabela_anual(lista):
    tabela = montar_tabela_anual(lista)
    print(f"{'Mês':<12}{'kWh/hora':>10}{'kWh/dia':>10}{'kWh/mês':>12}")
    print("-" * 44)
    for linha in tabela:
        print(f"{linha[0]:<12}{linha[1]:>10.3f}{linha[2]:>10.2f}{linha[3]:>12.2f}")
    print("-" * 44)

    # Máximo e média dos 12 meses (coluna kWh/mês da matriz)
    valores_mes = [linha[3] for linha in tabela]
    maximo = max(valores_mes)
    media = sum(valores_mes) / len(valores_mes)
    print(f"Consumo máximo: {maximo:.2f} kWh/mês")
    print(f"Consumo médio dos {len(valores_mes)} meses: {media:.2f} kWh/mês")

# Funções auxiliares de escolha

def escolher_do_dicionario(dicionario, titulo):
    
    print(titulo)
    for id_, nome in dicionario.items():
        print(f"  {id_} - {nome}")
    while True:
        try:
            escolha = int(input("Digite o id: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue
        if escolha in dicionario:
            return escolha
        print("Erro: id não existe.")


def achar_linha(id_imovel, id_equipamento):
    
    for linha in associacao:
        if linha[0] == id_imovel and linha[1] == id_equipamento:
            return linha
    return None


def selecionar_registro(id_imovel):
    
    lista = mostrar_equipamentos(id_imovel)
    if len(lista) == 0:
        return None
    while True:
        try:
            numero = int(input("Número do registro: "))
        except ValueError:
            print("Erro: digite um número inteiro.")
            continue
        if 1 <= numero <= len(lista):
            id_equipamento = lista[numero - 1]["id_equipamento"]
            return achar_linha(id_imovel, id_equipamento)
        print("Erro: número fora da lista.")

# Ações do menu

def cadastrar():
    """PB08: cadastra equipamento em um imóvel."""
    id_imovel = escolher_do_dicionario(imoveis, "\nImóveis:")
    id_equip = escolher_do_dicionario(equipamentos, "\nEquipamentos:")
    if achar_linha(id_imovel, id_equip) is not None:
        print("Esse equipamento já está no imóvel. Use a opção Editar.")
        return
    quantidade = ler_quantidade()
    horas = ler_horas()
    salvar_registro(id_imovel, id_equip, quantidade, horas)
    print("Registro salvo!")

def consultar():
    """PB10: consulta os equipamentos e mostra a tabela de consumo do ano."""
    id_imovel = escolher_do_dicionario(imoveis, "\nImóveis:")
    print(f"\nEquipamentos de '{imoveis[id_imovel]}':")
    lista = mostrar_equipamentos(id_imovel, com_consumo=True)
    if len(lista) > 0:  # sem equipamentos não há tabela para mostrar
        print("\nConsumo do ano:")
        mostrar_tabela_anual(lista)

def editar():
    """PB09 T01 e T02: seleciona e edita (Enter mantém o valor atual)."""
    id_imovel = escolher_do_dicionario(imoveis, "\nImóveis:")
    linha = selecionar_registro(id_imovel)
    if linha is None:
        return
    print("Aperte Enter para manter o valor atual.")
    print(f"Quantidade atual: {linha[2]}")
    linha[2] = ler_quantidade(atual=linha[2])
    print(f"Horas atuais: {linha[3]}")
    linha[3] = ler_horas(atual=linha[3])
    print("Registro atualizado!")

def remover():
    """PB09 T03: remove com confirmação prévia (Sim/Não)."""
    id_imovel = escolher_do_dicionario(imoveis, "\nImóveis:")
    linha = selecionar_registro(id_imovel)
    if linha is None:
        return
    resposta = input(f"Remover '{equipamentos[linha[1]]}'? (s/n): ").strip().lower()
    if resposta == "s":
        associacao.remove(linha)
        print("Registro removido!")
    else:
        print("Remoção cancelada. Nada foi alterado.")

# Menu principal

def main():
    while True:
        print("\n=== Dimensionamento Energético Residencial ===")
        print("1 - Cadastrar equipamento no imóvel")
        print("2 - Consultar equipamentos do imóvel")
        print("3 - Editar registro de uso")
        print("4 - Remover registro de uso")
        print("0 - Sair")
        opcao = input("Opção: ").strip()
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

main()