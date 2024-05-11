import pm4py
from datetime import timedelta

def n_to_weekday(i):
    weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return dict(zip(range(7), weekday_labels))[i]

def find_calendars(log):
    """
    {resource: {WEEKDAY: (sH,eH)}}
    se quel weekday non si lavora mettere None
    """

    weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    calendars = dict()
    log_df = pm4py.convert_to_dataframe(log)
    log_df['weekday'] = log_df['time:timestamp'].apply(lambda x: n_to_weekday(x.weekday()))
    log_df['hour'] = log_df['time:timestamp'].apply(lambda x: x.hour)

    resources = pm4py.get_event_attribute_values(log, "org:resource").keys()

    for res in resources:
        calendars[res] = dict()
        log_df_res = log_df[log_df['org:resource'] == res]
        for wd in weekday_labels:
            log_df_act_roles_wd = log_df_res[log_df_res['weekday'] == wd]
            if len(log_df_act_roles_wd) == 0:
                calendars[res][wd] = None
            calendars[res][wd] = (log_df_act_roles_wd['hour'].min(), log_df_act_roles_wd['hour'].max())
            if not(calendars[res][wd][0] >= 0):
                calendars[res][wd] = None
    return calendars


def find_calendars_roles(log):
    """
    {role: {WEEKDAY: (sH,eH)}}
    se quel weekday non si lavora mettere None
    """

    weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    calendars = dict()
    log_df = pm4py.convert_to_dataframe(log)
    log_df['weekday'] = log_df['time:timestamp'].apply(lambda x: n_to_weekday(x.weekday()))
    log_df['hour'] = log_df['time:timestamp'].apply(lambda x: x.hour)

    roles = pm4py.get_event_attribute_values(log, "org:role").keys()

    for role in roles:
        calendars[role] = dict()
        log_df_role = log_df[log_df['org:role'] == role]
        for wd in weekday_labels:
            log_df_act_roles_wd = log_df_role[log_df_role['weekday'] == wd]
            if len(log_df_act_roles_wd) == 0:
                calendars[role][wd] = None
            calendars[role][wd] = (log_df_act_roles_wd['hour'].min(), log_df_act_roles_wd['hour'].max())
            if not(calendars[role][wd][0] >= 0):
                calendars[role][wd] = None
    return calendars
    

def return_time_from_calendar(current_time, calendar):
    n_wd = current_time.weekday()
    wd = n_to_weekday(n_wd)
    h = current_time.hour
    if calendar[wd]:
        if h < calendar[wd][0]:
            current_time = current_time.replace(hour=calendar[wd][0], minute=0, second=0)
            current_time = current_time + timedelta(seconds=1)
            return current_time
        elif h > calendar[wd][1]:
            current_time = current_time + timedelta(days=1)
            n_wd = current_time.weekday()
            wd = n_to_weekday(n_wd)
        else:
            current_time = current_time + timedelta(seconds=1)
            return current_time
    j_day = 0
    while not calendar[wd]:
        j_day += 1
        n_wd = (n_wd + 1) % 7
        wd = n_to_weekday(n_wd)
    if j_day > 0:
        current_time = current_time + timedelta(days=j_day)
    current_time = current_time.replace(hour=calendar[wd][0], minute=0, second=0)
    current_time = current_time + timedelta(seconds=1)  
    return current_time