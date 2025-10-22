# -*- coding: utf-8 -*-
import os
import re
import json
import statistics


#Função para ordenar os arquivos numericamente
def natural_sort_key(texto):
    import re
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', texto)]

#Análise léxica
def extrair_palavras(texto):
    """Extrai palavras com pelo menos 3 caracteres (inclui acentos)."""
    if not texto or not texto.strip():
        return []
    return re.findall(r'\b[a-zA-ZÀ-ÿ]{3,}\b', texto.lower())

def calcular_wl(texto):
    #Comprimento médio das palavras
    palavras = extrair_palavras(texto)
    if not palavras:
        return 0.0
    total_caracteres = sum(len(p) for p in palavras)
    return total_caracteres / len(palavras)

def calcular_ld(texto):
    #Diversidade lexical = tipos/tokens
    palavras = extrair_palavras(texto)
    if not palavras:
        return 0.0
    tipos = len(set(palavras))
    tokens = len(palavras)
    return tipos / tokens if tokens > 0 else 0.0

def calcular_fr(texto):
    #Proporção de palavras raras
    palavras = extrair_palavras(texto)
    if not palavras:
        return 0.0
    # Nesse código, uma palavra rara foi considerada como uma palavra com mais de 5 caracteres
    raras = [p for p in palavras if len(p) >= 5]
    return len(raras) / len(palavras)

def calcular_lci(texto, w1=0.3, w2=0.4, w3=0.3):
    """Índice de complexidade lexical combinado."""
    wl = calcular_wl(texto)
    ld = calcular_ld(texto)
    fr = calcular_fr(texto)
    lci = w1 * wl + w2 * ld + w3 * fr
    return lci, wl, ld, fr


# Leitura dos datasets

def processar_data():
    PASTA = "Data"
    if not os.path.isdir(PASTA):
        print(f"Pasta 'Data' não encontrada.")
        return []

    subpastas = [d for d in os.listdir(PASTA) if os.path.isdir(os.path.join(PASTA, d))]
    subpastas.sort(key=natural_sort_key)
    
    lcis = []
    print("COMANDOS ORIGINAIS (Data)")
    for subpasta in subpastas:
        xml_path = os.path.join(PASTA, subpasta, "prompt.xml")
        if not os.path.isfile(xml_path):
            continue

        try:
            with open(xml_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
            match = re.search(r"<body>(.*?)</body>", conteudo, re.DOTALL | re.IGNORECASE)
            if not match:
                continue
            body = match.group(1).strip()
            if not body:
                continue

            lci, wl, ld, fr = calcular_lci(body)
            if lci > 0:
                print(f"{subpasta:<20} - LCI: {lci:.4f} (WL={wl:.2f}, LD={ld:.4f}, FR={fr:.4f})")
                lcis.append(lci)
        except:
            continue

    return lcis

def processar_qwenmax():
    PASTA = "QwenMax"
    if not os.path.isdir(PASTA):
        print(f"Pasta 'QwenMax' não encontrada.")
        return []

    json_files = [f for f in os.listdir(PASTA) if f.endswith(".json")]
    json_files.sort(key=natural_sort_key)
    
    lcis = []
    print("COMANDOS SINTÉTICOS (QwenMax)")
    
    for arquivo in json_files:
        caminho = os.path.join(PASTA, arquivo)
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            
            if "comando_tematico" in dados and isinstance(dados["comando_tematico"], dict):
                comandos = list(dados["comando_tematico"].values())
            elif isinstance(dados, dict) and all(isinstance(v, str) for v in dados.values()):
                comandos = list(dados.values())
            elif isinstance(dados, list):
                comandos = dados
            else:
                continue

            for i, cmd in enumerate(comandos):
                if not isinstance(cmd, str):
                    continue
                cmd = cmd.strip()
                if not cmd:
                    continue
                lci, wl, ld, fr = calcular_lci(cmd)
                if lci > 0:
                    nome_exibicao = f"{arquivo}#{i}"
                    print(f"{nome_exibicao:<20} → LCI: {lci:.4f} (WL={wl:.2f}, LD={ld:.4f}, FR={fr:.4f})")
                    lcis.append(lci)

        except Exception as e:
            continue

    return lcis


# Execução principal
def main():
    print("Métrica de Complexidade Lexical (LCI)")
    
    lcis_originais = processar_data()
    lcis_sinteticos = processar_qwenmax()

    # --- Originais ---
    print("\n" + "="*70)
    print("Dataset Data")
    print("="*70)
    if lcis_originais:
        media = statistics.mean(lcis_originais)
        desvio = statistics.stdev(lcis_originais) if len(lcis_originais) > 1 else 0.0
        print(f"Média do LCI:   {media:.4f}")
        print(f"Desvio padrão:  {desvio:.4f}")
    else:
        print("Nenhum comando original processado.")

    # --- Sintéticos ---
    print("\n" + "="*70)
    print("Dataset QwenMax")
    print("="*70)
    if lcis_sinteticos:
        media = statistics.mean(lcis_sinteticos)
        desvio = statistics.stdev(lcis_sinteticos) if len(lcis_sinteticos) > 1 else 0.0
        print(f"Média do LCI:   {media:.4f}")
        print(f"Desvio padrão:  {desvio:.4f}")
    else:
        print("Nenhum comando sintético processado.")
if __name__ == "__main__":
    main()
