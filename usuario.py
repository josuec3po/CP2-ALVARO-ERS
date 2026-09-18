import sqlite3

# PB01[T01] Criar o arquivo do banco SQLite. ===========================================================
def inicializar_banco():
    
    conexao = sqlite3.connect('database.db')
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
    print("Tabela 'usuarios' configurada com sucesso no banco!")

# Teste isolado para PB01[T01]
if __name__ == "__main__":
   inicializar_banco()
# =======================================================================================================

import getpass

def obter_dados_cadastro():
    # PB01 [T02] - Desenvolver entradas (inputs) para cadastro ==========================================
    while True:
        print("\n--- TELA DE CADASTRO ---")
        nome = input("Digite seu nome completo: ").strip()
        email = input("Digite seu e-mail: ").strip()
        senha = getpass.getpass("Digite sua senha (a digitação ficará invisível por segurança): ").strip()
        # obs: No flet o getpass fica ft.TextField(password=True)

        # T03: Validação de campos vazios
        if not nome or not email or not senha:
            print("Erro: Todos os campos são obrigatórios!\n")
            continue

        if "@" not in email:
            print("Erro: Digite um e-mail válido")
            continue
        
        return nome, email, senha

# Teste isolado para PB01[T02]
if __name__ == "__main__":
    nome, email, senha = obter_dados_cadastro()
    print(f"\n[Teste] Dados recebidos com sucesso!")
    print(f"Nome: {nome} | E-mail: {email} | Senha: (oculta por segurança, mas recebido no código)")

import bcrypt

def salvar_usuario(nome, email, senha):
    # Criptografa a senha e salva o novo usuário no banco de dados.
    # Gera o hash seguro da senha usando bcrypt
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt)
    
    try:
        conexao = sqlite3.connect('database.db')
        cursor = conexao.cursor()
        
        # Executa a inserção no banco
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha_hash)
            VALUES (?, ?, ?)
        ''', (nome, email, senha_hash))
        
        conexao.commit()
        print(f"\nUsuário '{nome}' foi registrado.")

    except sqlite3.IntegrityError:
        # Trava para nao registrar mesmo email
        print(f"\nErro: E-mail '{email}' já cadstrado. Use outro!")
    finally:
        conexao.close()

# Fluxo de teste T04
if __name__ == "__main__":
    inicializar_banco()
    n, e, s = obter_dados_cadastro()
    salvar_usuario(n, e, s)