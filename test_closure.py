def wrap_func(c, d, **kwargs):
    def closure_func(a, b):
        print(c + d)
    return closure_func

args = {"a":1, "b":2, "c":3, "d":4, "e":5}
closure = wrap_func(**args)
closure(args['a'], args['b'])  # This will print 7 (c+d)