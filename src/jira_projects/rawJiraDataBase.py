from constants import JiraJsonKeyConstants as JiraJsonKeyConst
class JiraDataBase:
    _idColumnName='ID'
    def __init__(self, searchQuery, columns, outputFileName):
        self.file_name: str = outputFileName
        self.search_query: str = searchQuery
        self.columns = columns
        self.csv_row_list = {
            JiraDataBase._idColumnName: 0
        }

        #Build the row_list using the columns array
        temp_columns = self.columns.copy()
        for column in temp_columns:
                if len(column[JiraJsonKeyConst.STATUSES.value]) == 0:
                    self.columns.remove(column)

        for column in self.columns:
            self.csv_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = ''

    def clear_later_workflow_column_value(self, mapped_column_for_status):
        found: bool = False        
        for value in self.csv_row_list:
            if value == mapped_column_for_status:
                found = True
                continue
            if found == True:
                self.csv_row_list[value] = ''

    def set_column_value(self, mapped_column_for_status, created):
        if mapped_column_for_status == '' or mapped_column_for_status is None:
            print(f'mapping not found for Issue ID: {self.csv_row_list[JiraDataBase._idColumnName]} stauts changed on {created}')
            return
        self.csv_row_list[mapped_column_for_status] = created

    def set_row_values_to_blank(self):
        for columns in self.csv_row_list:
            self.csv_row_list[columns] = ''

    def set_issue_id(self, issue_id):
        self.csv_row_list[JiraDataBase._idColumnName]= issue_id

    def get_mapped_column_for_status(self, current_status):
         mapped_column: str = ''
         for column in self.columns:            
             for status in column[JiraJsonKeyConst.STATUSES.value]:
                if status.casefold() == current_status.casefold():
                    mapped_column = column[JiraJsonKeyConst.COLUMN_NAME.value]
                    return mapped_column
         if mapped_column == '':
             print(f'INFO: No mapped Column found for status {current_status}, hence status ignored..')
         return mapped_column
    
    def get_first_column_having_mapped_status(self):
        first_column_with_mapped_status: str = ''
        for column in self.columns:
            for status in column[JiraJsonKeyConst.STATUSES.value]:
                first_column_with_mapped_status = column[JiraJsonKeyConst.COLUMN_NAME.value]
                return first_column_with_mapped_status
        