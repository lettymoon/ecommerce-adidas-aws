import uuid
import boto3
import json
from datetime import datetime
import requests

def lambda_handler(event, context):
    s3_client = boto3.client('s3')

    for record in event['Records']:
        payload = record["body"]
        
        try:
            payload_json = json.loads(payload)
            produtos = payload_json["produtos"]
            url_transportadora = payload_json["url_transportadora"]
            id_pedido = payload_json["id_pedido"]
            nome_loja = "Adidas"
            
            if not produtos or not isinstance(produtos, list) or len(produtos) == 0:
                raise ValueError("A lista de produtos está inválida ou vazia.")
            if not url_transportadora:
                raise ValueError("A URL da transportadora não foi fornecida.")
            if not id_pedido:
                raise ValueError("O id_pedido não foi fornecido.")
        
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Erro ao processar o payload: {str(e)}")
            continue

        body_s3 = {
            "produtos": produtos,
            "url_transportadora": url_transportadora,
            "nome_loja": nome_loja
        }

        try:
            s3_response = s3_client.put_object(Body=str(json.dumps(body_s3)), Bucket="ecommerce-adidas", Key=f"pedidos/{str(id_pedido)}.json")
            if s3_response.get('ResponseMetadata', {}).get('HTTPStatusCode') != 200:
                raise Exception(f"Erro ao enviar dados para o S3. Status: {s3_response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
            print(f"Arquivo {id_pedido}.json armazenado no S3 com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar no S3: {str(e)}")
            continue

        body = {
            "produtos": produtos,
            "nome_loja": nome_loja
        }

        try:
            response = requests.post(url_transportadora, json=body)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()  
                    print("Recurso criado com sucesso!")
                except ValueError as e:
                    print(f"Erro ao tentar decodificar o JSON: {e}")
                    print(f"Resposta da API: {response.text}")  
            else:
                print(f"Erro: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar a requisição para a transportadora: {str(e)}")
