import os
from shiny import App, ui, render

app_ui = ui.page_fluid(
    ui.h2("Aplikasi Shiny dengan Pygal"),
    ui.output_ui("pygal_chart")
)

def server(input, output, session):
    @output
    @render.ui
    def pygal_chart():
        # Membuat grafik Pygal
        bar_chart = pygal.Bar()
        bar_chart.title = 'Contoh Grafik Bar'
        bar_chart.add('Data 1', [10, 20, 30, 40])
        bar_chart.add('Data 2', [15, 25, 35, 45])

        # Menyimpan grafik ke file sementara
        temp_file = "temp_chart.svg"
        bar_chart.render_to_file(temp_file)

        # Mengembalikan file SVG sebagai elemen HTML
        with open(temp_file, "r") as f:
            svg_content = f.read()
        os.remove(temp_file)  # Hapus file setelah dibaca
        return ui.HTML(svg_content)

app = App(app_ui, server)