import re
from dataclasses import dataclass

from objetos import Personagem


@dataclass
class DadosProcessados:
    personagem_alvo: Personagem
    trocas_disponiveis: list[Personagem]

    def to_dict(self) -> dict[str, dict[str, int | str] | list[dict[str, int | str]]]:
        return {
            "personagem_alvo": self.personagem_alvo.to_dict(),
            "trocas_disponiveis": [p.to_dict() for p in self.trocas_disponiveis],
        }


class PersonegemParser:
    PRADRAO_LINHA: re.Pattern[str] = re.compile(
        r"^#(\d+) - ([^|]+?)(?: \|? [^ |]+ )?(\d+) ka"
    )

    @classmethod
    def parse(cls, linha: str) -> Personagem | None:
        if not (match := cls.PRADRAO_LINHA.search(linha.strip())):
            return None
        return Personagem(
            rank=int(match.group(1)), nome=match.group(2), kakera=int(match.group(3))
        )


class ProcessadorLista:
    def __init__(self, parser: PersonegemParser) -> None:
        self.parser: PersonegemParser = parser

    def converterLista(self, mudae: str) -> DadosProcessados:
        with open(file=mudae, mode="r", encoding="utf-8") as file:
            linhas: list[str] = [linha for linha in file if linha.strip()]

        if not linhas:
            raise ValueError("Arquivo vazio.")

        alvo: Personagem | None = self.parser.parse(linhas[0])
        if not alvo:
            raise ValueError("Primeira linha invalida.")

        trocas: list[Personagem] = [
            personagem
            for linha in linhas[1:]
            if (personagem := self.parser.parse(linha))
        ]

        return DadosProcessados(alvo, trocas)


# teste = ProcessadorLista(PersonegemParser()).converterLista("mudae.txt")
# print(teste)
