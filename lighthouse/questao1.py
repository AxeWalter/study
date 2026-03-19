import pandas as pd


def import_csv(path):
    df = pd.read_csv(path, skip_blank_lines=False)
    return df


def basic_stats(df):
    total_lines = len(df)
    blank_lines = df.isnull().all(axis=1).sum()
    total_cols = len(df.columns)
    dates_iso = pd.to_datetime(df['sale_date'], format='%Y-%m-%d', errors='coerce')
    dates_br = pd.to_datetime(df['sale_date'], format='%d-%m-%Y', errors='coerce')
    dates = dates_iso.fillna(dates_br)

    min_date = dates.min().strftime('%d/%m/%Y')
    max_date = dates.max().strftime('%d/%m/%Y')

    print(f"""
    Visão Geral do Dataset
    
    Total de Linhas: {total_lines}
    Total de Linhas em Branco: {blank_lines}
    Total de Colunas: {total_cols}
    Data Mínima: {min_date}
    Data Máxima: {max_date}
    """)


def total_stats(df):
    min_val = df['total'].min()
    max_val = df['total'].max()
    mean = df['total'].mean()

    print(f"""
    Análise de Valores Numéricos
    
    Valor Mínimo: R$ {min_val:,.2f}
    Valor Máximo: R$ {max_val:,.2f}
    Valor Médio: R$ {mean:,.2f}
    """)


def data_quality(df):
    median = df['total'].median()
    q1 = df['total'].quantile(0.25)
    q3 = df['total'].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = df[(df['total'] < lower) | (df['total'] > upper)]

    null_counts = df.isnull().sum()

    dates_iso = pd.to_datetime(df['sale_date'], format='%Y-%m-%d', errors='coerce')
    dates_br = pd.to_datetime(df['sale_date'], format='%d-%m-%Y', errors='coerce')
    dates = dates_iso.fillna(dates_br)
    unparsed = dates.isna().sum()

    print(f"""
    Diagnóstico de Qualidade

    1. Outliers (IQR)
    Mediana: R$ {median:,.2f}
    Q1: R$ {q1:,.2f} | Q3: R$ {q3:,.2f} | IQR: R$ {iqr:,.2f}
    Limite inferior: R$ {lower:,.2f}
    Limite superior: R$ {upper:,.2f}
    Outliers encontrados: {len(outliers)} ({len(outliers)/len(df)*100:.1f}% do dataset)

    2. Valores Nulos
    {null_counts.to_string()}

    3. Inconsistências de Formato (sale_date)
    Formato YYYY-MM-DD : {dates_iso.notna().sum()}
    Formato DD-MM-YYYY : {dates_br.notna().sum()}
    Datas não parseadas: {unparsed}
    """)


if __name__ == '__main__':
    path = r"C:\Users\Valter\Desktop\lighthouse\vendas_2023_2024.csv"
    df = import_csv(path)
    basic_stats(df)
    total_stats(df)
    data_quality(df)