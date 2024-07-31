import main_jira_to_csv_data_extractor as jira_data_extractor
import main_extractor
from helper.constants import DateUtilConstants as DateUtilConst

twig_date_format: str = DateUtilConst.DATE_FORMAT_TWIG.value 
main_extractor.main(output_date_format=twig_date_format)