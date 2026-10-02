from database import conectar


# ============================================================
# USUÁRIOS
# ============================================================

def criar_usuario(nome, email, senha):
    """
    Cria um novo usuário.

    Args:
        nome (str): Nome do usuário.
        email (str): E-mail do usuário.
        senha (str): Senha do usuário.

    Returns:
        int: ID do usuário criado.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        sql = """
            INSERT INTO usuarios (nome, email, senha)
            VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (nome, email, senha))
        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def buscar_usuario(usuario_id):
    """
    Busca um usuário pelo ID.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        sql = """
            SELECT id, nome, email
            FROM usuarios
            WHERE id = %s
        """

        cursor.execute(sql, (usuario_id,))

        return cursor.fetchone()

    finally:
        cursor.close()
        conexao.close()


def listar_usuarios():
    """
    Retorna todos os usuários.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, email
            FROM usuarios
            ORDER BY id
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def atualizar_usuario(usuario_id, nome, email, senha=None):
    """
    Atualiza os dados de um usuário.

    Se senha for None, a senha atual não será alterada.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        if senha is not None:
            sql = """
                UPDATE usuarios
                SET nome = %s,
                    email = %s,
                    senha = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (nome, email, senha, usuario_id)
            )

        else:
            sql = """
                UPDATE usuarios
                SET nome = %s,
                    email = %s
                WHERE id = %s
            """

            cursor.execute(
                sql,
                (nome, email, usuario_id)
            )

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


def deletar_usuario(usuario_id):
    """
    Exclui um usuário pelo ID.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "DELETE FROM usuarios WHERE id = %s",
            (usuario_id,)
        )

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# IMÓVEIS
# ============================================================

def criar_imovel(proprietario, endereco):
    """
    Cria um imóvel para um usuário.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        sql = """
            INSERT INTO imoveis (proprietario, endereco)
            VALUES (%s, %s)
        """

        cursor.execute(sql, (proprietario, endereco))
        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def listar_imoveis(proprietario=None):
    """
    Lista imóveis.

    Se proprietario for informado, retorna apenas os imóveis
    pertencentes ao usuário especificado.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        if proprietario is not None:

            sql = """
                SELECT id, proprietario, endereco
                FROM imoveis
                WHERE proprietario = %s
                ORDER BY id
            """

            cursor.execute(sql, (proprietario,))

        else:

            cursor.execute("""
                SELECT id, proprietario, endereco
                FROM imoveis
                ORDER BY id
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def atualizar_imovel(imovel_id, endereco):
    """
    Atualiza o endereço de um imóvel.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE imoveis
            SET endereco = %s
            WHERE id = %s
        """, (endereco, imovel_id))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


def deletar_imovel(imovel_id):
    """
    Exclui um imóvel.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "DELETE FROM imoveis WHERE id = %s",
            (imovel_id,)
        )

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# CÔMODOS
# ============================================================

def criar_comodo(nome, imovel):
    """
    Cria um cômodo dentro de um imóvel.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO comodos (nome, imovel)
            VALUES (%s, %s)
        """, (nome, imovel))

        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def listar_comodos(imovel=None):
    """
    Lista os cômodos.

    Se imovel for informado, retorna apenas os cômodos
    pertencentes ao imóvel.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        if imovel is not None:

            cursor.execute("""
                SELECT id, nome, imovel
                FROM comodos
                WHERE imovel = %s
                ORDER BY id
            """, (imovel,))

        else:

            cursor.execute("""
                SELECT id, nome, imovel
                FROM comodos
                ORDER BY id
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def atualizar_comodo(comodo_id, nome):
    """
    Atualiza o nome de um cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE comodos
            SET nome = %s
            WHERE id = %s
        """, (nome, comodo_id))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


def deletar_comodo(comodo_id):
    """
    Exclui um cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute(
            "DELETE FROM comodos WHERE id = %s",
            (comodo_id,)
        )

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# CATÁLOGO DE ELETRODOMÉSTICOS
# ============================================================

def criar_eletrodomestico(nome, potencia):
    """
    Adiciona um eletrodoméstico ao catálogo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO catalogo_eletrodomesticos
                (nome, potencia)
            VALUES (%s, %s)
        """, (nome, potencia))

        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def listar_eletrodomesticos():
    """
    Retorna todos os eletrodomésticos do catálogo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, potencia
            FROM catalogo_eletrodomesticos
            ORDER BY nome
        """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def atualizar_eletrodomestico(eletrodomestico_id, nome, potencia):
    """
    Atualiza um eletrodoméstico do catálogo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE catalogo_eletrodomesticos
            SET nome = %s,
                potencia = %s
            WHERE id = %s
        """, (nome, potencia, eletrodomestico_id))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


