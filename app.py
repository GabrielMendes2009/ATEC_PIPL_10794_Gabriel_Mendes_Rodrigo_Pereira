# Decimal é usado para validar preços sem os problemas de precisão de float.
from decimal import Decimal, InvalidOperation

# Path permite construir caminhos compatíveis com Linux, macOS e Windows.
from pathlib import Path

# Objetos principais do Flask:
# - Flask cria a aplicação;
# - flash mostra mensagens temporárias ao utilizador;
# - redirect e url_for fazem redirecionamentos seguros;
# - render_template processa ficheiros HTML Jinja2;
# - request lê dados enviados pelo navegador.
from flask import Flask, flash, redirect, render_template, request, url_for

# or_ permite combinar vários filtros SQLAlchemy numa única pesquisa.
from sqlalchemy import or_

# IntegrityError aparece por exemplo, quando se tenta repetir uma matrícula.
from sqlalchemy.exc import IntegrityError

# Importamos o modelo Automovel e o objeto db criado em models.py.
from models import Automovel, db


# Diretório onde este app.py está localizado.
# A base de dados fica junto do código e mantém os dados entre execuções.
BASE_DIR = Path(__file__).resolve().parent

# Criação da aplicação Flask.
app = Flask(__name__)

# A SECRET_KEY é necessária para o Flask armazenar mensagens flash na sessão.
# Em produção, deve ser substituída por uma variável de ambiente secreta.
app.config["SECRET_KEY"] = "chave-desenvolvimento-trocar-em-producao"

# SQLite é uma base de dados relacional armazenada num único ficheiro.
# A notação sqlite:/// aponta para um caminho relativo/absoluto de ficheiro.
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'automoveis.db'}"

# Desativamos notificações extra de alterações para evitar overhead desnecessário.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa o SQLAlchemy usando a configuração da aplicação Flask.
db.init_app(app)

# Cria as tabelas caso ainda não existam.
# O contexto da aplicação é necessário para o Flask-SQLAlchemy saber qual app usar.
with app.app_context():
    db.create_all()


def converter_dados_formulario(formulario):
    """Lê, normaliza e valida os campos enviados pelo formulário.

    O navegador envia todos os valores como texto. Por isso, esta função
    converte ano e quilometragem para int e preço para Decimal antes de
    criar o objeto Automovel.

    Retorna um par ``(dados, erros)``. Os dados são reaproveitados no HTML
    quando existe um erro, para o utilizador não perder o que escreveu.
    """
    erros = []

    # strip remove espaços acidentais no início/fim.
    # A matrícula é convertida para maiúsculas para normalizar o valor.
    dados = {
        "marca": formulario.get("marca", "").strip(),
        "modelo": formulario.get("modelo", "").strip(),
        "matricula": formulario.get("matricula", "").strip().upper(),
        "combustivel": formulario.get("combustivel", "").strip(),
        "estado": formulario.get("estado", "").strip().lower(),
        "descricao": formulario.get("descricao", "").strip(),
    }

    # Campos de texto obrigatórios.
    for campo, nome in (
        ("marca", "Marca"),
        ("modelo", "Modelo"),
        ("matricula", "Matrícula"),
        ("combustivel", "Combustível"),
    ):
        
        if not dados[campo]:
            erros.append(f"{nome} é obrigatório.")

    # Se o utilizador não enviar estado, usamos o valor padrão.
    # Se enviar outro valor, rejeitamos antes de tocar na base de dados.
    if not dados["estado"]:
        dados["estado"] = "disponível"

    elif dados["estado"] not in {"disponível", "vendido"}:
        erros.append("O estado deve ser 'disponível' ou 'vendido'.")

    # Conversão e validação do ano.
    try:
        dados["ano"] = int(formulario.get("ano", ""))
        if dados["ano"] < 1886:
            erros.append("O ano deve ser igual ou superior a 1886.")
        elif dados["ano"] > 2026:
            erros.append("O ano não pode ser maior que o ano atual")

    except (TypeError, ValueError):
        # Mantemos o texto original para voltar a mostrá-lo no formulário.
        dados["ano"] = formulario.get("ano", "")
        erros.append("O ano deve ser um número inteiro válido.")

    # Conversão e validação da quilometragem.
    try:
        dados["quilometragem"] = int(formulario.get("quilometragem", ""))
        if dados["quilometragem"] < 0:
            erros.append("A quilometragem não pode ser negativa.")

    except (TypeError, ValueError):
        dados["quilometragem"] = formulario.get("quilometragem", "")
        erros.append("A quilometragem deve ser um número inteiro válido.")

    # Decimal aceita ponto ou vírgula como separador decimal.
    try:
        texto_preco = formulario.get("preco", "").replace(",", ".")
        dados["preco"] = Decimal(texto_preco)
        if dados["preco"] < 0:
            erros.append("O preço não pode ser negativo.")

    except (AttributeError, InvalidOperation):
        dados["preco"] = formulario.get("preco", "")
        erros.append("O preço deve ser um número válido.")

    return dados, erros


