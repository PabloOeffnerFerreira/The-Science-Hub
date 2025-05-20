## INSTALL.pt-BR.md

# Guia de Instalação – Science Hub (Português Brasileiro)

Bem-vindo ao Science Hub!  
Este guia foi feito para te ajudar a instalar o Science Hub no seu computador, de forma simples e rápida.

O Science Hub é uma plataforma criada para estudar e fazer ciência usando ferramentas, bibliotecas, imagens e até uma inteligência artificial local — tudo rodando no seu próprio PC, sem depender da internet.

---

## Requisitos

- **Sistema operacional:** Windows 10 ou 11 (também funciona no Linux e macOS)
- **Memória:** 8 GB RAM (recomendado: 16 GB ou mais)
- **Placa de vídeo:** Pelo menos 4 GB de VRAM (para usar a IA com modelos grandes, recomendado 8 GB ou mais)
- **Python:** Versão 3.13.3 (recomendado), mas versões acima de 3.10 também funcionam
- **Git:** Necessário para baixar o código (veja abaixo)
- **Ollama:** Apenas se quiser usar o Assistente de IA (veja o passo extra abaixo)

---

## Passo a Passo

### 1. Instale o Python

Se ainda não tem o Python:
- Acesse: https://www.python.org/downloads/windows/
- Baixe o **Python 3.13.3**
- Durante a instalação, marque a opção “Add Python to PATH” (ou “Adicionar Python ao PATH”)

### 2. Instale o Git (se precisar)

- Acesse: https://git-scm.com/download/win
- Baixe e instale normalmente

### 3. Baixe o Science Hub

Abra o **Prompt de Comando** (ou **Terminal**) e digite:

```sh
git clone https://github.com/PabloOeffnerFerreira/The-Science-Hub.git
cd The-Science-Hub
````

### 4. (Opcional, mas recomendado) Crie um Ambiente Virtual

Isso evita conflitos com outros programas Python.

```sh
python -m venv venv
venv\Scripts\activate
```

No Linux ou Mac:

```sh
source venv/bin/activate
```

### 5. Instale as Dependências

No terminal já dentro da pasta do projeto:

```sh
pip install -r requirements.txt
pip install Pillow tkinterdnd2
```

Se aparecer algum erro de pacote, pode tentar atualizar o pip:

```sh
python -m pip install --upgrade pip
```

### 6. (Opcional) Instale o RDKit

O RDKit é necessário para algumas funções de química:

```sh
conda install -c conda-forge rdkit
```

(Para isso, precisa ter o [Anaconda ou Miniconda](https://docs.conda.io/en/latest/miniconda.html) instalado)

### 7. (Opcional) Instale o Ollama para Assistente de IA

Se quiser usar a IA offline (sem internet):

* Acesse: [https://ollama.com/download](https://ollama.com/download)
* Baixe e instale para seu sistema operacional
* Depois de instalar, abra o terminal e puxe um modelo de IA, por exemplo:

```sh
ollama pull dolphin3:8b
ollama pull tinyllama:1.1b
```

### 8. Rode o Science Hub

Na pasta do projeto, execute:

```sh
python hub.py
```

---

## Dicas e Solução de Problemas

* **Erro "pip" não reconhecido:** Abra o terminal novamente ou reinicie o PC.
* **Erro de permissão:** Tente abrir o Prompt de Comando como Administrador.
* **Problema ao instalar pacotes:** Verifique se está com o ambiente virtual ativado e se o Python está no PATH.
* **Se algo der errado:**
  Fique tranquilo, me avise (Pablo) que eu posso te ajudar pelo WhatsApp ou chamada!

---

## Mais Informações

* O Science Hub salva suas bibliotecas e imagens localmente — você não perde nada se fechar o programa.
* O assistente de IA só funciona se o Ollama estiver rodando e você tiver baixado pelo menos um modelo.
* Se quiser aprender mais ou contribuir, veja a página no GitHub:
  [https://github.com/PabloOeffnerFerreira/The-Science-Hub](https://github.com/PabloOeffnerFerreira/The-Science-Hub)

---

*Qualquer dúvida, é só perguntar!*

