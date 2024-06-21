
from FlowMetricsCSV.CsvService import CsvService
from FlowMetricsCSV.FlowMetricsService import FlowMetricsService

def generate_flow_metrics_report(board_name: str, input_csv_file_name:str, start_column_name: str, done_column_name: str, id_column_name: str, date_format: str):
    csv_service = CsvService()
    flow_metrics_service = FlowMetricsService(False, "Charts")
    work_items = csv_service.parse_items(input_csv_file_name, ",", start_column_name, done_column_name, date_format, date_format, "", id_column_name)
    days_of_history = 180
    flow_metrics_service.plot_cycle_time_scatterplot(work_items, days_of_history, [50, 70, 85, 95], ["red", "orange", "lightgreen", "darkgreen"], f"{board_name}_Cycle Time Scatter Plot.png")
    flow_metrics_service.plot_work_item_age_scatterplot(work_items, days_of_history, [5, 10], ["orange", "red"], f"{board_name}_WorkItemAge.png")
    flow_metrics_service.plot_throughput_run_chart(work_items, days_of_history, f"{board_name}_Throughput.png", "days")
    flow_metrics_service.plot_work_in_process_run_chart(work_items, days_of_history, f"{board_name}_WorkInProcess.png")
    flow_metrics_service.plot_work_started_vs_finished_chart(work_items, days_of_history, "orange", "green", f"{board_name}_StartedVsFinished.png")
    # below function is thorughing error when estiamtion is not provided
    # flow_metrics_service.plot_estimation_vs_cycle_time_scatterplot(work_items, days_of_history, f"{board_name}_EstimationVsCycleTime.png", "")