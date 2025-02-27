import json
import boto3
import os
import requests
from datetime import datetime
import uuid

# aws clients
s3 = boto3.client("s3")
sqs = boto3.client("sqs")

# url da fila sqs, bucket s3 e url API Produto
UPDATE_PRODUCT_URL = os.environ.get("UPDATE_PRODUCT_URL") 
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")

def lambda_handler(event, context):
    try:
        #step 1: obter a lista de produtos e noma da loja da fila sqs
        for record in event["Records"]:
            body = json.loads(record["body"])
            id_transporte = body.get("id_transporte", "")
            produtos = body.get("produtos", [])
            nome_loja = body.get("nome_loja", "")

            if not nome_loja or not produtos or not id_transporte:
                raise Exception ("Dados inválidos")

        #step 2: salvar no bucket s3
        s3_data = {
            "id_transporte": id_transporte,
            "produtos": produtos,
            "nome_loja": nome_loja
        }

        try:
            s3.put_object(
                Bucket="ecommerce-adidas",
                Key=f"transporte/{str(uuid.uuid4())}.json",
                Body=str(json.dumps(s3_data))
            )
        except Exception as e:
            raise Exception(f"Erro ao salvar dado no bucket: {str(e)}")

        #print(f"Dado salvo no bucket: {s3_file_name}")
            
            
        #step 3: update (patch) da quantidade de produtos na API PRODUTO
        for produto in produtos:
            id_produto = produto["id_produto"]
            quantidade = produto["quantidade"]

            patch_url = f"{UPDATE_PRODUCT_URL}/estoque/{id_produto}"
            patch_payload = {"quantidade": quantidade}

            response_patch = requests.patch(patch_url, json=str(json.dumps(patch_payload)))

            #to-do: refletir sobre erros que podem ocorrer na requisição patch
            if response_patch.status_code != 200:
                raise Exception ("Falha ao atualizar")
            

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processo completo"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


