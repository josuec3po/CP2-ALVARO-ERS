import csv
from pathlib import Path

# Diretório onde este arquivo .py está localizado
BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_BATERIAS = BASE_DIR / "baterias.csv"
ARQUIVO_INVERSORES = BASE_DIR / "inversores.csv"
ARQUIVO_MODULOS = BASE_DIR / "modulos.csv"


# Campos que devem ser inteiros
CAMPOS_INT = {
    "id",
    "capacidade_ah",
    "dod_pct",
    "ciclos",
}

# Campos que devem ser números decimais
CAMPOS_FLOAT = {
    "tensao_nominal_v",
    "capacidade_kwh",
    "preco_brl",
}


def converter_valor(campo, valor):
    """
    Converte os valores do CSV para os tipos numéricos apropriados.

    Campos inteiros:
        id, capacidade_ah, dod_pct, ciclos

    Campos float:
        tensao_nominal_v, capacidade_kwh, preco_brl

    Demais campos permanecem como string.
    """
    if valor is None:
        return valor

    valor = valor.strip()

    if valor == "":
        return None

    if campo in CAMPOS_INT:
        try:
            return int(valor)
        except ValueError:
            raise ValueError(
                f"Valor inválido para o campo inteiro '{campo}': {valor}"
            )

    if campo in CAMPOS_FLOAT:
        try:
            return float(valor.replace(",", "."))
        except ValueError:
            raise ValueError(
                f"Valor inválido para o campo decimal '{campo}': {valor}"
            )

    return valor


def preparar_registro(registro):
    """
    Converte todos os campos de um registro para os tipos corretos.
    """
    return {
        campo: converter_valor(campo, valor)
        for campo, valor in registro.items()
    }


def ler_csv(caminho):
    """
    Lê um arquivo CSV separado por ';' e retorna uma lista de dicionários.
    """
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo CSV não encontrado: {caminho}"
        )

    registros = []

    with open(caminho, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, delimiter=";")

        if leitor.fieldnames is None:
            raise ValueError(f"O arquivo {caminho} não possui cabeçalho.")

        for linha in leitor:
            registros.append(preparar_registro(linha))

    return registros


# ============================================================
# LEITURA DOS DATASETS
# ============================================================

def ler_baterias():
    """Lê o dataset de baterias."""
    return ler_csv(ARQUIVO_BATERIAS)


def ler_inversores():
    """Lê o dataset de inversores."""
    return ler_csv(ARQUIVO_INVERSORES)


def ler_modulos():
    """Lê o dataset de módulos/painéis solares."""
    return ler_csv(ARQUIVO_MODULOS)


# ============================================================
# CRUD GENÉRICO
# ============================================================

def adicionar_registro(caminho, registro):
    """
    Adiciona um novo registro ao CSV.

    Exemplo:
        adicionar_registro(
            ARQUIVO_BATERIAS,
            {
                "id": 7,
                "fabricante": "Exemplo",
                ...
            }
        )
    """
    caminho = Path(caminho)

    registros = ler_csv(caminho)

    if not registros:
        raise ValueError("Não é possível adicionar sem cabeçalho.")

    campos = list(registros[0].keys())

    novo_registro = {
        campo: registro.get(campo)
        for campo in campos
    }

    novo_registro = preparar_registro(novo_registro)

    with open(caminho, "a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )

        escritor.writerow(novo_registro)


def buscar_por_id(caminho, id_registro):
    """
    Busca um registro pelo ID.
    """
    registros = ler_csv(caminho)

    id_registro = int(id_registro)

    for registro in registros:
        if registro["id"] == id_registro:
            return registro

    return None


def atualizar_registro(caminho, id_registro, novos_dados):
    """
    Atualiza um registro existente pelo ID.
    """
    caminho = Path(caminho)

    registros = ler_csv(caminho)
    id_registro = int(id_registro)

    encontrado = False

    for registro in registros:
        if registro["id"] == id_registro:
            for campo, valor in novos_dados.items():
                if campo != "id" and campo in registro:
                    registro[campo] = converter_valor(campo, valor)

            encontrado = True
            break

    if not encontrado:
        return False

    salvar_csv(caminho, registros)

    return True


def excluir_registro(caminho, id_registro):
    """
    Exclui um registro pelo ID.
    """
    caminho = Path(caminho)

    registros = ler_csv(caminho)
    id_registro = int(id_registro)

    novos_registros = [
        registro
        for registro in registros
        if registro["id"] != id_registro
    ]

    if len(novos_registros) == len(registros):
        return False

    salvar_csv(caminho, novos_registros)

    return True


def salvar_csv(caminho, registros):
    """
    Salva uma lista de registros novamente no CSV.
    """
    caminho = Path(caminho)

    if not registros:
        return

    campos = list(registros[0].keys())

    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";"
        )

        escritor.writeheader()
        escritor.writerows(registros)


