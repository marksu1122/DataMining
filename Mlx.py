import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules


def Mlx(itemsets, minimumSup, confidence):
    te = TransactionEncoder()  # 定義模型
    df_tf = te.fit_transform(itemsets)
    df = pd.DataFrame(df_tf, columns=te.columns_)
    frequentSet = apriori(df, min_support=minimumSup)
    """
	比較效能時 統一使用 mlxtend的 association Rule
	return frequentSet
	"""
    res = association_rules(frequentSet, metric="confidence", min_threshold=confidence)
    return res[["antecedents", "consequents", "support", "confidence"]]

