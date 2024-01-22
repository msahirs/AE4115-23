import itertools
import numpy as np
from matplotlib import pyplot as plt

def gen_int_range(n):
    return [i for i in range(n)]

A = gen_int_range(4)
B = gen_int_range(4)

comb = [item for item in itertools.product(A,B)]

comb = np.array(comb)
AB_int = (comb[:,0] * comb[:,1])%4
comb = np.hstack((comb, AB_int[:,np.newaxis]))
print(comb)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

ax.scatter(comb[:,0],comb[:,1],comb[:,2],c=comb[:,2],cmap='twilight',edgecolors='k')
ax.legend()
plt.show()
