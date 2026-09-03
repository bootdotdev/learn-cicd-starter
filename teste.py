catalogo = {
    "filme_01": {
        "titulo": "Interestelar",
        "ano": 2014,
        "detalhes": {  # <--- Outro dicionário aqui dentro!
            "diretor": "Christopher Nolan",
            "duracao": "2h 49m"
        }
    },
    "filme_02": {
        "titulo": "Vingadores: Ultimato",
        "ano": 2019,
        "detalhes": {
            "diretor": "Irmãos Russo",
            "duracao": "3h 01m"
        }
    }
}


print(catalogo["filme_01"]["detalhes"]["diretor"])