-- PB14: estrutura do banco central D1 e do adaptador para testes locais.
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
    email TEXT NOT NULL COLLATE NOCASE UNIQUE CHECK (length(trim(email)) > 0),
    senha_hash TEXT NOT NULL CHECK (length(trim(senha_hash)) > 0)
);

CREATE TABLE IF NOT EXISTS imoveis (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    identificacao TEXT NOT NULL CHECK (length(trim(identificacao)) > 0),
    localidade TEXT NOT NULL CHECK (length(trim(localidade)) > 0),
    tipo TEXT NOT NULL CHECK (length(trim(tipo)) > 0)
);
CREATE INDEX IF NOT EXISTS idx_imoveis_usuario ON imoveis(usuario_id);

CREATE TABLE IF NOT EXISTS consumos (
    id INTEGER PRIMARY KEY,
    imovel_id INTEGER NOT NULL REFERENCES imoveis(id) ON DELETE RESTRICT,
    ano INTEGER NOT NULL CHECK (typeof(ano) = 'integer' AND ano BETWEEN 1 AND 9999),
    mes INTEGER NOT NULL CHECK (typeof(mes) = 'integer' AND mes BETWEEN 1 AND 12),
    consumo_kwh REAL NOT NULL CHECK (
        typeof(consumo_kwh) IN ('integer', 'real')
        AND consumo_kwh >= 0 AND consumo_kwh < 1e999
    ),
    UNIQUE (imovel_id, ano, mes)
);
