# 🤖 Chatbot para Análise de PDFs - Projeto DIO

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como parte do desafio **"Criando um Chatbot Baseado em Conteúdo de PDFs"** da DIO.
A ideia era criar um sistema inteligente que conseguisse analisar documentos PDF e responder perguntas sobre seu conteúdo usando IA generativa. Segui todos os requisitos do curso e ainda **melhorei o projeto adicionando uma funcionalidade extra muito importante**: o **Modo Sem IA**.

---

### 🎯 Por que adicionei o Modo Sem IA?

Durante o desenvolvimento, percebi que muitos usuários se beneficiariam se fosse adicionada uma versão que **não exigisse o uso de API**, o que tornaria a aplicação mais relevante para quem for utilizá-la  
(claro, pensando fora de um uso empresarial, atendendo tanto ao uso na empresa quanto ao uso doméstico),  
**já que o custo da API se torna um fator alto**.

Por isso, criei um sistema completo de análise que funciona **100% localmente, sem uso de IA** —  
**porém, não tão completo quanto a versão com IA** — garantindo que todos possam usar o chatbot e moldar da forma que desejar.

---

## ✨ Funcionalidades

### ✅ **Obrigatórias (do curso)**

- 📄 **Carregamento de PDFs** — Lê e processa documentos PDF  
- 🔍 **Sistema de Busca** — Encontra informações nos documentos  
- 🤖 **IA Generativa** — Responde perguntas usando OpenAI  
- 💬 **Chat Interativo** — Interface para conversar com os documentos

### 🎁 **Extras (minhas contribuições)**

- 🎯 **Modo Sem IA** — Análise textual completa e gratuita  
- 📊 **Ferramentas de Análise** — Estatísticas, palavras-chave, comparações  
- 🔐 **Gerenciador de Chaves** — Interface amigável para configurar API  
- 💾 **Histórico Persistente** — Salva todas as conversas  
- 📈 **Exportação de Dados** — Gera relatórios em JSON

---

## 🛠️ Tecnologias Usadas

- 🐍 **Python 3.8+** — Linguagem principal  
- 📘 **PyPDF2** — Leitura de arquivos PDF  
- 🧠 **NLTK** — Processamento de linguagem natural  
- 🤖 **OpenAI API** — IA generativa (opcional)  
- 💾 **JSON** — Armazenamento de configurações e histórico

---

## 🚀 Como Usar

### 1. Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/chatbot-pdf-dio.git
cd chatbot-pdf-dio
```
# Instale as dependências
```bash
pip install -r requirements.txt
```

2. Adicione Seus Documentos
Coloque seus arquivos PDF ou TXT na pasta inputs/:

 
inputs/
├── artigo_cientifico.pdf
├── relatorio_trabalho.pdf
└── documento_exemplo.txt
 
3. Execute o Chatbot
```bash
bash
python chatbot.py
```
4. Escolha o Modo de Uso:
🤖 Modo com IA (Para quem tem acesso à OpenAI)
Configure sua chave API no menu

Faça perguntas em linguagem natural

Receba respostas inteligentes baseadas no documento

🎯 Modo sem IA:
Análise completa do texto

Estatísticas detalhadas

Busca por palavras-chave

Comparação de termos

Exportação de relatórios

📸 Como Funciona
📋 Menu Principal
```text
🚀 Chatbot para Análise de PDFs
==========================================
Desenvolvido com Python + OpenAI
Modo Duplo: Com IA e Sem IA

📋 Menu Principal
========================
1 - 🤖 Modo com IA Generativa
2 - 🎯 Modo sem IA (Análise)     ← MEU DIFERENCIAL!
3 - 📁 Listar arquivos
4 - 📝 Ver histórico
5 - ❌ Sair
```
🎯 Modo Sem IA - Exemplo de Uso
```text
🎯 Modo Sem IA - documento_exemplo.txt
==================================================
1 - 📊 Resumo do documento
2 - 🔍 Buscar palavra
3 - 🔑 Palavras-chave
4 - 📈 Estatísticas
5 - ⚖️ Comparar palavras
6 - 📄 Ver metadados
7 - 💾 Exportar análise
8 - 🔙 Voltar
```

🔍 Sobre IA Generativa
A IA funciona muito melhor quando recebe trechos relevantes do documento

É importante limitar o contexto para não exceder os tokens da API

Prompts bem estruturados fazem total diferença na qualidade das respostas

📊 Sobre Análise de Texto
Densidade léxica é uma métrica legal para avaliar a complexidade do texto

Palavras que aparecem só uma vez geralmente são termos técnicos importantes

A média de palavras por sentença diz muito sobre a legibilidade

🎯 Sobre Acessibilidade
Muita gente não tem condições de pagar por APIs caras

Ferramentas de análise local e gratuita são super valorizadas

Oferecer múltiplas opções torna o software mais democrático

📈 Possibilidades Futuras
📚 Suporte a Múltiplos Documentos — Analisar vários PDFs juntos

🌐 Interface Web — Versão online acessível pelo navegador

🔗 Mais APIs de IA — Integrar com Claude, Gemini, etc.

📱 Aplicativo Mobile — Versão para celular

👥 Colaboração — Compartilhar análises com outras pessoas

## 👨‍💻 Sobre o Desenvolvedor
Patric Oliveira
Estudante de programação apaixonado por criar soluções acessíveis e úteis.

🌐 Portfolio: https://patricoliveira.com.br

## 🎉 Conclusão

Cara, desenvolver esse projeto foi uma experiência incrível. Consegui **atender todos os requisitos** que a DIO pediu no desafio, mas o que mais me deixou animado foi ter ido **além do básico**. Olha só o que consegui demonstrar com esse projeto:

✅ **Minha habilidade técnica** - Mostrei que domino Python e consigo trabalhar com processamento de texto de verdade  
✅ **Pensamento crítico** - Identifiquei que muita gente não teria acesso por causa do custo das APIs  
✅ **Criatividade na prática** - Desenvolvi uma solução alternativa que resolve o problema  
✅ **Compromisso com a comunidade** - Garanti que o conhecimento fique acessível pra todo mundo

O **Modo Sem IA** não era nada obrigatório, mas eu pensei que, vamos criar algo que possa ser moldado para uso pessoal, empresarial ou como quiser. Foi minha forma de garantir que **tecnologia de qualidade** esteja disponível tanto pra quem quer usar em casa, estudando, quanto pra pequenas empresas que precisam de uma solução sem gastar fortunas.No final, é bom saber que é um projeto que pode ter possibilidade de adicionar inúmeras melhorias, em ambas as funcionalidades.
