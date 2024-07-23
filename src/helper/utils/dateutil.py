from datetime import datetime, timedelta
from helper.constants import DateUtilConstants as DateUtilConst


class DateUtil:

    def __init__(self, date_format):
        self.format = date_format

    def convert_jira_date(self, jira_date_time):
        if bool(jira_date_time): # check if date passed in not empty or None
            date_obj = datetime.strptime(jira_date_time, DateUtilConst.DATE_FORMAT_JIRA.value)
            return date_obj.strftime(self.format)
        else:
            return jira_date_time
        
    def get_all_date_till_today(self, start_date_str):
        start_date = datetime.strptime(start_date_str, self.format)
        today = datetime.today()
        date_list = []
        
        while start_date <= today:
            date_list.append(start_date.strftime(self.format))
            start_date += timedelta(days=1)
        dates = {
            'Dates': date_list
        }
        return dates
