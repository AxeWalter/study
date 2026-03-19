import pandas as pd
import requests
import json
import matplotlib.pyplot as plt


def import_csv(path):
    df = pd.read_csv(path)
    dates = pd.to_datetime(df['sale_date'], format='%Y-%m-%d', errors='coerce')
    dates_br = pd.to_datetime(df['sale_date'], format='%d-%m-%Y', errors='coerce')
    df['sale_date'] = dates.fillna(dates_br)
    return df


def import_json(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for product in data:
        for entry in product['historic_data']:
            rows.append({
                'id_product': product['product_id'],
                'product_name': product['product_name'],
                'start_date': pd.to_datetime(entry['start_date'], format='%d/%m/%Y'),
                'usd_price': entry['usd_price']
            })

    return pd.DataFrame(rows)


def get_exchange_rates(df):
    min_date = (df['sale_date'].min() - pd.Timedelta(days=5)).strftime('%m-%d-%Y')
    max_date = df['sale_date'].max().strftime('%m-%d-%Y')

    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial='{min_date}'&@dataFinalCotacao='{max_date}'&$format=json"
    response = requests.get(url)
    data = response.json()['value']

    exchange_rates = {}
    for item in data:
        date = pd.to_datetime(item['dataHoraCotacao']).date()
        exchange_rates[date] = item['cotacaoVenda']

    return exchange_rates


def get_usd_price(df_sales, df_costs):
    df_sales = df_sales.sort_values('sale_date')
    df_costs = df_costs.sort_values('start_date')

    df = pd.merge_asof(
        df_sales,
        df_costs,
        left_on='sale_date',
        right_on='start_date',
        by='id_product',
        direction='backward'
    )
    df = df.drop(columns=['start_date'])

    return df


def full_cost_brl_and_loss(df, exchange_rates):
    def find_exchange_rate(date):
        date = date.date()
        while date not in exchange_rates:
            date -= pd.Timedelta(days=1).to_pytimedelta()
        return exchange_rates[date]

    df['exchange_rate'] = df['sale_date'].apply(find_exchange_rate)
    df['full_cost_brl'] = (df['usd_price'] * df['qtd'] * df['exchange_rate']).round(2)
    df['loss'] = df['full_cost_brl'] > df['total']

    return df


def aggregate_by_product(df):
    df_aggregated = df.groupby('id_product').agg(
        total_revenue=('total', 'sum'),
        total_cost=('full_cost_brl', 'sum')
    ).round(2)

    df_aggregated['total_loss'] = (df_aggregated['total_revenue'] - df_aggregated['total_cost']).round(2)
    df_aggregated['percentual'] = (df_aggregated['total_loss'] / df_aggregated['total_revenue'] * 100).round(2)

    names = df.drop_duplicates('id_product').set_index('id_product')['product_name']
    df_aggregated['product_name'] = df_aggregated.index.map(names)

    return df_aggregated


def plot_top10_loss(df_aggregated):
    top10 = df_aggregated[df_aggregated['total_loss'] < 0].nsmallest(10, 'total_loss')
    plt.figure(figsize=(12, 6))
    plt.bar(top10['product_name'], top10['total_loss'].abs())
    plt.title('10 Produtos com Maior Prejuízo Total')
    plt.xlabel('Nome do Produto')
    plt.ylabel('Prejuízo Total (BRL)')
    plt.xticks(rotation=45, ha='right', fontsize='small')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x / 1e6:.1f}M'))

    for bar in plt.gca().patches:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'R$ {bar.get_height() / 1e6:.1f}M',
            ha='center', va='bottom', fontsize=10
        )

    plt.tight_layout()
    plt.savefig('loss_by_product.png')


def plot_all_loss_by_product(df_aggregated):
    df_loss = df_aggregated[df_aggregated['total_loss'] < 0].copy()

    plt.figure(figsize=(12, 6))
    plt.scatter(range(len(df_loss)), df_loss['total_loss'].abs(), alpha=0.7)
    plt.title('Prejuízo Total de Todos os Produto')
    plt.xlabel('Produtos')
    plt.ylabel('Prejuízo Total (BRL)')
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R$ {x/1e6:.1f}M'))
    plt.grid(linestyle='--', color='lightgray', alpha=0.7)
    plt.tight_layout()
    plt.savefig('all_loss_by_product.png')


if __name__ == '__main__':
    path = r"C:\Users\Valter\Desktop\lighthouse\vendas_2023_2024.csv"
    json_path = r"C:\Users\Valter\Desktop\lighthouse\custos_importacao.json"

    df_sales = import_csv(path)
    df_costs = import_json(json_path)
    df_usd_price = get_usd_price(df_sales, df_costs)
    exchange_rates = get_exchange_rates(df_usd_price)
    df_final = full_cost_brl_and_loss(df_usd_price, exchange_rates)

    df_aggregated = aggregate_by_product(df_final)
    plot_top10_loss(df_aggregated)
    plot_all_loss_by_product(df_aggregated)
