import os
p = r'd:\123\cowkb\.git\index.lock'
print('exists:', os.path.exists(p))
try:
    os.remove(p)
    print('removed!')
except Exception as e:
    print('failed:', e)
