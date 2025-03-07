library(tidyverse)
library(csv)
wd = "/home/hi/Documents/projects/Scraping Profil Desa/hasil"
daftar_desa <- read.csv("data/data_daftar_desa.csv")
# bkb <- fread("data/data_bkb.csv")
# write.csv(bkb, "data/data_bkb.csv")
bkb <- read_csv("data/data_bkb.csv")

bkb_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-data_bkb_result.xlsx")

bkb_scrap <- bkb_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, Kelurahan_Desa) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan_Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(bkb_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_BKB", "BULAN")

sum(bkb_scrap$JUMLAH_BKB)

#kolom_v1 <- rep("JANUARI", 648)

bkb <- rbind(bkb, bkb_scrap)

write_csv(bkb, "data/data_bkb.csv")

###BKR
# bkr <- fread("data/data_bkr.csv")
# write.csv(bkr, "data/data_bkr.csv")
bkr <- read_csv("data/data_bkr.csv")
bkr_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-data_bkr_result.xlsx")

bkr_scrap <- bkr_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, Kelurahan_Desa) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan_Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 1))

colnames(bkr_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_BKR", "BULAN")

sum(bkr_scrap$JUMLAH_BKR)

bkr <- rbind(bkr, bkr_scrap)
write_csv(bkr, "data/data_bkr.csv")

#bkl
# bkl <- fread("data/data_bkl.csv")
# write.csv(bkl, "data/data_bkl.csv")
bkl <- read_csv("data/data_bkl.csv")

bkl_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-k0_bkl.xlsx")

bkl_scrap <- bkl_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, Kelurahan_Desa) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan_Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(bkl_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_BKL", "BULAN")

sum(bkl_scrap$JUMLAH_BKL)

bkl <- rbind(bkl, bkl_scrap)
write_csv(bkl_scrap, "data/data_bkl.csv")

#upppka
# uppka <- fread("data/data_uppka.csv")
# write.csv(uppka, "data/data_uppka.csv")
uppka <- read_csv("data/data_uppka.csv")

uppka_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-data_uppka.xlsx")

uppka_scrap <- uppka_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, Kelurahan_Desa) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan_Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(uppka_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_UPPKA", "BULAN")

sum(uppka_scrap$JUMLAH_UPPKA)

uppka <- rbind(uppka, uppka_scrap)
write_csv(uppka, "data/data_uppka.csv")

#
# pikr <- fread("data/data_pikr.csv")
# write.csv(pikr, "data/data_pikr.csv")
pikr <- read_csv("data/data_pikr.csv")

pikr_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025_feb_k0_pikr.xlsx")

pikr_scrap <- pikr_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, `Kelurahan/Desa`) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan/Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(pikr_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_PIKR", "BULAN")

sum(pikr_scrap$JUMLAH_PIKR)

pikr <- rbind(pikr, pikr_scrap)
write_csv(pikr, "data/data_pikr.csv")

#
# kkb <- fread("data/data_kkb.csv")
# write.csv(kkb, "data/data_kkb.csv")
kkb <- read_csv("data/data_kkb.csv")

kkb_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-k0-kkb.xlsx")

kkb_scrap <- kkb_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, `Kelurahan/Desa`) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan/Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(kkb_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_KKB", "BULAN")

sum(kkb_scrap$JUMLAH_KKB)

kkb <- rbind(kkb, kkb_scrap)
write_csv(kkb_scrap, "data/data_kkb.csv")

#
# rdk <- fread("data/data_rdk.csv")
# write.csv(rdk, "data/data_rdk.csv")
rdk <- read_csv("data/data_rdk.csv")

rdk_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-data_k0_rdk.xlsx")

rdk_scrap <- rdk_scrap %>%
  dplyr::group_by(Provinsi, Kabupaten, Kecamatan, `Kelurahan/Desa`) %>%
  summarise(JUMLAH = n()) %>%
  full_join(daftar_desa, by = c("Provinsi" = "PROVINSI",
                                "Kabupaten" = "KABUPATEN",
                                "Kecamatan" = "KECAMATAN",
                                "Kelurahan/Desa" = "KELURAHAN")) %>%
  replace_na(list(JUMLAH = 0)) %>%
  ungroup() %>%
  mutate(BULAN = rep("FEBRUARI", 648))

colnames(rdk_scrap) <- c("PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "JUMLAH_RDK", "BULAN")

sum(rdk_scrap$JUMLAH_RDK)

rdk <- rbind(rdk, rdk_scrap)
write_csv(rdk, "data/data_rdk.csv")


###FASKES
sdm_kb <- read_csv("data/data_faskes_siga.csv") 
sdm_kb_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-faskes_siga.xlsx")
sdm_kb_scrap <- sdm_kb_scrap %>%
  mutate(`Nama Bidan` = substr(`Nama Bidan` , start = 1, stop = 3),
         `NIK Bidan` = substr(`NIK Bidan` , start = 1, stop = 3))

colnames(sdm_kb_scrap) <-  c("NO", "PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "NAMA FASKES",
                             "NO REGISTRASI", "NAMA BIDAN", "NIK BIDAN", "ALAMAT", "NO HP", "PROFESI",
                             "PELATIHAN", "STATUS UPDATE", "BULAN")

sdm_kb <- rbind(sdm_kb, sdm_kb_scrap)
write_csv(sdm_kb, "data/data_faskes_siga.csv")

##mix
# data_mix_kontra <- read.csv("data/data_mix_kontra.csv") 
data_mix_kontra_scrap_feb = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-kb_kontra.xlsx")
colnames(data_mix_kontra_scrap) <- c("NO", "PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "PA",
                                     "SUNTIK", "PIL", "KONDOM", "IMPLAN", "IUD", "VASEKTOMI",
                                     "TUBEKTOMI", "MAL", "KB MODERN", "KB TRADISIONAL", "BULAN")

write_csv(data_mix_kontra_scrap, "data/data_mix_kontra.csv")

##pus
# data_pus <- read_csv("data/data_pus.csv")

data_pus_scrap = readxl::read_excel(path = "/home/hi/Documents/projects/Scraping Profil Desa/hasil/2025-feb-pus1.xlsx")
colnames(data_pus_scrap) <- c("NO", "PROVINSI", "KABUPATEN", "KECAMATAN", "KELURAHAN", "PUS", 
                              "UNMET NEED", "BULAN")

data_pus_scrap <- rbind(data_pus, data_pus_scrap)
write_csv(data_pus_scrap, "data/data_pus.csv")
