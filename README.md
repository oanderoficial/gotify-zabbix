# Gotify-Zabbix

<p> Monitorando alertas ativos do Zabbix e enviando notificações para o Gotify.</p>

<img width="1466" height="1404" alt="image" src="https://github.com/user-attachments/assets/27b96581-420b-4b30-b96a-cebaa3b9c4c4" />
<br>


## 📑 Como funciona: 

## Autenticação no Zabbix

* Faz login na API do Zabbix para obter um token de autenticação.

## Coleta de alertas ativos

* Obtém a lista de alertas ativos (triggers) do Zabbix com informações como:
* Nome do host afetado
* Descrição do problema
* Prioridade do alerta
* Horário da última alteração

## Envio de notificações para o Gotify

* Para cada alerta, o script verifica se já foi notificado (para evitar mensagens repetidas).
* Se for um novo alerta, formata a mensagem e envia uma notificação via API do Gotify.
* A prioridade do alerta do Zabbix é mapeada para os níveis do Gotify.

![image](https://github.com/user-attachments/assets/6bc02383-2530-4b47-84cb-9bbb06f4e103)


## Loop contínuo de monitoramento

* O script fica rodando em loop, verificando novos alertas a cada 60 segundos.
* Se um novo alerta for encontrado, ele é notificado no Gotify.

## 📑 Como implantar: 

### 1) Configuração do Gotify

   Primeiro passo, será necessário configurar um ambiente Gotify, recomendo criar um container com Docker ou Proxmox-LXC. <br>
   Se você optar por usar o Gotify no Proxmox, existe um script na comunidade que automatiza a criação do ambiente. <br>
   <strong> Para criar um novo Proxmox VE Gotify LXC </strong> , execute o comando abaixo no Proxmox VE Shell:
   
   ```bash
   bash -c "$(wget -qLO - https://github.com/community-scripts/ProxmoxVE/raw/main/ct/gotify.sh)"
   ```
   ### Docker: 
   Se preferir usar o Docker, existem algumas imagens no DockerHub do Gotify, recomendo você utilizar a oficial: <br>
   <strong> Imagem oficial: </strong> https://hub.docker.com/r/gotify/server <br>
   ```bash
   docker pull gotify/server
   ```

### 2) Configuração Zabbix (Usuário com acesso a API)
   No script nos próximos passos vamos precisar apontar um usuário com acesso a API do Zabbix, será necessário que você tenha um configurado. 

   ![image](https://github.com/user-attachments/assets/882774d2-845c-47f2-b031-d2a9e819501c)

### 3) Configurações no script 
   As configurações no script são simples, primeiro vamos setar as credencias  de acesso do ambiente Zabbix: <br>
   ```python
   # CONFIGURAÇÕES DO ZABBIX API
   URL_ZABBIX = "http://SEU-AMBIENTE-ZABBIX.BR.NET/zabbix/api_jsonrpc.php"
   USUARIO_ZABBIX = "Admin" #USUÁRIO COM ACESSO A API
   SENHA_ZABBIX = "zabbix"
   ```
   Agora vamos setar as credencias de acesso ao ambiente Gotify: <br> 
   ```python
   # CONFIGURAÇÕES DO GOTIFY
   URL_GOTIFY = "http://SEU_AMBIENTE/message"
   TOKEN_GOTIFY = "COLOQUE-SEU-TOKEN-AQUI"
   ```

   O token você pega na aba APPS 

   ![image](https://github.com/user-attachments/assets/e7ea66a1-63ac-4bda-a54d-f06af17d0ce6)


   <strong>*** Se você ainda não tiver criado o application, crie um. </strong>

   ⚠️ <strong> Caso você esteja utilizando a versão do Zabbix 5.0.44 pra baixo será necessário mudar na função 'autenticar_zabbix' o parâmetro "username" para "user" </strong>

   ```python
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
   ```
   ### versão 5 do Zabbix (ou anteriores)

   ```python
   def autenticar_zabbix():
    """ Autentica na API do Zabbix e retorna o token """
    dados = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "user": USUARIO_ZABBIX,
            "password": SENHA_ZABBIX
        },
        "id": 1
    }
    resposta = requests.post(URL_ZABBIX, json=dados)
    return resposta.json().get("result")
   ````