# ============================================================
# FUNÇÕES ESPECÍFICAS DOS DATASETS
# ============================================================

def adicionar_bateria(bateria):
    """Adiciona uma bateria ao dataset."""
    adicionar_registro(ARQUIVO_BATERIAS, bateria)


def buscar_bateria(id_bateria):
    """Busca uma bateria pelo ID."""
    return buscar_por_id(ARQUIVO_BATERIAS, id_bateria)


def atualizar_bateria(id_bateria, dados):
    """Atualiza uma bateria."""
    return atualizar_registro(
        ARQUIVO_BATERIAS,
        id_bateria,
        dados
    )


def excluir_bateria(id_bateria):
    """Exclui uma bateria."""
    return excluir_registro(
        ARQUIVO_BATERIAS,
        id_bateria
    )


def adicionar_inversor(inversor):
    """Adiciona um inversor ao dataset."""
    adicionar_registro(ARQUIVO_INVERSORES, inversor)


def buscar_inversor(id_inversor):
    """Busca um inversor pelo ID."""
    return buscar_por_id(ARQUIVO_INVERSORES, id_inversor)


def atualizar_inversor(id_inversor, dados):
    """Atualiza um inversor."""
    return atualizar_registro(
        ARQUIVO_INVERSORES,
        id_inversor,
        dados
    )


def excluir_inversor(id_inversor):
    """Exclui um inversor."""
    return excluir_registro(
        ARQUIVO_INVERSORES,
        id_inversor
    )


def adicionar_modulo(modulo):
    """Adiciona um módulo/painel ao dataset."""
    adicionar_registro(ARQUIVO_MODULOS, modulo)


def buscar_modulo(id_modulo):
    """Busca um módulo/painel pelo ID."""
    return buscar_por_id(ARQUIVO_MODULOS, id_modulo)


def atualizar_modulo(id_modulo, dados):
    """Atualiza um módulo/painel."""
    return atualizar_registro(
        ARQUIVO_MODULOS,
        id_modulo,
        dados
    )


def excluir_modulo(id_modulo):
    """Exclui um módulo/painel."""
    return excluir_registro(
        ARQUIVO_MODULOS,
        id_modulo
    )


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":
    baterias = ler_baterias()
    inversores = ler_inversores()
    modulos = ler_modulos()

    print("Baterias:", len(baterias))
    print("Inversores:", len(inversores))
    print("Módulos:", len(modulos))

    if baterias:
        bateria = baterias[0]

        print("\nPrimeira bateria:")
        print(bateria)

        print("\nTipos dos campos numéricos:")
        print("id:", type(bateria["id"]))
        print("tensão:", type(bateria["tensao_nominal_v"]))
        print("capacidade:", type(bateria["capacidade_ah"]))
        print("kWh:", type(bateria["capacidade_kwh"]))
        print("preço:", type(bateria["preco_brl"]))
        print("ciclos:", type(bateria["ciclos"]))

        print("\nExemplo de cálculo:")
        energia_utilizavel = (
            bateria["capacidade_kwh"]
            * bateria["dod_pct"]
            / 100
        )

        print(
            f"Energia utilizável: "
            f"{energia_utilizavel:.2f} kWh"
        )
