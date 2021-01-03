# coding: utf-8
import numpy as np
import random
from Algorithms import Algorithm

class Genetic(Algorithm):
    def __init__(self,points,goods,filename=None):
        super().__init__(points,goods,filename)
        self.goodsType = list(self.goodsType)

    def set(self,population,crossRate,varyRate):
        """
        设置遗传算法的几个参数

        Parameters
        ----------
        population : int
            种群规模
        
        crossRate : float in (0,1)
            遗传时交叉的概率

        varyRate : float in (0,1)
            遗传时变异的概率
        """
        self.crossRate = crossRate
        self.varyRate = varyRate
        self.population = self._generate_population(population)

    def _generate_population(self,M):
        """
        生成初始种群
        生成M个随机解

        Parameters
        ----------
        M: int
            种群规模
        
        Returns
        -------
        population: list of list of int
            生成的初始解，是一个长度为M的列表；
            每一个项是一个列表，长度为self.goods;即随机遍历得到的一个实例路线；
        """
        population = []
        # 最终返回的Population 应该是一个M项的列表；每一项内容是一个sPoints，为一个解经过点的顺序
        for _ in range(M):
            # 考虑的简单一些，每一个解直接是每一种商品选一个点组成的，相当于没有考虑一类商品过多次的情况
            sPoints = []
            # 一个解的组成
            for opGoods in self.goodsType:
                # 对goodsType中每一个项，即可选的goods
                sPoints.append(np.random.choice(opGoods))
            np.random.shuffle(sPoints)
            population.append(sPoints)
        return population

    def findPoints(self,old_point):
        """
        输入一个点的坐标，返回其对应的商品所有可选坐标点
        为了方便变异函数实现功能

        Parameters
        ----------
        old_points: int
            要查询的点对应序号
        
        Returns
        -------
        goods: list of int
            查询得到的结果，返回与对应点具有相同商品种类的列表；

        例如[[0,2],[1,3,4],[5,6]]
        这样的一个goodsType
        输入findPoints(3)返回的结果是[1,3,4]
        """
        if old_point >= self.points:
            print("Out of Index")
            exit(1)
        for goods in self.goodsType:
            if old_point in goods:
                return goods

    def _calculate_cost(self):
        """
        计算当前种群各个个体的适应度
        
        Returns
        -------
        cost : list of int
            长度为种群规模的列表，每一项是对应个体的适应度
        """
        cost = []
        for sPoint in self.population:
            singleCost = 0
            for i in range(self.goods):
                singleCost += self.graph[sPoint[i],sPoint[(i+1)%self.goods]]
            cost.append(singleCost)
        return cost

    def selection(self,cost,func):
        """
        根据原始种群的cost，和计算代价的函数func选择新的种群成员；
        返回选择出的新成员

        Parameters
        ----------
        cost : 长度为种群规模的列表
            适应度列表，每一项值为对应序号个体的适应度值
        func : 函数
            用于计算适应度的函数

        Returns
        -------
        newM : list of list
            根据概率后选择的新种群

        """
        prob = []
        for i in cost:
            prob.append(func(i))
        
        sum_prob = sum(prob)
        for i in range(len(cost)):
            prob[i] = prob[i]/sum_prob

        idx = [x for x in range(len(cost))]

        newM = []
        for _ in range(len(cost)):
            newM.append(self.population[np.random.choice(idx,p=prob)])
        return newM


    def _merge(self,a,b,crossPoint):
        """
        将两个交叉的样本进行合并
        解决冲突的方法是将交叉部分已经覆盖到的商品除去，剩余商品采用原本个体的顺序进行组合

        Parameters:
        ----------
        a : list of int
            要合并的个体之一
        
        b : list of int
            要合并的个体之一

        crossPoint : int
            交叉坐标

        Returns:
        -------
        new_a : list of int
            完成交叉之后的个体a
        
        new_b : list of int
            完成交叉之后的个体b

        """
        if crossPoint > len(a) or crossPoint > len(b):
            print("交叉点超过数组界限！")
            exit(1)
        
        new_a = []
        new_b = []

        idx_a = [x for x in range(self.goods)]
        idx_b = idx_a.copy()
       
        aType = []
        bType = []
        # 得到的aType是a中各个点的商品种类列表
        for pointidx in range(len(a)):
            for goods in self.goodsType:
                if a[pointidx] in goods:
                    aType.append(self.goodsType.index(goods))
                    break

        for pointidx in range(len(b)):
            for goods in self.goodsType:
                if b[pointidx] in goods:
                    bType.append(self.goodsType.index(goods))
                    break

        a0 = a[:crossPoint]
        b0 = b[:crossPoint]

        for point in range(len(a0)):
            for goods in self.goodsType:
                if a0[point] in goods:
                    idx_b.append(bType[point])

        for point in range(len(b0)):
            for goods in self.goodsType:
                if b0[point] in goods:
                    idx_a.append(aType[point])

        for pointidx in range(len(aType)):
            if aType[pointidx] in idx_a:
                # 如果这个货品没有在b交叉来的染色体中
                new_a.append(a[pointidx])
        
        for pointidx in range(len(bType)):
            if bType[pointidx] in idx_b:
                new_b.append(b[pointidx])

        new_a = new_a + b[crossPoint:]
        new_b = new_b + a[crossPoint:]

        return new_a,new_b


    def _vary(self,M):
        """
         内部方法，对种群进行变异和交叉

         Parameters:
         ----------
         M : list of list of int
            原种群，结构是一系列解的列表
            每一个子项是一个解

        Returns
        -------
        newM : list of list of int
            经过变异和交叉之后的新种群

        """
         
        varyM = []
        # 变异后的种群
        for individual in M:
            if  self.varyRate > np.random.rand():
                tmp_individual = []
                vary_point = np.random.choice(individual)
                vary_point_idx = individual.index(vary_point)
                tmp_individual+=individual[:vary_point_idx]
                opPoints = self.findPoints(vary_point)
                tmp_individual.append(np.random.choice(opPoints))
                tmp_individual+=individual[vary_point_idx+1:]
                varyM.append(tmp_individual)
            else:
                varyM.append(individual)

        newM = []
        while varyM != []:
            a = random.choice(varyM)
            varyM.remove(a)
            if varyM==[]:
                newM.append(a)
                return newM
                # 种群规模为单数的情况，最终可能剩下一个a
            b = random.choice(varyM)
            varyM.remove(b)
            if self.crossRate > np.random.rand():
                crossPoint = np.random.randint(1,self.goods)
                a1,b1 = self._merge(a,b,crossPoint)
                newM.append(a1)
                newM.append(b1)
            else:
                newM.append(a)
                newM.append(b)
        return newM

    def fit(self,iteration):
        """
        输入迭代次数进行遗传算法的迭代
        无返回值，每一轮迭代的最优结果保存在self.result中

        Parameters
        ----------
        iteration : int
            迭代次数

        """
        for _ in range(iteration):
            cost=self._calculate_cost()
            self.result.append(min(cost))
            f = lambda x: 1/x
            # 选择时决定各个染色体被选中概率的函数
            # 由于cost越小，效果越好，应该设置一个单调减函数
            # 这里首先以1/x为例试一下效果

            newM = self.selection(cost,f)
            # 暂时的新的种群
            newM = self._vary(newM)
            # 经过变异和交叉
            self.population = newM


g = Genetic(39,25)
g.set(10,0,0.3)
g.fit(100)
print(g.result)