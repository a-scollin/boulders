from re import L


dim = ['N.','S.','E.','W.']

for d1 in dim:
    print(d1)
    for d2 in dim:
        print(d1+d2)
        for d3 in dim:
            print(d1+d2+d3)