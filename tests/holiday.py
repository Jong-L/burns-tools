import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 准备数据
dates = [datetime(2025, 9, 1), datetime(2025, 9, 2), datetime(2025, 9, 3), datetime(2025, 9, 4)]
values = [0.7, 1.8, 0.9, 2.4]

# 创建图形和坐标轴
fig, ax = plt.subplots()

# 绘制数据
ax.plot(dates, values)

# 格式化日期横轴
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# 自动调整日期标签使其不重叠
fig.autofmt_xdate()

# 显示图形
plt.show()