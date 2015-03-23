'''
Created on 9.1.2015

@author: Jaakko Leppakangas
'''

class MyException(Exception):
    """Derived class from exception"""

try:
    raise MyException('my detailed description')
except MyException as my:
    print my # outputs 'my detailed description'
