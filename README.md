# SaaS de Gestão de Lojas

Este é um projeto de uma plataforma SaaS (Software as a Service) desenvolvida em Python com o framework Flask. A plataforma permite que proprietários se cadastrem e criem suas próprias lojas online.

## Pré-requisitos

- Python 3.8 ou superior
- `pip` (gerenciador de pacotes do Python)

## Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento local.

1.  **Clone o repositório:**
    (Assumindo que você já tenha o código localmente)

2.  **Crie e ative um ambiente virtual:**
    - No macOS e Linux:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - No Windows:
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```

3.  **Instale as dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas necessárias a partir do arquivo `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

Após a instalação, você pode iniciar o servidor de desenvolvimento do Flask.

1.  **Execute o aplicativo:**
    ```bash
    flask run
    ```
    Ou, alternativamente:
    ```bash
    python run.py
    ```

2.  **Acesse a aplicação:**
    Abra seu navegador e acesse o seguinte endereço para começar:
    [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)

A aplicação estará rodando em modo de depuração, o que significa que o servidor será reiniciado automaticamente a cada alteração no código.
