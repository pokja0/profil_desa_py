from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import shinyswatch
from htmltools import css

import polars as pl
from shinywidgets import output_widget, render_widget

import plotly.express as px
import faicons

import shiny as pyshiny

import pandas as pd
from great_tables import GT, exibble, loc, style, md, html
from great_tables.data import islands

import itables
from itables.widget import ITable

from ipyleaflet import Map 
import folium
import ipyleaflet

import math

from pathlib import Path
import asyncio
from htmltools import head_content
import altair as alt


daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]

data_poktan = pl.read_csv("data/profil_poktan.csv", separator=";")

#data_poktan = pl.read_csv("data/profil_poktan.csv")
    
icon_title_tes = "About tooltips"
icons_fa_tes = ui.HTML(
     f'<svg aria-hidden="true" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{icon_title_tes}</title><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'
    )
def fa_info_circle(icon_title: str, icons_fa):
    # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa(&quot;info-circle&quot;, a11y = &quot;sem&quot;, title = icon_title)`
    return ui.span(icon_title, " ", icons_fa)
# ui.tooltip(
#     fa_info_circle(icon_title),
#     "Text shown in the tooltip."
# )

piggy_bank = fa_info_circle(icon_title_tes, icons_fa_tes)

def filter_poktan(data, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan):
    hasil = data.filter(
        pl.col("KABUPATEN").is_in(filter_kabupaten),
        pl.col("KECAMATAN").is_in(filter_kecamatan),
        pl.col("KELURAHAN").is_in(filter_desa),
        pl.col("BULAN").is_in(filter_bulan)
    )
    hasil = hasil.drop("BATAS")

    return hasil

def nilai_bulan_sebelum(bulan_terpilih):
    daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    index = daftar_bulan.index(bulan_terpilih)
    if index == 0:
        return daftar_bulan[0]  # Jika bulan terpilih adalah JANUARI, nilai_bulan_sebelum juga JANUARI
    else:
        return daftar_bulan[index - 1]

def bulan_hingga(bulan_terpilih):
    daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]
    index = daftar_bulan.index(bulan_terpilih)
    return daftar_bulan[:index + 1]

def format_number(number):
    return f"{number:,}".replace(",", ".")

# Mengurutkan bulan sesuai urutan kronologis
month_order = {
    'JANUARI': 1,
    'FEBRUARI': 2,
    'MARET': 3,
    'APRIL': 4,
    'MEI': 5,
    'JUNI': 6,
    'JULI': 7,
    'AGUSTUS': 8,
    'SEPTEMBER': 9,
    'OKTOBER': 10,
    'NOVEMBER': 11,
    'DESEMBER': 12
}

warna_kuning = "#d4a017"

warna_biru = "#3498db"

