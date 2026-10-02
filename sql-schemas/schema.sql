/*
=====================================================================
                    ESTRUTURA DO BANCO DE DADOS
=====================================================================

                         USUARIOS
                            │
                            │ 1:N
                            ▼
                         IMOVEIS
                            │
                            │ 1:N
                            ▼
                          COMODOS
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 │ 1:N                 │ 1:N
                 ▼                     ▼
     ELETRODOMESTICOS_COMODO     CONSUMO_ENERGETICO
                 │
                 │ N:1
                 ▼
       CATALOGO_ELETRODOMESTICOS


RELACIONAMENTOS:

USUARIOS
   └── possui vários → IMOVEIS

IMOVEIS
   └── possui vários → COMODOS

COMODOS
   ├── possui vários → ELETRODOMESTICOS_COMODO
   └── possui vários → CONSUMO_ENERGETICO

CATALOGO_ELETRODOMESTICOS
   └── define os eletrodomésticos disponíveis no sistema

ELETRODOMESTICOS_COMODO
   └── associa um eletrodoméstico do catálogo a um cômodo
       e registra seu tempo de uso.


=====================================================================
*/

CREATE DATABASE energias_alvaro;

USE energias_alvaro;

CREATE TABLE catalogo_eletrodomesticos (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nome VARCHAR(30) NOT NULL, 
	potencia INTEGER NOT NULL
);

CREATE TABLE usuarios (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nome VARCHAR(100) NOT NULL,
	email VARCHAR(50),
	senha VARCHAR(10)
);

CREATE TABLE imoveis (
	id INTEGER PRIMARY KEY AUTO_INCREMENT, 
	proprietario INTEGER NOT NULL,
	endereco VARCHAR(100),

	FOREIGN KEY (proprietario) REFERENCES usuarios(id)
);

CREATE TABLE comodos (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	nome VARCHAR(15) NOT NULL,
	imovel INTEGER NOT NULL,

	FOREIGN KEY (imovel) REFERENCES imoveis(id)
);

CREATE TABLE eletrodomesticos_comodo (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	comodo INTEGER NOT NULL,
	eletrodomestico INTEGER NOT NULL,
	tempo_uso DECIMAL(5, 2) NOT NULL,

	FOREIGN KEY (comodo) REFERENCES comodos(id),
	FOREIGN KEY (eletrodomestico) REFERENCES catalogo_eletrodomesticos(id)
);

CREATE TABLE consumo_energetico (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	comodo INTEGER NOT NULL,
	data TIMESTAMP NOT NULL,
	consumo_kwh DECIMAL(10, 2) NOT NULL,

	FOREIGN KEY (comodo) REFERENCES comodos(id)
);
