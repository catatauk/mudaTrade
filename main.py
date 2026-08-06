import json
from itertools import combinations
from pathlib import Path

from objetos import LoadConfig, MelhorTroca, Personagem, ResultadoAnalise
from parser import DadosProcessados, PersonegemParser, ProcessadorLista


# ============================================
# REGRAS
# ============================================
def eh_top_200(personagem: Personagem) -> bool:
    return personagem.rank <= 200

def rank_valido(rank1: int, rank2: int) -> bool:
    if rank1 > 4000 and rank2 > 4000:
        return True

    melhor_rank: int = min(rank1, rank2)
    pior_rank: int = max(rank1, rank2)

    if melhor_rank <= 200:
        if melhor_rank <= 100:
            limite: int = 200
        else:
            limite = melhor_rank * 2
        return pior_rank <= limite

    if melhor_rank <= 4000:
        return pior_rank <= melhor_rank * 2

    return False

def valor_valido(kakera1: int, kakera2: int) -> bool:
    mais_caro: int = max(kakera1, kakera2)
    menos_caro: int = min(kakera1, kakera2)

    diferenca: int = mais_caro - menos_caro
    limite:float = min(mais_caro * 0.4, 5000)

    return diferenca <= limite

def pode_trocar(item1: Personagem, item2: Personagem) -> bool:
    return valor_valido(item1.kakera, item2.kakera) and rank_valido(item1.rank, item2.rank)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def soma_kakera(personagens: list[Personagem]) -> int:
    return sum(p.kakera for p in personagens)

def count_top200(personagens: list[Personagem]) -> int:
    return sum(1 for p in personagens if eh_top_200(p))

# ============================================
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ============================================
def encontrar_melhor_troca(personagem_alvo: Personagem, lista_trocas: list[Personagem]) -> tuple[list[Personagem], Personagem] | None:
    melhores_resultados:list[tuple[list[Personagem],Personagem]] = []
    lista_exclusao: list[str] = LoadConfig.from_toml(Path("config.toml")).disable_list.waifus
    lista_trocas_filtrada: list[Personagem] = [p for p in lista_trocas if p.nome not in lista_exclusao]

    for n in range(1, min(5, len(lista_trocas_filtrada) + 1)):
        for combo in combinations(lista_trocas_filtrada, n):
            lista_multiplos: list[Personagem] = list(combo)

            if count_top200(lista_multiplos) > 1:
                continue

            if not any(rank_valido(personagem_alvo.rank, p.rank) for p in lista_multiplos):
                continue

            kakera_multiplos: int = soma_kakera(lista_multiplos)
            if not valor_valido(kakera_multiplos, personagem_alvo.kakera):
                continue

            melhores_resultados.append((lista_multiplos, personagem_alvo))

    if not melhores_resultados:
        return None

    melhores_resultados.sort(key=lambda x: abs(soma_kakera(x[0]) - x[1].kakera))
    return melhores_resultados[0]

# ============================================
# CARREGAR E ANALISAR JSON
# ============================================
def carregar_json(mudae_file: str) -> DadosProcessados:
    return ProcessadorLista(PersonegemParser()).converterLista(mudae_file)


def analisar_trocas(data: DadosProcessados) -> ResultadoAnalise:
    # Cria personagem alvo
    alvo_data: Personagem = data.personagem_alvo
    alvo:Personagem = Personagem(
        rank = alvo_data.rank,
        nome=alvo_data.nome,
        kakera=alvo_data.kakera
    )

    # Cria lista de trocas
    trocas: list[Personagem] = []
    for p in data.trocas_disponiveis:
        trocas.append(Personagem(
            rank=p.rank,
            nome=p.nome,
            kakera=p.kakera
        ))

    # Analisa
    resultado: tuple[list[Personagem], Personagem] | None = encontrar_melhor_troca(alvo, trocas)

    if resultado:
        multiplos, dado = resultado
        kakera_recebido: int = soma_kakera(multiplos)

        return {
            'alvo': alvo,
            'melhor_troca': {
                'dado': dado,
                'recebido': multiplos,
                'kakera_dado': dado.kakera,
                'kakera_recebido': kakera_recebido,
                'diferenca': abs(dado.kakera - kakera_recebido),
                'ganho': kakera_recebido - dado.kakera,
                'top200_recebido': count_top200(multiplos)
            },
            'total_trocas': len(trocas)
        }
    else:
        return {
            'alvo': alvo,
            'melhor_troca': None,
            'total_trocas': len(trocas)
        }

# ============================================
# EXIBIR RESULTADOS
# ============================================
def exibir_resultados(analise: ResultadoAnalise):
    mlist: str = ""
    print("=" * 70)
    print("🎯 PERSONAGEM ALVO (O QUE VOCÊ DÁ):")
    print(f"  {analise['alvo']}")

    print("\n" + "=" * 70)
    print(f"📊 Total de trocas analisadas: {analise['total_trocas']}")

    if analise['melhor_troca']:
        melhor: MelhorTroca = analise['melhor_troca']

        print("\n✅ MELHOR TROCA ENCONTRADA:")
        print("\n  Você DÁ (1 personagem):")
        print(f"    • {melhor['dado']}")

        print(f"\n  Você RECEBE ({len(melhor['recebido'])} personagens):")
        for p in melhor['recebido']:
            print(f"    • {p}")
            mlist += f"{p.nome} $ "
        print(f"\n    >> {mlist[:-2]}")
        print("\n  📊 RESUMO:")
        print(f"    Kakera dado: {melhor['kakera_dado']:,} ka")
        print(f"    Kakera recebido: {melhor['kakera_recebido']:,} ka")
        print(f"    Diferença: {melhor['diferenca']:,} ka")

        if melhor['ganho'] > 0:
            print(f"    📈 VOCÊ GANHA +{melhor['ganho']:,} ka!")
        elif melhor['ganho'] < 0:
            print(f"    📉 VOCÊ PERDE {abs(melhor['ganho']):,} ka")
        else:
            print("    ⚖️ TROCA EQUILIBRADA (mesmo kakera)")

        print(f"    Top 200 no lado recebido: {melhor['top200_recebido']}")
    else:
        print("\n❌ NENHUMA TROCA VÁLIDA ENCONTRADA")

# ============================================
# MAIN
# ============================================
def main():
    try:
        # Carrega o JSON
        data: DadosProcessados = carregar_json("mudae.txt")

        # Analisa as trocas
        analise: ResultadoAnalise = analisar_trocas(data)

        # Exibe os resultados
        exibir_resultados(analise)

    except FileNotFoundError as e:
        print(f"❌ ERRO: Arquivo não encontrado: {e}")
    except KeyError as e:
        print(f"❌ ERRO: Campo obrigatório faltando no JSON: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ ERRO: JSON inválido: {e}")

if __name__ == "__main__":
    main()
