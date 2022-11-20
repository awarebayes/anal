# %%

import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('~/Downloads/avg_fps_per_nthreads_orig.csv', header=None, names=['n_потоков', 'fps'])

avg_fps = df.groupby('n_потоков').mean()

print(avg_fps)
plt.rcParams.update({'font.size': 14}) # must set in top

# show average fps per nthreads

avg_fps.plot(kind='bar', title='Количество FPS в зависимости от количества потоков', legend=False)
plt.show()