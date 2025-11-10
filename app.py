# app.py (Servidor Python com Flask e Gemini API)

import os
from flask import Flask, request, jsonify
from google import genai
from flask_cors import CORS

# =========================================================================
# 1. CONFIGURAÇÃO DA API GEMINI
# =========================================================================

# Sua chave de API inserida diretamente para o teste (prática não recomendada para produção!)
CHAVE_DO_USUARIO = "AIzaSyB2WOKOuLvurpaVcfN2CfkYTkspfr6fkr4" 

client = None
chat_session = None

try:
    # Inicializa o cliente Gemini usando a chave fornecida
    client = genai.Client(api_key=CHAVE_DO_USUARIO)
    
    # Inicializa a sessão de chat, essencial para manter o histórico da conversa
    # entre as mensagens do frontend.
    chat_session = client.chats.create(model="gemini-2.5-flash")
    print("Cliente Gemini e sessão de chat inicializados com sucesso.")

except Exception as e:
    print("\n" + "="*50)
    print("ERRO DE INICIALIZAÇÃO DA API:")
    print("Não foi possível inicializar o cliente Gemini. Verifique se a chave é válida.")
    print(f"Detalhes: {e}")
    print("="*50 + "\n")


# =========================================================================
# 2. CONFIGURAÇÃO DO SERVIDOR FLASK
# =========================================================================

app = Flask(__name__)
# ESSENCIAL: Permite que o seu arquivo HTML (frontend) se comunique com este servidor.
CORS(app) 

# Rota de teste simples
@app.route('/')
def home():
    return "Servidor ECLYPSE AI-API rodando. Aguardando conexão do frontend."

# ROTA PRINCIPAL: Recebe a mensagem do JavaScript, chama o Gemini e retorna a resposta.
@app.route('/send_message', methods=['POST'])
def send_message():
    global chat_session
    
    if not client:
        return jsonify({"response": "Erro de configuração da API. O cliente Gemini não foi inicializado."}), 500

    # Pega o corpo da requisição (JSON enviado pelo JavaScript)
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({"response": "Por favor, digite uma mensagem válida."}), 400

    try:
        # Envia a mensagem para a sessão de chat do Gemini
        response = chat_session.send_message(user_message)
        
        # Retorna a resposta do Gemini para o JavaScript no formato JSON
        return jsonify({"response": response.text})
    
    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        return jsonify({"response": "Desculpe, ocorreu um erro ao processar sua mensagem."}), 500

# ROTA DE LIMPEZA: Cria uma nova sessão de chat, limpando o histórico.
@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    global chat_session
    
    if not client:
        return jsonify({"status": "Erro: Cliente Gemini não inicializado"}), 500

    try:
        # Cria uma nova sessão, que limpa o histórico anterior
        chat_session = client.chats.create(model="gemini-2.5-flash")
        print("Histórico de chat limpo (nova sessão iniciada).")
        return jsonify({"status": "Chat limpo"}), 200
    except Exception as e:
        print(f"Erro ao limpar o chat: {e}")
        return jsonify({"status": "Falha ao limpar o chat no servidor."}), 500


# =========================================================================
# 3. EXECUÇÃO DO SERVIDOR
# =========================================================================

if __name__ == '__main__':
    # Rodar o servidor na porta 5000 (a mesma que o JavaScript espera)
    app.run(debug=True, host='0.0.0.0', port=5000)