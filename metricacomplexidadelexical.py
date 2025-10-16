import os
import json
import re

PASTA = "QwenMax"

def limpar_texto(texto):
    """Remove pontuação e deixa só palavras."""
    texto = texto.lower()
    # Mantendo caracteres acentuados para o Português
    texto = re.sub(r"[^a-záéíóúàâêôãõç\s]", "", texto) 
    return texto

def calcular_metricas(texto):
    """Calcula WL, LD e FR a partir do texto."""
    texto = limpar_texto(texto)
    palavras = texto.split()
    if not palavras:
        return 0, 0, 0
    total_palavras = len(palavras)
    tipos = set(palavras)
    #Métricas
    WL = sum(len(p) for p in palavras) / total_palavras  #comprimento médio
    LD = len(tipos) / total_palavras                      #diversidade lexical (TTR)
    FR = sum(1 for p in tipos if palavras.count(p) == 1) / total_palavras  #palavras raras
    return WL, LD, FR

def calcular_LCI(WL, LD, FR, pesos=(1/3, 1/3, 1/3)):
    """Calcula o índice composto (LCI). Eles tem o mesmo peso"""
    w1, w2, w3 = pesos
    return w1 * WL + w2 * LD + w3 * FR

# Função auxiliar para a ordenação numérica dos arquivos
def obter_id_numerico(nome_arquivo):
    """Extrai o número inicial do nome do arquivo para ordenar o número dos arquivos de forma certa."""
    match = re.match(r'(\d+)', nome_arquivo)
    if match:
        return int(match.group(1)) 
    return float('inf')

def processar_pasta(caminho_pasta):
    """Percorre todos os arquivos JSON e calcula o Índice de Complexidade Lexical."""
    
    #Verifica se a pasta existe
    if not os.path.isdir(caminho_pasta):
        print(f"ERRO: O diretório '{caminho_pasta}' não existe ou não é uma pasta. Verifique o valor de 'PASTA'.")
        return

    resultados = []
    arquivos_encontrados = [f for f in os.listdir(caminho_pasta) if f.endswith(".json")]
    
    if not arquivos_encontrados:
        print(f"AVISO: A pasta '{caminho_pasta}' não contém arquivos .json.")
        return

    for nome in sorted(arquivos_encontrados, key=obter_id_numerico):
        caminho = os.path.join(caminho_pasta, nome)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            redacao_data = dados.get("redacao")
            texto = "" 

            if isinstance(redacao_data, str):
                texto = redacao_data
                
            elif isinstance(redacao_data, dict):
                
                partes_da_redacao = []
                
                chaves_numericas = sorted(redacao_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
                
                for chave in chaves_numericas:
                    parte = redacao_data.get(chave)
                    if isinstance(parte, str):
                        partes_da_redacao.append(parte)
                
                texto = " ".join(partes_da_redacao)
                
            if not texto:
                #Mensagem de aviso
                print(f"⚠️ {nome}: 'redacao' não pôde ser lida.")
                continue

            WL, LD, FR = calcular_metricas(texto)
            LCI = calcular_LCI(WL, LD, FR)
            resultados.append((nome, WL, LD, FR, LCI))
            
            #print em cada arquivo
            print(f"✅ {nome}: LCI = {LCI:.3f} (WL={WL:.3f}, LD={LD:.3f}, FR={FR:.3f})")

        except Exception as e:
            print(f"⚠️ Erro ao processar {nome}: {e}")

    #Exibe média geral
    if resultados:
        media_LCI = sum(r[4] for r in resultados) / len(resultados)
        print(f"\n Total de arquivos processados: {len(resultados)}")
        #Saída da média
        print(f" Média geral da métrica de Complexidade Lexical (LCI): {media_LCI:.3f}")
    else:
        print("Nenhum arquivo processado.")
        
    print("\n")
    print("LCI: Índice de Complexidade Lexical (Média ponderada de WL, LD e FR)")
    print("WL: Comprimento Médio da Palavra (Word Length)")
    print("LD: Diversidade Lexical (Lexical Diversity / TTR-Type-Token Ratio)")
    print("FR: Frequência de Palavras Raras (Frequency of Rare Words)")
if __name__ == "__main__":
    processar_pasta(PASTA)

