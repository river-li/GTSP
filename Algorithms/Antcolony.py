from Algorithms  import Algorithm
import numpy as np
import math
import random
from timeit import default_timer as timer

class Antcolony(Algorithm):
    def __init__(self, points, goods, filename=None):
        super().__init__(points, goods, filename)

    def _calculate_singlecost(self,path):
        singleCost = 0
        if len(path) < self.goods:
            return float("inf")

        for i in range(self.goods):
            singleCost += self.graph[path[i],path[(i+1) % self.goods]]
        return singleCost

    def find_best_cost(self,paths):
        bestcost = float("inf")
        for path in paths:
            cost = self._calculate_singlecost(path)
            if cost < bestcost:
                bestcost = cost
        self.result.append(bestcost)
        return bestcost

    def set(self,iteration):
        # m  蚁群规模 , alpha 信息素重要程度因子, beta 启发函数重要程度因子,
        # vol  信息素挥发因子; Q 信息素释放总量，这里选择每走一步，对应边增加一 ;iter_max 最大迭代次数 ,iter 初始值
        m = 100
        alpha = 2
        beta = 2
        vol = 0.5
        Q = 100
        iter_max = iteration
        iter = 1
        return m,alpha,beta,vol,Q,iter_max,iter

    def select_next_point(self,tabulist):
        #计算蚂蚁 k 在t时刻 从i到j的路径选择概率
        #p 描述前一状态i与后一状态j之间的转移概率，就是蚂蚁从第i个城市到第j个城市的概率
        # t 为 i到j 的残留信息素浓度   n 为 i 到 j 的启发信息 一般为 1./d 直接路径的倒数

        #p= math.pow(T,self.alpha)/math.pow(D,self.beta)
        p = 1
        return p


    def update_pheromone(self,Q,m,vol,pheromone_matrix,paths):
        # 三种更新方法，1.每周期更新  2.每步更新Q  3.每步更新Q/L L 为路径长度
        # 这里选择第一种，迭代完一次更新信息素，每次 +1
        # 根据存储的路径增加矩阵中的对应边的信息素
        # 信息素矩阵
        # m 蚂蚁数量, vol 挥发因子, pheromone_matrix 信息素矩阵, paths 记录所有蚂蚁的路径
        paths = paths[:]
        #前一轮信息素挥发
        pheromone_matrix = pheromone_matrix * (1-vol)
        for i in range(m):
            path = paths[i]
            for point in path:
                pheromone_matrix[point, (point + 1) % self.goods] += 1
                pheromone_matrix[(point + 1) % self.goods, point] = pheromone_matrix[point, (point + 1) % self.goods]
        return pheromone_matrix

    def __update_pheromone_gragh(self,Q,m,vol,pheromone_matrix,paths):
        # 获取每只蚂蚁在其路径上留下的信息素
        # 三种更新方法，1.每周期更新  2.每步更新Q  3.每步更新Q/L L 为路径花费
        # 这里选择第一种，迭代完一次更新信息素，每次Q/L
        # 根据存储的路径增加矩阵中的对应边的信息素
        # 信息素矩阵
        # m 蚂蚁数量, vol 挥发因子, pheromone_matrix 信息素矩阵, paths 记录所有蚂蚁的路径

        temp_pheromone = [[0.0 for col in range(self.points)] for raw in range(self.points)]
        for path in paths:
            for i in range(1, self.goods):
                start, end = path[i - 1], path[i]
                # 在路径上的每两个相邻城市间留下信息素，与路径总距离反比
                temp_pheromone[start][end] += Q / self._calculate_singlecost(path)
                temp_pheromone[end][start] = temp_pheromone[start][end]

        # 更新所有城市之间的信息素，旧信息素衰减加上新迭代信息素
        for i in range(self.points):
            for j in range(self.points):
                pheromone_matrix[i][j] = pheromone_matrix[i][j] * vol + temp_pheromone[i][j]
        return pheromone_matrix

    #随机初始化，把蚂蚁随机的放置
    def locate_ants(self,m):
        #m为蚂蚁数量
        m = m
        tabu_lists = []
        paths = []
        for i in range(m):
            start = np.random.randint(0, self.goods)
            spoint = np.random.choice(self.goodsType[start])
            path = []
            tabu_list = []
            path.append(spoint)
            tabu_list.append(start)
            tabu_lists.append(tabu_list)
            paths.append(path)
        return tabu_lists, paths

    def fit(self,iteration):
        m,alpha,beta,vol,Q,iter_max,iter = self.set(iteration)
        # pheromone_matrix 存放信息素的矩阵，起始为1
        pheromone_matrix = np.ones((self.points,self.points))
        while iter < iter_max:

            # 每一轮的迭代都要蚂蚁走完步长为L的路径
            # 记录每一轮的最优解
            # tabu_lists 存储每一个蚂蚁的tabulist，这里应该存储商品信息，已经走过的城市可以购买哪些商品,每一次迭代要清空
            # paths 即所有蚂蚁的路径
            tabu_lists, paths = self.locate_ants(m)
            for i in range(1,self.goods):
                # 计算蚂蚁 k 在t时刻 从i到j的路径选择概率
                # p 描述前一状态a与后一状态b之间的转移概率，就是蚂蚁从第a个城市到第b个城市的概率
                # t 为 a到b 的残留信息素浓度   n 为 a 到 b 的启发信息 一般为 1./d 直接路径的倒数
                for j in range(m):
                    #这里需要修改tabu_list，所以引用就可以
                    tabu_list = tabu_lists[j]
                    path = paths[j]
                    temp = set(np.arange(self.goods))
                    # remain_list 剩余未买的商品
                    remain_list = list(temp - set(tabu_list))
                    # 计算所有的未访问点的 p值
                    p = []
                    sum_p = 0
                    cur_point = path[-1]
                    # 用于找goods 和 pionts 的列表，存储元组 (goods,points)
                    find = []
                    for k in remain_list:
                        for l in self.goodsType[k]:
                            cur_p = math.pow(pheromone_matrix[cur_point][l],alpha)*math.pow(1.0/self.graph[cur_point][l],beta)
                            sum_p += cur_p
                            p.append(cur_p)
                            find.append((k,l))
                    # 这里需要解决 每个point 的概率 和 goods 要对应  这样才好加入tabulist
                    # 轮盘赌算法选择下一个
                    # 轮盘选择城市
                    total_prob = sum_p
                    next_city = -1
                    if total_prob > 0.0:
                        # 产生一个随机概率,0.0-total_prob
                        temp_prob = random.uniform(0.0, total_prob)
                        for n in range(len(p)):
                             # find中point应该和p中的访问概率 一一对应
                                # 轮次相减
                            temp_prob -= p[n]
                            if temp_prob <= 0.0:
                                next_city = find[n][1]
                                path.append(next_city)
                                tabu_list.append(find[n][0])
                                break
                    if next_city == -1:
                        # 轮盘赌没选出来下一个目的地，具体原因暂时不知道 ，随机选一个
                        # 原因是sum_p结果为0.0 推测因为信息素过小的原因
                        next_goods = np.random.choice(remain_list)
                        next_city = np.random.choice(self.goodsType[next_goods])
                        path.append(next_city)
                        tabu_list.append(next_goods)
            #更新信息素
            pheromone_matrix = self.__update_pheromone_gragh(Q,m,vol,pheromone_matrix,paths)
            # 选择这一轮中最优解
            cur_bestcost = self.find_best_cost(paths)

            if iter ==1 :
                bestcost = cur_bestcost
            else:
                if cur_bestcost < bestcost:
                    bestcost = cur_bestcost
            self.bestresult.append(bestcost)
            iter = iter + 1

tic = timer()


a = Antcolony(39,25)
a.fit(10000)
a.show_result()

toc = timer()

print('cost:',toc - tic) # 输出的时间，秒为单位
