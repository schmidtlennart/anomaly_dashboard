## scope test




a = 21

def add(x):
    x = x + 1

def add_mutable(x):
    x = [i+1 for i in x]

add(a)
print(a) # 21

add_mutable([a])
print(a) # 21

a = 21

def add():
    global a
    a = a + 1

def add_mutable():
    global a
    a = a + 1

add()
print(a) # 22

add_mutable()
print(a) # 23


# create test object
import pandas as pd
class Test:
    pass

Test.a = 21
Test.b = pd.DataFrame([1,2,3,4,5])


Test.b.mean()

from isewer_ast.callbacks import testcb

testcb(Test)

Test.a

