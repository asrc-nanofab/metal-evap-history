from utils.app_utils import load_clean_data

df = load_clean_data()

print(df.head())

df.Materials.unique().tolist()

len(df)

df
