from mysql.connector import errorcode
from dotenv import load_dotenv
from icecream import ic
import mysql.connector
import oracledb
import os

load_dotenv(override=True)

class MSql:
  def __init__(self):
    try:
      self.conexao = mysql.connector.connect(host=os.getenv('INTRA_HOST'), user=os.getenv('INTRA_USER'), password=os.getenv('INTRA_PASSWORD'))
      print("Banco de dados conectado!")
    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_BAD_DB_ERROR:
        print("O Banco de Dados não existe!")
      elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Usuário e/ou Senha inválidos!")
      else:
        print(err)
      self.conexao = None

  def fetchall(self, sql, database=None):
    if self.conexao is None:
      return {'success': False, 'message': 'Conexão com o banco de dados não estabelecida!'}
    if database is None:
      return {'success': False, 'message': 'Banco de Dados não informado!'}

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"USE {database}")
      cursor.execute(sql)
      colunas = [desc[0] for desc in cursor.description]
      resultado = cursor.fetchall()
      cursor.close()
      
      if len(resultado) == 0:
        return {"success": False, "message": "Nenhum registro foi localizado!" }
      
      # Combine column names with rows
      dados = [dict(zip(colunas, linha)) for linha in resultado]
      return {'success': True, 'dados': dados}
    except mysql.connector.Error as err:
      print(f"Erro ao executar o comando: {err}")
      return {'success': False, 'message': f"Erro ao executar o comando: {err}"}
    finally:
      self.conexao.close()

  def commit(self, sql, database=None):
    if self.conexao is None:
      return {'success': False, 'message': 'Conexão com o banco de dados não estabelecida!'}
    if database is None:
      return {'success': False, 'message': 'Banco de Dados não informado!'}

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"USE {database}")
      cursor.execute(sql)
      self.conexao.commit()
      cursor.close()
      return {'success': True}
    except mysql.connector.Error as err:
      print(f"Erro ao executar o comando: {err}")
      return {'success': False, 'message': f"Erro ao executar o comando: {err}"}
    finally:
      self.conexao.close()
# --------------------------------------------------------
class Ora:
  def __init__(self):
    try:
      # oracledb.init_oracle_client()
      dsn_tns = oracledb.makedsn(os.getenv('FACIL_HOST'), os.getenv('FACIL_PORT'), service_name=os.getenv('FACIL_SERVICE'))
      self.conexao = oracledb.connect(user=os.getenv('FACIL_USER'), password=os.getenv('FACIL_PASSWORD'), dsn=dsn_tns)
      self.msg = "Banco de dados conectado!"
    except oracledb.DatabaseError as err:
      error, = err.args
      if error.code == 1017:
        print("Autenticação com Banco de Dados inválida!")
        self.msg = "Autenticação com Banco de Dados inválida!"
      elif error.code == 12545:
        print("O Banco de Dados não existe!")
        self.msg = "O Banco de Dados não existe!"
      else:
        print(f"Erro ao conectar ao Banco de Dados: {err}")
        self.msg = f"Erro ao conectar ao banco de dados: {err}"
      self.conexao = None
  # -------------------------------------
  def fetchall(self, sql, database=None):
    if self.conexao is None:
      return {'success': False, 'message': self.msg}
    if database is None:
      return {'success': False, 'message': 'Banco de Dados não informado!'}

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {database}")
      cursor.execute(sql)
      colunas = [desc[0] for desc in cursor.description]
      resultado = cursor.fetchall()
      cursor.close()
      
      # ic(len(resultado) == 0)
      if len(resultado) == 0:
        return {"success": False, "message": "Nenhum registro foi localizado!" }
        
      # Combine column names with rows
      dados = [dict(zip(colunas, linha)) for linha in resultado]
      return {'success': True, 'dados': dados}
    except oracledb.DatabaseError as err:
      error, = err.args
      print(f"Erro ao executar o comando: {error.message}")
      return {'success': False, 'message': f"Erro ao executar o comando: {error.message}"}
    finally:
      self.conexao.close()
  # -------------------------------------
  def commit(self, sql, database=None):
    if self.conexao is None:
      return {'success': False, 'message': 'Conexão com o banco de dados não estabelecida!'}
    if database is None:
      return {'success': False, 'message': 'Banco de Dados não informado!'}

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {database}")
      cursor.execute(sql)
      self.conexao.commit()
      cursor.close()
      return {'success': True}
    except oracledb.DatabaseError as err:
      error, = err.args
      print(f"Erro ao executar o comando: {error.message}")
      return {'success': False, 'message': f"Erro ao executar o comando: {error.message}"}
    finally:
      self.conexao.close()
# --------------------------------------------------------

# db = MSql()
# print(db.fetchall("SELECT * FROM RF_PLANOS", "integra"))
# print(db.fetchall("SELECT * FROM USUARIO", "tarefas_alerta"))

