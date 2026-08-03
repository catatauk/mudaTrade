import json
import re

dados: dict[str, dict[str, int|str]|list[dict[str, int|str]]] = {"personagem_alvo": {},
    "trocas_disponiveis": []
}

PRADRAO_LINHA = re.compile(r"^#([0-9]+) - (.+) ([0-9]+) ka")

rank = ""
nome = ""
kakera = ""

def formatarLinha(linha:str):
    return PRADRAO_LINHA.search(linha)

def personagens(rank:int, nome:str, kakera:int):
    per = {"rank": rank,"nome": nome,"kakera": kakera}
    return per


def converterLista():
    with open(file="list.txt", mode="r", encoding="utf-8") as file:
        for nLinha, linha in enumerate(file, start=1):
            linha = linha.strip()
            p = formatarLinha(linha)
            if p:
                rank = p.group(1)
                nome = p.group(2)
                kakera = p.group(3)

            if linha and nLinha == 1:
                dados["personagem_alvo"].update(personagens(int(rank), nome, int(kakera)))
                continue
            if linha and nLinha > 1:
                dados["trocas_disponiveis"].append(personagens(int(rank), nome, int(kakera)))

    jt = json.dumps(dados, ensure_ascii=False, indent=4)
    return jt

print(converterLista())
