-- impacta.criptomoeda definition

-- Drop table

-- DROP TABLE impacta.criptomoeda;

create database airflow;
CREATE SCHEMA impacta AUTHORIZATION airflow;

CREATE TABLE impacta.criptomoeda (
	id serial4 NOT NULL,
	nome varchar(255) NOT NULL,
	codigo varchar(255) NOT NULL,
	CONSTRAINT criptomoeda_pkey PRIMARY KEY (id)
);

-- impacta.valores definition

-- Drop table

-- DROP TABLE impacta.valores;

CREATE TABLE impacta.valores (
	id serial4 NOT NULL,
	id_criptomoeda int4 NOT NULL,
	valor numeric(15, 5) NOT NULL,
	valor_24h numeric(10, 5) NOT NULL,
	valor_7d numeric(10, 5) NOT NULL,
	valor_30d numeric(10, 5) NOT NULL,
	valor_60d numeric(10, 5) NOT NULL,
	valor_90d numeric(10, 5) NOT NULL,
	data_cadastro timestamp NULL,
	CONSTRAINT valores_pkey PRIMARY KEY (id)
);


-- impacta.valores foreign keys

ALTER TABLE impacta.valores ADD CONSTRAINT valores_ibfk_1 FOREIGN KEY (id_criptomoeda) REFERENCES impacta.criptomoeda(id);