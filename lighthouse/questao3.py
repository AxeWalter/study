import json
import pandas as pd


def import_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def convert_costs(data):
    df = pd.json_normalize(
        data,
        record_path='historic_data',
        meta=['product_id', 'product_name', 'category']
    )
    df = df[['product_id', 'product_name', 'category', 'start_date', 'usd_price']]
    return df


if __name__ == '__main__':
    input_path = r"C:\Users\Valter\Desktop\lighthouse\custos_importacao.json"
    output_path = r"C:\Users\Valter\Desktop\lighthouse\custos_importacao.csv"

    data = import_json(input_path)
    df = convert_costs(data)
    df.to_csv(output_path, index=False)
