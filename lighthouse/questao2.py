import pandas as pd
import unicodedata


def import_csv(path):
    df = pd.read_csv(path, skip_blank_lines=False)
    return df


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


def convert_price(df):
    df['price'] = df['price'].str.replace('R$ ', '').astype(float)
    return df


def remove_duplicates(df):
    df = df.drop_duplicates(subset='code')
    return df


if __name__ == "__main__":
    path = r"C:\Users\Valter\Desktop\lighthouse\produtos_raw.csv"
    output_path = r"C:\Users\Valter\Desktop\lighthouse\produtos_clean.csv"
    df = import_csv(path)
    df = normalize_categories(df)
    df = convert_price(df)
    df = remove_duplicates(df)
    df.to_csv(output_path, index=False)