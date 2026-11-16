import os
import pandas as pd
import json
from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from app.core.mineradora import consultar_dados_processo

bp = Blueprint('mineradora', __name__)

@bp.route('/mineradora')
def exibir_dashboard():
    return render_template('dashboard.html')

@bp.route('/minerar', methods=['POST'])
def minerar():
    try:
        arquivo = request.files['arquivo']
        tipos_json = request.form['tipos']
        tipos_solicitados = json.loads(tipos_json)

        if not arquivo.filename.endswith('.csv'):
            print(f"Erro: Arquivo {arquivo.filename} não é CSV")
            return jsonify({'sucesso': False, 'erro': 'Formato inválido'})

        try:
            # Tenta ler com vírgula primeiro, se encontrar apenas 1 coluna, tenta ponto e vírgula (comum no Brasil)
            df = pd.read_csv(arquivo)
            if len(df.columns) <= 1:
                arquivo.seek(0)
                df = pd.read_csv(arquivo, sep=';')
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return jsonify({'sucesso': False, 'erro': f'Erro ao ler CSV: {str(e)}'})

        # Normaliza nomes das colunas (remove espaços e coloca em minúsculo)
        colunas_reais = [str(c).strip().lower() for c in df.columns]
        df.columns = colunas_reais

        # Lista de nomes possíveis para a coluna de processos (em minúsculo)
        colunas_possiveis = ['processo_cnj', 'numero_processo']
        coluna_encontrada = next((c for c in colunas_possiveis if c in colunas_reais), None)

        if not coluna_encontrada:
            print(f"Erro: Coluna de processo não encontrada. Colunas lidas: {colunas_reais}")
            return jsonify({'sucesso': False, 'erro': f"Coluna 'processo_cnj' ou 'numero_processo' ausente. Encontradas: {colunas_reais}"})

        resultado = []
        for _, row in df.iterrows():
            processo = str(row[coluna_encontrada]).strip()
            dados = consultar_dados_processo(processo, tipos_solicitados)

            if "cdas" in tipos_solicitados and "CDAs" in dados and dados["CDAs"]:
                for cda in dados["CDAs"]:
                    linha = {**dados, **cda}
                    linha.pop("CDAs", None)
                    resultado.append(linha)
            else:
                dados.pop("CDAs", None)
                resultado.append(dados)

        downloads_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        nome_arquivo = f"resultado_mineracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        caminho_completo = os.path.join(downloads_path, nome_arquivo)

        df_resultado = pd.DataFrame(resultado)
        df_resultado.to_excel(caminho_completo, index=False)

        return jsonify({'sucesso': True, 'arquivo': caminho_completo})

    except Exception as e:
        print("Erro na mineração:", e)
        return jsonify({'sucesso': False, 'erro': str(e)})
