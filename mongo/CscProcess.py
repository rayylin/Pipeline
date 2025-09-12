import pandas as pd

df = pd.read_csv(r"C:\\Users\\dwade\\Desktop\\Pipeline\\mongo\\CmpReg_TextilePlastic.csv")


print(df.head)

for idx, row in df.iterrows():
    print(row)