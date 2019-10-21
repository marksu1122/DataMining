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


def Sort(l1):
    """
    根據l1決定orderlist
    """
    orderList = []
    # value由大到小排序 相同則 由key從小到大排序
    sorted_x = sorted(l1.items(), key=lambda x: (-x[1], x[0]))
    # 排序後取出 key 存入 orderlist
    for itemset in sorted_x:
        for item in itemset[0]:
            orderList.append(item)
    return orderList


class Node:
    def __init__(self, name):
        """
        初始參數
        """
        self.name = name
        self.value = 1
        self.children = []
        self.parent = None
        self.next = None

    def insert(self, node, headerTable):
        """
        新增node 檢查children內是否已存在相同name的node 
        是的話value值+1 回傳已有的node
        如沒有則將node加入children內 並新增HeaderTable中的link 回傳新增的node
        """
        for child in self.children:
            if node.name == child.name:
                child.value += 1
                return child

        self.children.append(node)
        node.parent = self
        # 更新headerTable中的link
        node.link(headerTable)
        return node

    def link(self, headerTable):
        """
        實現headerTable中 指向下個相同item的Link
        """
        # 取出現有的node
        point = headerTable.get(self.name)
        # 如果header中存在node的話 將現在的node指向header中的node
        if point:
            self.next = point
        # 將現在的node取代原本的 (指標的概念)
        headerTable.update({self.name: self})

    def disp(self, ind=1):
        """
        印出FP-Tree的結構
        """
        print(" " * ind, self.name, " ", self.value)
        for child in self.children:
            child.disp(ind + 1)


def FPtree(itemsets, orderList):
    """
    產生FP-Tree 及 headerTable
    """
    root = Node("root")
    root.value = None
    headerTable = {}
    for itemset in itemsets:
        # 將不在oder的元素刪除
        for item in itemset.copy():
            if item not in orderList:
                itemset.remove(item)
        # 根據order排序每筆資料
        itemset = sorted(itemset, key=orderList.index)
        # 呼叫 class Node 建樹
        parent = root
        for item in itemset:
            node = Node(item)
            parent = parent.insert(node, headerTable)
    # 印出樹的結構
    # print("===========================================")
    # print(root.disp())
    # print("===========================================")
    return headerTable


def CondPatternBase(headerTable, orderList):
    """
    傳入的orderList為由小到大,從headerTable由小開始產生 Conditional Pattern Base
    """
    pathDic = {}
    # 由小到大
    for item in orderList:
        pathList = []
        dot = headerTable.get(item)
        # Tarce Link上的所有(同名)點
        while dot:
            node = dot.parent
            path = []
            # 找出路徑
            while node:
                if node.name != "root":
                    path.append(node.name)
                # 由最後一個點開始往上找 直到碰到root
                node = node.parent
            # 由於是由下往上 所以需要reverse成正確順序
            path.reverse()
            # path的權重 由最後一個點決定
            pathList.append([path, dot.value])
            # 如果有下一個點就繼續找出path
            dot = dot.next
        pathDic.update({headerTable.get(item).name: pathList})

    return pathDic


def FreqTree(prefix, value, minimumSup, orderList, patternList):
    """
    遞迴產生 conditional FP-Tree 並產生 frequent pattern
    """
    itemsets = []
    #  將所有的condition pattern base 建成 itesmset
    for item in value:
        count = int(item[1])
        # 根據 path權重決定出現次數
        while count:
            itemsets.append(item[0])
            count += -1
    # 同FP-Tree流程
    c1 = C1(itemsets)
    l1 = Lk(c1, minimumSup)
    orderList = Sort(l1)
    # 同FP-Tree流程的step1
    freqHd = FPtree(itemsets, orderList)

    # 中止條件 如果 headerTable空 跳出遞迴
    if not freqHd:
        return patternList

    orderList.reverse()
    # 同FP-Tree流程的step2
    pathDic = CondPatternBase(freqHd, orderList)

    # 同FP-Tree流程的step3
    for key, value in pathDic.items():
        count = 0
        for item in value:
            count = count + int(item[1])
        pattern = []
        # key to list
        item = []
        item.append(key)
        # 與headerTable中的 item組成 frequent Pattern
        pattern.append(prefix + item)
        # frequent
        pattern.append(count)
        patternList.append(pattern)
        FreqTree(prefix + item, value, minimumSup, orderList, patternList)

    return patternList


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


def FP_Growth(itemsets, minimumSup, confidence):
    """
    FP-Growth 主程式
    """
    patternTmp = {}
    frequentSet = {}
    ruleDict = {}
    datacount = len(itemsets)
    # 小數點ex:0.8 乘上itemset數 算出 minmum support
    minimumSup = minimumSup * datacount
    # 同Apriori
    c1 = C1(itemsets)
    l1 = Lk(c1, minimumSup)

    orderList = Sort(l1)
    # step1 FP-Trees & headerTable  construction
    headerTable = FPtree(itemsets, orderList)
    # 因為要從headerTable由下往上trace
    orderList.reverse()
    # step2 trace headerTable 找出 conditional pattern base
    pathDic = CondPatternBase(headerTable, orderList)
    # 還原orderlist
    orderList.reverse()
    # step3  根據 conditional pattern base 建出 conditional FP-tree 遞迴找出 frequent patterns
    for key, value in pathDic.items():
        if value:
            patternList = FreqTree(list(), value, minimumSup, orderList, list())
            patternTmp.update({key: patternList})

    # 統計 frequent patterns 的 support  並合併成一個dictionary(frequentSet)
    for key, value in l1.items():
        """
        #比較效能時 配合呼叫的mlxtend 轉成相同格式及統一排序     
        frequentSet.update({key: round(value / datacount, 6)})
        """
        frequentSet.update({key: value})
    for key, value in patternTmp.items():
        for item in value:
            pattern = item[0]
            pattern.insert(0, key)
            pattern.sort()
            """
            #比較效能時 配合呼叫的mlxtend 轉成相同格式及統一排序     
            frequentSet.update({tuple(pattern): round(item[1] / datacount, 6)})
            """
            frequentSet.update({tuple(pattern): item[1]})

    """
    #比較效能時 配合呼叫的mlxtend 轉成相同格式及統一排序     
    frequentSet = sorted(frequentSet.items(), key=lambda x: x[0])     
    frequentSet = sorted(frequentSet, key=lambda x: len(x[0]))
    df = pd.DataFrame(list(frequentSet), columns=['itemsets', 'support'])
    df = df.reindex(columns=['support','itemsets'])
    return df
    """
    # Rule Generation
    for key in frequentSet:
        count = len(key)
        if count > 1:
            ruleDict = RuleGeneration(
                list(key), count - 1, confidence, ruleDict, frequentSet
            )

    df = pd.DataFrame(list(ruleDict.items()), columns=["associationRule", "confidence"])
    return df
