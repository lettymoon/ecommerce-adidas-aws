<h1 align="center" style="font-weight: bold;"> Adidas SAM - AWS Project </h1>
# AWS Serverless E-Commerce System

[PYTHON_BADGE]:https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54 
[AWS_BADGE]:https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white
[LICENSE_BADGE]: https://img.shields.io/github/license/Ileriayo/markdown-badges?style=for-the-badge

![python][PYTHON_BADGE]
![aws][AWS_BADGE]
![license][LICENSE_BADGE]

## Visão Geral

Este projeto implementa um sistema de e-commerce baseado em uma arquitetura serverless utilizando serviços da AWS. Ele gerencia produtos, pedidos e envios.

## Arquitetura

O sistema é dividido em três principais funcionalidades:

- Gerenciamento de Produtos (CRUD de produtos armazenados em um banco relacional).

- Processamento de Pedidos (Armazena e processa pedidos utilizando DynamoDB e filas SQS).

- Gestão de Envios (Registra informações de envio e finaliza as entregas).

# Fluxo do Sistema

1. Produto

O API Gateway recebe requisições HTTP para gerenciamento de produtos.

As requisições são tratadas por um serviço ECS rodando Spring Boot.

O serviço se comunica com um banco RDS MySQL para armazenar os produtos.

2. Pedido

Um API Gateway recebe solicitações de criação de pedidos.

Um AWS Lambda (Python) processa os pedidos e os armazena no DynamoDB.

O pedido é enviado para uma fila SQS Orders.

Outro AWS Lambda consome a fila e envia os dados do pedido para o S3.

3. Envio

Um API Gateway recebe requisições para criar e finalizar envios.

Um AWS Lambda (Python) registra o envio no DynamoDB Shipping.

O envio é colocado na fila SQS Shipping.

Outro AWS Lambda finaliza o envio e registra os dados no S3.

## Tecnologias Utilizadas

API Gateway - Interface HTTP para interagir com o sistema.

AWS Lambda (Python) - Processamento serverless de pedidos e envios.

Amazon DynamoDB - Armazena pedidos e informações de envio.

Amazon SQS - Gerencia filas de pedidos e envios.

Amazon S3 - Armazena dados de pedidos e envios.

Amazon RDS (MySQL) - Banco relacional para produtos.

Amazon ECS (Spring Boot) - Microserviço para CRUD de produtos.


Criado por Letícia ❤️ | 🔗 [@lettymoon](https://github.com/lettymoon) | 📧 [leticiahcandido@gmail.com](mailto:leticiahcandido@gmail.com) 
