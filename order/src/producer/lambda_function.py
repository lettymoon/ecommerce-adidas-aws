import json
import boto3
import uuid
from datetime import datetime
import os
import requests

URL_QUEUE = os.environ.get("URL_QUEUE")

def lambda_handler(event, context):
    URL_INFRAESTRUTURA = "https://z97txngoub.execute-api.us-east-1.amazonaws.com/v1"
    client_sqs = boto3.client('sqs')

    dynamodb = boto3.resource('dynamodb')
    tabela = dynamodb.Table('adidas_pedido')

    try:
        body = json.loads(event["body"])
        produtos = body.get("produtos")
        url_transportadora = body.get("url_transportadora")
        
        if not produtos or not isinstance(produtos, list) or len(produtos) == 0:
            raise ValueError("A lista de produtos está inválida ou vazia.")
        
        if not url_transportadora:
            raise ValueError("A URL da transportadora não foi fornecida.")
        
        id_pedido = str(uuid.uuid4())
    except (json.JSONDecodeError, ValueError) as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": str(e)})
        }

    for produto in produtos:
        try:
            response_get = requests.get(URL_INFRAESTRUTURA + "/" + str(produto['id_produto']))
            if response_get.status_code != 200:
                raise Exception(f"Erro ao buscar dados do produto {produto['id_produto']}: {response_get.status_code}")
            
            data = response_get.json()
            if "nome_produto" not in data:
                raise ValueError(f"Dados do produto {produto['id_produto']} estão incompletos.")

            response = tabela.put_item(
                Item={
                    "Id": str(uuid.uuid4()),
                    "id_pedido": id_pedido,
                    "id_produto": produto['id_produto'],
                    "quantidade": produto['quantidade'],
                    "url_transportadora": url_transportadora,
                    "nome_produto": data['nome_produto'],
                    "nome_loja": "Adidas",
                    "data_pedido": str(datetime.now())
                }
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
                raise Exception(f"Erro ao inserir pedido na tabela DynamoDB para o produto {produto['id_produto']}")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar dados do produto {produto['id_produto']}: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": f"Erro ao buscar dados do produto {produto['id_produto']}: {str(e)}"})
            }
        except (ValueError, Exception) as e:
            print(f"Erro ao processar produto {produto['id_produto']}: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": f"Erro ao processar produto {produto['id_produto']}: {str(e)}"})
            }

    try:
        messages = [
            {
                "Id": id_pedido,
                "MessageBody": json.dumps({
                    "id_pedido": id_pedido,
                    "produtos": produtos,
                    "url_transportadora": url_transportadora
                })
            }
        ]

        msg = client_sqs.send_message_batch(
            QueueUrl=URL_QUEUE,
            Entries=messages
        )

        if msg.get('Failed', []):
            raise Exception(f"Erro ao enviar mensagens para o SQS: {msg['Failed']}")

    except (boto3.exceptions.Boto3Error, Exception) as e:
        print(f"Erro ao enviar mensagem para o SQS: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Erro ao enviar mensagem para o SQS: {str(e)}"})
        }

    return {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "produtos": produtos,
            "url_transportadora": url_transportadora
        })
    }