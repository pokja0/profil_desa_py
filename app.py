from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import shinyswatch
from htmltools import css

import polars as pl
from shinywidgets import output_widget, render_widget

import plotly.express as px
import faicons

import shiny as pyshiny

import pandas as pd
from great_tables import GT, exibble, loc, style
from ipyleaflet import Map 
import folium
import ipyleaflet

import math

import great_tables as gt
from itables.sample_dfs import get_countries
from itables.shiny import DT

from pathlib import Path
import asyncio
from htmltools import head_content
import altair as alt


daftar_bulan = ["JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI", "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER"]

data_poktan = pl.read_csv("data/profil_poktan.csv")

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
                                 choices=daftar_bulan[:2], selected="FEBRUARI")#,
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
                "Profil",
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
                ui.layout_column_wrap(
                    ui.card(
                        "Administrasi",
                    ),
                    ui.card(
                        ui.layout_column_wrap(
                            ui.output_ui("kepemilikan_poktan"),
                            ui.output_ui("profil_wilayah")
                        )
                    )
                ),
                ui.layout_column_wrap(
                    ui.card(
                        output_widget("grafik_piramida")
                    ),
                    ui.card(
                        ui.output_data_frame("tabel_piramida")
                    )
                ),
                # ui.layout_column_wrap(
                #     ui.card(
                #         ui.output_data_frame("df")
                #     )
                # )
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
                "Stunting"
            ),
        )
        
    ),
    ui.nav_panel(
        "Download Data", "ini"
    ),
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
    data_pkb = pl.read_csv("data/nama pkb.csv") 
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
                        ).select(['KECAMATAN', 'NAMA PKB']).unique().height)
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
    
    data_pus = pl.read_csv("data/data_pus.csv")
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
    
    data_mix = pl.read_csv("data/data_mix_kontra.csv")
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
    
    
    faskes_sdm = pl.read_csv("data/data_faskes_siga.csv")
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
    
    data_krs_verval = pl.read_csv("data/data_verval_krs_2024_sem1.csv")
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
                    pl.col("KRS").sum(),
                ]).select(pl.col("KRS")).item())

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

    sasaran_poktan = pl.read_csv("data/sasaran_poktan_gabung.csv")
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
    
    data_bkb = pl.read_csv("data/data_bkb.csv")
    data_bkr = pl.read_csv("data/data_bkr.csv")
    data_bkl = pl.read_csv("data/data_bkl.csv")
    data_uppka = pl.read_csv("data/data_uppka.csv")
    data_pikr = pl.read_csv("data/data_pikr.csv")
    data_kkb = pl.read_csv("data/data_kkb.csv")
    data_rdk = pl.read_csv("data/data_rdk.csv")
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
        ).select(pl.col("JUMLAH_BKB")).sum().item()

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
        ).select(pl.col("JUMLAH_BKR")).sum().item()

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
        ).select(pl.col("JUMLAH_BKL")).sum().item()

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
        ).select(pl.col("JUMLAH_UPPKA")).sum().item()

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
        ).select(pl.col("JUMLAH_PIKR")).sum().item()

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
        filter_bulan = [input.pilih_bulan()]

        jumlah_kkb = data_kkb.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("JUMLAH_KKB")).sum().item()

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
        filter_bulan = [input.pilih_bulan()]

        jumlah_rdk = data_rdk.filter(
            pl.col("KABUPATEN").is_in(filter_kabupaten),
            pl.col("KECAMATAN").is_in(filter_kecamatan),
            pl.col("KELURAHAN").is_in(filter_desa),
            pl.col("BULAN").is_in(filter_bulan)
        ).select(pl.col("JUMLAH_RDK")).sum().item()

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
    
    @render_widget
    @reactive.event(input.action_button)
    def grafik_piramida():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        
        kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
        kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                                    pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_lk = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Laki-laki"
        )

        kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
        kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_pr = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Perempuan"
        )

        df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

        # Daftar kategori usia
        ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
            "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
            "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
            "65 - 69", "70 - 74", "75+"]

        # Menghitung berapa kali daftar ku perlu diulang
        repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
        repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

        # Menambahkan kolom kategori umur
        df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])

        y_age = df_horizontal_join['Kategori_Umur'] 
        x_M = df_horizontal_join['Laki-laki'] 
        x_F = df_horizontal_join['Perempuan'] * -1

        if max(x_M) >= max(x_F):
            maks = max(x_M)
        else:
            maks = max(x_F)

        def round_up_to_nearest(number, base):
            return base * math.ceil(number / base)

        def auto_round_up(number):
            if number == 0:
                return 0
            base = 10 ** (len(str(number)) - 1)
            return round_up_to_nearest(number, base)

        maks1 = auto_round_up(maks)
        maks2 = auto_round_up(int(maks - (maks * 1 / 3)))
        maks3 = auto_round_up(int(maks - (maks * 2 / 3)))

        tick_vals = [-maks1, -maks2, -maks3, 0, maks1, maks2, maks3]
        tick_str = [str(abs(value)) for value in tick_vals]

        import plotly.graph_objects as gp
        # Creating instance of the figure 
        fig = gp.Figure() 
        

        # Adding Female data to the figure 
        fig.add_trace(gp.Bar(y = y_age, x = x_F, 
                            name = 'Perempuan', orientation = 'h',
                            marker=dict(color='#ffc107'),
                            hovertemplate='Perempuan Umur %{y}<br>Jumlah: %{customdata}<extra></extra>',
                            customdata=[abs(x) for x in x_F]
                            )) 

        # Adding Male data to the figure 
        fig.add_trace(gp.Bar(y= y_age, x = x_M,  
                            name = 'Laki-laki',  
                            orientation = 'h',
                            marker=dict(color='#0d6efd'),
                            hovertemplate='Laki-laki Umur %{y}<br> %{x}<extra></extra>')) 

        
        # Updating the layout for our graph 
        fig.update_layout(title={
                            'text': 'Piramida Penduduk ' + str(val_judul.get()),
                            'y': 0.98,  # Adjust this value to move the title up or down
                            'x': 0.5,  # Centered horizontally
                            'xanchor': 'center',
                            'yanchor': 'top'
                        },
                        title_font_size = 18, barmode = 'relative', 
                        bargap = 0.0, bargroupgap = 0, 
                        xaxis = dict(tickvals = tick_vals, 
                                    ticktext = tick_str, 
                                    title = 'Jumlah', 
                                    title_font_size = 14),
                        legend=dict(
                                orientation='h',
                                yanchor='bottom',
                                y=-0.3,  # Adjust this value to move the legend up or down
                                xanchor='center',
                                x=0.5
                        ),
                        plot_bgcolor='#f6f8fa',  # Set background color of the plot area to green
                        paper_bgcolor='#f6f8fa'  # Set background color of the entire canvas to green 
        )
        
        return fig

    @render.data_frame
    @reactive.event(input.action_button)
    def tabel_piramida():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        
        kelompok_umur_lk = pl.read_csv('data/PIRAMIDA PENDUDUK - Laki-laki.csv')
        kelompok_umur_lk = kelompok_umur_lk.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                                    pl.col("KECAMATAN").is_in(filter_kecamatan),
                                    pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_lk.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_lk.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_lk = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Laki-laki"
        )

        kelompok_umur_pr = pl.read_csv('data/PIRAMIDA PENDUDUK - Perempuan.csv')
        kelompok_umur_pr = kelompok_umur_pr.filter(pl.col("KABUPATEN").is_in(filter_kabupaten),
                            pl.col("KECAMATAN").is_in(filter_kecamatan),
                            pl.col("KELURAHAN").is_in(filter_desa))
        # Mendefinisikan range kolom yang akan dijumlahkan
        columns_to_sum = [kelompok_umur_pr.columns[i] for i in range(6, 23)]

        # Membuat daftar agregasi
        aggregations = [pl.sum(col) for col in columns_to_sum]

        # Melakukan pengelompokan dan agregasi
        result = kelompok_umur_pr.group_by("PROVINSI").agg(aggregations)

        # Asumsi bahwa 'result' adalah DataFrame yang dihasilkan dari kode sebelumnya
        columns_to_melt = [col for col in result.columns if col != "PROVINSI"]

        # Melakukan melt pada DataFrame
        melted_result_pr = result.melt(
            id_vars=["PROVINSI"], 
            value_vars=columns_to_melt, 
            variable_name="Age_Group", 
            value_name="Perempuan"
        )

        df_horizontal_join = melted_result_pr.join(melted_result_lk, on="Age_Group", how="inner")

        # Daftar kategori usia
        ku = ["0 - 1", "2 - 4", "5 - 9", "10 - 14", "15 - 19", 
            "20 - 24", "25 - 29", "30 - 34", "35 - 39", "40 - 44", 
            "45 - 49", "50 - 54", "55 - 59", "60 - 64", 
            "65 - 69", "70 - 74", "75+"]

        # Menghitung berapa kali daftar ku perlu diulang
        repeat_count = df_horizontal_join.shape[0] // len(ku) + 1
        repeated_ku = (ku * repeat_count)[:df_horizontal_join.shape[0]]

        # Menambahkan kolom kategori umur
        df_horizontal_join = df_horizontal_join.with_columns([pl.Series(name="Kategori_Umur", values=repeated_ku)])
        df_horizontal_join = df_horizontal_join.select('Kategori_Umur', 'Perempuan', 'Laki-laki')


        df_horizontal_join = df_horizontal_join.with_columns(
            (pl.col("Perempuan") + pl.col("Laki-laki")).alias("Total")
        )
        return render.DataGrid(df_horizontal_join)
    ### akhir profil

    ### awal KB
    data_pus = pl.read_csv("data/data_pus.csv")
    data_mix = pl.read_csv("data/data_mix_kontra.csv")
    @render_widget
    @reactive.event(input.action_button)
    def tren_pus():
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
            point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color='#3498db')
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

        # === Anotasi Label (Perubahan warna) ===
        start_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == first_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color='#3498db'  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PUS:Q'),
            text=alt.Text('JUMLAH PUS:N')
        )

        end_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == last_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=11, 
            fontWeight='bold', 
            color='#3498db'  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PUS:Q'),
            text=alt.Text('JUMLAH PUS:N')
        )

        # === Gabungkan Semua Elemen ===
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

        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_pa():
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
                .alias("PUS_formatted")
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
            point=alt.OverlayMarkDef(size=200, filled=True, fillOpacity=1, color='#3498db')
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
                        title='Jumlah PUS'
                    )),
            tooltip=[alt.Tooltip('BULAN:N'), alt.Tooltip('PUS_formatted:N')]
        )

        # === Anotasi Label (Perubahan warna) ===
        start_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == first_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=14, 
            fontWeight='bold', 
            color='#3498db'  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PUS:Q'),
            text=alt.Text('PUS_formatted:N')
        )

        end_label = alt.Chart(df_processed).transform_filter(
            alt.datum.BULAN == last_month
        ).mark_text(
            align='center', 
            dy=-25, 
            fontSize=14, 
            fontWeight='bold', 
            color='#3498db'  # Sesuaikan dengan warna point
        ).encode(
            x=alt.X('BULAN:N', sort=list(month_order.keys())),
            y=alt.Y('PUS:Q'),
            text=alt.Text('PUS_formatted:N')
        )

        # === Gabungkan Semua Elemen ===
        chart = alt.layer(base, start_label, end_label).properties(
            title='Tren Jumlah PUS di Sulawesi Barat'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False,
            labelFontSize=12,
            titleFontSize=14
        ).configure(
            padding=20,
            background='#f6f8fa'
        )

        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_unmet_need():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        aggregated =  data_pus.filter(
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
            aggregated
            .with_columns(
                pl.col("BULAN").replace(month_order).alias("month_order"),
                # Format angka dengan pemisah titik (.) untuk tooltip
                pl.col("PUS").map_elements(
                    lambda x: f"{x:,}".replace(",", "."),
                    return_dtype=pl.Utf8
                ).alias("PUS_formatted")
            )
            .sort("month_order")
        )

        # Hitung batas y-axis
        min_value = df_processed["PUS"].min()
        max_value = df_processed["PUS"].max()
        y_min = min_value - (min_value * 0.001)
        y_max = max_value + (max_value * 0.001)

        # Konversi ke Pandas untuk Altair
        df_for_viz = df_processed.to_pandas()

        # Buat grafik
        chart = alt.Chart(df_for_viz).mark_line(point=True).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0,  # Label horizontal
                        labelLimit=150,  # Batas lebar label sebelum otomatis rotate
                        labelOverlap="parity"  # Hindari tumpang tindih
                    )),
            y=alt.Y('PUS:Q',
                    scale=alt.Scale(domain=(y_min, y_max), nice=False),
                    axis=alt.Axis(
                        labelExpr='replace(format(datum.value, ",.0f"), ",", ".")',
                        title='Jumlah PUS'
                    )),
            tooltip=[
                alt.Tooltip('BULAN:N', title='Bulan'),
                alt.Tooltip('PUS_formatted:N', title='Jumlah PUS')
            ]
        ).properties(
            title='Tren Jumlah PUS di Sulawesi Barat'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False
        ).configure_point(
            size=100
        ).configure(
            padding=20,  # Tambah padding
            background='#f6f8fa'  # Warna background
        )

        return chart

    @render_widget
    @reactive.event(input.action_button)
    def tren_mkjp():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        aggregated =  data_pus.filter(
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
            aggregated
            .with_columns(
                pl.col("BULAN").replace(month_order).alias("month_order"),
                # Format angka dengan pemisah titik (.) untuk tooltip
                pl.col("PUS").map_elements(
                    lambda x: f"{x:,}".replace(",", "."),
                    return_dtype=pl.Utf8
                ).alias("PUS_formatted")
            )
            .sort("month_order")
        )

        # Hitung batas y-axis
        min_value = df_processed["PUS"].min()
        max_value = df_processed["PUS"].max()
        y_min = min_value - (min_value * 0.001)
        y_max = max_value + (max_value * 0.001)

        # Konversi ke Pandas untuk Altair
        df_for_viz = df_processed.to_pandas()

        # Buat grafik
        chart = alt.Chart(df_for_viz).mark_line(point=True).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0,  # Label horizontal
                        labelLimit=150,  # Batas lebar label sebelum otomatis rotate
                        labelOverlap="parity"  # Hindari tumpang tindih
                    )),
            y=alt.Y('PUS:Q',
                    scale=alt.Scale(domain=(y_min, y_max), nice=False),
                    axis=alt.Axis(
                        labelExpr='replace(format(datum.value, ",.0f"), ",", ".")',
                        title='Jumlah PUS'
                    )),
            tooltip=[
                alt.Tooltip('BULAN:N', title='Bulan'),
                alt.Tooltip('PUS_formatted:N', title='Jumlah PUS')
            ]
        ).properties(
            title='Tren Jumlah PUS di Sulawesi Barat'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False
        ).configure_point(
            size=100
        ).configure(
            padding=20,  # Tambah padding
            background='#f6f8fa'  # Warna background
        )

        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def bar_mix_kontrasepsi():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        aggregated =  data_pus.filter(
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
            aggregated
            .with_columns(
                pl.col("BULAN").replace(month_order).alias("month_order"),
                # Format angka dengan pemisah titik (.) untuk tooltip
                pl.col("PUS").map_elements(
                    lambda x: f"{x:,}".replace(",", "."),
                    return_dtype=pl.Utf8
                ).alias("PUS_formatted")
            )
            .sort("month_order")
        )

        # Hitung batas y-axis
        min_value = df_processed["PUS"].min()
        max_value = df_processed["PUS"].max()
        y_min = min_value - (min_value * 0.001)
        y_max = max_value + (max_value * 0.001)

        # Konversi ke Pandas untuk Altair
        df_for_viz = df_processed.to_pandas()

        # Buat grafik
        chart = alt.Chart(df_for_viz).mark_line(point=True).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0,  # Label horizontal
                        labelLimit=150,  # Batas lebar label sebelum otomatis rotate
                        labelOverlap="parity"  # Hindari tumpang tindih
                    )),
            y=alt.Y('PUS:Q',
                    scale=alt.Scale(domain=(y_min, y_max), nice=False),
                    axis=alt.Axis(
                        labelExpr='replace(format(datum.value, ",.0f"), ",", ".")',
                        title='Jumlah PUS'
                    )),
            tooltip=[
                alt.Tooltip('BULAN:N', title='Bulan'),
                alt.Tooltip('PUS_formatted:N', title='Jumlah PUS')
            ]
        ).properties(
            title='Tren Jumlah PUS di Sulawesi Barat'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False
        ).configure_point(
            size=100
        ).configure(
            padding=20,  # Tambah padding
            background='#f6f8fa'  # Warna background
        )

        return chart
    
    @render_widget
    @reactive.event(input.action_button)
    def donut_perbandingan_tenaga_kb():
        filter_kabupaten = val_kab.get()
        filter_kecamatan = val_kec.get()
        filter_desa = val_desa.get()
        filter_bulan = input.pilih_bulan()
        aggregated =  data_pus.filter(
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
            aggregated
            .with_columns(
                pl.col("BULAN").replace(month_order).alias("month_order"),
                # Format angka dengan pemisah titik (.) untuk tooltip
                pl.col("PUS").map_elements(
                    lambda x: f"{x:,}".replace(",", "."),
                    return_dtype=pl.Utf8
                ).alias("PUS_formatted")
            )
            .sort("month_order")
        )

        # Hitung batas y-axis
        min_value = df_processed["PUS"].min()
        max_value = df_processed["PUS"].max()
        y_min = min_value - (min_value * 0.001)
        y_max = max_value + (max_value * 0.001)

        # Konversi ke Pandas untuk Altair
        df_for_viz = df_processed.to_pandas()

        # Buat grafik
        chart = alt.Chart(df_for_viz).mark_line(point=True).encode(
            x=alt.X('BULAN:N', 
                    sort=list(month_order.keys()),
                    axis=alt.Axis(
                        labelAngle=0,  # Label horizontal
                        labelLimit=150,  # Batas lebar label sebelum otomatis rotate
                        labelOverlap="parity"  # Hindari tumpang tindih
                    )),
            y=alt.Y('PUS:Q',
                    scale=alt.Scale(domain=(y_min, y_max), nice=False),
                    axis=alt.Axis(
                        labelExpr='replace(format(datum.value, ",.0f"), ",", ".")',
                        title='Jumlah PUS'
                    )),
            tooltip=[
                alt.Tooltip('BULAN:N', title='Bulan'),
                alt.Tooltip('PUS_formatted:N', title='Jumlah PUS')
            ]
        ).properties(
            title='Tren Jumlah PUS di Sulawesi Barat'
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            grid=False
        ).configure_point(
            size=100
        ).configure(
            padding=20,  # Tambah padding
            background='#f6f8fa'  # Warna background
        )

        return chart
    ### akhir KB

    ###progress
    @render.text
    @reactive.event(input.button)
    async def compute():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 5):
                p.set(i, message="Computing")
                await asyncio.sleep(1)
                # Normally use time.sleep() instead, but it doesn't yet work in Pyodide.
                # https://github.com/pyodide/pyodide/issues/2354

        return "Done computing!"

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)