from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / 'data'
OUT_DIR = BASE_DIR / 'resultados'
GRAF_DIR = OUT_DIR / 'graficos'
OUT_DIR.mkdir(parents=True, exist_ok=True)
GRAF_DIR.mkdir(parents=True, exist_ok=True)

BASE_NAMES = [
    'Final baseline database - Brazil - Federal University of Santa Maria (with postgraduate students).xlsx',
    'Finalbaselinedatabase-Brazil-FederalUniversityofSantaMaria(withpostgraduatestudents).xlsx',
]
MED_NAMES = [
    'Medicamentos database - Brazil - Federal University of Santa Maria.xlsx',
    'Medicamentosdatabase-Brazil-FederalUniversityofSantaMaria.xlsx',
]

def _normalizar(nome):
    return ''.join(c.lower() for c in nome if c.isalnum())

def localizar_planilha(nomes):
    candidatos = []
    for nome in nomes:
        candidatos += [DATA_DIR / nome, BASE_DIR / nome]
    candidatos += [p for p in BASE_DIR.rglob('*.xlsx') if 'env' not in p.parts and '.git' not in p.parts]
    esperados = {_normalizar(nome) for nome in nomes}
    for caminho in candidatos:
        if caminho.exists() and _normalizar(caminho.name) in esperados:
            return caminho
    raise FileNotFoundError(
        'Planilha não encontrada. Coloque os dois arquivos Excel dentro de data/.\n'
        + '\n'.join(f'- {DATA_DIR / nome}' for nome in nomes)
    )
