import io
import sys

TEM_LIBS_IA = False
try:
    import torch
    # MUDANÇA 1: Importamos as classes do BLIP-2
    from transformers import Blip2Processor, Blip2ForConditionalGeneration
    from PIL import Image
    TEM_LIBS_IA = True
except ImportError as e:
    print(f"\n⚠️  AVISO DE DEBUG: Falha ao importar bibliotecas de IA.")
    print(f"   Erro exato: {e}")
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

        print("🧠 Carregando modelo BLIP-2 (Otimizado com BFloat16)...")
        try:
            if torch.cuda.is_available():
                self.device = "cuda"
                print(f"   ↳ Hardware AMD Detectado: GPU Ativa 🚀")
            else:
                self.device = "cpu"
                print("   ⚠️  Hardware: CPU (Fallback)")

            model_id = "Salesforce/blip2-opt-2.7b"
            self.processor = Blip2Processor.from_pretrained(model_id)
            
            # --- A MÁGICA DO BFLOAT16 ---
            # bfloat16 usa metade da RAM (como float16) mas mantém a 
            # estabilidade numérica do float32. Perfeito para RDNA2 (RX 6000+).
            dtype = torch.bfloat16
            
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                model_id,
                torch_dtype=dtype, 
                use_safetensors=True
            )
            
            self.model.to(self.device)
            self.carregado = True
            print("✅ Modelo BLIP-2 carregado (Leve e Estável)!")
            return True
        except Exception as e:
            print(f"❌ Falha ao carregar modelo: {e}")
            # Se der erro de memória mesmo assim, tentaremos limpar o cache
            torch.cuda.empty_cache()
            return False

    def descrever_imagem(self, image_data_bytes):
        if not self.carregado: return None
        try:
            raw_image = Image.open(io.BytesIO(image_data_bytes)).convert('RGB')
            if raw_image.width < 70 or raw_image.height < 70: return None

            # Prompt focado em leitura de estrutura
            pergunta = "Question: Describe the diagram and read the text inside the boxes. Answer:"
            
            # Precisamos converter o input para bfloat16 também
            dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
            
            inputs = self.processor(
                images=raw_image, 
                text=pergunta, 
                return_tensors="pt"
            ).to(self.device, dtype)

            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=100,
                min_length=35,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )

            descricao = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            return f"[VISUAL: {descricao}]"
        
        except Exception as e:
            print(f"Erro ao processar imagem: {e}")
            return None