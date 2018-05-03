#Last Updated: 8/26/17
from matplotlib import pyplot as plt
import matplotlib.mlab as m
import csv
import numpy as np

dic = {}
with open('./scoutRankExport.csv') as f:
	reader = csv.DictReader(f)
	for read in reader:
		dic[read['name']] = read['Z-Score']

dic = {k : float(v) for k, v in dic.items()}
keys = sorted(dic.keys(), key = lambda k: dic[k])
for k in keys:
	print(k, str(dic[k]))
mu = np.mean(dic.values())
sigma = np.std(dic.values())
print(mu, '\n', sigma)
plt.hist(dic.values(), normed = True)
x = np.linspace(min(dic.values()), max(dic.values()))
plt.plot(x, m.normpdf(x, mu, sigma))
plt.show()
