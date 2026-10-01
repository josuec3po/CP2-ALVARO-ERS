# login.py
# PB02 - Acesso à conta (login)

import dados


# T02 - Procurar o usuário pelo e-mail
def buscar_usuario_por_email(email):
    """Retorna o usuário encontrado ou None se o e-mail não existir."""
    for usuario in dados.usuarios:
        if usuario["email"] == email:
            return usuario
    return None


# T03 - Conferir a senha
def senha_correta(usuario, senha):
    """Retorna True se a senha digitada for igual à senha guardada."""
    return usuario["senha"] == senha


# Menu principal (provisório).
# Quando o menu real do sistema existir, troque esta função pela dele.
def menu_principal():
    print("Bem-vindo ao sistema,", dados.usuario_logado["nome"] + "!")


# T01 - Criar entrada de login
# T04 - Mensagens de erro e acesso ao sistema
def login():
    print("=== Login ===")
    email = input("E-mail: ").strip()
    senha = input("Senha: ").strip()

    usuario = buscar_usuario_por_email(email)

    if usuario is None or not senha_correta(usuario, senha):
        print("E-mail ou senha inválidos.")
        return False

    print("Login realizado com sucesso!")
    dados.usuario_logado = usuario  # PB15: guarda quem está logado
    menu_principal()
    return True
e

# Teste rápido: rode "python login.py"
if __name__ == "__main__":
    # Usuário de teste, só para testar o login sozinho
    dados.usuarios.append(
        {"id": 1, "nome": "Ana", "email": "ana@email.com", "senha": "1234"}
    )
    login()