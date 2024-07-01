from mysql.connector import errorcode
from dotenv import load_dotenv
import mysql.connector
import json
import os

load_dotenv(override=True)

class MSql:
  def __init__(self):
    try:
      self.conexao = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('USER'), password=os.getenv('PASSWORD'))
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
      return None
    if database is None:
      return "Banco de Dados não informado!"

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"USE {database}")
      cursor.execute(sql)
      resultado = cursor.fetchall()
      cursor.close()
      return resultado
    except mysql.connector.Error as err:
      print(f"Erro ao executar o comando: {err}")
      return None
    finally:
      self.conexao.close()

  def commit(self, sql, database=None):
    if self.conexao is None:
      return None
    if database is None:
      return "Banco de Dados não informado!"

    try:
      cursor = self.conexao.cursor()
      if database:
        cursor.execute(f"USE {database}")
      cursor.execute(sql)
      self.conexao.commit()
      cursor.close()
      return "Ok"
    except mysql.connector.Error as err:
      print(f"Erro ao executar o comando: {err}")
      return None
    finally:
      self.conexao.close()
# --------------------------------------------------------

# db = MSql()
# # print(db.fetchall("SELECT * FROM RF_PLANOS", "integra"))
# print(db.fetchall("SELECT * FROM USUARIO", "tarefas_alerta"))

