import re
from typing import Any

import hintTyps as ht

dados: Any = {"personagem_alvo": {},
    "trocas_disponiveis": []
}

def personagensDict(rank:int, nome:str, kakera:int) -> dict[str, int | str]:
    per = {"rank": rank,"nome": nome,"kakera": kakera}
    return per

class PersonegemParser:
    PRADRAO_LINHA = re.compile(r"^#([0-9]+) - (.+) ([0-9]+) ka")

    @classmethod
    def parse(cls, linha: str) -> ht.Personagem | None:
        if not (match := cls.PRADRAO_LINHA.search(linha.strip())):
            return None
        return ht.Personagem(
            rank=int(match.group(1)),
            nome=match.group(2),
            kakera=int(match.group(3))
        )

class ProcessadorLista:
    def __init__(self, parser: PersonegemParser) -> None:
        self.parser = parser

    def converterLista(self, mudae: str) -> ht.DadosJSON:
        with open(file=mudae, mode="r", encoding="utf-8") as file:
            linhas = [linha for linha in file if linha.strip()]

        if not linhas:
            raise ValueError("Arquivo vazio.")

        alvo = self.parser.parse(linhas[0])

        if not alvo:
            raise ValueError("Primeira linha invalida.")

        trocas = [personagem for linha in linhas[1:] if (personagem := self.parser.parse(linha))]

        dados["personagem_alvo"].update(personagensDict(alvo.rank, alvo.nome, alvo.kakera))
        for personagen in trocas:
            dados["trocas_disponiveis"].append(personagensDict(personagen.rank, personagen.nome, personagen.kakera))

        return dados


# teste = ProcessadorLista(PersonegemParser()).converterLista("mudae.txt")
# print(teste)
