import tomllib
from itertools import combinations
from pathlib import Path
from time import time

from objetos import LoadConfig, MelhorTroca, Personagem, ResultadoAnalise
from parser import DadosProcessados, PersonegemParser, ProcessadorLista


# ===========================================
# CLASSES
# ===========================================
def load_config() -> LoadConfig:
    return LoadConfig.from_toml(Path("config.toml"))


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
    limite: float = min(
        mais_caro * 0.4, min(load_config().user_config.kakera_gap, 5000)
    )

    return diferenca <= limite

def validar_individual(alvo: Personagem, item: Personagem) -> bool:
    #return (item.rank > 4000 or item.rank > alvo.rank and item.kakera < min(alvo.kakera * 1.4, alvo.kakera + 5000))
    if item.kakera < min(alvo.kakera * 1.4, alvo.kakera + 5000):
        if item.rank > 4000 or item.rank > alvo.rank:
            return True
        else:
            return rank_valido(rank1=alvo.rank, rank2=item.rank)
    else:
        return False



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
def encontrar_melhor_troca(
    personagem_alvo: Personagem, lista_trocas: list[Personagem]
) -> tuple[list[Personagem], Personagem] | None:
    primeiro_resultado: list[tuple[list[Personagem], Personagem]] = []
    lista_exclusao: list[str] = load_config().disable_list.waifus
    lista_trocas_filtrada: list[Personagem] = [
        p for p in lista_trocas if p.nome not in lista_exclusao and
        validar_individual(alvo=personagem_alvo, item=p)
    ]
    time_out: float = load_config().user_config.time_out
    time_start: float = time()

    for n in range(1, min(5, len(lista_trocas_filtrada) + 1)):
        for combo in combinations(lista_trocas_filtrada, n):
            lista_multiplos: list[Personagem] = list(combo)

            if time() - time_start > time_out:
                return None

            if count_top200(lista_multiplos) > 1:
                continue

            kakera_multiplos: int = soma_kakera(lista_multiplos)
            if not valor_valido(kakera_multiplos, personagem_alvo.kakera):
                continue

            return (lista_multiplos, personagem_alvo)

    if not primeiro_resultado:
        return None

    primeiro_resultado.sort(key=lambda x: abs(soma_kakera(x[0]) - x[1].kakera))
    return primeiro_resultado[0]


# ============================================
# CARREGAR E ANALISAR DADOS
# ============================================
def carregar_dados(mudae_file: str) -> DadosProcessados:
    return ProcessadorLista(PersonegemParser()).converterLista(mudae_file)


def analisar_trocas(data: DadosProcessados) -> ResultadoAnalise:
    # Cria personagem alvo
    alvo_data: Personagem = data.personagem_alvo
    alvo: Personagem = Personagem(
        rank=alvo_data.rank, nome=alvo_data.nome, kakera=alvo_data.kakera
    )

    # Cria lista de trocas
    trocas: list[Personagem] = []
    for p in data.trocas_disponiveis:
        trocas.append(Personagem(rank=p.rank, nome=p.nome, kakera=p.kakera))

    # Analisa
    resultado: tuple[list[Personagem], Personagem] | None = encontrar_melhor_troca(
        alvo, trocas
    )

    if resultado:
        multiplos, dado = resultado
        kakera_recebido: int = soma_kakera(multiplos)

        return {
            "alvo": alvo,
            "melhor_troca": {
                "dado": dado,
                "recebido": multiplos,
                "kakera_dado": dado.kakera,
                "kakera_recebido": kakera_recebido,
                "diferenca": abs(dado.kakera - kakera_recebido),
                "ganho": kakera_recebido - dado.kakera,
                "top200_recebido": count_top200(multiplos),
            },
            "total_trocas": len(trocas),
        }
    else:
        return {"alvo": alvo, "melhor_troca": None, "total_trocas": len(trocas)}


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

    if analise["melhor_troca"]:
        melhor: MelhorTroca = analise["melhor_troca"]

        print("\n✅ MELHOR TROCA ENCONTRADA:")
        print("\n  Você DÁ (1 personagem):")
        print(f"    • {melhor['dado']}")

        print(f"\n  Você RECEBE ({len(melhor['recebido'])} personagens):")
        for p in melhor["recebido"]:
            print(f"    • {p}")
            mlist += f"{p.nome} $ "
        print(f"\n    >> {mlist[:-2]}")
        print("\n  📊 RESUMO:")
        print(f"    Kakera dado: {melhor['kakera_dado']:,} ka")
        print(f"    Kakera recebido: {melhor['kakera_recebido']:,} ka")
        print(f"    Diferença: {melhor['diferenca']:,} ka")

        if melhor["ganho"] > 0:
            print(f"    📈 VOCÊ GANHA +{melhor['ganho']:,} ka!")
        elif melhor["ganho"] < 0:
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
        # Carrega dados brutos
        data: DadosProcessados = carregar_dados("mudae.txt")

        # Analisa as trocas
        analise: ResultadoAnalise = analisar_trocas(data)

        # Exibe os resultados
        exibir_resultados(analise)

    except FileNotFoundError as e:
        print(f"❌ ERRO: Arquivo não encontrado: {e}")
    except KeyError as e:
        print(f"❌ ERRO: Campo obrigatório faltando: {e}")
    except tomllib.TOMLDecodeError as e:
        print(f"❌ ERRO: Error no arquivo config: {e}")


if __name__ == "__main__":
    main()
