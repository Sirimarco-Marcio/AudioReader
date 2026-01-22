import pdfplumber
import pandas as pd
import ollama
import os
import json
import re
import time  # <--- IMPORTADO AQUI

# --- CONFIGURAÇÕES DE CAMINHOS ---
PDF_PATH = "../artigo_exemplo.pdf"
JSON_PATH = "../artigo_exemplo_contexto.json"
ARQUIVO_SAIDA = "roteiro_tabelas_ttsn.txt"

# Modelo
MODELO_LLM = "qwen2.5:1.5b"

def carregar_contexto():
    """Carrega o contexto global do JSON na raiz."""
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return dados.get("contexto", "Artigo acadêmico técnico.")
        except Exception as e:
            print(f"⚠️ Erro ao ler JSON: {e}")
    return "Contexto técnico genérico."

def limpar_para_tts(texto):
    """Limpa o texto para o robô de áudio (Remove [], %, símbolos)."""
    if not texto: return ""
    
    texto = re.sub(r'\[(.*?)\]', r' \1 ', texto)
    
    substituicoes = {
        "%": " por cento",
        "°": " graus ",
        "≈": " aproximadamente ",
        "∑": " soma ",
        "𝑻": " Tempo ",
        "𝑵": " Número ",
        "vs": " versus "
    }
    for orig, dest in substituicoes.items():
        texto = texto.replace(orig, dest)
        
    return re.sub(r'\s+', ' ', texto).strip()

def processar_tabelas():
    # Marca o tempo inicial total
    inicio_geral = time.time() 

    if not os.path.exists(PDF_PATH):
        print(f"❌ Erro: Não encontrei '{PDF_PATH}'. Verifique se o arquivo está na pasta raiz 'AudioReader'.")
        return

    print(f"📊 INICIANDO TESTE DE TABELAS (Sem Visão)")
    print(f"📂 Lendo: {PDF_PATH}")
    
    contexto = carregar_contexto()
    print(f"🧠 Contexto: '{contexto[:100]}...'")
    
    resultados = []

    with pdfplumber.open(PDF_PATH) as pdf:
        total_pags = len(pdf.pages)
        print(f"📖 O documento tem {total_pags} páginas. Varrendo...")

        for i, page in enumerate(pdf.pages):
            settings = {
                "vertical_strategy": "text", 
                "horizontal_strategy": "lines",
                "intersection_y_tolerance": 5
            }
            
            tabelas = page.extract_tables(settings)
            if not tabelas: tabelas = page.extract_tables()
            if not tabelas: continue

            print(f"   [Pág {i+1}] 🔎 Encontradas {len(tabelas)} tabela(s).")

            for idx, tabela in enumerate(tabelas):
                if not tabela or len(tabela) < 2: continue

                try:
                    tabela_limpa = [['' if c is None else c for c in row] for row in tabela]
                    df = pd.DataFrame(tabela_limpa[1:], columns=tabela_limpa[0])
                    df = df.replace(r'\n', ' ', regex=True)
                    tabela_md = df.to_markdown(index=False)
                    
                    num_cols = len(df.columns)
                    col_names = ", ".join([str(c) for c in df.columns])

                    if num_cols <= 10:
                        instrucao = (
                            f"A tabela tem {num_cols} colunas ({col_names}). "
                            "Faça uma leitura detalhada relacionando as colunas. Cite máximos, mínimos e anomalias."
                        )
                    else:
                        instrucao = "Tabela muito larga. Resuma apenas o objetivo macroscópico dos dados. NÃO leia valores individuais."

                    prompt = (
                        f"Você é um assistente técnico acadêmico.\n"
                        f"CONTEXTO DO ARTIGO: '{contexto}'\n"
                        f"DIRETRIZES DE TOM:\n"
                        f"- Seja extremamente formal e objetivo.\n"
                        f"- Se encontrar palavras quebradas ou cabeçalhos estranhos (como 'ioridade' ou 'o máx'), corrija-os pelo contexto (para 'Prioridade' ou 'Tempo máx') em vez de analisá-los literalmente. Não repita a introdução do estudo a cada tabela; faça uma análise contínua."
                        f"- Ignore cabeçalhos se forem números aleatórios ou sujeira de OCR.\n"
                        f"- {instrucao}\n\n"
                        f"DADOS BRUTOS:\n{tabela_md}\n\n"
                        f"RESPOSTA TÉCNICA (PT-BR):"
                    )

                    print(f"      ⏳ Enviando para LLM ({MODELO_LLM})...")
                    
                    # --- CRONÔMETRO LLM ---
                    inicio_llm = time.time()
                    
                    response = ollama.chat(
                        model=MODELO_LLM,
                        messages=[{'role': 'user', 'content': prompt}],
                        options={
                            'num_ctx': 2048,      # Pode voltar para 4096, sua placa aguenta sobrando!
                            'temperature': 0.3,
                            'num_gpu': 99,        # Garante que vai tudo para a VRAM
                        }
                    )
                    fim_llm = time.time()
                    tempo_llm = fim_llm - inicio_llm
                    # -----------------------

                    texto_raw = response['message']['content']
                    texto_final = limpar_para_tts(texto_raw)
                    
                    bloco_texto = f"--- Tabela {idx+1} (Pág {i+1}) ---\n{texto_final}\n"
                    resultados.append(bloco_texto)
                    
                    print(f"      ✅ Processada em {tempo_llm:.2f}s ({num_cols} colunas).")

                except Exception as e:
                    print(f"      ❌ Erro na tabela da pág {i+1}: {e}")

    # Salva o resultado
    if resultados:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            f.write(f"CONTEXTO USADO: {contexto}\n")
            f.write("="*50 + "\n\n")
            f.write("\n".join(resultados))
        print("\n" + "="*50)
        print(f"✅ SUCESSO! Roteiro salvo em: {ARQUIVO_SAIDA}")
    else:
        print("\n⚠️ Nenhuma tabela processada.")

    # --- CÁLCULO FINAL DE TEMPO ---
    fim_geral = time.time()
    tempo_total = fim_geral - inicio_geral
    minutos = int(tempo_total // 60)
    segundos = int(tempo_total % 60)
    
    print(f"⏱️ Tempo Total de Execução: {minutos}m {segundos}s")

if __name__ == "__main__":
    processar_tabelas()