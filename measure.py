from time import time

'''
 Simple decorator measuring time of function exevution
 Usage:
    @measureTime
    def f(a, b, c):
        pass
'''

def measureTime(func):
    def wrapped(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        print('\033[94m', end='')
        print('Execution time for ' + func.__name__ + ':', '%f'%round(time()-start, 15))
        print('\033[0m', end='')
        return ret

    return wrapped


if __name__ == 'main':
    pass
