import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

from crud import consumo_horario_imovel

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TARIFA_KWH = 0.85


# ============================================================
# FUNÇÕES DE PROCESSAMENTO DOS DADOS
# ============================================================

def obter_horarios(dados):
    """Retorna a lista de horários presentes nos dados."""
    return list(dados.keys())

def obter_potencias(dados):
    """Retorna somente os valores de potência."""
    return [dados[horario]["potencia"] for horario in dados]

def calcular_consumo_total(dados):
    """Calcula o consumo total em kWh."""
    return sum(dados[horario]["consumo"] for horario in dados)

def calcular_potencia_media(dados):
    """Calcula a potência média registrada."""
    potencias = obter_potencias(dados)
    if not potencias:
        return 0
    return sum(potencias) / len(potencias)

def calcular_pico(dados):
    """Retorna o maior valor de potência registrado."""
    potencias = obter_potencias(dados)
    if not potencias:
        return 0
    return max(potencias)

def calcular_custo(dados):
    """Calcula uma estimativa de custo utilizando a tarifa definida."""
    consumo = calcular_consumo_total(dados)
    return consumo * TARIFA_KWH


# ============================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ============================================================

class MonitorEnergia:

    def __init__(self, janela, imovel_id=1):
        """
        Inicializa a aplicação.
        """
        self.janela = janela
        self.imovel_id = imovel_id

        # Inicializa a estrutura de dados vazia
        self.dados = self.gerar_estrutura_vazia()

        # Configuração da janela.
        self.janela.title("Monitor de Consumo Energético Real")
        self.janela.geometry("1200x750")
        self.janela.minsize(900, 600)

        # Cria a interface.
        self.criar_interface()

        # Busca os dados iniciais do banco e atualiza a tela
        self.atualizar_dados()

    def gerar_estrutura_vazia(self):
        """Gera um dicionário com 24 horas zeradas."""
        estrutura = {}
        for i in range(24):
            hora_str = f"{i:02d}:00"
            estrutura[hora_str] = {"potencia": 0.0, "consumo": 0.0}
        return estrutura

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):
        """Cria todos os elementos visuais da aplicação."""

        titulo = ttk.Label(self.janela, text="Monitor de Consumo Energético", font=("Arial", 20, "bold"))
        titulo.pack(pady=(15, 5))

        subtitulo = ttk.Label(self.janela, text=f"Análise do consumo de energia elétrica (Imóvel ID: {self.imovel_id})")
        subtitulo.pack(pady=(0, 10))

        # Painel de Indicadores
        painel_indicadores = ttk.Frame(self.janela)
        painel_indicadores.pack(fill="x", padx=20, pady=10)

        self.lbl_consumo = ttk.Label(painel_indicadores, text="Consumo\n0.00 kWh", font=("Arial", 14, "bold"), anchor="center")
        self.lbl_consumo.pack(side="left", expand=True)

        self.lbl_media = ttk.Label(painel_indicadores, text="Potência média\n0.00 kW", font=("Arial", 14, "bold"), anchor="center")
        self.lbl_media.pack(side="left", expand=True)

        self.lbl_pico = ttk.Label(painel_indicadores, text="Pico\n0.00 kW", font=("Arial", 14, "bold"), anchor="center")
        self.lbl_pico.pack(side="left", expand=True)

        self.lbl_custo = ttk.Label(painel_indicadores, text="Custo estimado\nR$ 0,00", font=("Arial", 14, "bold"), anchor="center")
        self.lbl_custo.pack(side="left", expand=True)

        # Botões
        painel_botoes = ttk.Frame(self.janela)
        painel_botoes.pack(pady=5)

        btn_atualizar = ttk.Button(painel_botoes, text="Atualizar dados do Banco", command=self.atualizar_dados)
        btn_atualizar.pack(side="left", padx=5)

        # Área de Gráficos
        self.criar_graficos()


    # ========================================================
    # CRIAÇÃO DOS GRÁFICOS
    # ========================================================

    def criar_graficos(self):
        """Cria a figura Matplotlib e os dois gráficos."""
        self.figura = Figure(figsize=(10, 5), dpi=100)
        self.ax_potencia = self.figura.add_subplot(211)
        self.ax_consumo = self.figura.add_subplot(212)
        self.figura.tight_layout(h_pad=3)

        self.canvas = FigureCanvasTkAgg(self.figura, master=self.janela)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
        self.canvas.mpl_connect("motion_notify_event", self.mouse_movimento)


    # ========================================================
    # ATUALIZAÇÃO DOS GRÁFICOS
    # ========================================================

    def atualizar_graficos(self):
        """Redesenha os gráficos utilizando os dados consultados."""
        horarios = obter_horarios(self.dados)
        potencias = obter_potencias(self.dados)

        consumo_acumulado = []
        total = 0
        for horario in horarios:
            total += self.dados[horario]["consumo"]
            consumo_acumulado.append(total)

        # Gráfico Potência
        self.ax_potencia.clear()
        self.ax_potencia.plot(horarios, potencias, marker="o", linewidth=2, label="Potência Média (kW)")
        self.ax_potencia.fill_between(range(len(horarios)), potencias, alpha=0.15)
        self.ax_potencia.set_title("Potência Registrada por Hora")
        self.ax_potencia.set_ylabel("Potência (kW)")
        self.ax_potencia.grid(True, alpha=0.3)
        self.ax_potencia.legend()

        # Gráfico Consumo
        self.ax_consumo.clear()
        self.ax_consumo.plot(horarios, consumo_acumulado, marker="o", linewidth=2, label="Consumo acumulado", color="orange")
        self.ax_consumo.fill_between(range(len(horarios)), consumo_acumulado, alpha=0.15, color="orange")
        self.ax_consumo.set_title("Consumo acumulado")
        self.ax_consumo.set_ylabel("Energia (kWh)")
        self.ax_consumo.set_xlabel("Horário")
        self.ax_consumo.grid(True, alpha=0.3)
        self.ax_consumo.legend()

        self.figura.autofmt_xdate()
        self.canvas.draw_idle()

    # ========================================================
    # ATUALIZAÇÃO DOS INDICADORES E DADOS
    # ========================================================

    def atualizar_indicadores(self):
        """Atualiza os números apresentados no topo da aplicação."""
        consumo = calcular_consumo_total(self.dados)
        media = calcular_potencia_media(self.dados)
        pico = calcular_pico(self.dados)
        custo = calcular_custo(self.dados)

        self.lbl_consumo.config(text=f"Consumo\n{consumo:.2f} kWh")
        self.lbl_media.config(text=f"Potência média\n{media:.2f} kW")
        self.lbl_pico.config(text=f"Pico\n{pico:.2f} kW")
        self.lbl_custo.config(text=f"Custo estimado\nR$ {custo:.2f}")

    def atualizar_interface(self):
        """Atualiza todos os elementos da interface."""
        self.atualizar_graficos()
        self.atualizar_indicadores()

    def atualizar_dados(self):
        """
        Consulta o banco de dados MySQL para buscar os registros de hoje.
        Caso hoje não possua registos, retorna os dados do dia mais recente.
        """
        # Tenta buscar os dados do dia de hoje
        data_hoje = datetime.now().strftime('%Y-%m-%d')

        registros_db = consumo_horario_imovel(self.imovel_id, data_referencia=data_hoje)

        # Reseta os dados para 0.00 em todas as 24 horas
        self.dados = self.gerar_estrutura_vazia()

        # Preenche os horários correspondentes com o consumo retornado do banco
        if registros_db:
            for registro in registros_db:
                hora_int = registro['hora']
                hora_str = f"{hora_int:02d}:00"
                consumo = float(registro['consumo_total'])

                self.dados[hora_str]["consumo"] = consumo
                self.dados[hora_str]["potencia"] = consumo

        self.atualizar_interface()

    # ========================================================
    # INTERAÇÃO COM O MOUSE
    # ========================================================

    def mouse_movimento(self, evento):
        """Mostra informações do ponto mais próximo quando o mouse passa sobre o gráfico."""
        if evento.inaxes not in [self.ax_potencia, self.ax_consumo]:
            return

        if evento.xdata is None:
            return

        indice = round(evento.xdata)
        horarios = obter_horarios(self.dados)

        if indice < 0 or indice >= len(horarios):
            return

        horario = horarios[indice]

        if evento.inaxes == self.ax_potencia:
            valor = self.dados[horario]["potencia"]
            evento.inaxes.set_title(f"Potência às {horario}: {valor:.2f} kW")
        else:
            consumo = self.dados[horario]["consumo"]
            evento.inaxes.set_title(f"Consumo às {horario}: {consumo:.2f} kWh")

        self.canvas.draw_idle()

# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    janela = tk.Tk()
    app = MonitorEnergia(janela, imovel_id=1)
    janela.mainloop()