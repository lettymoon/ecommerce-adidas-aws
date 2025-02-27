import json
import boto3
import os
import uuid
from datetime import datetime

# aws clients
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table('adidas_transporte')

# url lista sqs 
SQS_QUEUE_URL = os.environ.get("SQS_QUEUE_URL")

def lambda_handler(event, context):
    try:
        #step 1: obter dados
        body = json.loads(event["body"])
        produtos = body.get("produtos", [])
        nome_loja = body.get("nome_loja", "")

        if not produtos or not nome_loja:
            raise Exception ("Dados inválidos")

        # step 2: salvar no banco de dados dynamoDB
        id_transporte = str(uuid.uuid4())
        erros_dynamodb = []

        for produto in produtos:
            item = {
                "Id": str(uuid.uuid4()),
                "id_transporte": id_transporte,
                "id_produto": produto["id_produto"],
                "quantidade": produto["quantidade"],
                "nome_loja": nome_loja,
                "data_pedido": datetime.now().isoformat(),
            }
            try:
                table.put_item(Item=item)
            except Exception as e:
                erro_msg = f"Erro ao salvar produto {produto['id_produto']} no DynamoDB: {str(e)}"
                erros_dynamodb.append(erro_msg)


        print("Pedido salvo no DynamoDB com sucesso.")

        #step 3: enviar para a fila sqs
        sqs_message = [
            {
                "Id": str(uuid.uuid4()),
                "MessageBody": json.dumps(
                    {
                        "id_transporte": id_transporte,
                        "produtos": produtos,
                        "nome_loja": nome_loja
                    }
                ),
            }
        ]

        try:
            response = sqs.send_message_batch(QueueUrl=SQS_QUEUE_URL, Entries=sqs_message)
        except Exception as e:
             raise Exception(f"Erro ao enviar mensagem para SQS: {str(e)}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processo completo"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
