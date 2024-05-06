import datetime
from constants import DateUtilConstants as DateUtilConst


class DateUtil:

    def __init__(self, date_format):
        self.format = date_format

    def convert_jira_date(self, jira_data_time):
        # 2023-11-20T09:45:25.000+0000
        # %Y-%m-%d
        # need to add code for checking correct input format - try catch statement
        if jira_data_time != '':
            date_obj = datetime.datetime.strptime(jira_data_time.split('T', 1)[0], '%Y-%m-%d')
            if self.format == DateUtilConst.DATE_FORMAT_TWIG.value:
                return str('%02d' % date_obj.year) + str('%02d' % date_obj.month) + str('%02d' % date_obj.day)
            if self.format == DateUtilConst.DATE_FORMAT_STANDARD.value:
                return str('%02d' % date_obj.day) + '.' + str('%02d' % date_obj.month) + '.' + str(
                    '%02d' % date_obj.year)
        else:
            return jira_data_time
