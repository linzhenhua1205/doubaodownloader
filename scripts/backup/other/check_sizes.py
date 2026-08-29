import os
d = "cnblogs_articles_test"
for f in os.listdir(d):
    size = os.path.getsize(os.path.join(d, f))
    print(f"{f}: {size/1024:.1f} KB")