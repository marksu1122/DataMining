import itertools
import operator
import pandas as pd


def C1(itemsets):
    """
    produce C1
    """
    C1 = {}
    # 統計 itemset中所有出現的次數
    for itemset in itemsets:
        for item in itemset:
            item = tuple([item])
            count = C1.get(item)
            # 如果是第一次新增的item 會 count = None 所以 C1.update({item: 1}) 反之 count = count+1
            C1.update({item: count + 1}) if count else C1.update({item: 1})
    return C1


def Lk(ck, minimumSup):
    """
    check minmumSupport ,produce Lk
    """
    # 將不滿足minmum support的item刪除
    for key in ck.copy():
        if ck[key] < minimumSup:
            del ck[key]
    return ck


def ListC2(l1):
    """
    permutations l1 to c2
    """
    listC1 = []
    listC2 = []
    # 將L1的key合成一個list
    for key in l1:
        listC1 += list(key)
    listC1.sort()
    # 排列組合成 C2
    for s in itertools.combinations(listC1, 2):
        listC2.append(list(s))
    return listC2


def Search(listCk, itemsets):
    """
    cacaulate Ck support
    """
    ck = {}
    # 計算support值
    for data in listCk:
        count = 0
        # 遞迴所有itemset 如果是子集 count+1
        for itemset in itemsets:
            if set(data) <= set(itemset):
                count += 1
        ck.update({tuple(data): count})
    return ck


# JoinStep
def JoinStep(lk):
    """
    permutations lk to ck
    """
    listk = []
    # newlist = Ck+1
    newlist = []
    # 將Lk的key 加入 listk
    for key in lk:
        listk.append(list(key))
    listk.sort()
    # 取得比對次數
    k = len(listk[0]) - 1
    # 取得 listk 中每一筆 list
    for i in range(len(listk)):
        p = listk[i]
        # 與 當筆list 之後的每一筆list比對
        for j in range(i + 1, len(listk)):
            q = listk[j]
            compare = True
            # list中的前k筆item 必須相同
            for a in range(k):
                if p[a] != q[a]:
                    compare = False
                    break
            # 如果相同 取出最後不同的item 組合 傳入 Ck+1
            if compare:
                temp = p.copy()
                temp.append(q[k])
                newlist.append(temp)
    return newlist


# PruneStep
def PruneStep(listk, lk):
    """
    check subset should be in lk-1
    """
    for data in listk:
        check = 0
        # 產生所有的subset
        for s in itertools.combinations(data, len(data) - 1):
            notfound = True
            # 檢查此subset是否存在
            for item in lk:
                if s == item:
                    check += 1
                    notfound = False
                    break
            # 如果有一個subset不存在 即跳出迴圈 節省時間
            if notfound:
                break
        # 長度為 n 的data 應該要有 n個 長度為(n-1)的子集
        if check != len(data):
            listk.remove(data)
    return listk


def RuleGeneration(candidate, i, confidence, ruleDict, frequentSet):
    """
    遞迴找出符合confidence的 association rule
    """
    for rule in itertools.combinations(candidate, i):
        # cacaulate confidence
        conf = frequentSet.get(tuple(candidate)) / frequentSet.get(tuple(rule))
        # cofidence:如果大的antecedent不滿足 他的子集也不會滿足
        if conf < confidence:
            continue
        ruleDict.update(
            {str(rule) + "=====>" + str(set(candidate).difference(set(rule))): conf}
        )
        if i > 1:
            # 找滿足的antecedent之subset
            RuleGeneration(candidate, i - 1, confidence, ruleDict, frequentSet)
    return ruleDict


def Apriori(itemsets, minimumSup, confidence):
    """
    Apriori 主程式
    """
    lkDic = {}
    frequentSet = {}
    ruleDict = {}
    # 資料筆數
    datacount = len(itemsets)
    # 小數點ex:0.8 乘上itemset數 算出 minmum support
    minimumSup = minimumSup * datacount
    # C1
    c1 = C1(itemsets)
    # L1
    l1 = Lk(c1, minimumSup)
    lkDic.update({"l1": l1})
    # C2
    listC2 = ListC2(l1)
    # 計算C2 內item 的出現次數
    c2 = Search(listC2, itemsets)
    # 動態變數名稱 （locals()["l%s" % k] ） 遞迴產生 Lk
    for k in range(2, datacount):
        # 傳入Ck 產生Lk
        locals()["l%s" % k] = Lk(locals()["c%s" % k], minimumSup)
        # 終止條件 如果lk為空集合即跳出迴圈
        if not locals()["l%s" % (k)]:
            break
        # 將Lk 存入 dict 中
        lkDic.update({"l" + str(k): locals()["l%s" % k]})

        # 由Lk 產生 Ck+1
        locals()["listL%s" % (k + 1)] = JoinStep(locals()["l%s" % k])
        locals()["listL%s" % (k + 1)] = PruneStep(
            locals()["listL%s" % (k + 1)], locals()["l%s" % k]
        )
        # 計算 Ck+1 內item的出現次數
        locals()["c%s" % (k + 1)] = Search(locals()["listL%s" % (k + 1)], itemsets)

        # 終止條件 如果Ck+1為空集合即跳出迴圈
        if not locals()["c%s" % (k + 1)]:
            break

    # 將所有Lk 集合成一個 frequentSet
    for data in lkDic.values():
        for key, value in data.items():
            """
            #比較效能時 配合呼叫的mlxtend 轉成相同格式及統一排序     
            frequentSet.update({key:round(value/datacount, 6)})
            """
            frequentSet.update({key: value})
    # Rule Generation
    for key in frequentSet:
        count = len(key)
        if count > 1:
            ruleDict = RuleGeneration(
                list(key), count - 1, confidence, ruleDict, frequentSet
            )
    """
    #比較效能時 配合呼叫的mlxtend 轉成相同格式及統一排序      
    frequentSet = sorted(frequentSet.items(), key=lambda x: x[0])
    frequentSet = sorted(frequentSet, key=lambda x: len(x[0]))
    df = pd.DataFrame(list(frequentSet), columns=['itemsets', 'support'])
    df = df.reindex(columns=['support','itemsets'])
    return df
    """
    df = pd.DataFrame(list(ruleDict.items()), columns=["associationRule", "confidence"])
    return df

