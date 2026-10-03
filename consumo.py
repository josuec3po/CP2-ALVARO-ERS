"""Camada de consumo: cadastro e histórico de consumo de energia por imóvel."""
import sqlite3
from persistencia import BancoDados, RegistroNaoEncontrado, ErroConexao


def cadastrar_consumo(usuario_id, imovel_id, ano, mes, consumo_kwh):
    """PB05/PB06: cadastra o consumo mensal de um imóvel.

    Retorna (True, mensagem) em sucesso, (False, mensagem) em erro.
    """
    banco = BancoDados()
    try:
        banco.salvar_consumo(usuario_id, imovel_id, ano, mes, consumo_kwh)
        return (True, "Consumo cadastrado com sucesso.")
    except ValueError as erro:
        return (False, f"Dados inválidos: {erro}")
    except RegistroNaoEncontrado:
        return (False, "Imóvel não encontrado para este usuário.")
    except sqlite3.IntegrityError:
        return (False, f"Já existe consumo cadastrado para {mes:02d}/{ano}.")
    except ErroConexao as erro:
        return (False, f"Não foi possível conectar ao banco: {erro}")


def consultar_historico(usuario_id, imovel_id):
    """PB07: histórico de consumo de um imóvel, em ordem cronológica.

    Retorna (True, lista_de_registros) em sucesso, (False, mensagem) em erro.
    """
    banco = BancoDados()
    try:
        registros = banco.listar_consumos(usuario_id, imovel_id)
        return (True, registros)
    except RegistroNaoEncontrado:
        return (False, "Imóvel não encontrado para este usuário.")
    except ErroConexao as erro:
        return (False, f"Não foi possível conectar ao banco: {erro}")