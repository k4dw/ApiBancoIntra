from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from dotenv import load_dotenv
from icecream import ic
from db import MSql, Ora
import pytz
import jwt
import os

ic.configureOutput(prefix='DEBUG: ', includeContext=True)
load_dotenv(override=True)

app = Flask(__name__)

# Função para obter a data e hora no fuso horário de Brasília
def brasil_current_time():
  brasil_tz = pytz.timezone('America/Sao_Paulo')
  return datetime.now(brasil_tz)

# Validação do Token para autozizar as requizições
def authorize(token, client_id, public_key_hex):
  if not token:
    return {'success': False, 'message': 'Token não fornecido'}
  if not client_id:
    return {'success': False, 'message': 'ClientId não fornecido'}
  if not public_key_hex:
    return {'success': False, 'message': 'ClientSecurity não fornecido'}
  
  token = token.split(" ")[1]
  
  public_key_bytes = bytes.fromhex(public_key_hex)
  
  try:
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
  except ValueError as e:
    return {'success': False, 'message': 'Erro ao carregar chave pública: ' + str(e)}
  
  try:
    payload = jwt.decode(token, public_key, algorithms=['EdDSA'])
  except jwt.ExpiredSignatureError:
    return {'success': False, 'message': 'Token expirado'}
  except jwt.InvalidTokenError as e:
    return {'success': False, 'message': 'Token inválido: ' + str(e)}
  
  if payload['user_id'] != client_id:
    return {'success': False, 'message': 'ClientId inválido'}
  
  # Calculando o tempo restante até a expiração do token
  expire_time = datetime.fromtimestamp(payload['exp'], pytz.utc)
  current_time = brasil_current_time()
  expire_in = round((expire_time - current_time).total_seconds())
  
  return {'success': True, 'message': 'Token válido', 'expire_in': expire_in}
# --------------------------------------------------------------------------------

# Status da API ---------
@app.route('/')
def status():
  return "<h1>API Online</h1>"

# Consultar dados no banco do Controle Inteno --------------------------------------------------------------
@app.route('/mysql/consulta/<data_base>', methods=['POST'])
def mysql_consulta(data_base):
  try:
    token = request.headers.get('Authorization')
    client_id = request.headers.get('ClientId')
    public_key_hex = request.headers.get('ClientSecurity')
    auth = authorize(token, client_id, public_key_hex)
    
    if auth.get("success"):
    # if True:
      db = MSql()
      sql =  request.json.get('query')
      if not sql:
        return jsonify({'success': False, 'message': 'Query SQL não fornecida.'}), 400
      dados = db.fetchall(sql, data_base)
      # ic(dados)
      return jsonify({'success': True, 'dados': dados})
    else:
      return jsonify(auth), 401
  except Exception as ex:
    return jsonify({'success': False, 'message': str(ex)}), 500

# Consultar dados no banco da Fácil ------------------------------------------------------------------------
@app.route('/oracle/consulta/<data_base>', methods=['POST'])
def oracle_consulta(data_base):
  try:
    token = request.headers.get('Authorization')
    client_id = request.headers.get('ClientId')
    public_key_hex = request.headers.get('ClientSecurity')
    auth = authorize(token, client_id, public_key_hex)
    
    if auth.get("success"):
      db = Ora()
      sql =  request.json.get('query')
      if not sql:
        return jsonify({'success': False, 'message': 'Query SQL não fornecida.'}), 400
      dados = db.fetchall(sql, data_base)
      # ic(dados)
      return jsonify({'success': True, 'dados': dados})
    else:
      return jsonify(auth), 401
  except Exception as ex:
    return jsonify({'success': False, 'message': str(ex)}), 500

# Inicia a aplicação ------------------------------
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)