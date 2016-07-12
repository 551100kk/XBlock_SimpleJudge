from easyprocess import EasyProcess
s = EasyProcess('timeout 5 bash -c "./a.out < out.txt > ooo"').call(timeout=2)
print(s)