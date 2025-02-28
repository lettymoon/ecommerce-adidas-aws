<h1 align="center" style="font-weight: bold;"> Projeto AWS - Endpoints de Pedido e Transportadora </h1>

## Descrição Geral
O sistema possui dois endpoints principais: **Endpoint de Pedido** e **Endpoint de Transportadora**. O objetivo é garantir que o pedido seja processado desde a solicitação até a entrega. O fluxo inclui interação com APIs externas, armazenamento de dados em **DynamoDB** e **S3**, e uso de **SQS** para processamento assíncrono.

---

## ENDPOINT - Pedido

### Descrição
Este endpoint é responsável por receber uma solicitação de pedido via API (POST), processar as informações recebidas, interagir com a API de produtos para recuperar os detalhes dos itens, armazenar os dados no **DynamoDB** e gerar uma mensagem para uma fila **SQS**. Além disso, ele interage com a transportadora para garantir que o pedido seja processado para entrega.

### Método: `POST`
**URL:** `/pedido`

### Payload de Entrada:
O payload enviado para o endpoint contém as informações sobre os produtos e a URL da transportadora:

```json
{
  "produtos": [
    {
      "id_produto": "number",
      "quantidade": "number"
    },
    {
      "id_produto": "number",
      "quantidade": "number"
    }
  ],
  "url_transportadora": "string"
}
```

#### Campos:

- **produtos**: Lista de objetos, cada um representando um produto no pedido.
  - **id_produto**: Identificador único do produto.
  - **quantidade**: Quantidade solicitada para o produto.

- **url_transportadora**: URL da API da transportadora para onde os dados de transporte serão enviados.

### Fluxo de Processamento:

1. **Recuperação de Dados dos Produtos**:
   Após o recebimento do pedido, a aplicação realiza uma requisição `GET` à API de Produtos para recuperar o nome de cada produto. A URL da API de produtos segue o formato:

   ```
   http://url.com/{id_produto}
   ```

   Exemplo de retorno da API de Produto:

   ```json
   {
     "id_produto": "string",
     "nome_produto": "string"
   }
   ```

2. **Armazenamento no DynamoDB**:
   Os dados dos produtos e do pedido são armazenados no **DynamoDB** com a seguinte estrutura de colunas:

### Estrutura de Armazenamento no DynamoDB

| **Coluna**              | **Descrição**                                                                 |
|-------------------------|-------------------------------------------------------------------------------|
| **Id**                  | Identificador único para cada produto dentro de um pedido (string).          |
| **id_pedido**           | Identificador único do pedido (comum a todos os produtos de um mesmo pedido). |
| **data_pedido**         | Data e hora em que o pedido foi realizado.                                   |
| **id_produto**          | Identificador do produto.                                                   |
| **nome_loja**           | Nome da loja que registrou o pedido.                                         |
| **nome_produto**        | Nome do produto obtido da API de produtos.                                   |
| **quantidade**          | Quantidade solicitada para o produto.                                        |
| **url_transportadora**  | URL da transportadora associada ao pedido.                                   |

#### Exemplo de Registro no DynamoDB

| **Id**       | **id_pedido** | **data_pedido**         | **id_produto** | **nome_loja** | **nome_produto** | **quantidade** | **url_transportadora**  |
|--------------|---------------|-------------------------|----------------|---------------|------------------|----------------|-------------------------|
| `001`        | `pedido_123`  | `2025-02-28T15:30:00Z`  | `101`          | `Minha Loja`  | `Produto A`      | `2`            | `http://transp.com/api` |
| `002`        | `pedido_123`  | `2025-02-28T15:30:00Z`  | `102`          | `Minha Loja`  | `Produto B`      | `1`            | `http://transp.com/api` |

3. **Fila SQS**:
   Após o armazenamento no DynamoDB, uma mensagem é enviada para a fila SQS com os dados do pedido no seguinte formato:

   ```json
   {
     "produtos": [
       {
         "id_produto": "number",
         "quantidade": "number"
       },
       {
         "id_produto": "number",
         "quantidade": "number"
       }
     ],
     "url_transportadora": "string"
   }
   ```

   Essa mensagem será processada por uma Lambda para interagir com a transportadora.

4. **Requisição para a Transportadora**:
   A Lambda que processa a fila SQS envia uma requisição para a URL da transportadora especificada no payload, no seguinte formato:

   ```json
   {
     "produtos": [
       {
         "id_produto": "number",
         "quantidade": "number"
       },
       {
         "id_produto": "number",
         "quantidade": "number"
       }
     ],
     "nome_loja": "string"
   }
   ```

