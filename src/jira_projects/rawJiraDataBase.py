from constants import JiraJsonKeyConstants as JiraJsonKeyConst


class JiraDataBase:
    _idColumnName = 'ID'

    def __init__(self, search_query, jira_board_columns, output_file_name):
        self.file_name: str = output_file_name
        self.search_query: str = search_query
        self.jira_board_columns = jira_board_columns
        self.csv_single_row_list = {
            JiraDataBase._idColumnName: 0
        }

        # Build the row_list using the columns array
        temp_columns = self.jira_board_columns.copy()
        for column in temp_columns:
            if len(column[JiraJsonKeyConst.STATUSES.value]) == 0:
                self.jira_board_columns.remove(column)

        for column in self.jira_board_columns:
            self.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = ''

    def clear_later_workflow_column_value(self, mapped_column_for_status):
        found: bool = False
        for value in self.csv_single_row_list:
            if value == mapped_column_for_status:
                found = True
                continue
            if found:
                self.csv_single_row_list[value] = ''

    def set_issue_id(self, issue_id):
        self.csv_single_row_list[JiraDataBase._idColumnName] = issue_id

    
    def set_board_column_value(self, mapped_column_for_status, status_change_date):
        if not mapped_column_for_status:
            self.csv_single_row_list[mapped_column_for_status] = status_change_date

    def set_row_values_to_blank(self):
        for columns in self.csv_single_row_list:
            self.csv_single_row_list[columns] = ''
    
    def get_mapped_column_for_status(self, current_status: str) -> str:
        mapped_column: str = ''
        loop_breaker = False
        for column in self.jira_board_columns:
            for status in column[JiraJsonKeyConst.STATUSES.value]:
                if status.casefold() == current_status.casefold():
                    mapped_column = column[JiraJsonKeyConst.COLUMN_NAME.value]
                    loop_breaker = True
                    break
            if loop_breaker:
                break
        return mapped_column

    def get_first_column_having_mapped_status(self):
        first_column_with_mapped_status: str = ''
        for jira_column in self.jira_board_columns:
            if len(jira_column)>0:
                first_column_with_mapped_status = jira_column[JiraJsonKeyConst.COLUMN_NAME.value]
                break
        
        return first_column_with_mapped_status
