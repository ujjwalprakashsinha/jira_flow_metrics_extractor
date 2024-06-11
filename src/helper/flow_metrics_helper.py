
from FlowMetricsCSV.CsvService import CsvService
from FlowMetricsCSV.FlowMetricsService import FlowMetricsService

def generate_flow_metrics_report(input_csv_file_name:str, start_column_name: str, done_column_name: str, id_column_name: str, date_format: str ):
    # ------------ Generate flow metric report if true -----------
    csv_service = CsvService()
    flow_metrics_service = FlowMetricsService(False, "Charts")
    items = csv_service.parse_items(input_csv_file_name, ",", start_column_name, done_column_name, date_format, date_format, "", id_column_name)
    flow_metrics_service.plot_cycle_time_scatterplot(items, 600, [50, 70, 85, 95], ["red", "orange", "lightgreen", "darkgreen"], "Cycle Time Scatter Plot")
    # -------------