import time

# 現在の時刻をフォーマットして表示
local_time = time.localtime()
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
hour_minits_time = time.strftime("%H:%M", local_time)
print(formatted_time)  
print(hour_minits_time)

# 2025-03-20 16:25:35
