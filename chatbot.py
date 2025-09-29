import os
import re
import json
from datetime import datetime
from collections import Counter
import statistics
# vou tentar importar essas bibliotecas de inicio 
try:
    import nltk
    from PyPDF2 import PdfReader
except ImportError as e:
    print(f"❌ Falta alguma biblioteca: {e}")
    print("💡 Tenta: pip install nltk PyPDF2")
    exit()

# Configurações - vou deixar aqui em cima pra ficar fácil de achar
PASTA_INPUTS = "./inputs/"
ARQUIVO_HISTORICO = "historico_conversas.json" 
ARQUIVO_CHAVES = "api_keys.json"
MAX_PREVIEW = 300
CONTEXTO_BUSCA = 100

# Criar pasta se não existir - isso sempre esqueço
if not os.path.exists(PASTA_INPUTS):
    os.makedirs(PASTA_INPUTS)
    print(f"📁 Criada pasta {PASTA_INPUTS}")

# Essa parte do NLTK é meio chata, mas vamos la
def setup_nltk():
    """Tenta configurar o NLTK, se der erro, paciência"""
    try:
        nltk.data.find('tokenizers/punkt')
    except:
        try:
            print("📥 Baixando recursos do NLTK...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except Exception as e:
            print(f"⚠️  Deu pau no NLTK: {e}")
            return False
    return True

# Chama a função - se não rodar, o programa continua mesmo assim
setup_nltk()

# Aqui eu criei um fallback pro quando o NLTK não funciona
# Fiz na mão mesmo, não sei se tá 100% mas funciona
class TokenizadorManual:
    @staticmethod
    def dividir_sentencas(texto):
        # Divisão simples por pontuação
        partes = re.split(r'[.!?]+', texto)
        return [p.strip() for p in partes if p.strip()]
    
    @staticmethod 
    def extrair_palavras(texto):
        texto = texto.lower()
        palavras = re.findall(r'\b\w+\b', texto)
        # Filtro palavras muito curtas e stopwords manuais
        stopwords = {'o', 'a', 'e', 'de', 'do', 'da', 'em', 'um', 'uma', 'para', 'com', 'os', 'as', 'se', 'que', 'por'}
        return [p for p in palavras if len(p) > 2 and p not in stopwords]

# Classe pra gerenciar as chaves - salva num JSON
class GerenciadorChaves:
    def __init__(self):
        self.arquivo = ARQUIVO_CHAVES
        self.chaves = self.carregar_chaves()
    
    def carregar_chaves(self):
        # Tenta carregar, se não existir, cria um novo
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"openai": ""}
        except Exception as e:
            print(f"❌ Erro ao carregar chaves: {e}")
            return {"openai": ""}
    
    def salvar_chaves(self):
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump(self.chaves, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False
    
    def get_chave_openai(self):
        return self.chaves.get("openai", "").strip()
    
    def set_chave_openai(self, chave):
        chave = chave.strip()
        if not chave:
            print("❌ Chave vazia!")
            return False
            
        self.chaves["openai"] = chave
        if self.salvar_chaves():
            print("✅ Chave salva com sucesso!")
            # Joga pra variável de ambiente também
            os.environ["OPENAI_API_KEY"] = chave
            return True
        else:
            print("❌ Falha ao salvar chave")
            return False
    
    def remover_chave(self):
        self.chaves["openai"] = ""
        if self.salvar_chaves():
            print("✅ Chave removida!")
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            return True
        return False
    
    def mostrar_status(self):
        chave = self.get_chave_openai()
        if chave:
            status = "✅ Configurada"
            # Mostra só pedaços da chave por segurança
            masked = f"{chave[:4]}...{chave[-4:]}"
        else:
            status = "❌ Não configurada"
            masked = "N/A"
        
        print(f"\n🔑 Status das Chaves:")
        print(f"OpenAI: {status}")
        print(f"Chave: {masked}")

# Classe pra lidar com arquivos PDF/TXT
class GerenciadorArquivos:
    @staticmethod
    def listar_arquivos():
        """Lista os arquivos na pasta inputs"""
        arquivos = []
        try:
            for arquivo in os.listdir(PASTA_INPUTS):
                if arquivo.lower().endswith((".pdf", ".txt")):
                    caminho_completo = os.path.join(PASTA_INPUTS, arquivo)
                    tamanho = os.path.getsize(caminho_completo) / 1024  # KB
                    
                    arquivos.append({
                        'nome': arquivo,
                        'caminho': caminho_completo,
                        'tamanho_kb': round(tamanho, 2),
                        'extensao': os.path.splitext(arquivo)[1].lower()
                    })
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
        
        if not arquivos:
            print("📁 Nenhum arquivo PDF ou TXT encontrado na pasta 'inputs'")
            
        return arquivos
    
    @staticmethod
    def carregar_arquivo(nome_arquivo):
        """Carrega um arquivo PDF ou TXT"""
        caminho = os.path.join(PASTA_INPUTS, nome_arquivo)
        
        try:
            if nome_arquivo.lower().endswith(".pdf"):
                # Processar PDF
                leitor = PdfReader(caminho)
                texto_completo = ""
                
                for num_pagina, pagina in enumerate(leitor.pages, 1):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += f"\n--- Página {num_pagina} ---\n{texto_pagina}"
                
                # Metadados do PDF
                metadados = {
                    'total_paginas': len(leitor.pages),
                    'autor': leitor.metadata.get('/Author', 'Não informado'),
                    'titulo': leitor.metadata.get('/Title', nome_arquivo),
                    'criacao': leitor.metadata.get('/CreationDate', 'Não informado')
                }
                
            else:
                # Processar TXT
                with open(caminho, "r", encoding="utf-8") as f:
                    texto_completo = f.read()
                
                metadados = {
                    'total_paginas': 1,
                    'autor': 'Não informado',
                    'titulo': nome_arquivo,
                    'criacao': 'Não informado'
                }
            
            # Limpar o texto - tirar espaços extras
            texto_limpo = re.sub(r'\s+', ' ', texto_completo).strip()
            palavras = texto_limpo.split()
            
            # Estatísticas básicas
            stats = {
                'total_palavras': len(palavras),
                'total_caracteres': len(texto_limpo),
                'palavras_unicas': len(set(palavras))
            }
            
            return {
                'texto': texto_limpo,
                'texto_original': texto_completo,
                'metadados': metadados,
                'estatisticas': stats,
                'nome_arquivo': nome_arquivo
            }
            
        except Exception as e:
            print(f"❌ Erro ao carregar {nome_arquivo}: {e}")
            return None

# Histórico de conversas
class HistoricoConversas:
    def __init__(self):
        self.arquivo = ARQUIVO_HISTORICO
        self.dados = self.carregar()
    
    def carregar(self):
        try:
            with open(self.arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"conversas": []}
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {e}")
            return {"conversas": []}
    
    def salvar(self, arquivo, pergunta, resposta, modo):
        nova_entrada = {
            "data": datetime.now().isoformat(),
            "arquivo": arquivo,
            "modo": modo,
            "pergunta": pergunta,
            "resposta": resposta
        }
        
        self.dados["conversas"].append(nova_entrada)
        
        try:
            with open(self.arquivo, "w", encoding="utf-8") as f:
                json.dump(self.dados, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Não consegui salvar no histórico: {e}")
    
    def mostrar(self):
        if not self.dados["conversas"]:
            print("📝 Nenhuma conversa no histórico ainda.")
            return
        
        print(f"\n📋 Histórico de Conversas:")
        print("=" * 70)
        
        # Mostra só as últimas 8 pra não ficar enorme
        for i, conversa in enumerate(self.dados["conversas"][-8:], 1):
            data = datetime.fromisoformat(conversa["data"]).strftime("%d/%m %H:%M")
            print(f"{i}. [{data}] {conversa['modo']} - {conversa['arquivo']}")
            print(f"   Pergunta: {conversa['pergunta'][:80]}...")
            print(f"   Resposta: {conversa['resposta'][:80]}...")
            print("-" * 70)

# Classe pra analisar textos - essa foi a mais trabalhosa
class AnalisadorTexto:
    def __init__(self, texto):
        self.texto = texto
        self.texto_lower = texto.lower()
        self.sentencas = self._dividir_em_sentencas()
        self.palavras = self._extrair_palavras_uteis()
    
    def _dividir_em_sentencas(self):
        # Tenta usar NLTK primeiro
        try:
            from nltk.tokenize import sent_tokenize
            return sent_tokenize(self.texto)
        except:
            # Se não der, usa o método manual
            return TokenizadorManual.dividir_sentencas(self.texto)
    
    def _extrair_palavras_uteis(self):
        # Tenta NLTK primeiro
        try:
            from nltk.tokenize import word_tokenize
            from nltk.corpus import stopwords
            
            stop_pt = set(stopwords.words('portuguese'))
            stop_en = set(stopwords.words('english'))
            todas_stopwords = stop_pt.union(stop_en)
            
            palavras = word_tokenize(self.texto_lower)
            # Filtra: só palavras com 3+ letras e que não são stopwords
            return [p for p in palavras if p.isalpha() and len(p) >= 3 and p not in todas_stopwords]
            
        except:
            # Fallback pro quando NLTK falha
            return TokenizadorManual.extrair_palavras(self.texto)
    
    def mostrar_resumo(self):
        print(f"\n📊 Resumo do Documento")
        print("=" * 50)
        
        print(f"📝 Total de sentenças: {len(self.sentencas)}")
        print(f"🔤 Total de palavras úteis: {len(self.palavras)}")
        print(f"📈 Palavras únicas: {len(set(self.palavras))}")
        
        if self.palavras:
            densidade = len(set(self.palavras)) / len(self.palavras)
            print(f"📏 Densidade léxica: {densidade:.1%}")
        
        # Mostra preview das páginas se tiver marcação de páginas
        partes = self.texto.split('--- Página')
        if len(partes) > 1:
            print(f"\n📄 Preview por página:")
            for i, pagina in enumerate(partes[1:6], 1):  # Mostra só as 5 primeiras
                linhas = pagina.split('\n')
                if len(linhas) > 1:
                    conteudo = ' '.join(linhas[1:])
                    preview = conteudo[:MAX_PREVIEW]
                    if len(conteudo) > MAX_PREVIEW:
                        preview += "..."
                    print(f"   📖 Página {i}: {preview}")
    
    def buscar_palavra(self, palavra):
        print(f"\n🔍 Buscando: '{palavra}'")
        print("=" * 50)
        
        # Regex pra encontrar a palavra com contexto
        padrao = re.compile(f".{{0,{CONTEXTO_BUSCA}}}{re.escape(palavra)}.{{0,{CONTEXTO_BUSCA}}}", re.IGNORECASE)
        resultados = padrao.findall(self.texto)
        
        if resultados:
            print(f"✅ Encontrado {len(resultados)} vezes:")
            for i, trecho in enumerate(resultados[:6], 1):  # Mostra só 6 resultados
                trecho_limpo = re.sub(r'\s+', ' ', trecho).strip()
                print(f"\n{i}. ...{trecho_limpo}...")
            
            if len(resultados) > 6:
                print(f"\n📎 ... e mais {len(resultados) - 6} resultados")
        else:
            print("❌ Palavra não encontrada")
    
    def analisar_palavras_chave(self):
        if not self.palavras:
            print("❌ Nada para analisar")
            return
        
        print(f"\n🔑 Análise de Palavras-Chave")
        print("=" * 50)
        
        # Conta frequência das palavras
        contador = Counter(self.palavras)
        top_15 = contador.most_common(15)
        
        print("📊 Palavras mais frequentes:")
        for palavra, freq in top_15:
            print(f"   {palavra}: {freq}x")
        
        # Palavras longas (geralmente termos técnicos)
        palavras_longas = [p for p in self.palavras if len(p) > 8]
        if palavras_longas:
            contador_longas = Counter(palavras_longas)
            print(f"\n🔬 Termos técnicos (mais de 8 letras):")
            for palavra, freq in contador_longas.most_common(5):
                print(f"   {palavra}: {freq}x")
    
    def mostrar_estatisticas(self):
        if not self.palavras or not self.sentencas:
            print("❌ Dados insuficientes")
            return
        
        print(f"\n📈 Estatísticas Detalhadas")
        print("=" * 50)
        
        try:
            palavras_por_sentenca = [len(s.split()) for s in self.sentencas]
            letras_por_palavra = [len(p) for p in self.palavras]
            
            print(f"📝 Média de palavras por sentença: {statistics.mean(palavras_por_sentenca):.1f}")
            print(f"🔠 Média de letras por palavra: {statistics.mean(letras_por_palavra):.2f}")
            print(f"📏 Sentença mais longa: {max(palavras_por_sentenca)} palavras")
            print(f"📏 Sentença mais curta: {min(palavras_por_sentenca)} palavras")
        except:
            print("❌ Erro ao calcular estatísticas")
        
        # Palavras que aparecem só uma vez
        contador = Counter(self.palavras)
        unicas = sum(1 for count in contador.values() if count == 1)
        print(f"🎯 Palavras únicas (só uma ocorrência): {unicas}")
    
    def comparar_palavras(self, palavra1, palavra2):
        freq1 = len(re.findall(re.escape(palavra1), self.texto_lower))
        freq2 = len(re.findall(re.escape(palavra2), self.texto_lower))
        
        print(f"\n⚖️ Comparando:")
        print("=" * 40)
        print(f"'{palavra1}': {freq1} ocorrências")
        print(f"'{palavra2}': {freq2} ocorrências")
        
        if freq1 > freq2:
            print(f"✅ '{palavra1}' é mais frequente")
        elif freq2 > freq1:
            print(f"✅ '{palavra2}' é mais frequente")
        else:
            print(f"⚡ São igualmente frequentes")
    
    def exportar_analise(self, nome_arquivo):
        dados = {
            "arquivo": nome_arquivo,
            "data_analise": datetime.now().isoformat(),
            "estatisticas": {
                "sentencas": len(self.sentencas),
                "palavras_uteis": len(self.palavras),
                "palavras_unicas": len(set(self.palavras)),
                "densidade_lexica": len(set(self.palavras)) / len(self.palavras) if self.palavras else 0
            },
            "top_palavras": dict(Counter(self.palavras).most_common(20))
        }
        
        nome_saida = f"analise_{nome_arquivo.split('.')[0]}.json"
        try:
            with open(nome_saida, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            print(f"✅ Análise salva em: {nome_saida}")
        except Exception as e:
            print(f"❌ Erro ao exportar: {e}")

# ========== MODO SEM IA ==========
def executar_modo_sem_ia(dados_arquivo):
    if not dados_arquivo or not dados_arquivo.get('texto'):
        print("❌ Problema ao carregar o arquivo")
        return
    
    analisador = AnalisadorTexto(dados_arquivo['texto'])
    
    while True:
        print(f"\n🎯 Modo Sem IA - {dados_arquivo['nome_arquivo']}")
        print("=" * 50)
        print("1 - 📊 Resumo do documento")
        print("2 - 🔍 Buscar palavra")
        print("3 - 🔑 Palavras-chave")
        print("4 - 📈 Estatísticas")
        print("5 - ⚖️ Comparar palavras")
        print("6 - 📄 Ver metadados")
        print("7 - 💾 Exportar análise")
        print("8 - 🔙 Voltar")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            analisador.mostrar_resumo()
        elif opcao == "2":
            palavra = input("Digite a palavra para buscar: ").strip()
            if palavra:
                analisador.buscar_palavra(palavra)
        elif opcao == "3":
            analisador.analisar_palavras_chave()
        elif opcao == "4":
            analisador.mostrar_estatisticas()
        elif opcao == "5":
            p1 = input("Primeira palavra: ").strip()
            p2 = input("Segunda palavra: ").strip()
            if p1 and p2:
                analisador.comparar_palavras(p1, p2)
        elif opcao == "6":
            print(f"\n📋 Metadados do arquivo:")
            for chave, valor in dados_arquivo['metadados'].items():
                print(f"   {chave}: {valor}")
            print(f"\n📊 Estatísticas básicas:")
            for chave, valor in dados_arquivo['estatisticas'].items():
                print(f"   {chave}: {valor}")
        elif opcao == "7":
            analisador.exportar_analise(dados_arquivo['nome_arquivo'])
        elif opcao == "8":
            break
        else:
            print("❌ Opção inválida")
        
        input("\nPressione Enter para continuar...")

# ========== MODO COM IA ==========
def gerenciar_chaves(gerenciador_chaves):
    while True:
        print(f"\n🔑 Gerenciar Chaves API")
        print("=" * 40)
        gerenciador_chaves.mostrar_status()
        print("\n1 - 📝 Adicionar/Atualizar Chave OpenAI")
        print("2 - 🗑️  Remover Chave OpenAI")
        print("3 - 🔙 Voltar")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == "1":
            print("\n📝 Configurar Chave da OpenAI")
            print("💡 Obtenha em: https://platform.openai.com/api-keys")
            
            chave_atual = gerenciador_chaves.get_chave_openai()
            if chave_atual:
                print(f"Chave atual: {chave_atual[:4]}...{chave_atual[-4:]}")
                confirmar = input("Substituir? (s/N): ").lower()
                if confirmar != 's':
                    continue
            
            nova_chave = input("Digite sua nova chave: ").strip()
            if nova_chave:
                gerenciador_chaves.set_chave_openai(nova_chave)
        
        elif opcao == "2":
            if gerenciador_chaves.get_chave_openai():
                confirmar = input("Tem certeza que quer remover a chave? (s/N): ").lower()
                if confirmar == 's':
                    gerenciador_chaves.remover_chave()
            else:
                print("❌ Nenhuma chave para remover")
        
        elif opcao == "3":
            break
        
        else:
            print("❌ Opção inválida")
        
        input("\nEnter para continuar...")

def executar_modo_com_ia(dados_arquivo, historico, gerenciador_chaves):
    # Verifica se openai está instalado
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ Biblioteca OpenAI não encontrada")
        print("💡 Instale com: pip install openai")
        return
    
    # Pega a chave
    chave = gerenciador_chaves.get_chave_openai()
    if not chave:
        print("❌ Chave da OpenAI não configurada")
        print("💡 Configure sua chave primeiro no menu de gerenciamento")
        return
    
    # Tenta conectar
    try:
        cliente = OpenAI(api_key=chave)
    except Exception as e:
        print(f"❌ Erro ao configurar OpenAI: {e}")
        return
    
    print(f"\n🤖 Modo Com IA - {dados_arquivo['nome_arquivo']}")
    print("=" * 50)
    print("💡 Faça perguntas sobre o documento")
    print("💡 Digite 'sair' para voltar")
    print("💡 Digite 'menu' para voltar ao menu anterior")
    
    while True:
        pergunta = input("\n🎯 Sua pergunta: ").strip()
        
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            break
        
        if pergunta.lower() == 'menu':
            return
        
        if not pergunta:
            print("❌ Pergunta não pode estar vazia")
            continue
        
        # Prepara o contexto - não pode ser muito grande
        contexto = dados_arquivo['texto']
        if len(contexto) > 4000:
            # Pega começo e fim do texto
            contexto = contexto[:2000] + " [...] " + contexto[-2000:]
        
        prompt = f"""
        Com base no seguinte documento, responda de forma precisa:

        DOCUMENTO:
        {contexto}

        PERGUNTA: {pergunta}

        Responda em português, sendo direto e baseado apenas no conteúdo do documento.
        Se a informação não estiver no documento, diga claramente.
        """
        
        try:
            print("⏳ Processando sua pergunta...")
            resposta = cliente.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            resposta_texto = resposta.choices[0].message.content.strip()
            print(f"\n🤖 Resposta:\n{resposta_texto}")
            
            # Salva no histórico
            historico.salvar(
                dados_arquivo['nome_arquivo'], 
                pergunta, 
                resposta_texto, 
                "Modo com IA"
            )
            
        except Exception as e:
            print(f"❌ Erro ao chamar a API: {e}")
            print("💡 Verifique sua chave da API e conexão com internet")

def menu_modo_com_ia(gerenciador_chaves, historico):
    while True:
        print(f"\n🤖 Modo Com IA Generativa")
        print("=" * 40)
        gerenciador_chaves.mostrar_status()
        print("\n1 - 📄 Selecionar arquivo e conversar")
        print("2 - 🔑 Gerenciar chaves API")
        print("3 - 🔙 Voltar ao menu principal")
        
        opcao = input("\nEscolha: ").strip()
        
        if opcao == "1":
            gerenciador = GerenciadorArquivos()
            arquivos = gerenciador.listar_arquivos()
            if not arquivos:
                continue
            
            print(f"\n📂 Arquivos disponíveis:")
            for i, arq in enumerate(arquivos, 1):
                print(f"{i}. {arq['nome']} ({arq['tamanho_kb']} KB)")
            
            try:
                escolha = int(input(f"\nEscolha um arquivo (1-{len(arquivos)}): ")) - 1
                if 0 <= escolha < len(arquivos):
                    dados = gerenciador.carregar_arquivo(arquivos[escolha]['nome'])
                    if dados:
                        executar_modo_com_ia(dados, historico, gerenciador_chaves)
                else:
                    print("❌ Escolha inválida")
            except ValueError:
                print("❌ Por favor, digite um número")
        
        elif opcao == "2":
            gerenciar_chaves(gerenciador_chaves)
        
        elif opcao == "3":
            break
        
        else:
            print("❌ Opção inválida")
        
        input("\nPressione Enter para continuar...")

# ========== PROGRAMA PRINCIPAL ==========
def main():
    historico = HistoricoConversas()
    gerenciador_chaves = GerenciadorChaves()
    
    print("🚀 Chatbot para Análise de PDFs")
    print("==========================================")
    print("Desenvolvido com Python + OpenAI")
    print("Modo Duplo: Com IA e Sem IA")
    
    while True:
        print("\n📋 Menu Principal")
        print("========================")
        print("1 - 🤖 Modo com IA Generativa")
        print("2 - 🎯 Modo sem IA (Análise)")
        print("3 - 📁 Listar arquivos")
        print("4 - 📝 Ver histórico")
        print("5 - ❌ Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "5":
            print("\n👋 Obrigado por usar o Chatbot! Até mais!")
            break
        
        elif opcao == "4":
            historico.mostrar()
        
        elif opcao == "3":
            gerenciador = GerenciadorArquivos()
            arquivos = gerenciador.listar_arquivos()
            if arquivos:
                print(f"\n📁 Arquivos disponíveis ({len(arquivos)} encontrados):")
                for i, arq in enumerate(arquivos, 1):
                    print(f"{i}. {arq['nome']} ({arq['tamanho_kb']} KB)")
        
        elif opcao == "2":
            gerenciador = GerenciadorArquivos()
            arquivos = gerenciador.listar_arquivos()
            if not arquivos:
                continue
            
            print(f"\n📂 Selecione um arquivo:")
            for i, arq in enumerate(arquivos, 1):
                print(f"{i}. {arq['nome']} ({arq['tamanho_kb']} KB)")
            
            try:
                escolha = int(input(f"\nEscolha (1-{len(arquivos)}): ")) - 1
                if 0 <= escolha < len(arquivos):
                    dados = gerenciador.carregar_arquivo(arquivos[escolha]['nome'])
                    if dados:
                        executar_modo_sem_ia(dados)
                else:
                    print("❌ Escolha inválida")
            except ValueError:
                print("❌ Por favor, digite um número válido")
        
        elif opcao == "1":
            menu_modo_com_ia(gerenciador_chaves, historico)
        
        else:
            print("❌ Opção inválida, tente novamente")

# Ponto de entrada do programa
if __name__ == "__main__":
    main()