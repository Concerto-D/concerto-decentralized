from concerto.exporters.gantt_chart import GanttChart
import sys

if len(sys.argv) != 2:
    print("Error: expecting one file as argument!")

gc = GanttChart.from_json(sys.argv[1])
gc.show_plotly(title=sys.argv[1][:-5])