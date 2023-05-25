# External librarys
from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import timedelta, datetime
import psycopg2
import numpy
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# DAG default arguments
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    "start_date": datetime(2023, 5, 25, 00, 00),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(hours=1),
    'execution_timeout': timedelta(hours=1),
    'schedule_interval': None
    }

HOST_BANCO_DADOS = "172.20.0.4"
CODIGO_CRIPTO = "BTC"
VALOR_MAXIMO_ALERTA = 130000

# DAG instance and tasks with decorators
@dag(default_args=default_args, description='Extração de dados de Criptomoedas')
def coin_market():
        
    @task
    def extrair_api_coin():
        import requests

        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=100&sort=market_cap&cryptocurrency_type=coins&tag=all&convert=BRL'
        response = requests.get(url,headers={"X-CMC_PRO_API_KEY":"91255b5a-886e-4587-b6bb-bc2f65846100","Accept":"*/*"})
        return response.json()
    """import json
       return json.loads("{\"status\":{\"timestamp\":\"2023-05-20T02:38:11.376Z\",\"error_code\":0,\"error_message\":null,\"elapsed\":22,\"credit_count\":1,\"notice\":null,\"total_count\":957},\"data\":[{\"id\":1,\"name\":\"Bitcoin\",\"symbol\":\"BTC\",\"slug\":\"bitcoin\",\"num_market_pairs\":10220,\"date_added\":\"2010-07-13T00:00:00.000Z\",\"tags\":[\"mineable\",\"pow\",\"sha-256\",\"store-of-value\",\"state-channel\",\"coinbase-ventures-portfolio\",\"three-arrows-capital-portfolio\",\"polychain-capital-portfolio\",\"binance-labs-portfolio\",\"blockchain-capital-portfolio\",\"boostvc-portfolio\",\"cms-holdings-portfolio\",\"dcg-portfolio\",\"dragonfly-capital-portfolio\",\"electric-capital-portfolio\",\"fabric-ventures-portfolio\",\"framework-ventures-portfolio\",\"galaxy-digital-portfolio\",\"huobi-capital-portfolio\",\"alameda-research-portfolio\",\"a16z-portfolio\",\"1confirmation-portfolio\",\"winklevoss-capital-portfolio\",\"usv-portfolio\",\"placeholder-ventures-portfolio\",\"pantera-capital-portfolio\",\"multicoin-capital-portfolio\",\"paradigm-portfolio\",\"bitcoin-ecosystem\"],\"max_supply\":21000000,\"circulating_supply\":19378331,\"total_supply\":19378331,\"infinite_supply\":false,\"platform\":null,\"cmc_rank\":1,\"self_reported_circulating_supply\":null,\"self_reported_market_cap\":null,\"tvl_ratio\":null,\"last_updated\":\"2023-05-20T02:36:00.000Z\",\"quote\":{\"BRL\":{\"price\":134269.96349425355,\"volume_24h\":54172468479.67883,\"volume_change_24h\":-28.3612,\"percent_change_1h\":-0.07765701,\"percent_change_24h\":0.24310808,\"percent_change_7d\":0.19957131,\"percent_change_30d\":-6.94182535,\"percent_change_60d\":-3.72792762,\"percent_change_90d\":8.74891908,\"market_cap\":2601927795949.562,\"market_cap_dominance\":46.3006,\"fully_diluted_market_cap\":2819669233379.3496,\"tvl\":null,\"last_updated\":\"2023-05-20T02:37:31.000Z\"}}}]}")"""
       
    @task
    def trata_informacoes(registros):

        lista_moedas_geral = []

        for coin in registros["data"]:
            brl = coin["quote"]["BRL"]
            valor = brl["price"]
            moeda = {
                "codigo":coin["symbol"],  
                "nome" : coin["name"],
                "valor" : numpy.around(valor,5) ,
                "valor_24h" : numpy.around(brl["percent_change_24h"],5),
                "valor_7d" : numpy.around(brl["percent_change_7d"],5),
                "valor_30d" : numpy.around(brl["percent_change_30d"],5),
                "valor_60d" : numpy.around(brl["percent_change_60d"],5),
                "valor_90d" : numpy.around(brl["percent_change_90d"],5)
            }
            lista_moedas_geral.append(moeda)

        return lista_moedas_geral
   
    @task
    def salva_banco_dados_relacional(registros):
        conexao = conecta_banco()
        
        try:
            for reg in registros:
                codigo = reg["codigo"]
                fech = executa_sql(conexao,"select id from criptomoeda where codigo=%s",(codigo,)).fetchone()
                id = 0
                if fech != None:
                    id = fech[0] 

                if id == 0:
                    executa_sql(conexao,"insert into criptomoeda(nome,codigo) values(%s,%s)",(reg["nome"],codigo))
                    id = executa_sql(conexao,"select id from criptomoeda where codigo=%s",(codigo,)).fetchone()[0]
                
                existe = False
                fech = executa_sql(conexao,"select count(*) > 0 from valores where id_criptomoeda=%s and date(data_cadastro)=%s",(id, str(datetime.today().date()))).fetchone()
                if fech != None:
                    existe = fech[0] 

                if existe == False:
                    executa_sql(conexao,"insert into valores(id_criptomoeda,valor,valor_24h,valor_7d,valor_30d,valor_60d,valor_90d,data_cadastro) values(%s,%s,%s,%s,%s,%s,%s,current_timestamp)",(id,reg["valor"],reg["valor_24h"],reg["valor_7d"],reg["valor_30d"],reg["valor_60d"],reg["valor_90d"]))
            
            conexao.close()
            return True
        except psycopg2.Error as e:
            return False


    @task
    def busca_moedas_abaixo_valor (salvou):
        conexao = conecta_banco()
        query = "select c.nome,round(v.valor,2) as valor from criptomoeda c inner join valores v on v.id_criptomoeda = c.id "
        query+= "where date(data_cadastro)=%s and v.valor < %s"

        fetch = None
        campos = ( str(datetime.today().date()),VALOR_MAXIMO_ALERTA)
   
        if CODIGO_CRIPTO != None:
            query+= " and c.codigo = %s"
            campos = ( str(datetime.today().date()),VALOR_MAXIMO_ALERTA,CODIGO_CRIPTO)

        fetch = executa_sql(conexao,query,campos).fetchall()
        
        lista = []
        for f in  fetch:
            moeda = {
                "nome":f[0],
                "valor": str(f[1])
            }
            lista.append(moeda)
        
        return lista
    
    @task
    def disparar_email(lista):
        import smtplib

        corpo_hmtl = ""

        if len(lista) <= 0:
            return False
        else:
            corpo_hmtl = "<h1>Lista de moedas que est&atilde;o abaixo de R$ 130.000,00:</h1>"
            corpo_hmtl += "<table><tr><td><strong>Nome</strong></td><td><strong>Valor</strong></td></tr>"
            for moeda in lista:
                corpo_hmtl+= "<tr><td>"+moeda["nome"]+"</td><td> R$ "+moeda["valor"]+"</td></tr>"
            corpo_hmtl+="</table>"

        corpo = MIMEText(corpo_hmtl, "html")
        message = MIMEMultipart("alternative")
        message.attach(corpo)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login("profissional.fabianorodrigues@gmail.com", "dwvwbxiybidpqtlf")
        server.sendmail("profissional.fabianorodrigues@gmail.com","fabiano.rodrigues.felix@hotmail.com",message.as_string())
        server.quit()

        return True
    
    def conecta_banco():
        import sys

        LOGGER = logging.getLogger("conecta_banco.task")
       
        try:
            conn = psycopg2.connect(
                user="airflow",
                password="airflow",
                host=HOST_BANCO_DADOS,
                port=5432,
                database="airflow"

            )
        except psycopg2.Error as e:
            LOGGER.info(f"Error connecting to Postgres Platform: {e}")
            sys.exit(1)

        return conn
    
    def executa_sql(conexao,query,campos):
        cur = conexao.cursor()
        cur.execute(query,campos)
        conexao.commit()
        return cur
    
    registros =  extrair_api_coin()
    lista_tratada = trata_informacoes(registros)
    salvou = salva_banco_dados_relacional(lista_tratada)
    lista = busca_moedas_abaixo_valor(salvou)
    disparar_email(lista)

dag = coin_market()
