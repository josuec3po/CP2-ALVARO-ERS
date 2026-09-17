import sqlite3

# PB01[T01] Criar o arquivo do banco SQLite. ===========================================================
def inicializar_banco():
    
    conexao = sqlite3.connect('energia.db')
    cursor = conexao.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL
        )
    ''')
    
    conexao.commit()
    conexao.close()
    print("Tabela 'usuarios' configurada com sucesso no banco energia.db!")

# Teste isolado para PB01[T01]
if __name__ == "__main__":
    inicializar_banco()
# =======================================================================================================

import getpass

def obter_dados_cadastro():
    # PB01 [T02] - Desenvolver entradas (inputs) para cadastro ==========================================
    print("\n--- TELA DE CADASTRO ---")
    nome = input("Digite seu nome completo: ").strip()
    email = input("Digite seu e-mail: ").strip()

    # Getpass garante segurança
    senha = getpass.getpass("Digite sua senha (a digitação ficará invisível por segurança): ").strip()

    # obs: No flet o getpass fica ft.TextField(password=True)
    
    return nome, email, senha

# Teste isolado para PB01[T02]
if __name__ == "__main__":
    nome, email, senha = obter_dados_cadastro()
    print(f"\n[Teste] Dados recebidos com sucesso!")
    print(f"Nome: {nome} | E-mail: {email} | Senha: (oculta por segurança, mas recebida no código)")