# 🎧 AudioReader - Conversor de Documentos para Audiobook

> Transforme relatórios técnicos, contratos e livros (PDF/DOCX) em áudios de alta fidelidade usando Vozes Neurais.

O **AudioReader** é uma ferramenta de produtividade desenvolvida em Python para profissionais que precisam otimizar seu tempo. Ele permite a técnica de *"Immersive Reading"* (ler acompanhando o áudio) ou o consumo passivo de conteúdo técnico, convertendo documentos estáticos em arquivos MP3 com narração natural (sem robótica).

## 🚀 Funcionalidades Atuais (CLI v2.0)

O projeto atualmente opera via linha de comando (CLI) com as seguintes capacidades:

- **Busca Recursiva Inteligente:** Escaneia automaticamente a pasta raiz e subpastas (como `PDFs/` e `DOCs/`) para encontrar arquivos compatíveis.
- **Suporte a Formatos:**
  - 📄 **PDF:** Extração de texto baseada em páginas (`pypdf`).
  - 📝 **DOCX:** Leitura estruturada de parágrafos (`python-docx`).
- **Motor de Áudio Neural:** Utiliza a biblioteca `edge-tts` (Microsoft Edge Online) para gerar vozes ultra-realistas (pt-BR Antonio ou Francisca) com entonação de contexto.
- **Feedback Visual:** Barras de progresso para a extração de texto e indicadores de status para a geração de áudio.
- **Organização Automática:**
  - Cria uma pasta dedicada para cada projeto (ex: `AUDIO - Relatório`).
  - Gera o arquivo MP3.
  - Realiza o backup automático do arquivo original para a pasta de destino.

## 🛠️ Instalação e Uso

### Pré-requisitos
Certifique-se de ter o Python 3.8+ instalado.

1. **Clone o repositório ou baixe os arquivos.**
2. **Instale as dependências:**

```bash
pip install pypdf python-docx edge-tts gTTS

```

### Como Rodar

1. Organize seus arquivos nas pastas `PDFs`, `DOCs` ou na raiz do projeto.
2. Execute o script principal:

```bash
python leitor.py

```

3. Um menu interativo aparecerá listando seus arquivos. Digite o número correspondente e aguarde a mágica acontecer!

## 🗺️ Roadmap de Desenvolvimento

O projeto está em evolução constante. Abaixo estão as etapas planejadas para as próximas versões:

### Fase 1: Interface Gráfica Profissional (GUI)

* [ ] Migração de CLI para **PySide6 (Qt)**.
* [ ] Implementação de **Multithreading (QThread)** para evitar congelamento da interface durante a renderização do áudio.
* [ ] Drag & Drop de arquivos.

### Fase 2: Inteligência de Leitura (SSML)

* [ ] Implementação de pausas inteligentes (respiração) entre parágrafos.
* [ ] Detecção de "Capítulos" e "Títulos" para inserção de pausas longas (2s+).
* [ ] Ajuste dinâmico de velocidade de fala (-5% para textos técnicos densos).

### Fase 3: Visão Computacional (OCR Avançado)

* [ ] **Integração com BLIP-2 (Bootstrapping Language-Image Pre-training):**
* Implementação de modelos de Vision-Language para ler e descrever imagens contidas nos PDFs.
* Capacidade de ler PDFs digitalizados (imagens) que não possuem camada de texto selecionável.
* Geração de legendas automáticas para gráficos e tabelas dentro do áudio.



## 📂 Estrutura do Projeto

```text
AudioReader/
├── DOCs/               # Pasta sugerida para arquivos Word
├── PDFs/               # Pasta sugerida para arquivos PDF
├── leitor.py           # Script principal (CLI + Core Logic)
├── README.md           # Documentação
└── AUDIO - [Nome]/     # (Gerado automaticamente)
    ├── backup.pdf      # Cópia do original
    └── audio.mp3       # Audiobook gerado

```

## 📄 Licença

Este projeto é de uso livre para fins educacionais e pessoais.