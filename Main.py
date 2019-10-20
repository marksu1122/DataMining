"""
    listC1 = []
    test = []
    listC2 = []
    for key in l1:
        listC1 = listC1 + list(key)
    listC1.sort()
    test.sort()
    print(test)
    print(list(l1.keys()))
    print(listC1)
    for s in itertool
"""
import os
import psutil
from time import process_time 
import pandas as pd
from mlxtend.frequent_patterns import association_rules



def get_process_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss

def main(funcList,dataname):
    itemsets = []
    frequent_itemsets = None

    data = pd.read_csv(dataname, sep="\\s+", names=["id", "seq", "item"])

    df = pd.DataFrame(data)
    df = df.groupby("id")["item"].apply(list)

    for data in df:
        itemsets.append(data)

    for data in funcList:
        module = __import__(data, globals(), locals(), [data])
        start = process_time()
        mem_before = get_process_memory() 
        frequent_itemsets = getattr(module, data)(itemsets, 0.7)
        mem_after = get_process_memory()
        stop = process_time()

        # print time memory 
        print (data," cost time======>",stop-start,"seconds")
        print(data," use memory======>", mem_after - mem_before,"bytes.")
        print(data,"consle===========================================")
        print(frequent_itemsets)
        #res = association_rules(frequent_itemsets,metric='confidence', min_threshold=0.8)
        #print(res[['antecedents', 'consequents', 'support','confidence']])
        print(data,"over=============================================")
    

funcList = ["Apriori","FP_Growth","Mlx"]
main(funcList,"data.ntrans_0.1.nitems_0.01.txt")