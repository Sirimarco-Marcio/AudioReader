import io
import sys

TEM_LIBS_IA = False
try:
    import torch
    from transformers import Blip2Processor, Blip2ForConditionalGeneration
    from PIL import Image
    import pytesseract
    TEM_LIBS_IA = True
except ImportError as e:
    print(f"\n⚠️  AVISO DE DEBUG: Falha ao importar libs.")
    print(f"   Erro: {e}")
except Exception as e:
    print(f"Erro crítico: {e}")

class VisionAI:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisionAI, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.processor = None
            cls._instance.device = None
            cls._instance.carregado = False
        return cls._instance

    def inicializar(self):
        if not TEM_LIBS_IA: return False
        if self.carregado: return True

        print("🧠 Carregando Pipeline Híbrido (BLIP-2 + OCR)...")
        try:
            if torch.cuda.is_available():
                self.device = "cuda"
                print(f"   ↳ GPU Ativa para Visão 🚀")
            else:
                self.device = "cpu"
                print("   ⚠️  CPU (Lento)")

            model_id = "Salesforce/blip2-opt-2.7b"
            self.processor = Blip2Processor.from_pretrained(model_id)
            
            # AMD RDNA2 prefere bfloat16
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16, 
                use_safetensors=True
            )
            self.model.to(self.device)
            
            self.carregado = True
            print("✅ Pipeline Híbrido pronto!")
            return True
        except Exception as e:
            print(f"❌ Falha ao carregar modelo: {e}")
            return False

    def _executar_ocr(self, imagem_pil):
        """Extrai texto puro caso exista."""
        try:
            # --psm 6 assume um bloco de texto uniforme, --psm 3 é automático (padrão)
            # lang='por+eng' ajuda a ler termos técnicos em inglês no meio do português
            texto = pytesseract.image_to_string(imagem_pil, lang='por+eng') 
            return " ".join(texto.split())
        except Exception as e:
            print(f"⚠️ Erro no OCR: {e}")
            return ""

    def descrever_imagem(self, image_data_bytes):
        if not self.carregado: return None
        try:
            raw_image = Image.open(io.BytesIO(image_data_bytes)).convert('RGB')
            if raw_image.width < 70 or raw_image.height < 70: return None

            # 1. Tenta ler o texto (OCR)
            texto_ocr = self._executar_ocr(raw_image)
            
            # 2. Analisa o visual (BLIP-2)
            # PROMPT GENÉRICO: Funciona para diagramas, fotos e prints de tela.
            pergunta = "Question: Describe the scene, content, or diagram shown in this image in detail. Answer:"
            
            inputs = self.processor(
                images=raw_image, 
                text=pergunta, 
                return_tensors="pt"
            ).to(self.device, torch.bfloat16)

            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=80,      # Descrição visual não precisa ser uma bíblia
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
            descricao_visual = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

            # 3. Monta a resposta final
            resultado = f"[VISUAL: {descricao_visual}]"
            
            # Só adiciona o bloco de texto se o OCR achou algo relevante (mais de 10 letras)
            # Isso evita sujar o áudio com ruído de OCR ("... , . ; '")
            if len(texto_ocr) > 10:
                resultado += f"\n[TEXTO DETECTADO NA IMAGEM: {texto_ocr}]"
                
            return resultado
        
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return None