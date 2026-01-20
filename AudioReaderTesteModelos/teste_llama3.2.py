import ollama
import pytesseract
from PIL import Image
import sys
import os
import time
import io

# --- CONFIGURAÇÕES ---
ARQUIVO_IMAGEM = "teste2.png" 
# Certifique-se de usar o nome exato do modelo que funcionou para você
MODELO_VISAO = "qwen2.5vl:3b" 

def converter_para_bytes(imagem_pil):
    """Converte uma imagem PIL para bytes prontos para o Ollama."""
    img_byte_arr = io.BytesIO()
    imagem_pil.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def teste_otimizado():
    if not os.path.exists(ARQUIVO_IMAGEM):
        print(f"❌ Erro: Arquivo '{ARQUIVO_IMAGEM}' não encontrado.")
        return

    print(f"🔧 Carregando imagem: {ARQUIVO_IMAGEM}")
    
    # 1. Carregar Imagem ORIGINAL (Alta Resolução)
    try:
        img_original = Image.open(ARQUIVO_IMAGEM)
        print(f"   ↳ Resolução original: {img_original.size}")
    except Exception as e:
        print(f"❌ Erro ao abrir imagem: {e}")
        return

    # 2. OCR na ORIGINAL (Aqui está o segredo da qualidade)
    #    Rodamos o Tesseract antes de reduzir, garantindo que ele leia as letras miúdas.
    print("   ↳ 📖 Executando OCR na imagem original (Alta Fidelidade)...")
    start_ocr = time.time()
    custom_config = r'--oem 3 --psm 3'
    texto_ocr = pytesseract.image_to_string(img_original, lang='por+eng', config=custom_config)
    print(f"      ✅ OCR concluído em {time.time() - start_ocr:.2f}s. Caracteres extraídos: {len(texto_ocr)}")

    # 3. Redimensionar Cópia para a IA (Para caber na GPU)
    #    Criamos uma cópia para não afetar a original caso precisasse usar de novo
    img_gpu = img_original.copy()
    MAX_SIZE = 768 # Tamanho seguro para VRAM e Contexto
    img_gpu.thumbnail((MAX_SIZE, MAX_SIZE))
    print(f"   ↳ 📉 Cópia redimensionada para {img_gpu.size} para envio à GPU.")
    
    # Prepara os bytes da imagem reduzida
    img_bytes_envio = converter_para_bytes(img_gpu)

    # 4. Enviar para IA com contexto controlado
    print("\n🚀 Enviando para o Ollama (GPU)...")
    start_ai = time.time()
    
    prompt = (
        f"Analise esta imagem retirada de um documento acadêmico.\n"
        f"Abaixo está o texto extraído via OCR da imagem original para te ajudar a ler detalhes pequenos:\n"
        f"'''{texto_ocr}'''\n\n"
        f"Com base na imagem visual (estrutura/formas) e no texto de apoio acima, explique detalhadamente o que é mostrado e qual a conclusão principal."
    )

    try:
        response = ollama.chat(
            model=MODELO_VISAO,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [img_bytes_envio] # Envia APENAS a versão leve
            }],
            options={
                'num_ctx': 2048,   # Contexto reduzido para garantir que cabe na VRAM
                'temperature': 0.1 # Temperatura baixa para ser fiel aos dados
            }
        )
        print("\n🤖 RESPOSTA:")
        print("-" * 50)
        print(response['message']['content'])
        print("-" * 50)
        print(f"⏱️ Tempo total da IA: {time.time() - start_ai:.2f}s")
        
    except Exception as e:
        print(f"\n❌ Erro na comunicação com Ollama: {e}")
        # Dica de debug caso falhe
        if "truncating" in str(e):
            print("💡 Dica: O contexto estourou. Tente diminuir ainda mais a imagem ou aumentar num_ctx levemente.")

if __name__ == "__main__":
    teste_otimizado()