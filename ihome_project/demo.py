# dict1 = {'name':'haha'}
# # print(dict1.get('name'))
# dict1['d'] = 'xx'
# print(dict1)
# c = list()
# for i in range(10):
#     c.append(i)
# print(c)

import functools


#
# class Demo(object):
#     def __init__(self, a=None):
#         self.a = a
#
#     def A(self):
#         return self.a is None
#
# s = Demo()
# print(s.A())
# s.hah = 'haha'
# print(s.hah)

# a = [1, 2, 3, 4]
# b = [2, 4, 5]
# c = set(a) | set(b)
# def select_sort(li):
#     # 首先定义一个最小值的初始下标，然后与数据集里面的值进行比较，下标的值换成小的一方的下		标
#     n = len(li)
#
#     for j in range(0, n-1):
#         min_index = j
#         for i in range(j+1, n):
#             if li[i] < li[min_index]:
#                 min_index = i
#         li[j], li[min_index] = li[min_index], li[j]
#
# li = [54,226,31,77,77,31,44,55,20]
# select_sort(li)
# print(li)

# def selection_sort(alist):
#     n = len(alist)
#     # 需要进行n-1次选择操作
#     for i in range(n-1):
#         # 记录最小位置
#         min_index = i
#         # 从i+1位置到末尾选择出最小数据
#         for j in range(i+1, n):
#             if alist[j] < alist[min_index]:
#                 min_index = j
#         # 如果选择出的数据不在正确位置，进行交换
#         if min_index != i:
#             alist[i], alist[min_index] = alist[min_index], alist[i]
#
# alist = [54,226,93,17,77,31,44,55,20]
# selection_sort(alist)
# # print(alist)
# import time
# #
# #
# # def shell_sort(li):
# #     n = len(li)
# #     gap = 4
# #     while gap > 0:
# #         for j in range(gap, n):
# #             for i in range(j, 0, -gap):
# #                 # while (i - gap) >= 0:
# #                 if li[i] < li[i - gap]:
# #                     li[i], li[i - gap] = li[i - gap], li[i]
# #                     # i -= gap
# #                 else:
# #                     break
# #         gap //= 2
# #
# #
# # if __name__ == "__main__":
# #     li = [4, 6, 52, 9, 49, 55, 455, 33]
# #     start_time = time.time()
# #
# #     shell_sort(li)
# #     end_time = time.time()
# #     print(end_time - start_time)
# #     print(li)
# # for i in range(5, 0, -1):
# #     print(i)
#
# def shell_sort(li):
#     n = len(li)
#     gap = 4
#     while gap > 0:
#         for i in range(gap, n):
#             while (i - gap) >= 0:
#                 if li[i] < li[i - gap]:
#                     li[i], li[i - gap] = li[i - gap], li[i]
#                     i -= gap
#                 else:
#                     break
#         gap //= 2
#
#
# if __name__ == "__main__":
#     li = [4, 6, 52, 9, 49, 55, 455, 33]
#     start_time = time.time()
#
#     shell_sort(li)
#     end_time = time.time()
#     print(end_time - start_time)
#     print(li)


# def merge_sort(alist):
#     if len(alist) <= 1:
#         return alist
#     # 二分分解
#     num = len(alist) // 2
#     left = merge_sort(alist[:num])
#     right = merge_sort(alist[num:])
#
#     # left与right的下标指针
#     l, r = 0, 0
#     result = []
#     while l < len(left) and r < len(right):
#         if left[l] <= right[r]:
#             result.append(left[l])
#             l += 1
#         else:
#             result.append(right[r])
#             r += 1
#     result += left[l:]print(name[:5])print(name[::-1])
#     result += right[r:]
#     return result
#
#
# alist = [54, 26, 93, 17, 77, 31, 44, 55, 20]
# sorted_alist = merge_sort(alist)
# print(sorted_alist)
#
# li = ['1', '3', '5', '7', '9']
# # li[0] = 'aha'
# # li.sort(reverse=True)
# li2 = li
# print(li2)
# print(li)

