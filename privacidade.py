# PB15 - Isolamento e privacidade dos imóveis

import CP1.dados as dados


# T02 - Guardar o usuário logado
# (o login em login.py já preenche dados.usuario_logado)
def sair():
    """Logout: ninguém fica logado."""
    dados.usuario_logado = None
    print("Você saiu da conta.")


# T01 - Ligar cada imóvel ao seu dono
# PROVISÓRIO
def cadastrar_imovel(nome):
    if dados.usuario_logado is None:
        print("Erro: faça login primeiro.")
        return None

    maior_id = 0
    for imovel in dados.imoveis:
        if imovel["id"] > maior_id:
            maior_id = imovel["id"]

    imovel = {
        "id": maior_id + 1,
        "id_usuario": dados.usuario_logado["id"],  # dono do imóvel
        "nome": nome,
    }
    dados.imoveis.append(imovel)
    return imovel


# T03 - Filtrar imóveis pelo usuário logado
def listar_meus_imoveis():
    
    meus = []
    if dados.usuario_logado is None:
        return meus

    for imovel in dados.imoveis:
        if imovel["id_usuario"] == dados.usuario_logado["id"]:
            meus.append(imovel)
    return meus


def buscar_meu_imovel(id_imovel):
   
    for imovel in listar_meus_imoveis():
        if imovel["id"] == id_imovel:
            return imovel
    return None


def editar_imovel(id_imovel, novo_nome):
    imovel = buscar_meu_imovel(id_imovel)
    if imovel is None:
        print("Erro: imóvel não encontrado.")
        return False

    imovel["nome"] = novo_nome
    return True


def excluir_imovel(id_imovel):
    imovel = buscar_meu_imovel(id_imovel)
    if imovel is None:
        print("Erro: imóvel não encontrado.")
        return False

    dados.imoveis.remove(imovel)
    return True