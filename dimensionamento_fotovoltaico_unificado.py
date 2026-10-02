import math
from typing import List, Dict, Optional, Tuple

def calcular_energia_alvo(consumo_mensal: float, fator_compensacao: float) -> float:
    """Calcula a energia mensal desejada (E_FV = C_m x f)."""
    return consumo_mensal * fator_compensacao

def calcular_potencia_necessaria(energia_alvo: float, hsp: float, dias: int, fator_desempenho: float) -> float:
    """Calcula a potência fotovoltaica necessária (P_FV = E_FV / (HSP x D x N))."""
    if hsp <= 0 or dias <= 0 or fator_desempenho <= 0:
        raise ValueError("HSP, dias e fator de desempenho devem ser maiores que zero.")
    return energia_alvo / (hsp * dias * fator_desempenho)

def selecionar_modulo(modulos: List[Dict], criterio: str = "custo_beneficio") -> Optional[Dict]:
    """Escolhe um módulo baseado num critério específico."""
    if not modulos:
        return None
        
    if criterio == "custo_beneficio":
        return min(modulos, key=lambda m: m['preco'] / m['potencia_wp'])
    elif criterio == "maior_potencia":
        return max(modulos, key=lambda m: m['potencia_wp'])
    
    return modulos[0]

def calcular_quantidade_e_potencia_instalada(potencia_fv_kw: float, potencia_modulo_w: float) -> Tuple[int, float]:
    """Calcula a quantidade de painéis e a potência efetiva instalada."""
    if potencia_modulo_w <= 0:
        raise ValueError("A potência do módulo deve ser maior que zero.")
    quantidade_paineis = math.ceil((potencia_fv_kw * 1000) / potencia_modulo_w)
    potencia_instalada_kw = (quantidade_paineis * potencia_modulo_w) / 1000
    return quantidade_paineis, potencia_instalada_kw

def dimensionar_sistema_completo(consumo_mensal: float, fator_compensacao: float, hsp: float, fator_desempenho: float, modulos_disponiveis: List[Dict]) -> Dict:
    """Executa o fluxo completo do dimensionamento fotovoltaico."""
    dias_no_mes = 30
    
    energia_alvo = calcular_energia_alvo(consumo_mensal, fator_compensacao)
    potencia_fv = calcular_potencia_necessaria(energia_alvo, hsp, dias_no_mes, fator_desempenho)
    
    modulo_selecionado = selecionar_modulo(modulos_disponiveis, criterio="custo_beneficio")
    if not modulo_selecionado:
        raise ValueError("Nenhum módulo disponível para seleção.")
        
    qtd_modulos, pot_instalada = calcular_quantidade_e_potencia_instalada(
        potencia_fv, modulo_selecionado['potencia_wp']
    )
    
    return {
        "energia_alvo_kwh": energia_alvo,
        "potencia_necessaria_kwp": potencia_fv,
        "modulo_escolhido": modulo_selecionado,
        "quantidade_modulos": qtd_modulos,
        "potencia_instalada_kwp": pot_instalada
    }

# --- Simulação e Integração com DB/Zip ---
if __name__ == "__main__":
    # Mock simulando dados extraídos dos esquemas SQL (sql-schemas/UT) do ZIP CP2-ALVARO-ERS-main
    catalogo_modulos = [
        {"modelo": "Painel Standard", "potencia_wp": 450, "preco": 800.00},
        {"modelo": "Painel Premium", "potencia_wp": 550, "preco": 1100.00},
        {"modelo": "Painel Económico", "potencia_wp": 330, "preco": 550.00}
    ]

    try:
        resultado = dimensionar_sistema_completo(
            consumo_mensal=500,
            fator_compensacao=1.0,
            hsp=4.5,
            fator_desempenho=0.75,
            modulos_disponiveis=catalogo_modulos
        )

        print("=== Relatório de Dimensionamento Fotovoltaico ===")
        print(f"Energia Alvo: {resultado['energia_alvo_kwh']:.2f} kWh/mês")
        print(f"Potência Necessária (FV): {resultado['potencia_necessaria_kwp']:.2f} kWp")
        print(f"Módulo Selecionado: {resultado['modulo_escolhido']['modelo']} ({resultado['modulo_escolhido']['potencia_wp']} Wp)")
        print(f"Quantidade de Módulos: {resultado['quantidade_modulos']} unidades")
        print(f"Potência Efetiva Instalada: {resultado['potencia_instalada_kwp']:.2f} kWp")

        potencia_necessaria_w = resultado['potencia_necessaria_kwp'] * 1000
        potencia_instalada_w = resultado['potencia_instalada_kwp'] * 1000
        print("\n--- Verificação de Unidades ---")
        print(f"Potência Necessária: {resultado['potencia_necessaria_kwp']:.2f} kWp = {potencia_necessaria_w:.2f} Wp")
        print(f"Potência Instalada: {resultado['potencia_instalada_kwp']:.2f} kWp = {potencia_instalada_w:.2f} Wp")
    except Exception as e:
        print(f"Erro durante o dimensionamento: {e}")
