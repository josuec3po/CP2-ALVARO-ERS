# PB15 T04 - Testes práticos de isolamento de dados

import builtins
import CP1.dados as dados
import CP1.cadastro as cadastro
import CP1.login as login
import CP1.privacidade as privacidade


def fazer_login(email, senha):
    
    respostas = iter([email, senha])
    builtins.input = lambda texto="": next(respostas)
    login.login()


def conferir(descricao, condicao):
    if condicao:
        print("[OK]    ", descricao)
    else:
        print("[FALHOU]", descricao)
        raise SystemExit(1)


# 1. Cadastrar o Usuário A, logar e criar a "Casa X"
cadastro.salvar_usuario("Usuario A", "a@email.com", "111")
fazer_login("a@email.com", "111")
privacidade.cadastrar_imovel("Casa X")
conferir("Usuário A vê a Casa X",
         len(privacidade.listar_meus_imoveis()) == 1)

# 2. Sair e cadastrar o Usuário B
privacidade.sair()
conferir("Logout limpou o usuário logado", dados.usuario_logado is None)
cadastro.salvar_usuario("Usuario B", "b@email.com", "222")
fazer_login("b@email.com", "222")

# 3. A Casa X não pode aparecer para o Usuário B
conferir("Usuário B NÃO vê a Casa X",
         len(privacidade.listar_meus_imoveis()) == 0)

# 4. Usuário B tenta mexer na Casa X (id 1) à força
conferir("Usuário B não consegue editar a Casa X",
         privacidade.editar_imovel(1, "Invadida") is False)
conferir("Usuário B não consegue excluir a Casa X",
         privacidade.excluir_imovel(1) is False)
conferir("A Casa X continua intacta no sistema",
         len(dados.imoveis) == 1 and dados.imoveis[0]["nome"] == "Casa X")

# 5. Usuário A volta e ainda tem a Casa X
privacidade.sair()
fazer_login("a@email.com", "111")
conferir("Usuário A ainda vê a Casa X",
         len(privacidade.listar_meus_imoveis()) == 1)

print()
print("Todos os testes passaram!")