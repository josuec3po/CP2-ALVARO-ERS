import mysql.connector
from mysql.connector import Error


# Configurações do banco
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "SUA_SENHA",
    "database": "energias_alvaro"
}


def conectar():
    """
    Cria e retorna uma conexão com o banco de dados.

    Returns:
        mysql.connector.connection.MySQLConnection:
            Conexão ativa com o banco.

    Raises:
        Error:
            Caso não seja possível conectar ao banco.
    """

    try:
        conexao = mysql.connector.connect(**DB_CONFIG)

        if conexao.is_connected():
            return conexao

    except Error as erro:
        print(f"Erro ao conectar ao banco: {erro}")
        raise
