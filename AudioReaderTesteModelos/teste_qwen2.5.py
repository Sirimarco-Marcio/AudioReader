import ollama
import pytesseract
from PIL import Image
import sys
import os
import time
import io

# --- CONFIGURAÇÕES ---
# Nome da imagem que você quer testar
ARQUIVO_IMAGEM = "teste2.png" 

# O modelo que você baixou. Mude para 'llava' se o llama3.2-vision não rodar.
MODELO_VISAO = "qwen2.5vl:3b"



def redimensionar_imagem(caminho_img, max_size=768):
    """Reduz a imagem para economizar tokens e VRAM."""
    img = Image.open(caminho_img)
    # Redimensiona mantendo a proporção (thumbnail não estica)
    img.thumbnail((max_size, max_size))
    
    # Converte para bytes para enviar ao Ollama
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG') # ou JPEG
    return img_byte_arr.getvalue(), img

def teste_otimizado():
    print(f"🔧 Carregando: {ARQUIVO_IMAGEM}")
    
    # 1. Carrega a Original na memória (Alta Resolução)
    img_original = Image.open(ARQUIVO_IMAGEM)
    
    # 2. OCR na ORIGINAL (Aqui recuperamos os caracteres perdidos)
    #    O Tesseract roda na CPU, então a resolução alta não trava a GPU.
    print("   ↳ Rodando OCR na imagem original (Alta Definição)...")
    custom_config = r'--oem 3 --psm 3'
    texto_ocr = pytesseract.image_to_string(img_original, lang='por+eng', config=custom_config)
    print(f"   ✅ OCR extraiu {len(texto_ocr)} caracteres (Máxima Fidelidade).")

    # 3. Redimensionar APENAS para enviar ao Ollama (Economia de GPU)
    max_size = 768 # ou 1024 se sua GPU aguentar bem
    img_copia = img_original.copy()
    img_copia.thumbnail((max_size, max_size))
    
    img_byte_arr = io.BytesIO()
    img_copia.save(img_byte_arr, format='PNG')
    img_bytes_envio = img_byte_arr.getvalue()
    
    print(f"   ↳ Imagem redimensionada para {img_copia.size} para envio à IA.")

    # 4. Enviar: Texto Rico + Imagem Leve
    prompt = (
        f"Analise esta imagem acadêmica.\n"
        f"DADOS PRECISOS DO TEXTO (OCR): '''{texto_ocr}'''\n\n"
        f"Com base na imagem visual (estrutura) e no texto extraído acima, explique o diagrama."
    )

    # ... (restante do código de envio para o Ollama igual)

    try:
        response = ollama.chat(
            model=MODELO_VISAO,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [img_bytes] # Envia a versão leve
            }],
            options={
                'num_ctx': 2048,   # Mantemos baixo para caber na VRAM
                'temperature': 0.1
            }
        )
        print("\n🤖 RESPOSTA:")
        print(response['message']['content'])
        print(f"\n⏱️ Tempo: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    teste_otimizado()