# print(li.count(1))
# st = 'ishifhsahfi'
# print(('i' not in st))
# 获取列表的第二个元素
# def takeSecond(elem):
#     return elem[0]
#
# # 列表
# random = [(2, 2), (3, 4), (4, 1), (1, 3)]
#
# # 指定第二个元素排序
# random.sort(key=takeSecond)
#
# # 输出类别
# print ('排序列表：', random)


# import random
#
# teacher = [1, 2, 3, 4, 5, 6, 7, 8]
# offer_room1 = []
# offer_room2 = []
# offer_room3 = []
# offer_room = [offer_room1, offer_room2, offer_room3]
# print(random.choice(offer_room))
#
# for i in teacher:
#     random.choice(offer_room).append(i)
# print(offer_room1, offer_room2, offer_room3)

# a=[1,3,5,6,7]                # 将序列a中的元素顺序打乱
# random.shuffle(a)
# print(a)

# dict1 = {'name':'tom','Tianmei':'keng'}
# for a,b in dict1.items():
#     print(a)
# print(list(zip([1, 2,3], [3, 4,5], [5, 6,5], [7, 8,5])))
# dict1= {'name':4}
# dict2= {'age':2}
# dict1.update(dict2)
# print(dict1)

# from gevent import spawn, joinall, monkey
#
# monkey.patch_all()
#
# import time
#
#
# def task(pid):
#     """
#     Some non-deterministic task
#     """
#     time.sleep(1)
#     print('Task %s done' % pid)
#
#
# def synchronous():
#     for i in range(10):
#         task(i)
#
#
# def asynchronous():
#     g_l = [spawn(task, i) for i in range(10)]
#     joinall(g_l)
#
#
# if __name__ == '__main__':
#     print('Synchronous:')
#     synchronous()
#
#     print('Asynchronous:')
#     asynchronous()
# filter(lambda x: x >= 5, [2, 9, 8, 7, 5])
# fn2 = lambda x:x+100functools.reduce(lambda x,y:x**y,[1,2,3,4,5])
# # print(fn2(10))
# print((lambda **kwargs: kwargs)(name='python', age=20))

# 计算list1中各个数字的二次方

# print(list(map(lambda x: x ** 2, [1,2,3,4,5])))
#
# print(functools.reduce(lambda x, y: x ** y, [1, 2, 3, 4, 5]))
# list1 = [2, 9, 8, 7, 5]
# list2 = list(filter(lambda x: x >= 5, list1))
# print(list1)
# print(list2)

# class Base(object):
#     def __init__(self):
#         self.name = 'fan'
#
#     def __make_coke(self):
#         print('haha')
#
#     def make(self):
#         print('xixi')
#
#
# class Child(Base):
#     def make_super(self):
#         super(Child, self).make()

# Child()._Base__make_coke()

# from multiprocessing import Process
# import time
#
#
# def dance():
#     for i in range(5):
#         print('跳舞中……')
#         time.sleep(0.5)
#
#
# def sing():
#     for i in range(5):
#         print('唱歌中……')
#         time.sleep(0.5)
#
#
# if __name__ == '__main__':
#     dance_process = Process(target=dance, name='my_process1')
#     sing_process = Process(target=sing)
#
#     dance_process.start()
#     sing_process.start()
import multiprocessing
import time
import os


def dance():
    print('dance:', os.getpid())
    print('dance的父进程:', os.getppid())
    print('dance:', multiprocessing.current_process())

    for i in range(5):
        print('跳舞中……')
        time.sleep(0.5)
        os.kill(os.getpid(), 9)


def sing():
    print('sing:', os.getpid())
    print('sing:', multiprocessing.current_process())

    for i in range(5):
        print('唱歌中……')
        time.sleep(0.5)


if __name__ == '__main__':
    print('main:', os.getpid())
    print('main:', multiprocessing.current_process())

    dance_process = multiprocessing.Process(target=dance, name='my_process1')
    sing_process = multiprocessing.Process(target=sing, name='my_process2')
    dance_process.start()
    sing_process.start()