"""
课表时间工具模块

定义每节课的时间映射，按以下规则：
早上 8:00 开始上课
- 45分钟小课 + 10分钟课间 + 45分钟小课 = 一大节课 (约1h40m)
- 大节课之间休息30分钟

时间安排：
  第1节  08:00 - 08:45   (上午第一大节-小课1)
  第2节  08:55 - 09:40   (上午第一大节-小课2) → 休息30分钟
  第3节  10:10 - 10:55   (上午第二大节-小课1)
  第4节  11:05 - 11:50   (上午第二大节-小课2) → 午休
  第5节  14:00 - 14:45   (下午第三大节-小课1)
  第6节  14:55 - 15:40   (下午第三大节-小课2) → 休息30分钟
  第7节  16:10 - 16:55   (下午第四大节-小课1)
  第8节  17:05 - 17:50   (下午第四大节-小课2)
"""

# 节次与时间映射
PERIOD_TIMES = {
    1: {'start': '08:00', 'end': '08:45', 'label': '上午第一节'},
    2: {'start': '08:55', 'end': '09:40', 'label': '上午第二节'},
    3: {'start': '10:10', 'end': '10:55', 'label': '上午第三节'},
    4: {'start': '11:05', 'end': '11:50', 'label': '上午第四节'},
    5: {'start': '14:00', 'end': '14:45', 'label': '下午第一节'},
    6: {'start': '14:55', 'end': '15:40', 'label': '下午第二节'},
    7: {'start': '16:10', 'end': '16:55', 'label': '下午第三节'},
    8: {'start': '17:05', 'end': '17:50', 'label': '下午第四节'},
}

# 大节（session）信息：包含哪两小节课，以及该大节的标签
SESSIONS = {
    1: {'periods': (1, 2), 'label': '上午第一大节', 'time_range': '08:00-09:40'},
    2: {'periods': (3, 4), 'label': '上午第二大节', 'time_range': '10:10-11:50'},
    3: {'periods': (5, 6), 'label': '下午第三大节', 'time_range': '14:00-15:40'},
    4: {'periods': (7, 8), 'label': '下午第四大节', 'time_range': '16:10-17:50'},
}

# 星期映射
WEEKDAYS = {
    1: '周一', 2: '周二', 3: '周三', 4: '周四',
    5: '周五', 6: '周六', 7: '周日'
}

TOTAL_PERIODS = 8  # 总节次数
TOTAL_DAYS = 7     # 每周天数


def get_period_time(period_num):
    """获取指定节次的时间信息"""
    return PERIOD_TIMES.get(period_num)


def get_all_periods():
    """获取所有节次的时间信息列表"""
    return [(num, info) for num, info in PERIOD_TIMES.items()]


def get_period_time_range(start_period, end_period):
    """获取从 start_period 到 end_period 的时间范围字符串"""
    start_info = PERIOD_TIMES.get(start_period)
    end_info = PERIOD_TIMES.get(end_period)
    if start_info and end_info:
        return f"{start_info['start']}-{end_info['end']}"
    return None


def get_session_info(period_num):
    """获取指定节次所属的大节信息"""
    for session_id, info in SESSIONS.items():
        if info['periods'][0] <= period_num <= info['periods'][1]:
            return session_id, info
    return None, None


def get_weekday_name(day_num):
    """获取星期名称"""
    return WEEKDAYS.get(day_num, '')


def format_schedule_time(start_period, end_period):
    """
    格式化上课时间显示
    例如: start_period=1, end_period=2 → "08:00-09:40 (第1-2节)"
    """
    time_range = get_period_time_range(start_period, end_period)
    period_range = f"第{start_period}-{end_period}节"
    if time_range:
        return f"{time_range} ({period_range})"
    return period_range


def format_schedule_summary(schedule):
    """
    格式化一条排课记录的简要信息
    返回如: "每周一 08:00-09:40 (第1-2节) 教1-101"
    """
    day_name = get_weekday_name(schedule.day_of_week)
    time_str = format_schedule_time(
        int(schedule.start_time), int(schedule.end_time)
    )
    parts = [f"每{day_name}", time_str]
    if schedule.classroom:
        parts.append(schedule.classroom)
    if hasattr(schedule, 'week_start') and schedule.week_start:
        parts.append(f"第{schedule.week_start}-{schedule.week_end}周")
    return ' '.join(parts)
