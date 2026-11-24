# ATEC_PIPL_10794_Gabriel_Mendes_Rodrigo_Pereira

Aplicação web desenvolvida em Flask para gerir o inventário de um stand automóvel. Os registos são guardados numa base de dados SQLite através do Flask-SQLAlchemy.

## Funcionalidades

- Registo de automóveis com validação de marca, modelo, ano, matrícula, quilometragem, combustível, estado, preço e descrição.
- Listagem dos automóveis existentes, ordenada pelos registos mais recentes.
- Pesquisa por marca, modelo ou matrícula, sem distinção entre maiúsculas e minúsculas, usando consultas SQLAlchemy com `ilike`.
- Mensagem informativa quando uma pesquisa não encontra resultados.
- Página de detalhes de cada automóvel.
- Edição de um automóvel através de um formulário já preenchido com os valores atuais.
- Eliminação de automóveis com confirmação no navegador e validação adicional no servidor.
- Layout comum através de `templates/base.html`.
- Estilos responsivos centralizados em `static/style.css`.

## Requisitos

- Python 3.10 ou superior.
- `pip` para instalar as dependências.

## Instalação

1. Abra um terminal na pasta do projeto:

   ```bash
   cd ATEC_PIPL_10794_Gabriel_Mendes_Rodrigo_Pereira-main
   ```

2. Crie um ambiente virtual (recomendado):

   ```bash
   python -m venv .venv
   ```

3. Ative o ambiente virtual:

   **Windows PowerShell**

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   **Linux/macOS**

   ```bash
   source .venv/bin/activate
   ```

4. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Execução

Execute a aplicação com:

```bash
python app.py
```

Depois, abra no navegador:

```text
http://127.0.0.1:5000
```

Na primeira execução é criado automaticamente o ficheiro `automoveis.db` na pasta do projeto. Esse ficheiro contém os dados do inventário e não precisa de ser criado manualmente.

## Utilização

- **Inventário:** mostra todos os automóveis e disponibiliza a pesquisa.
- **Pesquisar:** escreva parte da marca, do modelo ou da matrícula e selecione **Pesquisar**.
- **Ver:** abre a página com os detalhes completos do veículo.
- **Editar automóvel:** abre o formulário com os dados atuais já preenchidos.
- **Eliminar automóvel:** apresenta uma caixa de confirmação antes de remover o registo.
- **Novo automóvel:** abre o formulário de criação de um novo registo.

## Estrutura principal

```text
.
├── app.py                 # Configuração Flask, rotas, validação e operações CRUD
├── models.py              # Modelo Automovel e regras SQLAlchemy
├── requirements.txt       # Dependências Python
├── automoveis.db          # Criada automaticamente ao executar (não incluída no Git)
├── static/
│   └── style.css          # Estilos visuais e responsivos
└── templates/
    ├── base.html          # Estrutura e navegação comuns
    ├── criar.html         # Formulário de criação
    ├── editar.html        # Formulário de edição
    ├── listar.html        # Listagem e pesquisa
    ├── detalhes.html      # Detalhes, edição e eliminação
    └── 404.html           # Página de recurso inexistente
```

## Rotas principais

| Método | Rota | Objetivo |
|---|---|---|
| GET | `/` | Listar e pesquisar automóveis |
| GET/POST | `/automovel/novo` | Criar um automóvel |
| GET | `/automovel/<id>` | Consultar os detalhes |
| GET/POST | `/automovel/<id>/editar` | Editar um automóvel |
| POST | `/automovel/<id>/eliminar` | Eliminar um automóvel após confirmação |

## Notas de desenvolvimento

A `SECRET_KEY` existente é adequada apenas para desenvolvimento; num ambiente de produção deve ser substituída por uma variável de ambiente segura.
