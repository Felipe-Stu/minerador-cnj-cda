import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def consultar_dados_processo(numero_processo, tipos_solicitados):
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    service = Service(log_level="OFF")  # Suprime logs do ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 1.3)

    driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")

    dados = {
        "Número do Processo": numero_processo
    }

    try:
        parte1 = numero_processo.split(".8.26.")[0]
        foro_id = numero_processo[-4:]

        campo1 = wait.until(EC.element_to_be_clickable((By.ID, 'numeroDigitoAnoUnificado')))
        campo1.clear()
        campo1.send_keys(parte1)
        time.sleep(0.3)

        campo2 = wait.until(EC.element_to_be_clickable((By.ID, 'foroNumeroUnificado')))
        campo2.clear()
        campo2.send_keys(foro_id)
        time.sleep(0.3)

        campo2.send_keys(Keys.ENTER)
        time.sleep(0.3)

        # CDAs
        if "cdas" in tipos_solicitados:
            try:
                wait.until(EC.presence_of_element_located((By.ID, 'linkCda')))
                driver.execute_script("document.getElementById('linkCda').click();")
                print("✅ Botão 'Visualizar CDAs' clicado com JavaScript")
                time.sleep(1)

                linhas = driver.find_elements(By.CSS_SELECTOR, "#tableCdasPrincipais tbody tr")
                cda_dados = []

                for linha in linhas:
                    colunas = linha.find_elements(By.TAG_NAME, "td")
                    if len(colunas) == 6:
                        cda_dados.append({
                            "Número CDA": colunas[0].text.strip(),
                            "Valor": colunas[1].text.strip(),
                            "Dt. CDA": colunas[2].text.strip(),
                            "Valor atualizado": colunas[3].text.strip(),
                            "Dt. atualização": colunas[4].text.strip(),
                            "Situação CDA": colunas[5].text.strip()
                        })

                dados["CDAs"] = cda_dados

            except:
                print("⚠️ Processo sem botão 'Visualizar CDAs'. Salvando com campos nulos.")
                dados["CDAs"] = [{
                    "Número CDA": None,
                    "Valor": None,
                    "Dt. CDA": None,
                    "Valor atualizado": None,
                    "Dt. atualização": None,
                    "Situação CDA": None
                }]

        # Se precisar de campos que estão nos dados secundários, clicar para expandir
        if any(campo in tipos_solicitados for campo in ["valor_acao", "data_distribuicao", "area"]):
            try:
                wait.until(EC.presence_of_element_located((By.ID, 'botaoExpandirDadosSecundarios')))
                driver.execute_script("document.getElementById('botaoExpandirDadosSecundarios').click();")
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠️ Erro ao expandir dados secundários com JavaScript: {e}")

        # Informações únicas (campos do topo)
        campos_unicos = {
            "assunto": "assuntoProcesso",
            "vara": "varaProcesso",
            "classe": "classeProcesso",
            "valor_acao": "valorAcaoProcesso",
            "data_distribuicao": "dataHoraDistribuicaoProcesso",
            "area": "areaProcesso",
            "situacao": "labelSituacaoProcesso",
            "foro": "foroProcesso"
        }

        for campo, seletor in campos_unicos.items():
            if campo in tipos_solicitados:
                try:
                    valor = driver.find_element(By.ID, seletor).text.strip()
                    dados[campo.replace('_', ' ').capitalize()] = valor
                except:
                    dados[campo.replace('_', ' ').capitalize()] = None

        # Partes do processo
        if "partes_processo" in tipos_solicitados:
            try:
                nomes = driver.find_elements(By.CLASS_NAME, 'nomeParteEAdvogado')
                dados["Exequente"] = nomes[0].text.strip() if len(nomes) > 0 else None
                dados["Executado"] = nomes[1].text.strip() if len(nomes) > 1 else None
            except:
                dados["Exequente"] = None
                dados["Executado"] = None

        # Tipo de processo: Virtual ou Físico
        if "tipo_processo" in tipos_solicitados:
            try:
                driver.find_element(By.ID, 'linkPasta')
                dados["Tipo de Processo"] = "Virtual"
            except:
                dados["Tipo de Processo"] = "Físico"

        return dados

    except Exception as e:
        print(f"❌ Erro ao consultar processo {numero_processo}: {e}")
        return {"Número do Processo": numero_processo, "Erro": str(e)}

    finally:
        driver.quit()
