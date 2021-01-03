# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class Algorithm():
    def __init__(self,points,goods,filename=None):
        self.points = points
        self.goods = goods
        self.result = []
        
        if filename == None:
            self.graph = np.load('Graph_'+str(self.points)+'.npy',allow_pickle=True)
            self.goodsType = np.load('GoodsType_'+str(self.points)+'_'+str(self.goods)+'.npy',allow_pickle=True)
            self.typeList = np.load('TypeList_'+str(self.points)+'_'+str(self.goods)+'.npy',allow_pickle=True)
        else:
            self.graph = np.load(filename+'_Graph.npy',allow_pickle=True)
            self.goodsType = np.load(filename+'_GoodsType.npy',allow_pickle=True)
            self.typeList = np.load(filename+'_TypeList.npy',allow_pickle=True)

    def fit(self,iteration):
        """
        各个算法迭代的过程，求出最优解的过程，这个过程中将每一轮的最优解记录在self.result数组中
        """
        pass

    def show_result(self):
        """
        画出迭代图像
        """
        sns.set(style="white",palette="muted")
        x = [i+1 for i in range(len(self.result))]
        y = self.result
        
        plt.plot(x,y)
        plt.show()