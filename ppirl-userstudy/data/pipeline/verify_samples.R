pacman::p_load(fs, tidyverse, rebus)



vc_samples <- dir_ls("data_output/samples_sections_scrambling/")

df_sample_check <- 
  vc_samples %>% 
  str_extract_all(one_or_more(DGT), simplify = T) %>% 
  as_tibble() %>% 
  rename(section = V1, 
         sample = V2) %>% 
  mutate(section = section %>% as.integer(),
         sample = sample %>% as.integer(),
         file_name = vc_samples, 
         df = map(file_name, read_csv, col_names = F), 
         n = map_int(df, nrow))


df_sample_check %>% 
  arrange(section, sample) %>% 
  group_by(sample) %>% 
  summarise(overlap = df %>% reduce(semi_join, by = "X1") %>% nrow(.))

df_sample_check %>% 
  filter(sample)


overlap <-
df_sample_check$df %>% reduce(semi_join, "X1")

df_sample_check %>% 
  filter(section == 3, 
         sample == 3) %>% 
  pull(df)

