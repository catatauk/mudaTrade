import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict


# ======================================
# DATACLASSES
# ======================================
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
        return {"rank": self.rank, "nome": self.nome, "kakera": self.kakera}


@dataclass
class UserConfigLoad:
    kakera_gap: int
    time_out: float


@dataclass
class DisableListLoad:
    waifus: list[str]


@dataclass
class LoadConfig:
    disable_list: DisableListLoad
    user_config: UserConfigLoad

    @classmethod
    def from_toml(cls, path: Path) -> "LoadConfig":
        with open(file=path, mode="rb") as f:
            data = tomllib.load(f)

        return cls(
            disable_list=(DisableListLoad(waifus=data["disable_list"]["waifus"])),
            user_config=(
                UserConfigLoad(
                    kakera_gap=data["user_conf"]["kakera_gap"],
                    time_out=data["user_conf"]["time_out"],
                )
            ),
        )


# =============================================
# TIPAGENS
# =============================================


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
