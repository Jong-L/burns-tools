"""获取从一段时间内每天的农历日期，不包括年月"""
from datetime import datetime, timedelta,date,time
from itertools import accumulate
import json

from zhdate import ZhDate,CHINESENEWYEAR,CHINESEYEARCODE
import chinese_calendar as calendar

#写一个自己的from_datetime方法，因为原方法有bug
CHINESENEWYEAR.append("21010129")
def from_datetime(dt:datetime):
    """从公历日期生成农历日期
    
    Arguments:
        dt {datetime} -- 公历的日期
    
    Returns:
        ZhDate -- 生成的农历日期对象
    """
    # 获取公历年份
    lunar_year = dt.year
    # 判断当前公历日期是否在当年农历新年之前，如果在则农历年份减1
    if (datetime.strptime(CHINESENEWYEAR[lunar_year-1900], '%Y%m%d') - dt).days > 0:
        lunar_year -= 1
    # 获取当年农历新年的日期
    newyear_dt = datetime.strptime(CHINESENEWYEAR[lunar_year-1900], '%Y%m%d')
    # 计算距离当年农历新年的天数
    days_passed = (dt - newyear_dt).days
    # 获取当年农历年份的编码
    year_code = CHINESEYEARCODE[lunar_year - 1900]
    # 解码农历年份编码，获取每个月的天数
    month_days = ZhDate.decode(year_code)

    # 遍历累计的天数，确定农历月份和日期
    for pos, days in enumerate(accumulate(month_days)):
        if days_passed + 1 <= days:
            month = pos + 1
            lunar_day = month_days[pos] - (days - days_passed) + 1
            break

    # 判断是否为闰月
    leap_month = False
    # 根据年份编码确定月份
    if (year_code & 0xf) == 0 or month <= (year_code & 0xf):
        lunar_month = month
    else:
        lunar_month = month - 1

    # 判断是否为闰月
    if (year_code & 0xf) != 0 and month == (year_code & 0xf) + 1:
        leap_month = True
    
    # 返回生成的农历日期对象
    return ZhDate(lunar_year, lunar_month, lunar_day, leap_month)

ZHNUMS = '零一二三四五六七八九十'
# 获取开始到结束日期之间的所有节气
def get_solar(start_date,end_date):
    solar_terms=calendar.get_solar_terms(start_date, end_date)
    date_times=set()
    solar_terms_dict={}
    for i in range(len(solar_terms)):
        date=solar_terms[i][0]
        date_time=datetime.combine(date,time.min)
        date_times.add(date_time)
        solar_terms_dict[date_time]=solar_terms[i][1]
    return date_times,solar_terms_dict
if __name__ == '__main__':
    start_date=ZhDate.to_datetime(ZhDate(1900,1,1))
    end_date=ZhDate.to_datetime(ZhDate(2100,12,29))
    date_trans_dict={}#{%y-%m-%d:zh_day}
    date_times,solar_terms_dict=get_solar(start_date.date(),date(2099,12,29))
    #从start_date到end_date
    for i in range((end_date-start_date).days+1):
        date=start_date+timedelta(days=i)
        #是否是节气
        if date in date_times:
            zh_day=solar_terms_dict[date]
        else:
            zh_date=from_datetime(date)
            if zh_date.lunar_day <= 10:
                zh_day = f'初{ZHNUMS[zh_date.lunar_day]}'
            elif zh_date.lunar_day < 20:
                zh_day = f'十{ZHNUMS[zh_date.lunar_day - 10]}'
            elif zh_date.lunar_day == 20:
                zh_day = '二十'
            elif zh_date.lunar_day < 30:
                zh_day = f'二十{ZHNUMS[zh_date.lunar_day - 20]}'
            else:
                zh_day = '三十'
        
        date_str=date.strftime('%Y-%m-%d')
        date_trans_dict[date_str]=zh_day
    # end for
    start_date_str=start_date.strftime('%Y-%m-%d')
    end_date_str=end_date.strftime('%Y-%m-%d')
    dict={
        'start_date':start_date_str,
        'end_date':end_date_str,
        'date_trans_dict':date_trans_dict
    }
    with open('data/date_trans_dict.json','w',encoding='utf-8') as f:
        json.dump(dict,f,ensure_ascii=False,indent=4)