"""Modelos da base de dados da aplicação Stand Auto.

Este ficheiro contém a classe que representa a tabela ``automoveis``.
A classe é criada com SQLAlchemy e cada objeto Automovel corresponde a
uma linha nessa tabela.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates


# Objeto que faz a ligação entre o Flask e o SQLAlchemy.
# A instância é inicializada no app.py através de db.init_app(app).
db = SQLAlchemy()


class Automovel(db.Model):
     """Representa um automóvel guardado na base de dados.

     ``db.Model`` fornece os métodos de consulta e persistência, como:
     ``Automovel.query.all()`` e ``db.session.commit()``.
     """

     # Nome explícito da tabela criada na base de dados SQLite.
     __tablename__ = "automoveis"

     # Chave primária: identifica cada registo de forma automática e única.
     id = db.Column(db.Integer, primary_key=True)

     # nullable=False significa que o campo é obrigatório na base de dados.
     marca = db.Column(db.String(80), nullable=False)
     modelo = db.Column(db.String(80), nullable=False)

     # O ano e a quilometragem são inteiros porque permitem cálculos e filtros.
     ano = db.Column(db.Integer, nullable=False)
     quilometragem = db.Column(db.Integer, nullable=False)

     # unique=True impede duas linhas com a mesma matrícula.
     # index=True torna pesquisas por matrícula mais eficientes.
     matricula = db.Column(db.String(20), nullable=False, unique=True, index=True)

     # O combustível e o estado são texto controlado pelos valores recebidos.
     combustivel = db.Column(db.String(30), nullable=False)
     estado = db.Column(db.String(20), nullable=False, default="disponível")

     # Numeric guarda valores monetários com duas casas decimais.
     # É preferível a Float para evitar imprecisões típicas de números decimais.
     preco = db.Column(db.Numeric(10, 2), nullable=False)

     # Text permite guardar uma descrição maior do que um String curto.
     descricao = db.Column(db.Text, nullable=False, default="")

     # Estas regras são aplicadas diretamente pela base de dados.
     # Assim, a aplicação continua protegida mesmo que outro código tente
     # inserir valores inválidos sem passar pelo formulário HTML.
     __table_args__ = (
          CheckConstraint("ano >= 1886", name="ck_automovel_ano_valido"),
          CheckConstraint("quilometragem >= 0", name="ck_automovel_quilometragem_valida"),
          CheckConstraint("preco >= 0", name="ck_automovel_preco_valido"),
          CheckConstraint("estado IN ('disponível', 'vendido')", name="ck_automovel_estado_valido",),
     )

     @validates("marca", "modelo", "matricula", "combustivel")
     def validar_texto_obrigatorio(self, nome, valor):
          """Remove espaços e rejeita campos de texto vazios.

          O decorador ``validates`` faz com que este método seja chamado
          sempre que um dos campos indicados recebe um valor.
          """
          valor = str(valor or "").strip()
          if not valor:
               raise ValueError(f"O campo {nome} é obrigatório.")
          return valor

     @validates("estado")
     def validar_estado(self, nome, valor):
          """Garante que o estado possui uma das duas opções permitidas."""
          valor = str(valor or "").strip().lower()
          if valor not in {"disponível", "vendido"}:
               raise ValueError("O estado deve ser 'disponível' ou 'vendido'.")
          return valor

     def __repr__(self):
          """Representação útil para depuração no terminal."""
          return f"<Automovel {self.marca} {self.modelo} ({self.matricula})>"
