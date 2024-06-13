import pandas as pd

df = pd.read_csv("mydata.csv")

new_data = {
    "Date": "5 June"
}

df.loc[len(df)] = new_data

# print(df.drop(columns=["Unnamed: 0"]))

print(list(df["Date"])[-1])