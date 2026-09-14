# DESENVOLVIMENTO DO SISTEMA ====================================================================================================================
# Desenvolva um sistema simples para estimativa do consumo médio mensal de energia elétrica de uma residência.
# * O sistema deverá permitir o cadastro do imóvel, contendo informações básicas para sua identificação. 

# * Deverá também possuir uma base de dados de equipamentos elétricos, 
# na qual cada equipamento será identificado por seu nome, categoria e potência nominal em watts (W).

# * Para cada imóvel, o usuário poderá selecionar os equipamentos existentes na residência 
# e informar a quantidade e o tempo médio diário de utilização de cada equipamento.

# * A partir dessas informações, o sistema deverá calcular o consumo médio mensal estimado de cada equipamento, 
# considerando sua potência, quantidade e período de utilização. Ao final, deverá apresentar o consumo total médio mensal estimado do imóvel, 
# em kWh/mês, obtido pela soma do consumo de todos os equipamentos cadastrados.
# ================================================================================================================================================

# Dicionários com desc/ dos equipamentos e respectivos IDs unicos
equipamentos_domesticos = [
    {"id": 1, "nome": "Chuveiro Elétrico", "categoria": "Banheiro", "potencia_w": 5500},
    {"id": 2, "nome": "Geladeira Frost Free", "categoria": "Cozinha", "potencia_w": 250},
    {"id": 3, "nome": "TV LED 50 pol", "categoria": "Sala", "potencia_w": 150},
    {"id": 4, "nome": "Ar Condicionado 9000 BTUs", "categoria": "Quarto", "potencia_w": 1100},
    {"id": 5, "nome": "Lâmpada LED 9W", "categoria": "Iluminação", "potencia_w": 9},
    {"id": 6, "nome": "Computador Desktop", "categoria": "Escritório", "potencia_w": 400}
]

print("=== SISTEMA DE ESTIMATIVA DE CONSUMO DE ENERGIA ===")

# Cadastro do Imovel 
nome_imovel = input("Identificação do Imóvel (Casa, Apartamento): ")
proprietario = input("Nome do Proprietário: ")

# Lista que vai guardar os equipamentos 
equipamentos_do_imovel = []

# Loop principal =================================================================================================================================
while True:
    print("\n--- Equipamentos Disponíveis ---")
    for equipamento in equipamentos_domesticos:
        print(f"[{equipamento['id']}] {equipamento['nome']} ({equipamento['potencia_w']}W)")
    print("[0] Finalizar e calcular consumo")
    print("--------------------------------")
    
    escolha = int(input("Digite o número do equipamento: "))
    
    # Condição de parada do loop
    if escolha == 0:
        break
        
    # Busca o equipamento na nossa base de dados
    equipamento_selecionado = None
    for equipamento in equipamentos_domesticos:
        if equipamento['id'] == escolha:
            equipamento_selecionado = equipamento
            break # Achou o equipamento, pode parar de procurar
            
    # Se encontrou o equipamento, pede os detalhes de uso
    if equipamento_selecionado != None:
        qtd = int(input(f"Quantidade de '{equipamento_selecionado['nome']}': "))
        horas = float(input("Tempo médio de uso diário (em horas): "))
        
        # Salva a escolha em um novo dicionário e guarda na lista do imóvel
        item_adicionado = {
            "nome": equipamento_selecionado['nome'],
            "potencia": equipamento_selecionado['potencia_w'],
            "quantidade": qtd,
            "horas_diarias": horas
        }
        equipamentos_do_imovel.append(item_adicionado)
        print("Equipamento adicionado com sucesso!")
        
    else:
        print("Opção inválida. Tente novamente.")

# Cálculo e Relatorio Final
if len(equipamentos_do_imovel) > 0:
    print(f"\n{'='*60}")
    print(f" RELATÓRIO DE CONSUMO MENSAL")
    print(f" Imóvel: {nome_imovel} | Proprietário: {proprietario}")
    print(f"{'='*60}")
    
    consumo_total = 0
    
    for item in equipamentos_do_imovel:
        # Calcula o consumo de cada item da lista (formula: Potencia * Qtd * Horas * 30 dias / 1000)
        consumo_mensal = (item["potencia"] * item["quantidade"] * item["horas_diarias"] * 30) / 1000
        consumo_total = consumo_total + consumo_mensal
        
        print(f"- {item['quantidade']}x {item['nome']} ({item['potencia']}W)")
        print(f"  Uso diário: {item['horas_diarias']}h | Consumo: {consumo_mensal:.2f} kWh/mês")
        
    print(f"{'-'*60}")
    print(f" CONSUMO TOTAL ESTIMADO: {consumo_total:.2f} kWh/mês")
    print(f"{'='*60}\n")
else:
    print("\nNenhum equipamento foi cadastrado.")