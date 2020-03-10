import pandas as pd
import numpy as np

df = pd.DataFrame()
for i in range(5):
    for j in range(3):
        df['Run'+str(i)+' '+'Channel'+str(j)] = [0, 0, 0]
li = [str(i) for i in np.arange(0, 2, 0.02)]
df2 = pd.DataFrame(index=pd.Series(np.arange(0, 2, 0.02)))
df2['Temp'] = range(0, 100)
print(df2.iloc[int(0.022/0.02)]['Temp'])