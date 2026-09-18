"""PB03/PB04: menu de imóveis, chamado após a autenticação de PB02.

Contrato: executar_menu_imoveis(usuario_id, banco=None). O ID vem da sessão;
este módulo não cadastra usuários, verifica senhas nem solicita IDs ao usuário.
"""
import sqlite3

from persistencia import BancoDados, ErroConexao


class OperacaoCancelada(Exception):
    """Cancelamento solicitado antes de qualquer gravação."""


class MenuImoveis:
    def __init__(self, usuario_id, banco=None, *, entrada=input, saida=print):
        if type(usuario_id) is not int or not 1 <= usuario_id <= 9007199254740991:
            raise ValueError("O módulo de login deve fornecer um usuario_id inteiro positivo.")
        self.usuario_id = usuario_id
        self.banco = banco if banco is not None else BancoDados()
        self.entrada = entrada
        self.saida = saida

    def _campo(self, nome, atual=None):
        while True:
            sufixo = f" [{atual}] (Enter mantém)" if atual is not None else ""
            valor = self.entrada(f"{nome}{sufixo}: ").strip()
            if valor.casefold() == ":cancelar":
                raise OperacaoCancelada()
            if not valor and atual is not None:
                return atual
            if not valor:
                self.saida(f"{nome} é obrigatório. Preencha o campo.")
            elif len(valor) > 2000:
                self.saida(f"{nome} deve ter no máximo 2.000 caracteres.")
            else:
                return valor

    def _listar(self):
        imoveis = self.banco.listar_imoveis(self.usuario_id)
        if not imoveis:
            self.saida("Você ainda não tem imóveis cadastrados.")
        for numero, imovel in enumerate(imoveis, 1):
            self.saida(f"{numero}. {imovel['identificacao']} | {imovel['localidade']} | {imovel['tipo']}")
        return imoveis

    def _selecionar(self):
        imoveis = self._listar()
        if not imoveis:
            return None
        while True:
            escolha = self.entrada("Escolha o número da lista (0 cancela): ").strip()
            if escolha == "0" or escolha.casefold() == ":cancelar":
                raise OperacaoCancelada()
            # A seleção é uma posição na lista do usuário, nunca um ID livre.
            if escolha.isascii() and escolha.isdecimal() and len(escolha) <= 10:
                numero = int(escolha)
                if 1 <= numero <= len(imoveis):
                    return self.banco.buscar_imovel(self.usuario_id, imoveis[numero - 1]["id"])
            self.saida("Opção inválida. Escolha um número exibido na lista.")

    def _cadastrar(self):
        self.saida("Cadastro de imóvel. Digite :cancelar em qualquer campo para voltar.")
        identificacao = self._campo("Identificação")
        localidade = self._campo("Endereço/localidade")
        tipo = self._campo("Tipo (ex.: casa, apartamento)")
        self.banco.salvar_imovel(self.usuario_id, identificacao, localidade, tipo)
        self.saida("Imóvel cadastrado com sucesso.")

    def _editar(self):
        imovel = self._selecionar()
        if imovel is None:
            return
        self.saida("Edição de imóvel. Enter mantém o valor; :cancelar descarta as alterações.")
        novos = (
            self._campo("Identificação", imovel["identificacao"]),
            self._campo("Endereço/localidade", imovel["localidade"]),
            self._campo("Tipo", imovel["tipo"]),
        )
        anteriores = (imovel["identificacao"], imovel["localidade"], imovel["tipo"])
        if novos == anteriores:
            self.saida("Nenhuma alteração realizada.")
            return
        self.banco.atualizar_imovel(self.usuario_id, imovel["id"], *novos)
        self.saida("Imóvel atualizado com sucesso.")

    def _excluir(self):
        imovel = self._selecionar()
        if imovel is None:
            return
        self.saida(f"Excluir '{imovel['identificacao']}' em {imovel['localidade']}?")
        confirmacao = self.entrada("Digite EXCLUIR para confirmar; qualquer outra resposta cancela: ")
        if confirmacao.strip().upper() != "EXCLUIR":
            raise OperacaoCancelada()
        try:
            self.banco.excluir_imovel(self.usuario_id, imovel["id"])
        except sqlite3.IntegrityError:
            self.saida("Exclusão bloqueada: o imóvel possui registros vinculados. Seu histórico foi preservado.")
            return
        self.saida("Imóvel excluído com sucesso.")

    def executar(self):
        acoes = {"1": self._cadastrar, "2": self._listar, "3": self._editar, "4": self._excluir}
        try:
            while True:
                self.saida("\n=== MEUS IMÓVEIS ===\n1. Cadastrar\n2. Listar\n3. Editar\n4. Excluir\n0. Voltar")
                escolha = self.entrada("Opção: ").strip()
                if escolha == "0":
                    return
                acao = acoes.get(escolha)
                if acao is None:
                    self.saida("Opção inválida. Escolha uma opção do menu.")
                    continue
                try:
                    acao()
                except OperacaoCancelada:
                    self.saida("Operação cancelada. Nenhum dado foi alterado.")
                except ErroConexao:
                    self.saida("Não foi possível confirmar a operação no banco online. Confira a conexão/configuração e consulte os imóveis antes de repetir uma gravação.")
                except sqlite3.IntegrityError:
                    self.saida("Não foi possível salvar. Confira se o usuário está cadastrado e os vínculos são válidos.")
                except ValueError as erro:
                    self.saida(str(erro))
        except (EOFError, KeyboardInterrupt):
            self.saida("\nMenu encerrado. Operações já confirmadas permanecem salvas.")


def executar_menu_imoveis(usuario_id, banco=None, *, entrada=input, saida=print):
    """PB02 chama após login válido; retornar ao menu não encerra a sessão do app.

    usuario_id identifica uma conta já persistida pela PB01. Receber um ID não
    autentica ninguém: o módulo chamador é responsável por validar a sessão.
    banco pode ser a mesma instância BancoDados usada pelos outros módulos.
    """
    try:
        menu = MenuImoveis(usuario_id, banco, entrada=entrada, saida=saida)
    except ErroConexao as erro:
        saida(str(erro))
        return
    menu.executar()
