name = '1323Q17-1'
print(name[:4])
name2 = '973Q62-1'
print(name2[:3])
name3 = '1678Q84-1'
print(name3[4:-2])
names = name.split('-')[0]
print(names)
name4 = 'frc1678'
print(name4[3:])
a = {'aslll' : 'asda', 'asfd': ['asjd', 'asd', 'dsa']}
print(a.items())

q = []
w = ['asd', 'gsd', 'rdd']
e = ['n', 'as', 'ved']
q += w
q += e
print(q)
dss = []
for i in w:
	i = i[1:]
	dss.append(i)
	print(i)
print(dss)
n = 's'
s = 'n'
n += s + 's'
print(n)
