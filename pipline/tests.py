from django.test import TestCase
import os
import pandas as pd
# Create your tests here.
if __name__ == '__main__':

    df = pd.read_csv('/Users/steph/PycharmProjects/djangoProject/data/output/HGSC3.control.jf.csv', delimiter='\t')
    # 将 DataFrame 转换为 JSON 字符串
    json_data = df.to_json(orient='records')
    print(json_data)