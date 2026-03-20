import pandas as pd
import unicodedata


def import_csv(path):
    df = pd.read_csv(path)
    return df


# Compreendo que estou repetindo código, mas como pensei cada questão individualmente, não quis importar a função.
def normalize_categories(df):
    stems = {
        'eletr': 'eletronicos',
        'prop': 'propulsao',
        'anco': 'ancoragem',
        'encor': 'ancoragem',
    }

    def map_category(text):
        text = text.replace(' ', '').lower()
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        for stem, category in stems.items():
            if text.startswith(stem):
                return category
        return text

    df['actual_category'] = df['actual_category'].apply(map_category)
    return df


def calculate_metrics(df_sales, df_products):
    df = df_sales.merge(df_products[['code', 'actual_category']],
                        left_on='id_product',
                        right_on='code')

    df_aggregated = df.groupby('id_client').agg(
        faturamento_total=('total', 'sum'),
        frequencia=('id', 'count'),
        diversidade=('actual_category', 'nunique')
    ).round(2)

    df_aggregated['ticket_medio'] = (df_aggregated['faturamento_total'] / df_aggregated['frequencia']).round(2)

    return df_aggregated


def get_top10_elite(df_aggregated):
    df_elite = df_aggregated[df_aggregated['diversidade'] >= 3]
    df_elite = df_elite.sort_values(['ticket_medio', 'id_client'], ascending=[False, True])
    return df_elite.head(10)


def get_top_category(df_sales, df_products, top10):
    df = df_sales.merge(df_products[['code', 'actual_category']],
                        left_on='id_product',
                        right_on='code')

    df_elite = df[df['id_client'].isin(top10.index)]

    top_category = df_elite.groupby('actual_category')['qtd'].sum().idxmax()

    return top_category


if __name__ == '__main__':
    sales_path = r"C:\Users\Valter\Desktop\lighthouse\vendas_2023_2024.csv"
    products_path = r"C:\Users\Valter\Desktop\lighthouse\produtos_raw.csv"

    df_sales = import_csv(sales_path)
    df_products = import_csv(products_path)
    df_products_normalized = normalize_categories(df_products)

    df_aggregated = calculate_metrics(df_sales, df_products_normalized)
    top10 = get_top10_elite(df_aggregated)

    top_category = get_top_category(df_sales, df_products_normalized, top10)

    print(top10)
    print(f"Categoria com maior quantidade comprada pelo grupo elite: {top_category}")