from Algorithms import Algorithm
import math
import numpy as np
from timeit import default_timer as timer

class Annealing(Algorithm):
    def __init__(self, points, goods, filename=None):
        super().__init__(points, goods, filename)

    def set(self):
        # M个商品 ,t 起始温度; endt 终止温度; alpha 衰减率; L 迭代次数
        t = 10
        endt = 0.1
        alpha = 0.99
        L = 50

        return t, endt, alpha, L

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

    def fit(self, iteration):
        #内循环  终止条件迭代次数   外循环  终止条件为温度
        #交换的时候交换点集中的城市，再交换path中的顺序
        #cost记录所有的花费，singlecost记录单个点的花费
        t, endt, alpha, L = self.set()

        count = 0

        path = self._generate_path()
        cur_cost = self._calculate_singlecost(path)
        bestpath = path[:]
        # bestcost 为全局，cur_min为当前轮次
        bestcost = cur_cost
        cur_min = cur_cost

        #self.result.append(cur_cost)
        #self.bestresult.append(bestcost)
        while t > endt and count < iteration:
            count = count + 1
            cur_min = self._calculate_singlecost(path)
            for i in range(L):
                #左闭右开区间生成随机
                new_path = path[:]
                ran_num1 = np.random.randint(1,self.goods)
                point = path[ran_num1]
                for opGoods in self.goodsType:
                    if point in opGoods:
                        #从所有可以买该商品的城市中选一个出来交换
                        ran_num2 = np.random.randint(0, len(opGoods))
                        newpoint = opGoods[ran_num2]

                        #交换path中顺序
                        new_path[ran_num1] = new_path[ran_num1-1]
                        new_path[ran_num1 - 1] = newpoint
                        break
                new_cost = self._calculate_singlecost(new_path)
                """
                if new_cost == cur_cost:
                    count = count +1
                else:
                    if new_cost < cur_cost :
                        count = 0
                """

                if new_cost <= cur_cost:
                    #花费更小，接受解
                    cur_cost = new_cost
                    #self.result.append(new_cost)
                    path = new_path[:]

                        #bestpath = path[:]
                else:
                    if self.Metropolis(new_cost,cur_cost,t):
                        cur_cost = new_cost
                        #self.result.append(new_cost)
                        path = new_path[:]
                if cur_cost < cur_min:
                    cur_min = cur_cost

                #result.append(bestcost)
            self.result.append(cur_min)
            if cur_min < bestcost:
                bestcost = cur_min
            self.bestresult.append(bestcost)

            t = t*alpha
        #self.result = result
        #print(bestcost)


    def Metropolis(self, Ei, Ej, T, K=1):
        """
        Ei 新状态
        Ej 当前状态
        K  玻尔兹曼常数
        T  材料温度
        e的负指数幂
        """

        p = math.exp(-(Ei-Ej)/(K*T))
        r = np.random.uniform(0, 1)
        if p > r:
            #接受解
            return True
        else:
            return False

tic = timer()
a = Annealing(39,25)
a.fit(10000)
a.show_result()
toc = timer()

print('cost:',toc - tic) # 输出的时间，秒为单位