@app.route("/")
def listar_automoveis():
    """Rota GET principal: lista todos os automóveis ou filtra a pesquisa."""
    # Lemos o texto da caixa de pesquisa e removemos espaços desnecessários.
    pesquisa = request.args.get("q", "").strip()

    # Começamos pela consulta à tabela e só adicionamos filtros quando o
    # utilizador escreveu uma pesquisa.
    consulta = Automovel.query
    if pesquisa:
        # ilike faz uma comparação SQL sem distinguir maiúsculas de
        # minúsculas e os sinais % permitem encontrar o texto no meio do
        # campo. A pesquisa abrange marca, modelo e matrícula.
        termo = f"%{pesquisa}%"
        consulta = consulta.filter(
            or_(
                Automovel.marca.ilike(termo),
                Automovel.modelo.ilike(termo),
                Automovel.matricula.ilike(termo),
            )
        )

    # Mantemos os automóveis mais recentes no topo da listagem.
    automoveis = consulta.order_by(Automovel.id.desc()).all()
    return render_template(
        "listar.html",
        automoveis=automoveis,
        pesquisa=pesquisa,
        pesquisa_realizada=bool(pesquisa),
    )


@app.route("/automovel/novo", methods=["GET", "POST"])
def criar_automovel():
    """Mostra o formulário (GET) ou cria um automóvel (POST)."""
    if request.method == "POST":
        # request.form contém os campos enviados pelo formulário HTML.
        dados, erros = converter_dados_formulario(request.form)

        # Pode haver vários erros no mesmo envio; mostramos todos.
        if erros:
            for erro in erros:
                flash(erro, "erro")
            return render_template("criar.html", dados=dados), 400

        # Criamos um objeto Python que será convertido numa linha SQL.
        automovel = Automovel(**dados)
        db.session.add(automovel)

        try:
            # commit grava definitivamente a transação na base de dados.
            db.session.commit()

        except IntegrityError:
            # rollback desfaz a transação incompleta e liberta a sessão.
            db.session.rollback()
            flash("Já existe um automóvel com essa matrícula.", "erro")
            return render_template("criar.html", dados=dados), 400
        
        except ValueError as erro:
            # Captura validações declaradas no modelo SQLAlchemy.
            db.session.rollback()
            flash(str(erro), "erro")
            return render_template("criar.html", dados=dados), 400

        # Depois de guardar, redirecionamos para evitar reenvio do formulário
        # quando o utilizador atualiza a página no navegador.
        flash("Automóvel registado com sucesso.", "sucesso")
        return redirect(url_for("listar_automoveis"))

    # GET: primeira abertura do formulário.
    return render_template("criar.html", dados={"estado": "disponível"})


@app.route("/automovel/<int:automovel_id>")
def detalhes_automovel(automovel_id):
    """Rota GET que mostra um automóvel pelo identificador inteiro."""
    # get_or_404 consulta a base de dados e responde 404 se não encontrar.
    automovel = db.get_or_404(Automovel, automovel_id)
    return render_template("detalhes.html", automovel=automovel)

@app.route("/automovel/<int:automovel_id>/editar", methods=["GET", "POST"])
def editar_automovel(automovel_id):
    """Mostra e atualiza o formulário de um automóvel existente."""
    # get_or_404 impede a edição de um identificador que não existe.
    automovel = db.get_or_404(Automovel, automovel_id)

    if request.method == "POST":
        # Reutilizamos a mesma validação usada no registo de automóveis.
        dados, erros = converter_dados_formulario(request.form)

        if erros:
            # Os dados enviados voltam ao formulário para o utilizador
            # corrigir apenas os campos inválidos.
            for erro in erros:
                flash(erro, "erro")
            return render_template(
                "editar.html", automovel=automovel, dados=dados
            ), 400

        # Atualizamos todos os campos editáveis com os novos valores.
        for campo, valor in dados.items():
            setattr(automovel, campo, valor)

        try:
            # O commit grava as alterações na linha já existente.
            db.session.commit()
        except IntegrityError:
            # A matrícula continua única mesmo quando o registo é editado.
            db.session.rollback()
            flash("Já existe um automóvel com essa matrícula.", "erro")
            return render_template(
                "editar.html", automovel=automovel, dados=dados
            ), 400
        except ValueError as erro:
            # Capturamos também as validações declaradas no modelo.
            db.session.rollback()
            flash(str(erro), "erro")
            return render_template(
                "editar.html", automovel=automovel, dados=dados
            ), 400

        flash("Automóvel atualizado com sucesso.", "sucesso")
        return redirect(url_for("detalhes_automovel", automovel_id=automovel.id))

    # No primeiro acesso, os valores atuais são enviados para preencher os
    # campos automaticamente, sem obrigar a redigitar os dados.
    return render_template("editar.html", automovel=automovel, dados=automovel)


@app.route("/automovel/<int:automovel_id>/eliminar", methods=["POST"])
def remover_automovel(automovel_id):
    """Elimina um automóvel depois da confirmação feita no formulário."""
    # O endpoint aceita apenas POST para evitar eliminações acidentais através
    # de uma simples visita a um link GET.
    automovel = db.get_or_404(Automovel, automovel_id)

    # A caixa de confirmação JavaScript é a primeira barreira no navegador;
    # esta verificação no servidor garante que o formulário confirmou a ação.
    if request.form.get("confirmacao") != "eliminar":
        flash("A eliminação foi cancelada.", "erro")
        return redirect(url_for("detalhes_automovel", automovel_id=automovel.id))

    # Apagamos o objeto e confirmamos a transação na base de dados.
    db.session.delete(automovel)
    db.session.commit()
    flash("Automóvel eliminado com sucesso.", "sucesso")
    return redirect(url_for("listar_automoveis"))

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    """Página amigável para endereços ou automóveis inexistentes."""
    return render_template("404.html"), 404


# Este bloco só é executado quando corremos ``python app.py`` diretamente.
# Não é executado quando os testes importam ``app``.
if __name__ == "__main__":
    # debug=True recarrega o servidor durante o desenvolvimento e mostra
    # erros detalhados. Deve ser desativado num ambiente de produção.
    app.run(debug=True)
