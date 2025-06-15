import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt
import sqlite3

# Load the dataset
df = pd.read_csv('amazon.csv')

# Clean prices: remove ₹ and commas, convert to float
df['discounted_price'] = df['discounted_price'].str.replace('₹','').str.replace(',','').astype(float)
df['actual_price'] = df['actual_price'].str.replace('₹','').str.replace(',','').astype(float)
df['discount_percentage'] = df['discount_percentage'].str.replace('%','').astype(float)

# Compute price difference
df['price_diff'] = df['actual_price'] - df['discounted_price']

# Safely split the 'category' column
category_split = df['category'].str.split('|', expand=True)

# Rename columns dynamically based on how many parts exist
category_split.columns = [f'category_level_{i+1}' for i in range(category_split.shape[1])]

# Join with the original dataframe
df = pd.concat([df, category_split], axis=1)

# Check cleaned data
print(df[['product_name', 'actual_price', 'discounted_price', 'discount_percentage', 'category']].head())

# Top categories with biggest average discount
top_discounts = df.groupby('category')['discount_percentage'].mean().sort_values(ascending=False).head(20)

# Plot graph
plt.figure(figsize=(10,8))
top_discounts.plot(kind='bar', color='skyblue')
top_discounts = top_discounts.head(20)
plt.title('Average Discount by Main 20 Category')
plt.xlabel('Product Category')
plt.ylabel('Average Discount (%)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Export cleaned data for Tableau
df_export = df[['product_name', 'category', 'actual_price', 'discounted_price', 'discount_percentage', 'price_diff']]
df_export.to_csv('cleaned_amazon_data.csv', index=False)

# Connect to local SQLite database
conn = sqlite3.connect('amazon.db')
cursor = conn.cursor()

# Write dataframe to SQL table
df.to_sql('amazon_data', conn, if_exists='replace', index=False)

# Optional: Export the SQL CREATE + INSERT script
with open('amazon_export.sql', 'w') as f:
    for line in conn.iterdump():
        f.write(f'{line}\n')

conn.close()
print("SQL file 'amazon_export.sql' created successfully.")