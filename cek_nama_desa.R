library(tidyverse)

data_poktan <- read.csv2("I:/Datin/Project/profil_desa_py/data/profil_poktan.csv")

data_poktan |>
  summarise(n_distinct(KELURAHAN))

data_faskes <- read.csv2("I:/Datin/Project/profil_desa_py/data/data_mix_kontra.csv")

data_faskes_januari = data_faskes %>%
  filter(
    BULAN == "JANUARI")

sum(data_faskes_januari$PA)

data_faskes_filter = data_faskes %>%
  filter(KABUPATEN %in% unique(data_poktan$KABUPATEN),
        KECAMATAN %in% unique(data_poktan$KECAMATAN),
        KELURAHAN %in% unique(data_poktan$KELURAHAN),
        BULAN == "JANUARI")

data_faskes_januari %>%
  group_by(PROVINSI) |>
  summarise(jumlah = n_distinct(NO.REGISTRASI))

beda_nama = anti_join(data_faskes_januari, data_faskes_filter, by = c("KABUPATEN", "KECAMATAN", "KELURAHAN"))

sum(cek_jumlah_desa$jumlah)