app_ui = ui.page_navbar(
    ui.head_content(ui.include_css("www/style.css")),
    ui.nav_panel(
        "Dashboard",
        #ui.img(src = "https://bkkbnsulbar.id/wp-content/uploads/2022/12/cropped-logobkkbnsulbar.png", height = "100px"),
        ui.layout_column_wrap(
            ui.input_selectize("pilih_kab", "Pilih Kabupaten", choices=[], multiple=False),
            ui.input_selectize("pilih_kec", "Pilih Kecamatan", choices=[], multiple=False),
            ui.input_selectize("pilih_desa", "Pilih Desa/Kelurahan", choices=[], multiple=False),
            ui.input_selectize("pilih_bulan", "BULAN", 
                                 choices=daftar_bulan[:8], selected="AGUSTUS")#,
            # ui.input_selectize("pilih_tahun", "TAHUN", 
            #                     choices=['2025', '2024'])                    
        ),
        ui.input_action_button(
            "action_button", "Tampilkan Data"
        ),
        ui.br(),
        ui.h6(
            ui.p(""),
            ui.output_text("judul_wilayah"),
            class_="text-lg-center text-left",
        ),
        ui.br(),
        ui.navset_card_pill(
            ui.nav_panel(
                "Ringkasan",
                ui.div(
                    ui.layout_column_wrap(
                        ui.value_box(
                            "PKB / PLKB",
                            ui.output_text("nama_pkb"),
                            ui.output_text("jumlah_wilker_pkb"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("clipboard-user"),
                            class_="margin-10px theme-valuebox"
                        ),
                        ui.value_box(
                            "Tim Pendamping Keluarga",
                            ui.output_text("jumlah_tpk"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("people-roof"),
                            class_="margin-10px"
                        ),
                    )
                ),
                ui.br(),
                ui.div(             
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Pasangan Usia Subur",
                            ui.output_text("jumlah_pus"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("restroom"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Unmet Need",
                            ui.output_text("jumlah_unmet_need"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("person-circle-exclamation"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "KB MKJP",
                            ui.output_text("jumlah_mkjp"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("pills"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Kontrasepsi Favorit",
                            ui.output_text("kontrasepsi_favorit"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("pills"),
                            class_="margin-10px"
                        )
                    )
                ),
                ui.div(
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Tempat Pelayanan KB",
                            ui.output_text("tempat_pelayanan_kb"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("house-medical"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Tempat Pelayanan KB Terlatih",
                            ui.output_text("tempat_pelayanan_kb_terlatih"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("house-medical-circle-check"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Tenaga Kesehatan Pelayanan KB",
                            ui.output_text("tenaga_kesehatan_kb"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("hospital-user"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Tenaga Kesehatan Pelayanan KB Terlatih",
                            ui.output_text("tenaga_kesehatan_kb_terlatih"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("user-nurse"),
                            class_="margin-10px"
                        )
                    )                  
                ),
                ui.div(
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Jumlah KRS",
                            ui.output_text("jumlah_krs"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("house-chimney-window"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Keluarga Punya BADUTA",
                            ui.output_text("jumlah_keluarga_punya_baduta"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("person-breastfeeding"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "PUS Hamil",
                            ui.output_text("jumlah_pus_hamil"),
                            theme=ui.ValueBoxTheme(class_="", fg = "#f6f8fa", bg = "#0B538E"),
                            showcase= faicons.icon_svg("person-pregnant"),
                            class_="margin-10px"
                        )
                )   
                ),
                ui.div(
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Sasaran BKB",
                            ui.output_text("jumlah_sasaran_bkb"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("baby"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Sasaran BKR",
                            ui.output_text("jumlah_sasaran_bkr"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("child-reaching"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Sasaran BKL",
                            ui.output_text("jumlah_sasaran_bkl"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("person-cane"),
                            class_="margin-10px"
                        )
                    )
                )
            ),
            ui.nav_panel(
                "Keluarga Berencana",
                    ui.layout_column_wrap(
                        ui.card(
                            output_widget("tren_pus"),  
                            full_screen=True
                        ),
                        ui.card(
                            output_widget("tren_pa"),  
                            full_screen=True
                        ),
                        ui.card(
                            output_widget("tren_unmet_need"),  
                            full_screen=True
                        )
                    ),
                    ui.layout_column_wrap(
                        ui.card(
                            output_widget("tren_mkjp"),  
                            full_screen=True
                        ),
                        ui.card(
                            output_widget("bar_mix_kontrasepsi"),  
                            full_screen=True
                        ),
                        ui.card(
                            output_widget("donut_perbandingan_tenaga_kb"),  
                            full_screen=True
                        )
                    )
            ),
            ui.nav_panel(
                "Poktan",
                    # Container utama dengan CSS Grid
                ui.div(
                    ui.output_ui("jumlah_desa"),
                    # Value Box 1
                    ui.output_ui("kepemilikan_bkb"),
                    ui.output_ui("kepemilikan_bkr"),
                    ui.output_ui("kepemilikan_bkl"),
                    ui.output_ui("kepemilikan_uppka"),
                    ui.output_ui("kepemilikan_pikr"),
                    ui.output_ui("kepemilikan_kkb"),
                    ui.output_ui("kepemilikan_rdk"),
                    class_="custom-grid"  # Class CSS untuk grid
                ),
                ui.div(
                    output_widget("tabel_reactable", height="3000px")
                ),
                # ui.layout_column_wrap(
                #     ui.card(
                #         ui.output_data_frame("df")
                #     )
                # )
            ),
            ui.nav_panel(
                "Stunting",
                ui.div(
                    ui.layout_column_wrap(
                        ui.value_box(
                            "Jumlah Keluarga",
                            ui.output_text("jumlah_keluarga"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("child-reaching"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Jumlah Keluarga Sasaran",
                            ui.output_text("jumlah_keluarga_sasaran"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("child-reaching"),
                            class_="margin-10px"
                        ),
                        ui.value_box(
                            "Jumlah KRS",
                            ui.output_text("jumlah_krs_menu"),
                            theme=ui.ValueBoxTheme(class_="", bg = "#f6f8fa", fg = "#0B538E"),
                            showcase= faicons.icon_svg("child-reaching"),
                            class_="margin-10px"
                        )
                    )
                ),
                ui.layout_column_wrap(
                    ui.card(
                        output_widget("peringkat_kesejahteraan"),  
                        full_screen=True
                    ),
                    ui.card(
                        output_widget("faktor_krs"),  
                        full_screen=True
                    )
                ),
                ui.layout_column_wrap(
                    ui.card(
                        output_widget("pie_punya_baduta"),
                        full_screen=True
                    ),
                    ui.card(
                        output_widget("pie_punya_balita"),
                        full_screen=True
                    ),
                    ui.card(
                        output_widget("pie_pus_hamil"),
                        full_screen=True
                    )
                )
            ),
        )
        
    ),
#    ui.nav_panel(
#        "Eksplor Data", 
#        "Maaf, Sedang Dalam Pengembangan"
#    ),
#    ui.nav_panel(
#        "Download Data", "Maaf, Se"
#    ),
    title= ui.tags.div(
        ui.img(src="https://harimulya.com/wp-content/uploads/2024/12/logo-kemendukbangga.png", height="40px", style="margin-right: 10px;"),  # Gambar logo
        "Profil Desa"  # Teks title
    )
)


def server(input, output, session):
    @reactive.effect
    def _():
        daftar_kab = data_poktan['KABUPATEN'].unique()
        daftar_kab = list(daftar_kab)
        daftar_kab.insert(0, "SEMUA KABUPATEN")
        ui.update_selectize(
            "pilih_kab",
            choices=daftar_kab
        )

    
    @reactive.effect
    def _():
        kondisi = input.pilih_kab()
        if kondisi == "SEMUA KABUPATEN":
            daftar_kec = ["SEMUA KECAMATAN"]
        else:
            daftar_kec = (data_poktan
                .select(["KABUPATEN","KECAMATAN"])
                .filter(data_poktan['KABUPATEN'] == input.pilih_kab())
                .select("KECAMATAN"))
            daftar_kec = daftar_kec["KECAMATAN"].unique()
            daftar_kec = list(daftar_kec)
            daftar_kec.insert(0, "SEMUA KECAMATAN")
        ui.update_selectize(
            "pilih_kec",
            choices=daftar_kec
        )

    @reactive.effect
    def _():
        if input.pilih_kec() == "SEMUA KECAMATAN":
            daftar_desa = ["SEMUA DESA/KELURAHAN"]
        else:
            daftar_desa = (data_poktan
                .select(["KECAMATAN","KELURAHAN"])
                .filter(data_poktan['KECAMATAN'] == input.pilih_kec())
                .select("KELURAHAN"))
            daftar_desa = list(daftar_desa["KELURAHAN"])
            daftar_desa.insert(0, "SEMUA DESA/KELURAHAN")
            
        ui.update_selectize(
            "pilih_desa",
            choices=daftar_desa
        )

    

    @render.text
    @reactive.event(input.action_button)
    def judul_wilayah():
        profil = "PROFIL"
        bulan = input.pilih_bulan()
        if input.pilih_kab() == "SEMUA KABUPATEN":
            teks = profil + " - PROVINSI SULAWESI BARAT - " + bulan + " 2025"
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() == "SEMUA KECAMATAN":
            teks = profil + " - KABUPATEN " + input.pilih_kab() + " - " + bulan + " 2025"
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            teks = profil + " - KECAMATAN " + input.pilih_kec() + " - " + bulan + " 2025"
        else:
            teks = profil + " - DESA/KELURAHAN " + input.pilih_desa() + " - " + bulan + " 2025"

        return "\n" + teks

    val_judul = reactive.value(0)
    @reactive.effect
    def _():
        if input.pilih_kab() == "SEMUA KABUPATEN":
            teks = " - PROVINSI SULAWESI BARAT"
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() == "SEMUA KECAMATAN":
            teks = " - KABUPATEN " + input.pilih_kab()
        elif input.pilih_kab() != "SEMUA KABUPATEN" and input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            teks = " - KECAMATAN " + input.pilih_kec()
        else:
            teks = "DESA/KELURAHAN" + input.pilih_desa()

        val_judul.set(teks)

    val_kab = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        kondisi_input = input.pilih_kab()
        if kondisi_input == "SEMUA KABUPATEN":
            filter_kabupaten = data_poktan.select("KABUPATEN").unique().to_series().to_list()
        else:
            filter_kabupaten = [input.pilih_kab()]
        val_kab.set(filter_kabupaten)

    
    val_kec = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        filter_kabupaten = val_kab.get()
        kondisi_input = input.pilih_kec()
        if kondisi_input == "SEMUA KECAMATAN":
            filter_kecamatan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(data_poktan.select("KECAMATAN").unique().to_series().to_list()))
            filter_kecamatan = filter_kecamatan.select("KECAMATAN").unique().to_series().to_list()
        else:
            filter_kecamatan = [input.pilih_kec()]
        val_kec.set(filter_kecamatan)

    val_desa = reactive.value(0)
    @reactive.effect
    def _():
        #reactive.invalidate_later(0.5)
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        kondisi_input = input.pilih_desa()
        if kondisi_input == "SEMUA DESA/KELURAHAN":
            filter_desa = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(data_poktan.select("KELURAHAN").unique().to_series().to_list()))
            filter_desa = filter_desa.select("KELURAHAN").unique().to_series().to_list()
        else:
            filter_desa = [input.pilih_desa()]

        val_desa.set(filter_desa)

    ##Ringkasan
    data_pkb = pl.read_csv("data/nama pkb.csv", separator=";") 
    data_tpk = pl.read_csv("data/nama_tpk.csv")
    @render.text
    @reactive.event(input.action_button)
    def nama_pkb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        if len(filter_desa) == 1:
            nama_pkb = data_pkb.filter(
                            pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa)
                        )['NAMA PKB'][0]
        else:
            nama_pkb = "Jumlah: " + str(data_pkb.filter(
                            pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa)
                        ).select(['KABUPATEN', 'NAMA PKB']).unique().height)
        return nama_pkb
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_wilker_pkb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return "Jumlah Wilker: " + str(len(data_pkb.filter(
                            pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa)
                        )))
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_tpk():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return "Jumlah TPK: " + str(
            data_tpk.filter(
                pl.col("Kota").is_in(filter_kabupaten),
                pl.col("Kecamatan").is_in(filter_kecamatan),
                pl.col("Kelurahan").is_in(filter_desa)
            ).select(['Kecamatan', 'Register']).unique().height
        )
    
    data_pus = pl.read_csv("data/data_pus.csv",separator=";")
    @render.text
    @reactive.event(input.action_button)
    def jumlah_pus():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return "Jumlah PUS: " + str(
           format_number(data_pus.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa),
                pl.col("BULAN").is_in(filter_bulan)
            ).select(pl.col("PUS").sum()).item()
            )
        )
    

    @render.text
    @reactive.event(input.action_button)
    def jumlah_unmet_need():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return "Persentase: " + str(
            round(
                data_pus.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).group_by('PROVINSI').agg([
                    pl.col("PUS").sum(),
                    pl.col("UNMET NEED").sum()
                ]).with_columns(
                    (pl.col("UNMET NEED") / pl.col("PUS"))* 100
                ).select(pl.col("UNMET NEED")).item()  
            , 2)
        )  + "%"
    
    data_mix = pl.read_csv("data/data_mix_kontra.csv", separator=";")
    @render.text
    @reactive.event(input.action_button)
    def jumlah_mkjp():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return "Persentase: " + str(
            round(
                data_mix.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).group_by('PROVINSI').agg([
                    pl.col("IMPLAN").sum(),
                    pl.col("IUD").sum(),
                    pl.col("VASEKTOMI").sum(),
                    pl.col("TUBEKTOMI").sum(),
                    pl.col("KB MODERN").sum()
                ]).with_columns(
                    (((pl.col("IUD") + pl.col("IMPLAN") + pl.col("VASEKTOMI") + pl.col("TUBEKTOMI")) / pl.col("KB MODERN"))* 100).alias('MKJP')
                ).select(pl.col("MKJP")).item()   
            , 2)
        )  + "%"
    
    @render.text
    @reactive.event(input.action_button)
    def kontrasepsi_favorit():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        mix_kontra = data_mix.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).group_by('PROVINSI').agg([
            pl.col("SUNTIK").sum(),
            pl.col("PIL").sum(),
            pl.col("KONDOM").sum(),
            pl.col("MAL").sum(),
            pl.col("IMPLAN").sum(),
            pl.col("IUD").sum(),
            pl.col("VASEKTOMI").sum(),
            pl.col("TUBEKTOMI").sum()
        ])
        result = (
            mix_kontra
            .select(
                pl.exclude("PROVINSI")  # Exclude kolom non-numerik (PROVINSI)
            )
            .row(0)  # Ambil baris pertama sebagai tuple
        )

        # Temukan nilai maksimum dan nama kolom
        max_value = max(result)
        max_column = mix_kontra.columns[1:][result.index(max_value)]  # Cari nama kolom berdasarkan indeks nilai maksimum

        return f"{max_column} ({format_number(max_value)})"
    
    
    faskes_sdm = pl.read_csv("data/data_faskes_siga.csv", separator=";")
    @render.text
    @reactive.event(input.action_button)
    def tempat_pelayanan_kb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        
        return format_number(faskes_sdm.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).select(pl.col("NO REGISTRASI").n_unique()).item())
    
    @render.text
    @reactive.event(input.action_button)
    def tempat_pelayanan_kb_terlatih():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return faskes_sdm.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).filter(
                    (pl.col("PELATIHAN").str.contains("IUD")) |
                    (pl.col("PELATIHAN").str.contains("IMPLAN")) |
                    (pl.col("PELATIHAN").str.contains("Tubektomi")) |
                    (pl.col("PELATIHAN").str.contains("Vasektomi"))
                ).select(pl.col("NO REGISTRASI").n_unique()).item()
    
    @render.text
    @reactive.event(input.action_button)
    def tenaga_kesehatan_kb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return format_number(
            faskes_sdm.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).shape[0]
        )
    
    @render.text
    @reactive.event(input.action_button)
    def tenaga_kesehatan_kb_terlatih():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return format_number(
            faskes_sdm.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(filter_bulan)
                ).filter(
                    (pl.col("PELATIHAN").str.contains("IUD")) |
                    (pl.col("PELATIHAN").str.contains("IMPLAN")) |
                    (pl.col("PELATIHAN").str.contains("Tubektomi")) |
                    (pl.col("PELATIHAN").str.contains("Vasektomi"))
                ).shape[0]
        )
    
    data_krs_verval = pl.read_csv("data/data_verval_krs_2024_sem2.csv", separator=";")
    @render.text
    @reactive.event(input.action_button)
    def jumlah_krs():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("JUMLAH KRS").sum(),
                ]).select(pl.col("JUMLAH KRS")).item())

    @render.text
    @reactive.event(input.action_button)
    def jumlah_keluarga_punya_baduta():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("PUNYA BADUTA").sum(),
                ]).select(pl.col("PUNYA BADUTA")).item())
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_pus_hamil():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("PUS HAMIL").sum(),
                ]).select(pl.col("PUS HAMIL")).item())

    sasaran_poktan = pl.read_csv("data/sasaran_poktan_gabung.csv", separator=";")
    @render.text
    @reactive.event(input.action_button)
    def jumlah_sasaran_bkb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return format_number(sasaran_poktan.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa),
                pl.col("BULAN").is_in(filter_bulan)
            ).group_by(
                'PROVINSI'
            ).agg([
                pl.col("SASARAN BKB").sum(),
            ]).select(pl.col("SASARAN BKB")).item())
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_sasaran_bkr():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return format_number(sasaran_poktan.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa),
                pl.col("BULAN").is_in(filter_bulan)
            ).group_by(
                'PROVINSI'
            ).agg([
                pl.col("SASARAN BKR").sum(),
            ]).select(pl.col("SASARAN BKR")).item())
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_sasaran_bkl():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return format_number(sasaran_poktan.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa),
                pl.col("BULAN").is_in(filter_bulan)
            ).group_by(
                'PROVINSI'
            ).agg([
                pl.col("SASARAN BKL").sum(),
            ]).select(pl.col("SASARAN BKL")).item())
    ##bawah ringkasan

    ### Profil

    # @render.data_frame
    # @reactive.event(input.action_button)
    # def df():
    #     filter_kabupaten = val_kab.get()
    #     filter_kecamatan = val_kec.get()
    #     filter_desa = val_desa.get()
    #     data_poktan = pl.read_csv("data/profil_poktan.csv")
            
    #     data_poktan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
    #                                      pl.col("KECAMATAN").is_in(filter_kecamatan),
    #                                      pl.col("KELURAHAN").is_in(filter_desa)
    #                                     )
    #     return render.DataGrid(data_poktan)  
    
    data_bkb = pl.read_csv("data/data_bkb.csv",separator=";")
    data_bkr = pl.read_csv("data/data_bkr.csv", separator=";")
    data_bkl = pl.read_csv("data/data_bkl.csv", separator=";")
    data_uppka = pl.read_csv("data/data_uppka.csv", separator=";")
    data_pikr = pl.read_csv("data/data_pikr.csv", separator=";")
    data_kkb = pl.read_csv("data/data_kkb.csv", separator=";")
    data_rdk = pl.read_csv("data/data_rdk.csv", separator=";")
    def jumlah_desa_pembanding():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        return data_bkb.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa),
                pl.col("BULAN").is_in(filter_bulan)
            ).height

    @render.ui
    @reactive.event(input.action_button)
    def jumlah_desa():
        warna_fg = "#f6f8fa"
        warna_bg = "#0B538E"
        return ui.value_box(
                "Desa / Kelurahan",
                jumlah_desa_pembanding(),
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase_layout="bottom",
                class_="custom-box",
                showcase=faicons.icon_svg("circle-check")
            )

    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_bkb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        jumlah_bkb = data_bkb.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("YANG ADA")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_bkb:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah BKB",
                jumlah_bkb,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )
    
    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_bkr():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        jumlah_bkr = data_bkr.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("YANG ADA")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_bkr:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah BKR",
                jumlah_bkr,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )
    
    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_bkl():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        jumlah_bkl = data_bkl.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("YANG ADA")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_bkl:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah BKL",
                jumlah_bkl,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )

    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_uppka():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        jumlah_uppka = data_uppka.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("YANG ADA")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_uppka:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah UPPKA",
                jumlah_uppka,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )
    
    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_pikr():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        jumlah_pikr = data_pikr.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("YANG ADA")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_pikr:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah PIK-R",
                jumlah_pikr,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )
    
    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_kkb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()

        jumlah_kkb = data_kkb.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa)
        ).select(pl.col("JUMLAH KAMPUNG KB")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_kkb:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah KKB",
                jumlah_kkb,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )

    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_rdk():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        #filter_bulan = [input.pilih_bulan()]

        jumlah_rdk = data_rdk.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa)
        ).select(pl.col("JUMLAH RUMAH DATAKU")).sum().item()

        if jumlah_desa_pembanding() <= jumlah_rdk:
            warna_fg = "#f6f8fa"
            warna_bg = "#0B538E"
            showcase = faicons.icon_svg("circle-check")
        else:
            warna_fg = "#f6f8fa"
            warna_bg = "#B22222"
            showcase = faicons.icon_svg("circle-xmark")
        return ui.value_box(
                "Jumlah RDK",
                jumlah_rdk,
                theme=ui.ValueBoxTheme(
                    class_="", 
                    bg = warna_bg, 
                    fg = warna_fg),
                showcase=showcase,
                showcase_layout="bottom",
                class_="custom-box"
            )

    @render.ui
    @reactive.event(input.action_button)
    def kepemilikan_poktan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]

        bkb = pl.read_excel("data/data_bkb.xlsx")
        bkr = pl.read_excel("data/data_bkr.xlsx")
        bkl = pl.read_excel("data/data_bkl.xlsx")
        uppka = pl.read_excel("data/data_uppka.xlsx")
        pikr = pl.read_excel("data/data_pikr.xlsx")
        kkb = pl.read_excel("data/data_kkb.xlsx")
        rdk = pl.read_excel("data/data_rdk.xlsx")
        daftar_desa = pl.read_csv("data/data_daftar_desa.csv")

        bkb = filter_poktan(bkb, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        bkr = filter_poktan(bkr, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        bkl = filter_poktan(bkl, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        uppka = filter_poktan(uppka, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        pikr = filter_poktan(pikr, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        kkb = filter_poktan(kkb, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        rdk = filter_poktan(rdk, filter_kabupaten, filter_kecamatan, filter_desa, filter_bulan)
        daftar_desa = daftar_desa.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa)
            )
        
        data_poktan = pl.DataFrame({
            "Desa/Kel": daftar_desa.height,
            "Kampung KB": kkb["JUMLAH_KKB"].sum(),
            "Rumah DataKu": rdk["JUMLAH_RDK"].sum(),
            "BKB": bkr["JUMLAH_BKR"].sum(),
            "BKR": bkr["JUMLAH_BKR"].sum(),
            "BKL": bkl["JUMLAH_BKL"].sum(),
            "UPPKA": uppka["JUMLAH_UPPKA"].sum(),
            "PIK-R": pikr["JUMLAH_PIKR"].sum()
        })

        data_poktan = data_poktan.unpivot(["Desa/Kel", "Kampung KB", "Rumah DataKu",
                            "BKB", "BKR", "BKL", "UPPKA", "PIK-R"], 
                            variable_name="Poktan", value_name="Keterangan")
        # data_poktan = pl.read_csv("data/profil_poktan.csv")
            
        # data_poktan = data_poktan.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
        #                                     pl.col("KECAMATAN").is_in(filter_kecamatan),
        #                                     pl.col("KELURAHAN").is_in(filter_desa))
        # # List kolom yang akan dihitung
        # columns_to_count = ["Kampung KB", "Rumah DataKU", "BKB", "BKR", "BKL", "UPPKA", "PIK-R"]

        # # Menghitung jumlah "Ada" untuk setiap kolom
        # counts = [data_poktan[col].str.count_matches("Ada").sum() for col in columns_to_count]

        # # Menghitung jumlah desa unik berdasarkan kombinasi KECAMATAN dan KELURAHAN
        # unique_desa = data_poktan.select(["KECAMATAN", "KELURAHAN"]).unique().shape[0]

        # # Membuat DataFrame hasil
        # results = pl.DataFrame({
        #     "Kategori": ["Desa/Kelurahan"] + columns_to_count,
        #     "Jumlah": [unique_desa] + counts
        # })
        return GT(data_poktan)
    
    @render.ui
    @reactive.event(input.action_button)
    def profil_wilayah():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        data_sd = pl.read_csv("data/profil_sumber_daya.csv")
        
        data_sd = data_sd.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                                            pl.col("KELURAHAN").is_in(filter_desa))

        # Menghitung jumlah total untuk LUAS_WILAYAH dan JUMLAH_PENDUDUK
        total_luas_wilayah = round(data_sd["LUAS_WILAYAH"].sum(),2)
        total_jumlah_penduduk = int(data_sd["JUMLAH_PENDUDUK"].sum())

        # Menghitung rata-rata untuk KEPADATAN_PENDUDUK
        avg_kepadatan_penduduk = round(total_jumlah_penduduk/total_luas_wilayah, 2)

        # Membuat DataFrame hasil
        results = pl.DataFrame({
            "Indikator": ["Luas Wilayah", "Jumlah Penduduk", "Kepadatan Penduduk"],
            "Nilai": [total_luas_wilayah, total_jumlah_penduduk, avg_kepadatan_penduduk]
        })
        return GT(results)
    
    # @render_widget
    # @reactive.event(input.action_button)
    # def grafik_piramida():
    #     filter_kabupaten = val_kab.get()
    #     filter_kecamatan = val_kec.get()
    #     filter_desa = val_desa.get()
        
    #     kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
    #     kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
    #                                 pl.col("KECAMATAN").is_in(filter_kecamatan),
    #                                 pl.col("KELURAHAN").is_in(filter_desa))
    #     # Mendefinisikan range kolom yang akan dijumlahkan
    #     columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

    #     # Membuat daftar agregasi
    #     aggregations = [pl.sum(col) for col in columns_to_sum]

    #     # Melakukan pengelompokan dan agregasi
    #     result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

    #     # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
    #     columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

    #     # Melakukan melt pada DataFrame
    #     melted_result_lk = result.melt(
    #         id_vars=["PROVINSI"], 
    #         value_vars=columns_to_melt, 
    #         variable_name="Age_Group", 
    #         value_name="Laki-laki"
    #     )

    #     kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
    #     kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
    #                         pl.col("KECAMATAN").is_in(filter_kecamatan),
    #                         pl.col("KELURAHAN").is_in(filter_desa))
    #     # Mendefinisikan range kolom yang akan dijumlahkan
    #     columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

    #     # Membuat daftar agregasi
    #     aggregations = [pl.sum(col) for col in columns_to_sum]

    #     # Melakukan pengelompokan dan agregasi
    #     result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

    #     # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
    #     columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

    #     # Melakukan melt pada DataFrame
    #     melted_result_pr = result.melt(
    #         id_vars=["PROVINSI"], 
    #         value_vars=columns_to_melt, 
    #         variable_name="Age_Group", 
    #         value_name="Perempuan"
    #     )

    #     df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

    #     # Daftar kategori usia
    #     ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
    #         "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
    #         "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
    #         "65 - 69", "70 - 74", "75+"]

    #     # Menghitung berapa kali daftar ku perlu diulang
    #     repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
    #     repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

    #     # Menambahkan kolom kategori umur
    #     df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])

    #     y_age = df_horizontal_join['Kategori_Umur'] 
    #     x_M = df_horizontal_join['Laki-laki'] 
    #     x_F = df_horizontal_join['Perempuan'] * -1

    #     if max(x_M) >= max(x_F):
    #         maks = max(x_M)
    #     else:
    #         maks = max(x_F)

    #     def round_up_to_nearest(number, base):
    #         return base * math.ceil(number / base)

    #     def auto_round_up(number):
    #         if number == 0:
    #             return 0
    #         base = 10 ** (len(str(number)) - 1)
    #         return round_up_to_nearest(number, base)

    #     maks1 = auto_round_up(maks)
    #     maks2 = auto_round_up(int(maks - (maks * 1 / 3)))
    #     maks3 = auto_round_up(int(maks - (maks * 2 / 3)))

    #     tick_vals = [-maks1, -maks2, -maks3, 0, maks1, maks2, maks3]
    #     tick_str = [str(abs(value)) for value in tick_vals]

    #     import plotly.graph_objects as gp
    #     # Creating instance of the figure 
    #     fig = gp.Figure() 
        

    #     # Adding Female data to the figure 
    #     fig.add_trace(gp.Bar(y = y_age, x = x_F, 
    #                         name = 'Perempuan', orientation = 'h',
    #                         marker=dict(color='#ffc107'),
    #                         hovertemplate='Perempuan Umur %{y}<br>Jumlah: %{customdata}<extra></extra>',
    #                         customdata=[abs(x) for x in x_F]
    #                         )) 

    #     # Adding Male data to the figure 
    #     fig.add_trace(gp.Bar(y= y_age, x = x_M,  
    #                         name = 'Laki-laki',  
    #                         orientation = 'h',
    #                         marker=dict(color='#0d6efd'),
    #                         hovertemplate='Laki-laki Umur %{y}<br> %{x}<extra></extra>')) 

        
    #     # Updating the layout for our graph 
    #     fig.update_layout(title={
    #                         'text': 'Piramida Penduduk ' + str(val_judul.get()),
    #                         'y': 0.98,  # Adjust this value to move the title up or down
    #                         'x': 0.5,  # Centered horizontally
    #                         'xanchor': 'center',
    #                         'yanchor': 'top'
    #                     },
    #                     title_font_size = 18, barmode = 'relative', 
    #                     bargap = 0.0, bargroupgap = 0, 
    #                     xaxis = dict(tickvals = tick_vals, 
    #                                 ticktext = tick_str, 
    #                                 title = 'Jumlah', 
    #                                 title_font_size = 14),
    #                     legend=dict(
    #                             orientation='h',
    #                             yanchor='bottom',
    #                             y=-0.3,  # Adjust this value to move the legend up or down
    #                             xanchor='center',
    #                             x=0.5
    #                     ),
    #                     plot_bgcolor='#f6f8fa',  # Set background color of the plot area to green
    #                     paper_bgcolor='#f6f8fa'  # Set background color of the entire canvas to green 
    #     )
        
    #     return fig

    # @render.data_frame
    # @reactive.event(input.action_button)
    # def tabel_piramida():
    #     filter_kabupaten = val_kab.get()
    #     filter_kecamatan = val_kec.get()
    #     filter_desa = val_desa.get()
        
    #     kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
    #     kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
    #                                 pl.col("KECAMATAN").is_in(filter_kecamatan),
    #                                 pl.col("KELURAHAN").is_in(filter_desa))
    #     # Mendefinisikan range kolom yang akan dijumlahkan
    #     columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

    #     # Membuat daftar agregasi
    #     aggregations = [pl.sum(col) for col in columns_to_sum]

    #     # Melakukan pengelompokan dan agregasi
    #     result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

    #     # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
    #     columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

    #     # Melakukan melt pada DataFrame
    #     melted_result_lk = result.melt(
    #         id_vars=["PROVINSI"], 
    #         value_vars=columns_to_melt, 
    #         variable_name="Age_Group", 
    #         value_name="Laki-laki"
    #     )

    #     kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
    #     kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
    #                         pl.col("KECAMATAN").is_in(filter_kecamatan),
    #                         pl.col("KELURAHAN").is_in(filter_desa))
    #     # Mendefinisikan range kolom yang akan dijumlahkan
    #     columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

    #     # Membuat daftar agregasi
    #     aggregations = [pl.sum(col) for col in columns_to_sum]

    #     # Melakukan pengelompokan dan agregasi
    #     result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

    #     # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
    #     columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

    #     # Melakukan melt pada DataFrame
    #     melted_result_pr = result.melt(
    #         id_vars=["PROVINSI"], 
    #         value_vars=columns_to_melt, 
    #         variable_name="Age_Group", 
    #         value_name="Perempuan"
    #     )

    #     df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

    #     # Daftar kategori usia
    #     ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
    #         "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
    #         "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
    #         "65 - 69", "70 - 74", "75+"]

    #     # Menghitung berapa kali daftar ku perlu diulang
    #     repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
    #     repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

    #     # Menambahkan kolom kategori umur
    #     df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])
    #     df_horizontal_join = df_horizontal_join.select('Kategori_Umur', 'Perempuan', 'Laki-laki')


    #     df_horizontal_join = df_horizontal_join.with_columns(
    #         (pl.col("Perempuan") + pl.col("Laki-laki")).alias("Total")
    #     )
    #     return render.DataGrid(df_horizontal_join)
    # ### akhir profil

    ### awal KB
    #data_pus = pl.read_csv("data/data_pus.csv")
    #data_mix = pl.read_csv("data/data_mix_kontra.csv")
    @render_widget
    @reactive.event(input.action_button)
    async def tren_pus():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Sedang Proses", detail="Tunggu ya")
            p.set(1, message="Tunggu ya")

            filter_kabupaten = val_kab.get()
            filter_kecamatan = val_kec.get()
            filter_desa = val_desa.get()
            filter_bulan = input.pilih_bulan()
            df_processed =  data_pus.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa),
                    pl.col("BULAN").is_in(bulan_hingga(filter_bulan))
                ).group_by(
                    'PROVINSI', 'BULAN'
                ).agg([
                    pl.col("PUS").sum()
                ])

            # Proses data dengan Polars
            df_processed = (
                df_processed
                .with_columns(
                    # Konversi bulan ke numerik
                    pl.col("BULAN")
                    .replace(month_order)
                    .cast(pl.Int32)
                    .alias("month_order")
                )
                .with_columns(
                    pl.col("PUS")
                    .map_elements(
                        lambda x: f"{x:,}".replace(",", "."),
                        return_dtype=pl.Utf8
                    )
                    .alias("JUMLAH PUS")
                )
                .sort("month_order")
                .drop("month_order")
            )

            # Ambil bulan pertama dan terakhir
            first_month = df_processed["BULAN"][0]
            last_month = df_processed["BULAN"][-1]

            # Hitung batas y-axis
            y_min = df_processed["PUS"].min() * 0.95
            y_max = df_processed["PUS"].max() * 1.05

            # === Base Chart ===
            base = alt.Chart(df_processed).mark_line(
                point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color=warna_biru)
            ).encode(
                x=alt.X('BULAN:N', 
                        sort=list(month_order.keys()),
                        axis=alt.Axis(
                            labelAngle=0, 
                            labelLimit=200, 
                            labelOverlap="parity",
                            labelExpr="slice(datum.label, 0, 3)"  # Ambil 3 huruf pertama
                        )),
                y=alt.Y('PUS:Q',
                        scale=alt.Scale(domain=(y_min, y_max)),
                        axis=alt.Axis(
                            labelExpr='replace(format(datum.value, ",.0f"), ",", ".")', 
                            title='JUMLAH PUS',
                            tickCount=5  # BATASI 5 TICK SAJA
                        )),
                tooltip=[alt.Tooltip('BULAN:N'), alt.Tooltip('JUMLAH PUS:N')]
            )

            p.set(2, message="Tunggu ya")
            # === Anotasi Label (Perubahan warna) ===
            start_label = alt.Chart(df_processed).transform_filter(
                alt.datum.BULAN == first_month
            ).mark_text(
                align='center', 
                dy=-25, 
                fontSize=11, 
                fontWeight='bold', 
                color=warna_kuning  # Sesuaikan dengan warna point
            ).encode(
                x=alt.X('BULAN:N', sort=list(month_order.keys())),
                y=alt.Y('PUS:Q'),
                text=alt.Text('JUMLAH PUS:N')
            )

            p.set(3, message="Tunggu ya")
            end_label = alt.Chart(df_processed).transform_filter(
                alt.datum.BULAN == last_month
            ).mark_text(
                align='center', 
                dy=-25, 
                fontSize=11, 
                fontWeight='bold', 
                color=warna_kuning  # Sesuaikan dengan warna point
            ).encode(
                x=alt.X('BULAN:N', sort=list(month_order.keys())),
                y=alt.Y('PUS:Q'),
                text=alt.Text('JUMLAH PUS:N')
            )

            p.set(4, message="Sedikit lagi")

            chart = alt.layer(base, start_label, end_label).properties(
                title=alt.TitleParams(
                    'Tren Jumlah PUS',
                    anchor='middle',  # Judul rata kiri
                    offset=20
                ),
                width='container',  # Lebar menyesuaikan layar
                height='container'
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                grid=False,
                labelFontSize=12,
                titleFontSize=14
            ).configure(
                padding={"left": 0, "right": 0, "top": 20, "bottom": 0},  # Sesuaikan padding
                background='#f6f8fa',
                autosize=alt.AutoSizeParams(
                    type='fit',
                    contains='padding'
                )
            ).configure_legend(
                disable=True  # Hapus legenda jika tidak diperlukan
            )
           
            p.set(5, message="Sedikit lagi")
            # === Gabungkan Semua Elemen ===
            
        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_pa():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        df_processed =  data_mix.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(bulan_hingga(filter_bulan))
        ).group_by(
            'PROVINSI', 'BULAN'
        ).agg([
            pl.col("PA").sum()
        ])

        # Proses data dengan Polars
        df_processed = (
            df_processed
            .with_columns(
                # Konversi bulan ke numerik
                pl.col("BULAN")
                .replace(month_order)
                .cast(pl.Int32)
                .alias("month_order")
            )
            .with_columns(
                pl.col("PA")
                .map_elements(
                    lambda x: f"{x:,}".replace(",", "."),
                    return_dtype=pl.Utf8
                )
                .alias("JUMLAH PA")
            )
            .sort("month_order")
            .drop("month_order")
        )

        # Ambil bulan pertama dan terakhir
        first_month = df_processed["BULAN"][0]
        last_month = df_processed["BULAN"][-1]

        # Hitung batas y-axis
        y_min = df_processed["PA"].min() * 0.95
        y_max = df_processed["PA"].max() * 1.05

        # === Base Chart ===
        base = alt.Chart(df_processed).mark_line(
            color=warna_kuning,
            point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color=warna_kuning)
        ).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0, 
                        labelLimit=200, 
                        labelOverlap="parity",
                        labelExpr="slice(datum.label, 0, 3)"  # Ambil 3 huruf pertama
                    )),
            y=alt.Y('PA:Q',
                    scale=alt.Scale(domain=(y_min, y_max)),
                    axis=alt.Axis(
                        labelExpr='replace(format(datum.value, ",.0f"), ",", ".")', 
                        title='JUMLAH PA',
                        tickCount=5  # BATASI 5 TICK SAJA
                    )),
            tooltip=[alt.Tooltip('BULAN:N'), alt.Tooltip('JUMLAH PA:N')]
        )

        # === Anotasi Label (Perubahan warna) ===
        start_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == first_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=12, 
            fontWeight='bold', 
            color=warna_biru
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PA:Q'),
            text=alt.Text('JUMLAH PA:N')
        )

        end_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == last_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color=warna_biru  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PA:Q'),
            text=alt.Text('JUMLAH PA:N')
        )


        chart = alt.layer(base, start_label, end_label).properties(
            title=alt.TitleParams(
                'Tren Jumlah PA',
                anchor='middle',  # Judul rata kiri
                offset=20
            ),
            width='container',  # Lebar menyesuaikan layar
            height='container'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False,
            labelFontSize=12,
            titleFontSize=14
        ).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},  # Sesuaikan padding
            background='#f6f8fa',
            autosize=alt.AutoSizeParams(
                type='fit',
                contains='padding'
            )
        ).configure_legend(
            disable=True  # Hapus legenda jika tidak diperlukan
        )

        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_unmet_need():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        df_processed = data_pus.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(bulan_hingga(filter_bulan))
        ).group_by('PROVINSI', 'BULAN').agg([
            pl.col("PUS").sum(),
            pl.col("UNMET NEED").sum()
        ]).with_columns(
            ((pl.col("UNMET NEED") / pl.col("PUS"))* 100).round(2).alias('UNMET NEED')
        )

        # Proses data dengan Polars
        df_processed = (
            df_processed
            .with_columns(
                # Konversi bulan ke numerik
                pl.col("BULAN")
                .replace(month_order)
                .cast(pl.Int32)
                .alias("month_order")
            )
            .sort("month_order")
            .drop("month_order")
        )

        # Ambil bulan pertama dan terakhir
        first_month = df_processed["BULAN"][0]
        last_month = df_processed["BULAN"][-1]

        # Hitung batas y-axis
        y_min = df_processed["UNMET NEED"].min() * 0.95
        y_max = df_processed["UNMET NEED"].max() * 1.05


        # Format kolom persentase ke string dengan koma dan %
        persentase_list = df_processed["UNMET NEED"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        df_processed = df_processed.with_columns(pl.Series("UNMET NEED (%)", persentase_format))

        # === Base Chart ===
        base = alt.Chart(df_processed).mark_line(
            point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color=warna_biru)
        ).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0, 
                        labelLimit=200, 
                        labelOverlap="parity",
                        labelExpr="slice(datum.label, 0, 3)"  # Ambil 3 huruf pertama
                    )),
            y=alt.Y('UNMET NEED:Q',
                    scale=alt.Scale(domain=(y_min, y_max)),
                    axis=alt.Axis(
                        title='PERSENTASE UNMET NEED',
                        tickCount=3,  # BATASI 5 TICK SAJA
                        )
                    ),
            tooltip=[alt.Tooltip('BULAN:N'), alt.Tooltip('UNMET NEED (%):N')]
        )

        # === Anotasi Label (Perubahan warna) ===
        start_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == first_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color=warna_kuning  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('UNMET NEED:Q'),
            text=alt.Text('UNMET NEED (%):N')
        )

        end_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == last_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color=warna_kuning  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('UNMET NEED:Q'),
            text=alt.Text('UNMET NEED (%):N')
        )


        chart = alt.layer(base, start_label, end_label).properties(
            title=alt.TitleParams(
                'Tren Persentase Unmet Need',
                anchor='middle',  # Judul rata kiri
                offset=20
            ),
            width='container',  # Lebar menyesuaikan layar
            height='container'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False,
            labelFontSize=12,
            titleFontSize=14
        ).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},  # Sesuaikan padding
            background='#f6f8fa',
            autosize=alt.AutoSizeParams(
                type='fit',
                contains='padding'
            )
        ).configure_legend(
            disable=True  # Hapus legenda jika tidak diperlukan
        )

        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_mkjp():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()

        df_processed = data_mix.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(bulan_hingga(filter_bulan))
        ).group_by('PROVINSI', "BULAN").agg([
            pl.col("IMPLAN").sum(),
            pl.col("IUD").sum(),
            pl.col("VASEKTOMI").sum(),
            pl.col("TUBEKTOMI").sum(),
            pl.col("KB MODERN").sum()
        ]).with_columns(
            (((pl.col("IUD") + pl.col("IMPLAN") + pl.col("VASEKTOMI") + pl.col("TUBEKTOMI")) / pl.col("KB MODERN"))* 100).round(2).alias('MKJP')
        )

        # Proses data dengan Polars
        df_processed = (
            df_processed
            .with_columns(
                # Konversi bulan ke numerik
                pl.col("BULAN")
                .replace(month_order)
                .cast(pl.Int32)
                .alias("month_order")
            )
            .sort("month_order")
            .drop("month_order")
        )

        # Ambil bulan pertama dan terakhir
        first_month = df_processed["BULAN"][0]
        last_month = df_processed["BULAN"][-1]

        # Hitung batas y-axis
        y_min = df_processed["MKJP"].min() * 0.95
        y_max = df_processed["MKJP"].max() * 1.05

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = df_processed["MKJP"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        df_processed = df_processed.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # === Base Chart ===
        base = alt.Chart(df_processed).mark_line(
            color=warna_kuning,
            point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color=warna_kuning)
        ).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0, 
                        labelLimit=200, 
                        labelOverlap="parity",
                        labelExpr="slice(datum.label, 0, 3)"  # Ambil 3 huruf pertama
                    )),
            y=alt.Y('MKJP:Q',
                    scale=alt.Scale(domain=(y_min, y_max)),
                    axis=alt.Axis(
                        title='PERSENTASE MKJP',
                        tickCount=3,  # BATASI 5 TICK SAJA
                        )
                    ),
            tooltip=[alt.Tooltip('BULAN:N'), alt.Tooltip('PERSENTASE_FORMAT:N', title='PERSENTASE')]
        )

        # === Anotasi Label (Perubahan warna) ===
        start_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == first_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color=warna_biru  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('MKJP:Q'),
            text=alt.Text('PERSENTASE_FORMAT:N', title='PERSENTASE')
        )

        end_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == last_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color=warna_biru  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('MKJP:Q'),
            text=alt.Text('PERSENTASE_FORMAT:N', title='PERSENTASE')
        )


        chart = alt.layer(base, start_label, end_label).properties(
            title=alt.TitleParams(
                'Tren Persentase MKJP',
                anchor='middle',  # Judul rata kiri
                offset=20
            ),
            width='container',  # Lebar menyesuaikan layar
            height='container'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False,
            labelFontSize=12,
            titleFontSize=14
        ).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},  # Sesuaikan padding
            background='#f6f8fa',
            autosize=alt.AutoSizeParams(
                type='fit',
                contains='padding'
            )
        ).configure_legend(
            disable=True  # Hapus legenda jika tidak diperlukan
        )

        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def bar_mix_kontrasepsi():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        mix_kontra = data_mix.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in([filter_bulan])
        ).group_by('PROVINSI').agg([
            pl.col("SUNTIK").sum(),
            pl.col("PIL").sum(),
            pl.col("KONDOM").sum(),
            pl.col("MAL").sum(),
            pl.col("IMPLAN").sum(),
            pl.col("IUD").sum(),
            pl.col("VASEKTOMI").sum(),
            pl.col("TUBEKTOMI").sum()
        ])

        # Ubah data menjadi format "long" menggunakan `unpivot`
        mix_kontra = mix_kontra.unpivot(
            index="PROVINSI",  # Kolom yang tetap
            on=["SUNTIK", "PIL", "KONDOM", "MAL", "IMPLAN", "IUD", "VASEKTOMI", "TUBEKTOMI"],  # Kolom yang di-unpivot
            variable_name="METODE_KB",  # Nama kolom untuk metode KB
            value_name="JUMLAH"  # Nama kolom untuk jumlah pengguna
        )

        # Urutkan data berdasarkan jumlah pengguna (terbesar ke terkecil)
        mix_kontra = mix_kontra.sort("JUMLAH", descending=True)

        # Menghitung total jumlah pengguna
        total_jumlah = mix_kontra["JUMLAH"].sum()

        # Menambahkan kolom persentase (dengan 2 angka desimal)
        mix_kontra = mix_kontra.with_columns(
            (pl.col("JUMLAH") / total_jumlah * 100).round(2).alias("PERSENTASE"),
            # Format angka dengan pemisah titik (.) untuk tooltip
            pl.col("JUMLAH").map_elements(
                lambda x: f"{x:,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("JUMLAH FORMATTED")
        )

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = mix_kontra["PERSENTASE"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        mix_kontra = mix_kontra.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # Mengurutkan data berdasarkan jumlah secara descending
        mix_kontra = mix_kontra.sort("JUMLAH", descending=True)

        # Membuat grafik batang horizontal dengan Altair
        chart = (
            alt.Chart(mix_kontra)
            .mark_bar(color=warna_biru)
            .encode(
                y=alt.Y("METODE_KB:N", title="Metode KB", sort="-x"),
                x=alt.X("JUMLAH:Q", title="Jumlah Pengguna",
                        axis=alt.Axis(
                        tickCount=3,  # BATASI 5 TICK SAJA
                        )),
                tooltip=[
                    alt.Tooltip("METODE_KB", title="Metode KB"),
                    alt.Tooltip("JUMLAH FORMATTED:Q", title="Jumlah"),
                    alt.Tooltip("PERSENTASE_FORMAT:N", title="Persentase")
                ]
            )
        )

        # Menambahkan label di ujung batang
        text = (
            alt.Chart(mix_kontra)
            .mark_text(align="left", baseline="middle", dx=5)
            .encode(
                y=alt.Y("METODE_KB:N", sort="-x"),
                x=alt.X("JUMLAH:Q"),
                text="JUMLAH FORMATTED:Q"
            )
        )

        chart = alt.layer(chart, text).properties(
                width='container',
                height='container',
                title="Perbandingan Pengguna Metode KB"
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                grid=False,
                labelFontSize=12,
                titleFontSize=14
            ).configure(
                padding={"left": 0, "right": 3, "top": 20, "bottom": 0},  # Sesuaikan padding
                background='#f6f8fa',
                autosize=alt.AutoSizeParams(
                    type='fit',
                    contains='padding'
                )
            ).configure_legend(
                disable=True  # Hapus legenda jika tidak diperlukan
            )
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def donut_perbandingan_tenaga_kb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        
        # Klasifikasi tenaga kerja berdasarkan kolom PELATIHAN
        data_with_classification = faskes_sdm.with_columns(
            pl.when(
                pl.col("PELATIHAN").str.contains("(?i)IUD|Implan|Tubektomi|Vasektomi")
            ).then(pl.lit("Sudah Terlatih")).otherwise(pl.lit("Belum Terlatih")).alias("KLASIFIKASI")
        )

        # Hitung jumlah tenaga kerja untuk setiap klasifikasi
        summary_data = data_with_classification.group_by("KLASIFIKASI").agg(
            pl.len().alias("count")  # Menggunakan .len() sebagai pengganti .count()
        )

        # Tambahkan kolom persentase
        total_count = summary_data["count"].sum()
        summary_data = summary_data.with_columns(
            (pl.col("count") / total_count * 100).round(2).alias("PERSENTASE")
        )

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = summary_data["PERSENTASE"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        summary_data = summary_data.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # Definisi warna
        color_scale = alt.Scale(
            domain=["Sudah Terlatih", "Belum Terlatih"],
            range=[warna_biru, warna_kuning]  # Biru untuk Sudah Terlatih, Kuning untuk Belum
        )

        # Tambahkan kolom gabungan klasifikasi dan persentase
        summary_data = summary_data.with_columns(
            (pl.col("KLASIFIKASI") + "\n" + pl.col("PERSENTASE_FORMAT")).alias("LABEL")
        )

        # Basis chart
        base = alt.Chart(summary_data).encode(
            theta=alt.Theta("count:Q", stack=True),
            color=alt.Color("KLASIFIKASI:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("KLASIFIKASI:N", title="Status"),
                alt.Tooltip("count:Q", title="Jumlah"),
                alt.Tooltip("PERSENTASE_FORMAT:N", title="Persentase")
            ]
        ).properties(
            width='container',
            height='container',
            title=" Status Pelatihan Dokter/Bidan"
        )

        # Arc (donut)
        arc = base.mark_arc(
            outerRadius=120,
            innerRadius=80
        )

        # Label di luar donut dengan dua baris
        text = base.mark_text(  
            radius=145,
            size=11,    
            #align="center",
            #baseline="bottom",
            lineBreak="\n"  # Pemisah baris
        ).encode(
            text="LABEL:N"  # Kolom gabungan
        )


        # Gabungkan grafik
        chart = alt.layer(arc, text).properties(
                width='container',
                height='container',
                title="Perbandingan Pengguna Metode KB"
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                grid=False,
                labelFontSize=12,
                titleFontSize=14
            ).configure(
                padding={"left": 0, "right": 3, "top": 20, "bottom": 0},  # Sesuaikan padding
                background='#f6f8fa',
                autosize=alt.AutoSizeParams(
                    type='fit',
                    contains='padding'
                )
            ).configure_legend(
                disable=True  # Hapus legenda jika tidak diperlukan
            )

        return chart
    ### akhir KB

    ### awal KRS
    @render.text
    @reactive.event(input.action_button)
    def jumlah_keluarga():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("JUMLAH KELUARGA").sum(),
                ]).select(pl.col("JUMLAH KELUARGA")).item())
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_keluarga_sasaran():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("JUMLAH KELUARGA SASARAN").sum(),
                ]).select(pl.col("JUMLAH KELUARGA SASARAN")).item())
    
    @render.text
    @reactive.event(input.action_button)
    def jumlah_krs_menu():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        return format_number(data_krs_verval.filter(
                    pl.col("KABUPATEN").is_in(filter_kabupaten),
                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                    pl.col("KELURAHAN").is_in(filter_desa)
                ).group_by(
                    'PROVINSI'
                ).agg([
                    pl.col("JUMLAH KRS").sum(),
                ]).select(pl.col("JUMLAH KRS")).item())
    
    @render_widget
    @reactive.event(input.action_button)
    def peringkat_kesejahteraan():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        data_kesejahteraan = data_krs_verval.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa)
        ).group_by('PROVINSI').agg([
            pl.col("KESEJAHTERAAN 1").sum(),
            pl.col("KESEJAHTERAAN 2").sum(),
            pl.col("KESEJAHTERAAN 3").sum(),
            pl.col("KESEJAHTERAAN 4").sum(),
            pl.col("KESEJAHTERAAN > 4").sum()
        ])


        data_kesejahteraan = data_kesejahteraan.unpivot(
            index="PROVINSI",  # Kolom yang tetap
            on=["KESEJAHTERAAN 1", "KESEJAHTERAAN 2", "KESEJAHTERAAN 3", "KESEJAHTERAAN 4", "KESEJAHTERAAN > 4"],  # Kolom yang di-unpivot
            variable_name="TINGKAT KESEJAHTERAAN",  # Nama kolom untuk metode KB
            value_name="JUMLAH"  # Nama kolom untuk jumlah pengguna
        )

        # Buat custom order untuk tingkat kesejahteraan
        custom_order = ["KESEJAHTERAAN 1", "KESEJAHTERAAN 2", "KESEJAHTERAAN 3", "KESEJAHTERAAN 4", "KESEJAHTERAAN > 4"]

        # Hitung total jumlah
        total_jumlah = data_kesejahteraan["JUMLAH"].sum()

        # Menambahkan kolom persentase dan formatting
        data_kesejahteraan = data_kesejahteraan.with_columns(
            (pl.col("JUMLAH") / total_jumlah * 100).round(2).alias("PERSENTASE"),
            # Format angka dengan pemisah titik
            pl.col("JUMLAH").map_elements(
                lambda x: f"{int(x):,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("JUMLAH_FORMATTED")
        )

        # Format kolom persentase ke string dengan koma dan %
        data_kesejahteraan = data_kesejahteraan.with_columns(
            pl.col("PERSENTASE").map_elements(
                lambda x: f"{float(x):.2f}%".replace('.', ','),
                return_dtype=pl.Utf8
            ).alias("PERSENTASE_FORMAT")
        )

        # Warna untuk setiap tingkat kesejahteraan
        color_scale = alt.Scale(
            domain=custom_order,
            range=["#FF4500", "#FFA500", "#FFD700", "#3CB371", "#2E8B57"]  # Merah, Oranye, Kuning, Hijau muda, Hijau tua
        )


        # Membuat grafik batang horizontal dengan Altair
        chart = (
            alt.Chart(data_kesejahteraan)
            .mark_bar()
                .encode(
                    y=alt.Y("TINGKAT KESEJAHTERAAN:N", 
                            title="Tingkat Kesejahteraan", 
                            sort=custom_order),  # Urutkan sesuai custom order
                    x=alt.X("JUMLAH:Q", title="Jumlah Pengguna",
                            axis=alt.Axis(tickCount=3)),
                    color=alt.Color("TINGKAT KESEJAHTERAAN:N", 
                                scale=color_scale, 
                                legend=None),
                    tooltip=[
                        alt.Tooltip("TINGKAT KESEJAHTERAAN", title="Tingkat Kesejahteraan"),
                        alt.Tooltip("JUMLAH_FORMATTED:N", title="Jumlah"),
                        alt.Tooltip("PERSENTASE_FORMAT:N", title="Persentase")
                    ]
            )
        )

        # Menambahkan label di ujung batang
        text = (
            alt.Chart(data_kesejahteraan)
            .mark_text(align="left", baseline="middle", dx=5)
            .encode(
                y=alt.Y("TINGKAT KESEJAHTERAAN:N", sort="-x"),
                x=alt.X("JUMLAH:Q"),
                text=alt.X("JUMLAH_FORMATTED:N")
            )
        )

        chart = alt.layer(chart, text).properties(
                width='container',
                height='container',
                title="Perbandingan Pengguna Metode KB"
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                grid=False,
                labelFontSize=12,
                titleFontSize=14
            ).configure(
                padding={"left": 0, "right": 3, "top": 20, "bottom": 10},  # Sesuaikan padding
                background='#f6f8fa',
                autosize=alt.AutoSizeParams(
                    type='fit',
                    contains='padding'
                )
            ).configure_legend(
                disable=True  # Hapus legenda jika tidak diperlukan
            )
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def faktor_krs():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        faktor_krs = data_krs_verval.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa)
        ).group_by('PROVINSI').agg([
            pl.col("SUMBER AIR MINUM TIDAK LAYAK").sum(),
            pl.col("JAMBAN TIDAK LAYAK").sum(),
            pl.col("TERLALU MUDA").sum(),
            pl.col("TERLALU TUA").sum(),
            pl.col("TERLALU DEKAT").sum(),
            pl.col("TERLALU BANYAK").sum(),
            pl.col("BUKAN PESERTA KB MODERN").sum()
        ])

        faktor_krs = faktor_krs.unpivot(
            index="PROVINSI",  # Kolom yang tetap
            on=["SUMBER AIR MINUM TIDAK LAYAK", "JAMBAN TIDAK LAYAK", "TERLALU MUDA", "TERLALU TUA", "TERLALU DEKAT", "TERLALU BANYAK", "BUKAN PESERTA KB MODERN"],  # Kolom yang di-unpivot
            variable_name="FAKTOR KRS",  # Nama kolom untuk metode KB
            value_name="JUMLAH"  # Nama kolom untuk jumlah pengguna
        )


        # Urutkan data berdasarkan jumlah pengguna (terbesar ke terkecil)
        faktor_krs = faktor_krs.sort("JUMLAH", descending=True)

        # Menambahkan kolom persentase (dengan 2 angka desimal)
        # Menambahkan kolom persentase (dengan 2 angka desimal)
        faktor_krs = faktor_krs.with_columns(
            # Format angka dengan pemisah titik menggunakan map_elements
            pl.col("JUMLAH").map_elements(
                lambda x: f"{int(x):,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("JUMLAH FORMATTED")
        )

        # Mengurutkan data berdasarkan jumlah secara descending
        faktor_krs = faktor_krs.sort("JUMLAH", descending=True)

        # Membuat grafik batang horizontal dengan Altair
        chart = (
            alt.Chart(faktor_krs)
            .mark_bar(color=warna_biru)
            .encode(
                y=alt.Y("FAKTOR KRS:N", title="Faktor KRS", sort="-x"),
                x=alt.X("JUMLAH:Q", title="Jumlah",
                        axis=alt.Axis(
                        tickCount=3,  # BATASI 5 TICK SAJA
                        )),
                tooltip=[
                    alt.Tooltip("FAKTOR KRS", title="Faktor"),
                    alt.Tooltip("JUMLAH FORMATTED:Q", title="Jumlah")
                ]
            )
        )

        # Menambahkan label di ujung batang
        text = (
            alt.Chart(faktor_krs)
            .mark_text(align="left", baseline="middle", dx=5)
            .encode(
                y=alt.Y("FAKTOR KRS:N", sort="-x"),
                x=alt.X("JUMLAH:Q"),
                text="JUMLAH FORMATTED:Q"
            )
        )

        chart = alt.layer(chart, text).properties(
        width='container',
        height='container',
        title="Perbandingan Faktor KRS"
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                grid=False,
                labelFontSize=12,
                titleFontSize=14
            ).configure(
                padding={"left": 0, "right": 10, "top": 20, "bottom": 10},  # Sesuaikan padding
                background='#f6f8fa',
                autosize=alt.AutoSizeParams(
                    type='fit',
                    contains='padding'
                )
            ).configure_legend(
                disable=True  # Hapus legenda jika tidak diperlukan
            )
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def pie_punya_baduta():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        if input.pilih_kab() == "SEMUA KABUPATEN":
            data_kel_baduta = data_krs_verval.group_by(['KABUPATEN']).agg([
                pl.col("PUNYA BADUTA").sum()
            ])
            data_kel_baduta = data_kel_baduta.rename({
                "KABUPATEN": "KATEGORI"
            })
            subtitle_pie = "Berdasarkan Kabupaten"
            atur_radius = 100
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() == "SEMUA KECAMATAN":
            data_kel_baduta = data_krs_verval.with_columns(
                pl.when(pl.col("KABUPATEN") == str(input.pilih_kab()))
                .then(pl.lit(str(input.pilih_kab())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BADUTA").alias("PUNYA BADUTA")
            )
            subtitle_pie = input.pilih_kab() + " dan Kabupaten Lainnya"
            atur_radius = 150
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            data_kel_baduta = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten)
            ).with_columns(
                pl.when(pl.col("KECAMATAN") == str(input.pilih_kec()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BADUTA").alias("PUNYA BADUTA")
            )
            subtitle_pie = input.pilih_kec() + " dan Kec Lainnya \ndi Kab." + input.pilih_kab()
            atur_radius = 150
        else:
            data_kel_baduta = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan)
            ).with_columns(
                pl.when(pl.col("KELURAHAN") == str(input.pilih_desa()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BADUTA").alias("PUNYA BADUTA")
            )
            subtitle_pie = input.pilih_desa() + " dan Desa/Kelurahan Lainnya di Kec." + input.pilih_kec()
            atur_radius = 150

        data_kel_baduta = data_kel_baduta.with_columns(
            (pl.col("PUNYA BADUTA") / data_kel_baduta["PUNYA BADUTA"].sum() * 100).round(2).alias("PERSENTASE")
        )

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = data_kel_baduta["PERSENTASE"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        data_kel_baduta = data_kel_baduta.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # Definisi warna
        color_scale = alt.Scale(
            domain=["Sudah Terlatih", "Belum Terlatih"],
            range=[warna_biru, warna_kuning]  # Biru untuk Sudah Terlatih, Kuning untuk Belum
        )

        # Tambahkan kolom gabungan klasifikasi dan persentase
        data_kel_baduta = data_kel_baduta.with_columns(
            (pl.col("KATEGORI") + "\n" + pl.col("PERSENTASE_FORMAT")).alias("LABEL"),
            pl.col("PUNYA BADUTA").map_elements(
                lambda x: f"{int(x):,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("PUNYA BADUTA FORMATTED")
        ).sort('PERSENTASE')

        base = alt.Chart(data_kel_baduta, title=alt.Title(
            "Perbandingan Keluarga Memiliki Baduta",
            subtitle=subtitle_pie
        )).encode(
            alt.Theta("PUNYA BADUTA:Q").stack(True),
            alt.Color("KATEGORI:N", scale=alt.Scale(scheme='dark2')).legend(None),
            order=alt.Order("PUNYA BADUTA", sort="descending"),
            tooltip=[
                alt.Tooltip("KATEGORI", title="Wilayah"),
                alt.Tooltip("PUNYA BADUTA FORMATTED:Q", title="Jumlah")
            ]
        )

        pie = base.mark_arc(outerRadius=120)
        text = base.mark_text(radius=atur_radius, size=11, lineBreak="\n").encode(text="LABEL:N", color=alt.value("black"))
        
        # Gabungkan grafik pie dan teks, lalu atur warna latar belakang menjadi oranye
        chart = (pie + text).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},
            background='#f6f8fa'  # Mengubah latar belakang menjadi oranye
        )
            
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def pie_punya_balita():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        if input.pilih_kab() == "SEMUA KABUPATEN":
            data_kel_baduta = data_krs_verval.group_by(['KABUPATEN']).agg([
                pl.col("PUNYA BALITA").sum()
            ])
            data_kel_baduta = data_kel_baduta.rename({
                "KABUPATEN": "KATEGORI"
            })
            subtitle_pie = "Berdasarkan Kabupaten"
            atur_radius = 100
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() == "SEMUA KECAMATAN":
            data_kel_baduta = data_krs_verval.with_columns(
                pl.when(pl.col("KABUPATEN") == str(input.pilih_kab()))
                .then(pl.lit(str(input.pilih_kab())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BALITA").alias("PUNYA BALITA")
            )
            subtitle_pie = input.pilih_kab() + " dan Kabupaten Lainnya"
            atur_radius = 150
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            data_kel_baduta = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten)
            ).with_columns(
                pl.when(pl.col("KECAMATAN") == str(input.pilih_kec()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BALITA").alias("PUNYA BALITA")
            )
            subtitle_pie = input.pilih_kec() + " dan Kec Lainnya \ndi Kab." + input.pilih_kab()
            atur_radius = 150
        else:
            data_kel_baduta = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan)
            ).with_columns(
                pl.when(pl.col("KELURAHAN") == str(input.pilih_desa()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUNYA BALITA").alias("PUNYA BALITA")
            )
            subtitle_pie = input.pilih_desa() + " dan Desa/Kelurahan Lainnya di Kec." + input.pilih_kec()
            atur_radius = 150

        data_kel_baduta = data_kel_baduta.with_columns(
            (pl.col("PUNYA BALITA") / data_kel_baduta["PUNYA BALITA"].sum() * 100).round(2).alias("PERSENTASE")
        )

        data_kel_baduta = data_kel_baduta.with_columns(
            (pl.col("PUNYA BALITA") / data_kel_baduta["PUNYA BALITA"].sum() * 100).round(2).alias("PERSENTASE")
        )

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = data_kel_baduta["PERSENTASE"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        data_kel_baduta = data_kel_baduta.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # Definisi warna
        color_scale = alt.Scale(
            domain=["Sudah Terlatih", "Belum Terlatih"],
            range=[warna_biru, warna_kuning]  # Biru untuk Sudah Terlatih, Kuning untuk Belum
        )

        # Tambahkan kolom gabungan klasifikasi dan persentase
        data_kel_baduta = data_kel_baduta.with_columns(
            (pl.col("KATEGORI") + "\n" + pl.col("PERSENTASE_FORMAT")).alias("LABEL"),
            pl.col("PUNYA BALITA").map_elements(
                lambda x: f"{int(x):,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("PUNYA BALITA FORMATTED")
        ).sort('PERSENTASE')

        base = alt.Chart(data_kel_baduta, title=alt.Title(
            "Perbandingan Keluarga Memiliki Balita",
            subtitle=subtitle_pie
        )).encode(
            alt.Theta("PUNYA BALITA:Q").stack(True),
            alt.Color("KATEGORI:N", scale=alt.Scale(scheme= 'dark2')).legend(None),
            order=alt.Order("PUNYA BALITA", sort="descending"),
            tooltip=[
                alt.Tooltip("KATEGORI", title="Wilayah"),
                alt.Tooltip("PUNYA BALITA FORMATTED:Q", title="Jumlah")
            ]
        )

        pie = base.mark_arc(outerRadius=120)
        text = base.mark_text(radius=atur_radius, size=11, lineBreak="\n").encode(text="LABEL:N", color=alt.value("black"))
        
        # Gabungkan grafik pie dan teks, lalu atur warna latar belakang menjadi oranye
        chart = (pie + text).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},
            background='#f6f8fa'  # Mengubah latar belakang menjadi oranye
        )
            
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def pie_pus_hamil():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        if input.pilih_kab() == "SEMUA KABUPATEN":
            data_pus_hamil = data_krs_verval.group_by(['KABUPATEN']).agg([
                pl.col("PUS HAMIL").sum()
            ])
            data_pus_hamil = data_pus_hamil.rename({
                "KABUPATEN": "KATEGORI"
            })
            subtitle_pie = "Berdasarkan Kabupaten"
            atur_radius = 100
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() == "SEMUA KECAMATAN":
            data_pus_hamil = data_krs_verval.with_columns(
                pl.when(pl.col("KABUPATEN") == str(input.pilih_kab()))
                .then(pl.lit(str(input.pilih_kab())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUS HAMIL").alias("PUS HAMIL")
            )
            subtitle_pie = input.pilih_kab() + " dan Kabupaten Lainnya"
            atur_radius = 150
        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() != "SEMUA KECAMATAN" and input.pilih_desa() == "SEMUA DESA/KELURAHAN":
            data_pus_hamil = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten)
            ).with_columns(
                pl.when(pl.col("KECAMATAN") == str(input.pilih_kec()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUS HAMIL").alias("PUS HAMIL")
            )
            subtitle_pie = input.pilih_kec() + " dan Kec Lainnya \ndi Kab." + input.pilih_kab()
            atur_radius = 150
        else:
            data_pus_hamil = data_krs_verval.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("KECAMATAN").is_in(filter_kecamatan)
            ).with_columns(
                pl.when(pl.col("KELURAHAN") == str(input.pilih_desa()))
                .then(pl.lit(str(input.pilih_kec())))
                .otherwise(pl.lit("LAINNYA"))
                .alias("KATEGORI")
            ).group_by("KATEGORI").agg(
                pl.sum("PUS HAMIL").alias("PUS HAMIL")
            )
            subtitle_pie = input.pilih_desa() + " dan Desa/Kelurahan Lainnya di Kec." + input.pilih_kec()
            atur_radius = 150

        data_pus_hamil = data_pus_hamil.with_columns(
            (pl.col("PUS HAMIL") / data_pus_hamil["PUS HAMIL"].sum() * 100).round(2).alias("PERSENTASE")
        )

        # Format kolom persentase ke string dengan koma dan %
        persentase_list = data_pus_hamil["PERSENTASE"].to_list()
        persentase_format = [f"{x:.2f}".replace('.', ',') + '%' for x in persentase_list]
        data_pus_hamil = data_pus_hamil.with_columns(pl.Series("PERSENTASE_FORMAT", persentase_format))

        # Tambahkan kolom gabungan klasifikasi dan persentase
        data_pus_hamil = data_pus_hamil.with_columns(
            (pl.col("KATEGORI") + "\n" + pl.col("PERSENTASE_FORMAT")).alias("LABEL"),
            pl.col("PUS HAMIL").map_elements(
                lambda x: f"{int(x):,}".replace(",", "."),
                return_dtype=pl.Utf8
            ).alias("PUS HAMIL FORMATTED")
        ).sort('PERSENTASE')

        base = alt.Chart(data_pus_hamil, title=alt.Title(
            "Perbandingan PUS Hamil",
            subtitle=subtitle_pie
        )).encode(
            alt.Theta("PUS HAMIL:Q").stack(True),
            alt.Color("KATEGORI:N", scale=alt.Scale(scheme= 'dark2')).legend(None),
            order=alt.Order("PUS HAMIL", sort="descending"),
            tooltip=[
                alt.Tooltip("KATEGORI", title="Wilayah"),
                alt.Tooltip("PUS HAMIL FORMATTED:Q", title="Jumlah")
            ]
        )

        pie = base.mark_arc(outerRadius=120)
        text = base.mark_text(radius=atur_radius, size=11, lineBreak="\n").encode(text="LABEL:N", color=alt.value("black"))
        
        # Gabungkan grafik pie dan teks, lalu atur warna latar belakang menjadi oranye
        chart = (pie + text).configure(
            padding={"left": 0, "right": 0, "top": 20, "bottom": 0},
            background='#f6f8fa'  # Mengubah latar belakang menjadi oranye
        )
            
        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def tabel_reactable():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = [input.pilih_bulan()]
        if input.pilih_kab() == "SEMUA KABUPATEN":
            jenjang = "KABUPATEN"

        elif input.pilih_kab() != "SEMUA KABUPATEN" and  input.pilih_kec() == "SEMUA KECAMATAN":
            jenjang = "KECAMATAN"
        else:
            jenjang = "KELURAHAN"
        def process_data(df, unit_name):
            # Pastikan kolom yang akan dihitung adalah numerik
            df = df.with_columns([
                pl.col("YANG ADA").cast(pl.Int64),
                pl.col("YANG LAPOR").cast(pl.Int64)
            ])
            
            # Lakukan filter dan agregasi
            processed_df = df.filter(
                pl.col("KABUPATEN").is_in(filter_kabupaten),
                pl.col("BULAN").is_in(filter_bulan),
                pl.col("KECAMATAN").is_in(filter_kecamatan),
                pl.col("KELURAHAN").is_in(filter_desa)
            ).group_by([jenjang]).agg([
                pl.col("YANG ADA").sum().alias(f"JUMLAH {unit_name}"),
                pl.col("YANG LAPOR").sum().alias(f"JUMLAH {unit_name} LAPOR")
            ]).with_columns(
                (
                    pl.col(f"JUMLAH {unit_name}") - pl.col(f"JUMLAH {unit_name} LAPOR")
                ).alias(f"{unit_name} BELUM LAPOR")
            )
            
            return processed_df

        # Proses setiap DataFrame menggunakan fungsi
        result_bkb = process_data(data_bkb, "BKB")
        result_bkr = process_data(data_bkr, "BKR")
        result_bkl = process_data(data_bkl, "BKL")
        result_uppka = process_data(data_uppka, "UPPKA")
        result_pikr = process_data(data_pikr, "PIK-R")

        # Gabungkan semua hasil ke dalam satu DataFrame tunggal
        # Gunakan join berantai pada kolom 'KABUPATEN'
        final_result = result_bkb.join(
            result_bkr, on=jenjang, how='inner'
        ).join(
            result_bkl, on=jenjang, how='inner'
        ).join(
            result_uppka, on=jenjang, how='inner'
        ).join(
            result_pikr, on=jenjang, how='inner'
        )

        return ITable(final_result,  
                      caption="A table rendered with ITable", 
                      buttons=["copyHtml5", "excelHtml5"],
                      scrollX=True,
                      paging = False,
                      fixedColumns={"start": 1},
                      select=True) 
        # Note: df is an optional argument 
    ### eksplore
    ### esplore

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)