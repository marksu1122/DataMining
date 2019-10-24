import os
import psutil
from time import process_time
import pandas as pd
from mlxtend.frequent_patterns import association_rules


def get_process_memory():
    """
    取得現在記憶體資訊
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def main(funcList, dataname, support, confidence):
    """
    根據傳入的funcList 呼叫
    """
    itemsets = []
    frequent_itemsets = None

    data = pd.read_csv(dataname, sep="\\s+", names=["id", "seq", "item"])
    df = pd.DataFrame(data)
    df = df.groupby("id")["item"].apply(list)

    for data in df:
        itemsets.append(data)

    for data in funcList:
        # 動態import Class
        module = __import__(data, globals(), locals(), [data])
        start = process_time()
        mem_before = get_process_memory()
        """ 
        #單純比較產生frequentSet效能時 統一使用 mlxtend的 association Rule 
        frequent_itemsets = getattr(module, data)(itemsets, support,confidence)
        print(data,"consle===========================================")
        print(frequent_itemsets)
        print(data,"over=============================================")
        """
        # 呼叫模組
        associationRule = getattr(module, data)(itemsets, support, confidence)
        print(data, "consle===========================================")
        print(associationRule)
        print(data, "over=============================================")
        mem_after = get_process_memory()
        stop = process_time()
        print(data, " cost time======>", stop - start, "seconds")
        print(data, " use memory======>", mem_after - mem_before, "bytes.")


# funcList = ["Apriori","FP_Growth","Mlx"]
funcList = ["Apriori"]
# main(funcList,"data.ntrans_1.nitems_0.1.txt",support = 0.7)
# main(funcList,"data.ntrans_10.nitems_0.1.txt",support = 0.1)
main(funcList, "data.ntrans_0.1.nitems_0.01.txt", support=0.8, confidence=0.7)
# main(funcList,"data.ntrans_0.1.nitems_0.01.txt",support = 0.8,confidence =0.3)
# main(funcList,"data.ntrans_0.1.nitems_0.01.txt",support = 0.3,confidence =0.9)
# main(funcList,"data.ntrans_0.1.nitems_0.01.txt",support = 0.3,confidence =0.3)

