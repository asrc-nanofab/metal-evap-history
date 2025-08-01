from shared_utils import load_clean_data

df = load_clean_data()

print(df.head())

df.Material.unique().tolist()

len(df)
