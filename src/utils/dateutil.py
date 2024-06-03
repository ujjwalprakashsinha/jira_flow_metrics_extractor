import datetime
from constants import DateUtilConstants as DateUtilConst


class DateUtil:

    def __init__(self, date_format):
        self.format = date_format

    def convert_jira_date(self, jira_data_time):
        if jira_data_time != '':
            date_obj = datetime.datetime.strptime(jira_data_time, DateUtilConst.DATE_FORMAT_JIRA.value)
            return date_obj.strftime(self.format)
        else:
            return jira_data_time
