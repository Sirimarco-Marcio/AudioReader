import os
from pathlib import Path

def listar_arquivos_recursivo(diretorio_base='.'):
    extensoes = {'.pdf', '.docx', '.doc'}
    arquivos_encontrados = []
    
    for root, dirs, files in os.walk(diretorio_base):
        # Ignora pastas de output
        if "AUDIO -" in root:
            continue
            
        for file in files:
            caminho_completo = Path(root) / file
            if caminho_completo.suffix.lower() in extensoes and not file.startswith('~$'):
                arquivos_encontrados.append(str(caminho_completo))
                
    return sorted(arquivos_encontrados)

def criar_pasta_destino(arquivo_path):
    arquivo_path = Path(arquivo_path)
    nome_pasta = f"AUDIO - {arquivo_path.stem}"
    
    if not os.path.exists(nome_pasta):
        os.makedirs(nome_pasta)
    
    return Path(nome_pasta)