def deletar_eletrodomestico(eletrodomestico_id):
    """
    Remove um eletrodoméstico do catálogo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM catalogo_eletrodomesticos
            WHERE id = %s
        """, (eletrodomestico_id,))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# ELETRODOMÉSTICOS DOS CÔMODOS
# ============================================================

def adicionar_eletrodomestico_comodo(
    comodo,
    eletrodomestico,
    tempo_uso
):
    """
    Adiciona um eletrodoméstico a um cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO eletrodomesticos_comodo
                (comodo, eletrodomestico, tempo_uso)
            VALUES (%s, %s, %s)
        """, (
            comodo,
            eletrodomestico,
            tempo_uso
        ))

        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def listar_eletrodomesticos_comodo(comodo):
    """
    Retorna todos os eletrodomésticos de um cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                ec.id,
                ec.comodo,
                e.id AS eletrodomestico_id,
                e.nome,
                e.potencia,
                ec.tempo_uso
            FROM eletrodomesticos_comodo ec
            INNER JOIN catalogo_eletrodomesticos e
                ON ec.eletrodomestico = e.id
            WHERE ec.comodo = %s
            ORDER BY e.nome
        """, (comodo,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def atualizar_tempo_uso(id_eletrodomestico_comodo, tempo_uso):
    """
    Atualiza o tempo de uso de um eletrodoméstico.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            UPDATE eletrodomesticos_comodo
            SET tempo_uso = %s
            WHERE id = %s
        """, (tempo_uso, id_eletrodomestico_comodo))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


def remover_eletrodomestico_comodo(id_eletrodomestico_comodo):
    """
    Remove um eletrodoméstico de um cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM eletrodomesticos_comodo
            WHERE id = %s
        """, (id_eletrodomestico_comodo,))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# CONSUMO ENERGÉTICO
# ============================================================

def registrar_consumo(comodo, data, consumo_kwh):
    """
    Registra o consumo energético de um cômodo.

    Args:
        comodo (int): ID do cômodo.
        data: Data/hora do registro.
        consumo_kwh (float): Consumo em kWh.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO consumo_energetico
                (comodo, data, consumo_kw)
            VALUES (%s, %s, %s)
        """, (
            comodo,
            data,
            consumo_kwh
        ))

        conexao.commit()

        return cursor.lastrowid

    finally:
        cursor.close()
        conexao.close()


def listar_consumo(comodo=None):
    """
    Lista os registros de consumo.

    Se comodo for informado, retorna somente os registros
    daquele cômodo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        if comodo is not None:

            cursor.execute("""
                SELECT id, comodo, data, consumo_kw
                FROM consumo_energetico
                WHERE comodo = %s
                ORDER BY data
            """, (comodo,))

        else:

            cursor.execute("""
                SELECT id, comodo, data, consumo_kw
                FROM consumo_energetico
                ORDER BY data
            """)

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def deletar_consumo(consumo_id):
    """
    Exclui um registro de consumo.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor()

        cursor.execute("""
            DELETE FROM consumo_energetico
            WHERE id = %s
        """, (consumo_id,))

        conexao.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        conexao.close()


# ============================================================
# CONSULTAS ÚTEIS PARA OS GRÁFICOS
# ============================================================

def consumo_por_comodo(imovel):
    """
    Retorna o consumo total de cada cômodo de um imóvel.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id,
                c.nome,
                SUM(ce.consumo_kw) AS consumo_total
            FROM comodos c
            INNER JOIN consumo_energetico ce
                ON c.id = ce.comodo
            WHERE c.imovel = %s
            GROUP BY c.id, c.nome
            ORDER BY consumo_total DESC
        """, (imovel,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()


def consumo_por_data(comodo):
    """
    Retorna o consumo de um cômodo agrupado por data.
    """

    conexao = conectar()

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                DATE(data) AS data,
                SUM(consumo_kw) AS consumo_total
            FROM consumo_energetico
            WHERE comodo = %s
            GROUP BY DATE(data)
            ORDER BY data
        """, (comodo,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conexao.close()
