from random import choice, random
import sqlite3
import pandas as pd
from datetime import datetime

db = sqlite3.connect("data.db")
cur = db.cursor()
import matplotlib.pyplot as plt
import cufflinks as cf

cf.set_config_file(theme='pearl')

# WHERE start BETWEEN '{datetime.now().date()} 00:00:00.00' AND '{datetime.now().date()} 24:00:00'"
entries = cur.execute(f"SELECT * FROM screentime").fetchall()

data = {}
for i in entries:
    if i[0] in data:
        data[i[0]] += i[3]/60
    else:
        data.update({i[0]: i[3]/60})

data_points = []
for i in entries:
    i = list(i)
    i[1] = datetime.fromisoformat(i[1]).date()
    i[3] = i[3]/60
    data_points.append(i)
df = pd.DataFrame(data_points, columns=["App", "Start Date", "End Date", "Total Seconds"])
agg_tips = df.groupby(['Start Date', 'App'])['Total Seconds'].sum().sort_values(ascending=False).unstack().fillna(0)
agg_tips.sort_values([i for i in data])

print(agg_tips.to_string())

# Very simple one-liner using our agg_tips DataFrame.
agg_tips.plot(kind='bar', stacked=True)

# Just add a title and rotate the x-axis labels to be horizontal.
plt.title('Screen Time by Day')
plt.xticks(rotation=0, ha='center')

plt.show()