# dados.py
# Arquivo compartilhado por todo o grupo: guarda os dados na memória.

# PB01 - lista de usuários cadastrados.
# Cada usuário é um dicionário:
# {"id": 1, "nome": "Ana", "email": "ana@email.com", "senha": "1234"}
usuarios = []

# PB15 - lista de imóveis (cada imóvel terá a chave "id_usuario").
imoveis = []

# PB15 - guarda o usuário logado (None = ninguém logado).
usuario_logado = None