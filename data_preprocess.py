import numpy as np
import pandas as pd

def main():
    df_phs = pd.read_csv("data/phs_data.csv", encoding="cp932", header=None, dtype=object)
    df_phs.columns = ["dept", "name", "phone_number"]
    df_phs["direct_phone_number"] = np.nan
    df_phs.to_csv("data/phs_data_unicode.csv", encoding="utf-8", index=False)

    df_naisen = pd.read_csv("data/naisen_data.csv", encoding="cp932", header=None, dtype=object)
    df_naisen.columns = ["dept", "name", "phone_number", "direct_phone_number"]
    df_naisen.to_csv("data/naisen_data_unicode.csv", encoding="utf-8", index=False)


if __name__ == "__main__":
    main()