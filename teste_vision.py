# Arquivo: teste_vision.py
import sys
import os
from app.core.vision import VisionAI

def teste_local():
    print("--- INICIANDO TESTE DO BLIP (ARQUIVO LOCAL) ---")
    
    # Nome do arquivo que você salvou na pasta
    nome_arquivo = "teste.png"
    
    if not os.path.exists(nome_arquivo):
        print(f"❌ Erro: O arquivo '{nome_arquivo}' não foi encontrado na pasta.")
        print("Salve a imagem do fluxograma nessa pasta com esse nome.")
        return

    # Lê a imagem em bytes
    with open(nome_arquivo, "rb") as f:
        img_bytes = f.read()
    
    # Inicializa a IA
    vision = VisionAI()
    sucesso = vision.inicializar()
    
    if sucesso:
        print(f"\n📸 Analisando imagem: {nome_arquivo}...")
        descricao = vision.descrever_imagem(img_bytes)
        print(f"\n📝 RESULTADO DA IA: {descricao}")
    else:
        print("Falha ao inicializar IA.")

if __name__ == "__main__":
    teste_local()