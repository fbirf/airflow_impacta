
  
  

# Configuração do Projeto

  

O projeto utiliza Docker, Python, PosgreSQL e MongoDB. 

Na pasta raiz, execute o comando `docker-compose up` e aguarde a montagem dos containers.  

No arquivo **criptomoedas.py**, existe as seguintes constantes:

-  **CODIGO_CRIPTO** : None para buscar todas as moedas ou define um código de uma criptomoeda para filtrar, exemplo "BTC" para Bitcoin

-  **VALOR_MAXIMO_ALERTA** : define o valor máximo para realizar a busca e disparar o e-mail.

-  **ENDERECO_EMAIL** : define o destinatário do disparo do e-mail.

  

# Acesso

Os dados para acessar o **Airflow** são:

**URL**: localhost:8080/

**Usuário**: airflow

**Senha**: airflow

  

Os dados para acessar o **MongoDB** são:

**URL**: localhost:27017/

**Usuário**: root

**Senha**: 123

  

Os dados para acessar o **PostgreSQL** são:

**URL**: localhost:5432/

**Usuário**: airflow

**Senha**: airflow

## Debuggar script na máquina local

Para debuggar o script, devemos comentar **todas as anotações e imports relacionados ao airflow** e **alterar as strings de conexão** do MongoDB e PostgreSQL para o host localhost (para rodar no Docker, eles utilizam os IPs 10.0.0.2 e 10.0.0.3 respectivamente)