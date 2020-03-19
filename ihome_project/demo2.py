# class Demo(object):
#     def __init__(self):
#         self.name = 'zhangsan'
#         self.age = 12
#
#     def __str__(self):
#         return self.name
#
# # dict = {'b': 12, 'a': 13, 'c': 14, 'd': 15}
# print(dict.items())
# print(sorted(dict.items(), key=lambda x: x[1]))
# import multiprocessing
# import time
#
#
# # 定义进程所需要执行的任务
# def task():
#     for i in range(10):
#         print("任务执行中...")
#         time.sleep(0)
#
# if __name__ == '__main__':
#     # 创建子进程
#     sub_process = multiprocessing.Process(target=task)
#     sub_process.start()
#
#     # 主进程延时0.5秒钟
#     time.sleep(0)
#     print('xixi')
#     exit()
#     print('haha')
# import multiprocessing
# import time
#
#
# # 定义进程所需要执行的任务
# def task():
#     for i in range(10):
#         print("任务执行中...")
#         time.sleep(0.2)
#
# if __name__ == '__main__':
#     # 创建子进程
#     sub_process = multiprocessing.Process(target=task)
#     # 设置守护主进程，主进程退出子进程直接销毁，子进程的生命周期依赖与主进程
#     # sub_process.daemon = True
#
#     sub_process.start()
#
#     time.sleep(0.5)
#     print("over")
#     # 让子进程销毁
#     sub_process.terminate()
#     exit()
# import threading
# import time
#
# def task():
#     time.sleep(1)
#     print('当前线程：',threading.current_thread().name)
#
# if __name__ == '__main__' :
#
#     for _ in range(5):
#         sub_thread = threading.Thread(target= task)
#         sub_thread.start()
#
# import threading
#
# g_num = 0
#
#
# def sum_num1():
#     # for i in range(1000000):
#     #     global g_num
#     #     g_num += 1
#
#     print('sum1:')
#
#
# def sum_num2():
#     # for i in range(1000000):
#     #     global g_num
#     #     g_num += 1
#
#     print('sum2:')
#
# def sum_num3():
#     # for i in range(1000000) :
#     #     global g_num
#     #     g_num += 1
#
#     print('sum3:')
#
# if __name__ == '__main__':
#     while True:
#         sub_thread1 = threading.Thread(target=sum_num1, name='mythread1',daemon=True)
#         sub_thread2 = threading.Thread(target=sum_num2, name='mythread2',daemon=True)
#         sub_thread3 = threading.Thread(target=sum_num3, name='mythread3',daemon=True)
#
#         sub_thread1.start()
#
#         sub_thread2.start()
#
#         sub_thread3.start()
#
#
#
#
# def make_div(func):
#     """对被装饰的函数的返回值 div标签"""
#     def inner(*args, **kwargs):
#         return "<div>" + func() + "</div>"
#     return inner
#
#
# def make_p(func):
#     """对被装饰的函数的返回值 p标签"""
#     def inner(*args, **kwargs):
#         return "<p>" + func() + "</p>"
#     return inner
#
#
# # 装饰过程: 1 content = make_p(content) 2 content = make_div(content)
# # content = make_div(make_p(content))
# @make_div
# @make_p
# def content():
#     return "人生苦短"
#
# result = content()
#
# print(result)

# class Person(object):
#
#     def __init__(self):
#         self.__age = 0
#
#     # 装饰器方式的property, 把age方法当做属性使用, 表示当获取属性时会执行下面修饰的方法
#     @property
#     def age(self):
#         return self.__age
#
#     # 把age方法当做属性使用, 表示当设置属性时会执行下面修饰的方法
#     @age.setter
#     def age(self, new_age):
#         if new_age >= 150:
#             print("成精了")
#         else:
#             self.__age = new_age
#
# # 创建personmy_generator
# p = Person()
# print(p.age)
# p.age = 100
# print(p.age)
# p.age = 1000
# li = (1, 2, 4, 8)
# s = [('name', i) for i in li]
# print(type(s))

# my_generator = (i * 2 for i in range(5))
# print(my_generator)
# print(next(my_generator))
# print(next(my_generator))
# print(next(my_generator))
# print(next(my_generator))



# def fibonacci(num):
#     a = 0
#     b = 1
#
#     current_index = 0
#
#
#     while current_index < num:
#         result = a
#         a, b = b, a + b
#         current_index += 1
#         yield result
#
# fib = fibonacci(6)
#
# for value in fib:
#     print(value)

# def fib
# def my_num(x):
#     if x <= 1:
#         return x
#
#     else:
#         return (my_num(x-2) + my_num(x-1))
#
# for i in range(0, 10):
#     print(my_num(i))

# import re
#
# result = re.match('haha','haha456')
# s = result.group()
# print(result)
# print(s)

# import re
# #
# ret = re.match('^#\w*#$', '#幸福是奋斗出来的#')
# print(ret.group())
#
import re

li = ["apple", "banana", "orange", "pear"]
# 遍历，单独匹配每个值
for value in li:
    ret = re.match('apple|pear', value)
    if ret:
        print("%s是我想要的" % ret.group())

    else:
        print("%s不是我要的" % value)
