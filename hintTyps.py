from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Personagem:
    rank: int
    nome: str
    kakera: int
    extra: str = ""

    def __str__(self):
        if self.extra:
            return f"#{self.rank} - {self.nome} | {self.extra} · {self.kakera:,} ka"
        return f"#{self.rank} - {self.nome} · {self.kakera:,} ka"

    def to_dict(self) -> dict[str, int | str]:
        return {
            "rank": self.rank,
            "nome": self.nome,
            "kakera": self.kakera
        }

# =============================================
# TIPAGENS
# ============================================
class PersonagemJSON(TypedDict):
    rank: int
    nome: str
    kakera: int

class ConfiguracoesJSON(TypedDict):
    max_personagens_por_troca: int

class DadosJSON(TypedDict):
    personagem_alvo: PersonagemJSON
    trocas_disponiveis: list[PersonagemJSON]

class MelhorTroca(TypedDict):
    dado: Personagem
    recebido: list[Personagem]
    kakera_dado: int
    kakera_recebido: int
    diferenca: int
    ganho: int
    top200_recebido: int

class ResultadoAnalise(TypedDict):
    alvo: Personagem
    melhor_troca: MelhorTroca | None
    total_trocas: int
