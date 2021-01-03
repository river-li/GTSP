from Algorithms import Algorithm
import math
import numpy as np
from timeit import default_timer as timer

class Tabu(Algorithm):
    def __init__(self, points, goods, filename=None):
        super().__init__(points, goods, filename)

    def _generate_path(self):
        # Path随机生成一个解
        # 从商品出发，选择城市，售卖同一个商品的城市其实就是点集
        sPoints = []
        for opGoods in self.goodsType:
            # 依次选择点集中的城市
            sPoints.append(np.random.choice(opGoods))
        np.random.shuffle(sPoints)
        return sPoints

    def _calculate_singlecost(self,path):
        singleCost = 0
        for i in range(self.goods):
            singleCost += self.graph[path[i],path[(i+1)%self.goods]]
        return singleCost

    def set(self):
        # tabulen 禁忌长度  不能太长，至少不能大于 goods/2 ，否则领域操作的时候选不了
        # 领域动作，交换位置，点的交换
        self.tabulen = int(self.goods/3)


# 领域操作可以设置为与模拟退火中相同的操作
    def fit(self,iteration):

        result = self.result
        bestresult = self.bestresult
        # tabu_list 直接存储路径
        tabu_list = []
        cur_path = self._generate_path()
        cur_cost = self._calculate_singlecost(cur_path)

        bestpath = cur_path[:]
        bestcost = cur_cost
        result.append(cur_cost)
        bestresult.append(bestcost)
        count = 0
        while count <= iteration:
            count = count+1
            cur_path, cur_cost, bestpath, bestcost,tabu_list =self.neighbours(cur_path,bestpath,bestcost,tabu_list)
            result.append(cur_cost)
            bestresult.append(bestcost)



    def neighbours(self,path,bestpath,bestcost,tabu_list):
        """
        选取 goods/2 的点作为交换的邻居节点
        paths 用于存储所有的领域
        :param path:
        :param tabu_list:
        :return:
        """
        # list不能作为字典的Key，但是这里要实现的是领域中的  path 和 cost 一一对应的存储 ,所以选择使用lℹist对元组(path,cost)进行存储
        candidate = []
        cur_path = path
        bestpath = bestpath
        bestcost = bestcost
        cur_cost = self._calculate_singlecost(path)

        for i in range(int(self.goods/2)):
            temp_path = path[:]

            random_a = np.random.randint(0, self.goods)
            random_b = np.random.randint(0, self.goods)
            random_c = np.random.randint(0, self.goods)
            #a,b 用于两两交换

            temp_path[random_a], temp_path[random_b] = temp_path[random_b], temp_path[random_a]
            #c 单点替换
            point = temp_path[random_c]

            for opGoods in self.goodsType:
                if point in opGoods:
                    random_d = np.random.randint(0, len(opGoods))
                    newpoint = opGoods[random_d]
                    temp_path[random_c] = newpoint
                    break
            if (temp_path,self._calculate_singlecost(temp_path)) not in candidate:
                candidate.append((temp_path,self._calculate_singlecost(temp_path)))

        #所有候选集合计算完毕,进行排序
        candidate.sort(key=lambda x:x[1])
        #看是否在禁忌表中,包括当前解  历史最优解
        #破禁要求大于最优解 或者超过禁忌长度
        # 1.结果优于当前最优结果,之前没在禁忌表中则加入，在的话先pop出，再加入
        # 2.如果没有达到最优解，则选取不再禁忌表中的最优解
        #paths = candidate[:]
        if candidate[0][1] < bestcost:
            bestcost = candidate[0][1]
            bestpath = candidate[0][0][:]
            if bestpath in tabu_list:
                tabu_list.remove(bestpath)
            tabu_list.append(bestpath)
        else:
            for i in range(self.tabulen):
                if candidate[i][0] not in tabu_list:
                    cur_path = candidate[i][0][:]
                    cur_cost = self._calculate_singlecost(cur_path)
                    tabu_list.append(cur_path)
                    break
        if len(tabu_list) > self.tabulen:
            #达到禁忌长度，破禁，先进先出
            tabu_list.pop(0)

        return cur_path,cur_cost,bestpath,bestcost,tabu_list


tic = timer()

t = Tabu(39,25)
t.set()
t.fit(10000)
t.show_result()

toc = timer()

print('cost:',toc - tic) # 输出的时间，秒为单位



