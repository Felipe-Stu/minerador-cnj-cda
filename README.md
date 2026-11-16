# Minerador CNJ / CDA (TJSP)

Aplicação desktop que consulta processos no portal público e-SAJ do Tribunal de Justiça de São Paulo e consolida os dados em uma planilha Excel, incluindo as Certidões de Dívida Ativa (CDAs) de execuções fiscais.

Projeto pessoal de aprendizado, criado para suprir uma necessidade pontual de levantamento de dados e para praticar automação web com Python.

## O que faz

- Lê um arquivo CSV com números de processos no padrão CNJ do TJSP (`NNNNNNN-DD.AAAA.8.26.OOOO`).
- Consulta cada processo no e-SAJ com o Chrome em modo headless (Selenium).
- Extrai os campos escolhidos na tela: CDAs, classe, assunto, data de distribuição, partes, valor da ação, área, situação, foro, vara e se o processo é virtual.
- Gera `resultado_mineracao_<data>.xlsx` na pasta **Downloads**, com uma linha por CDA.

Testado com lotes de até 2 mil processos, que levaram de 4 a 6 horas.

## Tecnologias

Python, Flask, Selenium, pandas, openpyxl, Electron e HTML/CSS/JavaScript.

## Estrutura

```text
main.py                  Servidor Flask
app/core/mineradora.py   Consulta e extração no e-SAJ (Selenium)
app/core/process.py      Rotas: leitura do CSV e geração do Excel
app/templates/           Interface (dashboard)
app/static/              CSS e JavaScript da interface
electron/                Janela desktop que inicia e encerra o Flask
exemplo_processos.csv    Formato esperado do arquivo de entrada
```

## Como executar (Windows)

Requisitos: Python 3.10+, Node.js e Google Chrome.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd electron
npm install
```

Depois, execute `Iniciar.bat`. A janela abre em alguns segundos.

## Arquivo de entrada

CSV com uma coluna `numero_processo` (ou `processo_cnj`) e um processo por linha. Vírgula e ponto e vírgula são aceitos. Veja `exemplo_processos.csv`.

## Limitações conhecidas

- Cada processo leva de 7 a 11 segundos, porque um Chrome novo é aberto por consulta.
- Não há indicador de progresso: a tela mostra "Processando..." até o fim do lote.
- O resultado só é salvo ao final; uma interrupção no meio perde o lote.
- Funciona apenas para o TJSP e depende da estrutura atual das páginas do e-SAJ.

## Privacidade

As planilhas geradas contêm nomes das partes, que são dados pessoais. Por isso os arquivos `.csv` e `.xlsx` não são versionados (veja `.gitignore`). Use a ferramenta respeitando a LGPD e os termos de uso do portal.
