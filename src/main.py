from dados import carregar_bases
from phq9 import preparar_grupos
from descritiva import calcular_diferencas
from modelo_ml import executar_modelo
from graficos import gerar_graficos
from relatorio import gerar_relatorio


def main():
    print('[1/6] Carregando e relacionando bases...')
    base, medicamentos, relacionada = carregar_bases()
    print('[2/6] Calculando PHQ-9 e separando grupos...')
    df, subgrupo, resumo, comparacao = preparar_grupos(relacionada)
    print(resumo.to_string(index=False))
    print('[3/6] Calculando diferenças entre grupos...')
    efeitos = calcular_diferencas(subgrupo)
    print('[4/6] Executando machine learning...')
    modelo, metricas = executar_modelo(subgrupo, medicamentos)
    print(metricas.to_string(index=False))
    print('[5/6] Gerando gráficos...')
    gerar_graficos(df, subgrupo, metricas, efeitos)
    print('[6/6] Gerando relatório...')
    caminho = gerar_relatorio(df, subgrupo, resumo, comparacao, metricas, efeitos)
    print(f'\nConcluído. Resultados salvos em: {caminho.parent}')


if __name__ == '__main__':
    main()
