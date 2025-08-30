import chinese_calendar as calendar
import datetime

# 检查某天是否为节假日
today = datetime.date(2024, 10, 1)

is_holiday = calendar.is_holiday(today)
print(is_holiday)  # 返回 True 或 False

on_holiday, holiday_name = calendar.get_holiday_detail(today)
print(on_holiday, holiday_name)  # 返回 True 或 False，节假日名称

# 获取某天的节气
end_of_day = datetime.date(2025, 8, 31)
term = calendar.get_solar_terms(datetime.date(1900,1,31), datetime.date(2099,12,29))
print(term)  # 输出节气名称，如"处暑"