5. **Armazenamento no S3**:
   Após o envio da requisição à transportadora, os dados do pedido e informações de envio são salvos em um arquivo JSON no **Amazon S3**. O nome do arquivo será o **id_pedido**.

   Exemplo de JSON salvo no S3:

   ```json
   {
     "produtos": [
       {
         "id_produto": "number",
         "quantidade": "number"
       },
       {
         "id_produto": "number",
         "quantidade": "number"
       }
     ],
     "url_transportadora": "string",
     "nome_loja": "string"
   }
   ```

---

## ENDPOINT - Transportadora

### Descrição
O **Endpoint de Transportadora** processa as informações de transporte de um pedido. Após o recebimento do pedido, o sistema interage com a API de estoque para atualizar o estoque, realiza o transporte e armazena as informações no **DynamoDB** e no **S3**.

### Método: `POST`
**URL:** `/transportadora`

### Payload de Entrada:
O payload enviado para o endpoint contém as informações dos produtos e o nome da loja associada ao pedido de transporte:

```json
{
  "produtos": [
    {
      "id_produto": "number",
      "quantidade": "number"
    },
    {
      "id_produto": "number",
      "quantidade": "number"
    }
  ],
  "nome_loja": "string"
}
```

#### Campos:

- **produtos**: Lista de objetos representando os produtos que serão transportados.
  - **id_produto**: Identificador único do produto.
  - **quantidade**: Quantidade solicitada para o transporte do produto.

- **nome_loja**: Nome da loja associada ao pedido de transporte.

### Fluxo de Processamento:

1. **Armazenamento no DynamoDB**:
   Após a solicitação de transporte ser recebida, os dados do pedido são salvos no **DynamoDB** com a seguinte estrutura:

### Estrutura de Armazenamento no DynamoDB

| **Coluna**              | **Descrição**                                                                 |
|-------------------------|-------------------------------------------------------------------------------|
| **Id**                  | Identificador único para cada produto dentro de um pedido de transporte (string). |
| **id_transporte**       | Identificador único do transporte, comum a todos os produtos de um mesmo pedido de transporte (string). |
| **data_pedido**         | Data e hora em que o transporte foi solicitado (data).                       |
| **id_produto**          | Identificador do produto.                                                   |
| **nome_loja**           | Nome da loja associada ao pedido de transporte.                              |
| **quantidade**          | Quantidade solicitada para o transporte do produto.                         |

#### Exemplo de Registro no DynamoDB

| **Id**       | **id_transporte**  | **data_pedido**         | **id_produto** | **nome_loja** | **quantidade** |
|--------------|--------------------|-------------------------|----------------|---------------|----------------|
| `001`        | `transporte_123`   | `2025-02-28T15:40:00Z`  | `101`          | `Adidas`      | `2`            |
| `002`        | `transporte_123`   | `2025-02-28T15:40:00Z`  | `102`          | `Adidas`      | `1`            |

2. **Fila SQS**:
   Após o armazenamento no DynamoDB, uma mensagem é enviada para a fila **SQS** com os dados do transporte no seguinte formato:

   ```json
   {
     "produtos": [
       {
         "id_produto": "number",
         "quantidade": "number"
       },
       {
         "id_produto": "number",
         "quantidade": "number"
       }
     ],
     "nome_loja": "string"
   }
   ```

3. **Baixa no Estoque**:
   Antes de finalizar o transporte, a função Lambda que processa a fila SQS envia uma requisição `PATCH` para a API de estoque. A URL é:

   ```
   http://url.com/estoque/{id_produto}
   ```

   O formato da requisição será:

   ```json
   {
     "quantidade": "number"
   }
   ```

   Onde **quantidade** é a quantidade do produto que está sendo removida do estoque.

4. **Finalização do Transporte**:
   Após a baixa no estoque ser confirmada, o transporte é finalizado.

5. **Armazenamento no S3**:
   Após a finalização do transporte, os dados do transporte, incluindo os produtos e o nome da loja, são salvos em um arquivo JSON no **S3**. O nome do arquivo será o **id_transporte**.

   Exemplo de JSON salvo no S3:

   ```json
   {
     "id_transporte": "string",
     "produtos": [
       { "id_produto": "number", "quantidade": "number" },
       { "id_produto": "number", "quantidade": "number" }
     ],
     "nome_loja": "string"
   }
   ```

---

## Considerações Finais

- **Endpoint de Pedido**:
  - Recebe os dados do pedido, consulta a API de produtos, envia a requisição para a transportadora e armazena as informações no **DynamoDB** e no **S3**.
  
- **Endpoint de Transportadora**:
  - Processa a solicitação de transporte, interage com a API de estoque para dar baixa nas quantidades de produtos e salva os dados no **DynamoDB** e no **S3**.

- O sistema utiliza recursos como ***API Gateway**, **Lambda Function**, **DynamoDB**, **SQS** e **S3**, garantindo um fluxo eficiente de pedidos e transportes.
