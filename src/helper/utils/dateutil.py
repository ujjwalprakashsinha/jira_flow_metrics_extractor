import datetime
from helper.constants import DateUtilConstants as DateUtilConst


class DateUtil:

    def __init__(self, date_format):
        self.format = date_format

    def convert_jira_date(self, jira_date_time):
        if bool(jira_date_time): # check if date passed in not empty or None
            date_obj = datetime.datetime.strptime(jira_date_time, DateUtilConst.DATE_FORMAT_JIRA.value)
            return date_obj.strftime(self.format)
        else:
            return jira_date_time
