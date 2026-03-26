import pandas as pd
import sqlite3


def import_csv(path):
    df = pd.read_csv(path)
    dates_iso = pd.to_datetime(df['sale_date'], format='%Y-%m-%d', errors='coerce')
    dates_br  = pd.to_datetime(df['sale_date'], format='%d-%m-%Y', errors='coerce')
    df['sale_date'] = dates_iso.fillna(dates_br)
    return df


def create_database(df):
    conn = sqlite3.connect('lh_nautical.db')
    cursor = conn.cursor()

    df.to_sql('vendas', conn, if_exists='replace', index=False)

    min_date = df['sale_date'].min()
    max_date = df['sale_date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')

    day_names = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }

    dim_dates = pd.DataFrame({
        'date': all_dates,
        'day_name': pd.Series(all_dates.dayofweek).map(day_names).values,
        'month': all_dates.month,
        'year': all_dates.year
    })

    dim_dates.to_sql('dimensao_datas', conn, if_exists='replace', index=False)

    conn.commit()
    return conn


if __name__ == '__main__':
    path = r"C:\Users\Valter\Desktop\lighthouse\vendas_2023_2024.csv"

    df = import_csv(path)
    conn = create_database(df)

    print(pd.read_sql('SELECT * FROM dimensao_datas LIMIT 10', conn))
    print(pd.read_sql('SELECT COUNT(*) FROM dimensao_datas', conn))