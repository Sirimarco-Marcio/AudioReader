import sys
import time
import shutil
import asyncio
from pathlib import Path

# Importando nossos módulos novos
from app.utils.file_manager import listar_arquivos_recursivo, criar_pasta_destino
from app.core.extractor import extrair_conteudo
from app.core.tts import gerar_audio_neural

# Cores
VERDE = '\033[92m'
AMARELO = '\033[93m'
AZUL = '\033[94m'
ROXO = '\033[95m'
RESET = '\033[0m'

def limpar_tela():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def barra_progresso_wrapper(atual, total, prefixo):
    """Wrapper visual para passar como callback"""
    percentual = ("{0:.1f}").format(100 * (atual / float(total)))
    sys.stdout.write(f'\r{prefixo}: {percentual}% Completo')
    sys.stdout.flush()

def main():
    while True:
        limpar_tela()
        print(f"{VERDE}=== AUDIOREADER MODULAR (V3) ==={RESET}")
        
        arquivos = listar_arquivos_recursivo()
        if not arquivos:
            print(f"{AMARELO}Nenhum arquivo encontrado.{RESET}")
            input("Enter para atualizar...")
            continue

        for i, arq in enumerate(arquivos):
            print(f"[{i+1}] {arq}")
        
        print(f"\n[0] Sair")
        
        # Pergunta sobre IA antes de selecionar o arquivo
        usar_ia = input(f"\n{ROXO}Ativar Inteligência Visual (Lento)? [s/N]: {RESET}").lower() == 's'
        
        opcao = input(f"{AZUL}Escolha o arquivo: {RESET}")
        if opcao == '0': break

        try:
            idx = int(opcao) - 1
            caminho_arquivo = arquivos[idx]
            
            print(f"\nProcessando: {caminho_arquivo}")
            pasta_destino = criar_pasta_destino(caminho_arquivo)
            shutil.copy2(caminho_arquivo, pasta_destino / Path(caminho_arquivo).name)

            # --- EXTRAÇÃO (Com ou sem IA) ---
            print(f"{AZUL}Iniciando extração...{RESET}")
            texto_completo = extrair_conteudo(
                caminho_arquivo, 
                usar_vision=usar_ia, 
                callback_progresso=barra_progresso_wrapper
            )
            print("\n") # Pula linha após barra de progresso

            # --- GERAÇÃO DE ÁUDIO ---
            if texto_completo:
                print(f"{AZUL}Gerando áudio neural...{RESET}")
                caminho_audio = pasta_destino / f"AUDIO - {Path(caminho_arquivo).stem}.mp3"
                
                inicio = time.time()
                asyncio.run(gerar_audio_neural(texto_completo, str(caminho_audio)))
                fim = time.time()
                
                print(f"{VERDE}✅ Sucesso! Tempo: {fim - inicio:.2f}s{RESET}")
                print(f"Arquivo salvo em: {caminho_audio}")
            else:
                print(f"{AMARELO}O arquivo parece vazio.{RESET}")

            input(f"\n{VERDE}Enter para voltar...{RESET}")

        except ValueError:
            print("Entrada inválida.")
            time.sleep(1)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            input()

if __name__ == "__main__":
    main()