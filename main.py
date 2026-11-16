import os
import secrets
import sys

# Sem terminal (iniciado pelo Electron), o Windows usa cp1252, que não aceita emojis.
# Força UTF-8 para que os prints com ✅/⚠️/❌ não interrompam a mineração.
for fluxo in (sys.stdout, sys.stderr):
    if hasattr(fluxo, 'reconfigure'):
        fluxo.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask
from app.core.process import bp as mineradora_bp

app = Flask(__name__,
            template_folder='app/templates',
            static_folder='app/static')
# A chave vem do ambiente; sem ela, uma chave aleatória é gerada a cada execução
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)

app.register_blueprint(mineradora_bp)

if __name__ == '__main__':
    # Permite que o Electron inicie o servidor com "python main.py"
    app.run(host='127.0.0.1', port=5000)
