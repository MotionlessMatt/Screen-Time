import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

# Connect to local database file
db = sqlite3.connect("data.db")
cur = db.cursor()

# Obtain a list of all entries
entries = cur.execute(f"SELECT * FROM screentime").fetchall()

# Create a modified version of entries without time.
data_points = []
for i in entries:
    i = list(i)
    i[1] = datetime.fromisoformat(i[1]).date()
    i[3] = i[3]/60 # Convert to minutes instead of seconds
    data_points.append(i)

# Create DataFrame and modify it for visualization of time spent per app per day
df = pd.DataFrame(data_points, columns=["App", "Start Date", "End Date", "Total Minutes"])
screentime_chart = df.groupby(['Start Date', 'App'])['Total Minutes'].sum().sort_values(ascending=False).unstack().fillna(0)
screentime_chart.plot(kind='bar', stacked=True, width=0.6)

# Matplotlib chart
plt.title('Screen Time by Day')
plt.xticks(rotation=0)
plt.ylabel("Minutes")
# Uncomment to show chart: plt.show()

# Plotly chart (This is the preferred chart for pure visualization.)
pd.options.plotting.backend = "plotly"
plotly_chart = screentime_chart.plot.bar(title="Screen Time by Day", labels={"value": "Time Elapsed (minutes)"})
plotly_chart.show()
