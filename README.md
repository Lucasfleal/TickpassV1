# TickpassV1 🎟️

[![Licença](https://img.shields.io/badge/licença-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Status do Projeto](https://img.shields.io/badge/status-em%20desenvolvimento-yellowgreen.svg)](https://github.com/Lucasfleal/TickpassV1)

---

## 📜 Índice

* [Sobre o Projeto](#-sobre-o-projeto)
* [✨ Principais Funcionalidades](#-principais-funcionalidades)
* [🛠️ Tecnologias Utilizadas](#-tecnologias-utilizadas)
* [🚀 Começando](#-começando)
    * [Pré-requisitos](#pré-requisitos)
    * [Instalação](#instalação)
* [📝 Uso](#-uso)
* [🤝 Como Contribuir](#-como-contribuir)
* [📄 Licença](#-licença)
* [📬 Contato](#-contato)

---

## 📖 Sobre o Projeto

O **TickpassV1** nasceu da necessidade de uma ferramenta robusta e intuitiva para a criação e gestão de eventos. A plataforma permite que organizadores cadastrem seus eventos, definam tipos de ingressos (com preços e quantidades), e acompanhem as vendas em tempo real. Para os usuários, oferece um portal para descobrir eventos, comprar ingressos de forma segura e acessá-los facilmente através de um QR Code único.

O objetivo principal é simplificar todo o ciclo de vida de um evento, desde o planejamento até o controle de entrada no dia.

---

## ✨ Principais Funcionalidades

* **Para Organizadores:**
    * ✅ Cadastro e gerenciamento completo de eventos (data, local, descrição, etc.).
    * 🎫 Criação de diferentes lotes e tipos de ingressos.
    * 📊 Dashboard com visão geral das vendas e receita.
    * 📱 Sistema de validação de ingressos via QR Code.
* **Para Usuários:**
    * 🔐 Autenticação segura (cadastro e login).
    * 🎉 Busca e visualização de eventos disponíveis.
    * 🛒 Processo de compra de ingressos simplificado.
    * 🎟️ Acesso aos ingressos comprados na área do usuário.

---

## 🛠️ Tecnologias Utilizadas

Este projeto foi desenvolvido com as seguintes tecnologias:

* **Backend:**
    * [Python](https://www.python.org/)
    * [Django](https://www.djangoproject.com/)
    * [Django Rest Framework](https://www.django-rest-framework.org/)
* **Banco de Dados:**
    * [PostgreSQL](https://www.postgresql.org/)
* **DevOps/Infraestrutura:**
    * [Docker](https://www.docker.com/)

---

## 🚀 Começando

Para executar o projeto em seu ambiente local, siga os passos abaixo.

### Pré-requisitos

Antes de começar, certifique-se de que você tem as seguintes ferramentas instaladas:

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Instalação

1.  **Clone o repositório:**
    ```sh
    git clone [https://github.com/Lucasfleal/TickpassV1.git](https://github.com/Lucasfleal/TickpassV1.git)
    ```

2.  **Acesse o diretório do projeto:**
    ```sh
    cd TickpassV1
    ```

3.  **Configure as variáveis de ambiente:**
    * Crie uma cópia do arquivo de exemplo `.env.example` e renomeie para `.env`.
    ```sh
    cp .env.example .env
    ```
    * Abra o arquivo `.env` e preencha as variáveis com as suas credenciais (chaves de API, segredos do banco de dados, etc.).

4.  **Inicie os contêineres com Docker Compose:**
    * Este comando irá construir as imagens e iniciar os serviços do backend, frontend e banco de dados.
    ```sh
    docker-compose up --build
    ```

5.  **Acesse a aplicação:**
    * **Frontend:** Abra seu navegador e acesse `http://localhost:3000`
    * **Backend (API):** A API estará disponível em `http://localhost:8000/api/`

---

## 📝 Uso

Após a instalação, você pode criar uma conta de usuário pela interface web para começar a explorar os eventos. Para testar as funcionalidades de organizador, você pode criar um superusuário Django com o seguinte comando em um novo terminal:

```sh
docker-compose exec backend python manage.py createsuperuser
