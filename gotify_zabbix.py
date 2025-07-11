import requests
import json
import time
from datetime import datetime

URL_ZABBIX = "http://SEU-AMBIENTE-ZABBIX.BR.NET/zabbix/api_jsonrpc.php"
USUARIO_ZABBIX = "Admin" #USUÁRIO COM ACESSO A API
SENHA_ZABBIX = "zabbix"

# CONFIGURAÇÕES DO GOTIFY
URL_GOTIFY = "http://SEU_AMBIENTE/message"
TOKEN_GOTIFY = "COLOQUE-SEU-TOKEN-AQUI"

# Dicionário para armazenar alertas já notificados
alertas_notificados = {}

# Mapeamento de Prioridade do Zabbix
MAPA_PRIORIDADE = {
    0: ("Informação", 1),  
    1: ("Aviso", 2),       
    2: ("Média", 3),       
    3: ("Alta", 4),        
    4: ("Desastre", 5),    
    5: ("Crítico", 5)      
}

def autenticar_zabbix():
    """ Autentica na API do Zabbix e retorna o token """
    dados = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": USUARIO_ZABBIX,
            "password": SENHA_ZABBIX
        },
        "id": 1
    }
    resposta = requests.post(URL_ZABBIX, json=dados)
    return resposta.json().get("result")

def obter_alertas(token_autenticacao):
    """ Obtém os alertas ativos do Zabbix com detalhes """
    dados = {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid", "description", "priority", "lastchange"],
            "filter": {"value": 1},  # Somente alertas ativos
            "sortfield": "lastchange",
            "sortorder": "DESC",
            "expandDescription": True,
            "selectHosts": ["host"]  # Obtém o nome do host afetado
        },
        "auth": token_autenticacao,
        "id": 2
    }
    resposta = requests.post(URL_ZABBIX, json=dados)
    return resposta.json().get("result", [])

def enviar_notificacao(alerta):
    """ Envia notificação para o Gotify com detalhes """
    id_alerta = alerta["triggerid"]
    descricao = alerta["description"]
    nivel_prioridade = int(alerta["priority"])
    timestamp_ultima_alteracao = int(alerta["lastchange"])

    # Converter timestamp para data legível
    ultima_alteracao = datetime.fromtimestamp(timestamp_ultima_alteracao).strftime('%d/%m/%Y %H:%M:%S')

    # Obter o host afetado
    hosts = alerta.get("hosts", [])
    if hosts:
        nome_host = hosts[0].get("host", "Desconhecido")
    else:
        nome_host = "Desconhecido"

    # Obter nome da prioridade e nível correto para o Gotify
    nome_prioridade, prioridade_gotify = MAPA_PRIORIDADE.get(nivel_prioridade, ("Desconhecido", 1))

    # Verifica se o alerta já foi notificado
    if id_alerta in alertas_notificados:
        return

    # Criar mensagem formatada com detalhes
    mensagem = f"🔴 **Alerta do Zabbix**\n\n"
    mensagem += f"🖥️ **Host**: {nome_host}\n"
    mensagem += f"⚠️ **Descrição**: {descricao}\n"
    mensagem += f"🔥 **Gravidade**: {nome_prioridade}\n"
    mensagem += f"🕒 **Última alteração**: {ultima_alteracao}\n"

    # Enviar notificação para o Gotify
    cabecalho = {
        "X-Gotify-Key": TOKEN_GOTIFY
    }
    dados_envio = {
        "message": mensagem,
        "title": f"Zabbix Alerta - {nome_prioridade}",
        "priority": prioridade_gotify
    }
    resposta = requests.post(URL_GOTIFY, headers=cabecalho, json=dados_envio)

    if resposta.status_code == 200:
        print(f"✅ Notificação enviada para {nome_host} - {descricao}")
        alertas_notificados[id_alerta] = True  # Marca como notificado
    else:
        print(f"❌ Erro ao enviar notificação: {resposta.status_code} - {resposta.text}")

def monitoramento():
    """ Loop para monitoramento contínuo """
    token_autenticacao = autenticar_zabbix()
    if not token_autenticacao:
        print("❌ Erro ao autenticar no Zabbix")
        return

    while True:
        alertas = obter_alertas(token_autenticacao)
        for alerta in alertas:
            enviar_notificacao(alerta)
        time.sleep(60)  # Verifica alertas a cada 60 segundos

if __name__ == "__main__":
    monitoramento()
