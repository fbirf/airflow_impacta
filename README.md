

# Configuração do Projeto

O projeto utiliza Docker, Python, PosgreSQL e MongoDB.

Na pasta raiz, execute o comando `docker-compose up` e aguarde a montagem dos containers.
 
Feito isso, execute o comando `docker inspect network airflow_impacta_default` e identifique os IPs dos containers **airflow_impacta-postgres-1** e **airflow_impacta-mongo-1**.  Estes IPs serão utilizados nas constantes a seguir.

No arquivo **criptomoedas.py**, existe as seguintes constantes:

 - **HOST_BANCO_RELACIONAL** : define o IP do host do PostgreSQL
 -  **HOST_BANCO_NAO_RELACIONAL**: define o IP do host do MongoDB
 - **CODIGO_CRIPTO** : None para buscar todas as moedas ou define um código de uma criptomoeda para filtrar, exemplo "BTC" para Bitcoin
 - **VALOR_MAXIMO_ALERTA** : define o valor máximo para realizar a busca e disparar o e-mail.
 - **ENDERECO_EMAIL** : define o destinatário do disparo do e-mail.

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
