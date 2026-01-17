import edge_tts
import asyncio

# Vozes constantes
VOZ_MASCULINA = "pt-BR-AntonioNeural"
VOZ_FEMININA = "pt-BR-FranciscaNeural"

async def gerar_audio_neural(texto, caminho_saida, voz=VOZ_MASCULINA):
    """
    Gera o áudio usando Edge-TTS.
    """
    if not texto or not texto.strip():
        return False

    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(caminho_saida)
    return True