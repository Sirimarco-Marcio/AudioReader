import fitz  # PyMuPDF
import ollama
import json
import os
import re

class GerenciadorContexto:
    def __init__(self, pdf_path, modelo_llm="llama3.2:3b"):
        self.pdf_path = pdf_path
        self.modelo_llm = modelo_llm
        self.arquivo_cache = pdf_path.replace(".pdf", "_contexto.json")

    def _limpar_texto_basico(self, texto):
        """Remove excesso de quebras de linha para economizar tokens."""
        return re.sub(r'\s+', ' ', texto).strip()

    def _eh_linha_de_sumario(self, linha):
        """
        Detecta se a linha é um índice de sumário (ex: 'Resumo ...... 5')
        para evitar falsos positivos.
        """
        # Verifica se termina com números ou tem muitos pontos
        if re.search(r'\.{3,}\s*\d+$', linha):
            return True
        if re.search(r'\s+\d+$', linha) and len(linha) < 80:
            return True
        return False

    def escanear_paginas_chave(self):
        """
        Lógica: Pega Capa + (Abstract/Resumo OU Introdução).
        Varre até a página 15 para garantir.
        """
        doc = fitz.open(self.pdf_path)
        
        # 1. Sempre pega a Capa (Título/Autor)
        texto_acumulado = f"--- CAPA/TÍTULO ---\n{doc[0].get_text()}\n\n"
        
        pagina_resumo_encontrada = False
        paginas_para_ler = []

        # 2. Scanner (Página 1 até 15)
        limite_busca = min(15, len(doc))
        
        print(f"🕵️ Escaneando páginas 1 a {limite_busca} em busca do Resumo...")
        
        for i in range(1, limite_busca):
            pagina_texto = doc[i].get_text()
            linhas = pagina_texto.split('\n')
            
            # Verifica as primeiras 10 linhas da página (onde fica o título da seção)
            cabecalho = " ".join(linhas[:10]).lower()
            
            # Palavras-chave fortes
            if "resumo" in cabecalho or "abstract" in cabecalho:
                # Verificação de segurança: Não é sumário?
                if not any(self._eh_linha_de_sumario(l) for l in linhas[:5] if "resumo" in l.lower() or "abstract" in l.lower()):
                    print(f"   📍 Resumo detectado na página {i+1}!")
                    paginas_para_ler.append(i)
                    # Pega também a próxima, vai que o resumo é grande
                    if i + 1 < len(doc):
                        paginas_para_ler.append(i + 1)
                    pagina_resumo_encontrada = True
                    break # Achou, parou.
        
        # Fallback: Se não achou resumo, tenta achar "Introdução"
        if not pagina_resumo_encontrada:
            print("   ⚠️ Resumo não explícito. Tentando achar 'Introdução'...")
            for i in range(1, limite_busca):
                if "introdução" in doc[i].get_text().lower()[:500]:
                    print(f"   📍 Introdução detectada na página {i+1}.")
                    paginas_para_ler.append(i)
                    break
        
        # Se falhou tudo, pega as páginas 1 e 2 como garantia
        if not paginas_para_ler:
            print("   ⚠️ Nada específico encontrado. Usando páginas 1 e 2 padrão.")
            paginas_para_ler = [1, 2]

        # Extrai o texto das páginas selecionadas
        for p_idx in paginas_para_ler:
            texto_acumulado += f"--- PÁGINA {p_idx+1} ---\n{doc[p_idx].get_text()}\n"

        return texto_acumulado

    def obter_contexto_global(self, forcar_atualizacao=False):
        """
        Gerencia o fluxo: Verifica Cache -> Se não tiver, Gera -> Salva.
        """
        # 1. Tenta carregar do disco (Cache)
        if not forcar_atualizacao and os.path.exists(self.arquivo_cache):
            try:
                with open(self.arquivo_cache, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    print(f"💾 Contexto carregado do cache: {self.arquivo_cache}")
                    return dados["contexto"]
            except:
                print("⚠️ Cache corrompido, gerando novamente.")

        # 2. Gera novo contexto
        texto_bruto = self.escanear_paginas_chave()
        
        print("🧠 Enviando texto selecionado para o Llama 3.2 definir o contexto...")
        
        prompt = (
            f"Analise o texto extraído das partes chave deste documento (Capa e Resumo/Introdução):\n"
            f"'''{texto_bruto[:6000]}'''\n\n" # Limite de caracteres de segurança
            f"TAREFA: Resuma em UMA FRASE TÉCNICA E DENSA o tema central, o objetivo e a área de estudo."
            f"Essa frase servirá de contexto para uma IA descrever gráficos e tabelas deste arquivo."
            f"Exemplo: 'Artigo de Engenharia Civil sobre resistência de concreto armado sob altas temperaturas.'"
            f"\n\nCONTEXTO:"
        )

        try:
            response = ollama.chat(
                model=self.modelo_llm,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.1, 'num_ctx': 4096}
            )
            contexto_gerado = response['message']['content'].strip()
            
            # 3. Salva no Cache
            with open(self.arquivo_cache, "w", encoding="utf-8") as f:
                json.dump({
                    "arquivo": self.pdf_path,
                    "contexto": contexto_gerado,
                    "paginas_lidas": "Capa + Detecção Automática"
                }, f, ensure_ascii=False, indent=4)
                
            print(f"✅ Contexto gerado e salvo: {contexto_gerado}")
            return contexto_gerado

        except Exception as e:
            print(f"❌ Erro ao gerar contexto: {e}")
            return "Documento técnico acadêmico."

# --- COMO USAR NO SEU PIPELINE ---

if __name__ == "__main__":
    PDF_ALVO = "artigo_exemplo.pdf"
    
    # Inicializa o gerenciador
    gerenciador = GerenciadorContexto(PDF_ALVO)
    
    # Pega o contexto (lê do disco se já existir, ou gera se for novo)
    contexto = gerenciador.obter_contexto_global()
    
    print("\n--- PRONTO PARA USAR NAS TABELAS E IMAGENS ---")
    print(f"Váriavel 'contexto': {contexto}")
    
    # Exemplo de como você passaria isso para a sua função de tabelas:
    # processar_tabelas_com_ia(pagina, i, contexto)