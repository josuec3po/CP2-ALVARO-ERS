# PB01 - Cadastro de usuário

import dados

# T03 - Validar os campos do cadastro
def validar_campos(nome, email, senha):

    if nome == "" or email == "" or senha == "":
        return "Todos os campos são obrigatórios."

    if "@" not in email:
        return "E-mail inválido: precisa conter '@'."

    return None


# T04 - Verificar se o e-mail já foi cadastrado
def email_ja_existe(email):
    for usuario in dados.usuarios:
        if usuario["email"] == email:
            return True
    return False


# T04 - Salvar o novo usuário
def salvar_usuario(nome, email, senha):
    novo_id = len(dados.usuarios) + 1

    usuario = {
        "id": novo_id,
        "nome": nome,
        "email": email,
        "senha": senha,
    }

    dados.usuarios.append(usuario)


# T02 - Receber os dados do cadastro
def cadastrar_usuario():
    print("=== Cadastro de Usuário ===")
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip()
    senha = input("Senha: ").strip()

    erro = validar_campos(nome, email, senha)
    if erro is not None:
        print("Erro:", erro)
        return False

    if email_ja_existe(email):
        print("Erro: este e-mail já está cadastrado.")
        return False

    salvar_usuario(nome, email, senha)
    print("Cadastro realizado com sucesso!")
    return True


# Teste 
if __name__ == "__main__":
    cadastrar_usuario()
    print(dados.usuarios)