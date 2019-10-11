from concerto.exporters.gantt_chart import GanttChart
import sys

if len(sys.argv) < 2:
    print("Error: expecting to convert at least one file!")

for file in sys.argv[1:]:
    gc = GanttChart.from_json(file)
    gc.export_plotly(file[:-5] + ".pdf", title=file[:-5])
