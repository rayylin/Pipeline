import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv(r'C:\\Users\\dwade\\Downloads\\AbTest.csv')

print(df.head())

df['DATE'] = pd.to_datetime(df['VDATE'])

# Basic summary
print(df['LandingPage'].value_counts())
print(df['Convert'].value_counts())
print(df.head())


# Subset to smartphone users only
# if we want to compare 3+ pages, we need to use chi-square
ab_df = df[(df['Channel'] == 'smartphone') & 
           (df['LandingPage'].isin(['Mobile_1', 'Mobile_2']))]

# Check counts
ab_df['LandingPage'].value_counts()


# Subset to smartphone users only
ab_df = df[(df['LandingPage'].isin(['Mobile_1', 'Mobile_2']))]

# Check counts
ab_df['LandingPage'].value_counts()

from statsmodels.stats.proportion import proportions_ztest

ab_summary = ab_df.groupby('LandingPage')['Convert'].agg(['sum', 'count'])
print(ab_summary)

# Convert to required format
successes = ab_summary['sum'].values
samples = ab_summary['count'].values

z_stat, p_val = proportions_ztest(count=successes, nobs=samples, alternative='two-sided')

print(f"Z-stat: {z_stat:.4f}, P-value: {p_val:.4f}")

if p_val < 0.05:
    print("✅ Statistically significant difference between landing pages.")
else:
    print("❌ No statistically significant difference.")





