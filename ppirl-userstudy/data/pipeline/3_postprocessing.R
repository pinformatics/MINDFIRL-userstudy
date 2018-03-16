library(tidyverse)
library(magrittr)

is_not_empty <- function(string) {
  if(is.na(string) | string == "" | string == ".") {
    return(FALSE)
  } else {
    return(TRUE)
  }
}

is_not_empty = Vectorize(is_not_empty)

col_names <- c("Group ID", "ID", 
               "FF", "First Name", 
               "Last Name", "LF",
               "DoB", "Sex", "Race",
               "Reg No.", "First Name", "Last Name",
               "DoB", "Sex", "Race",
               "Record ID", "type","Same")

#[Group ID, Reg No., FF, First Name, Last Name, LF, 
# DoB, Race, Reg No., First Name, Last Name, 
#DoB, Race, Record ID, type, Answer]


(starred_data <- read_csv("./data_intermediate/all_starred_race.csv", 
                          col_types = cols(.default = "c", `Group ID` = "i")) %>%
  mutate_all(funs(ifelse(is_not_empty(.),.,""))) %>%
    mutate(src = str_extract(`Record ID`, "[AB]")) %>%
      rename(fname = `First Name`,
             lname = `Last Name`))



(starred_data <- 
  starred_data %>%
    mutate(`Record ID` = str_extract(`Record ID`,"[0-9]+")))

starred_data <- 
  starred_data %>%
  select(`Group ID`, `Reg No.`, FF, fname, lname, LF,
         DoB,Sex, Race, `Reg No._1`, `First Name_1`, `Last Name_1`, DoB_1,Sex_1, Race_1, 
         `Record ID`, type, Same) %>%
  arrange(as.numeric(`Group ID`))

# Reorganize confusing variable names
starred_data <- 
  starred_data %>% 
    rename(id = `Group ID`,
           type = `Record ID`,
           page = type)


attention_test = c(1,7,13,19,25,31)

set.seed(1)
for(i in 1:10) {
  # group by type and get one random pair for each type
  # sampling to ensure different samples get different questions
  ids_table <-
    starred_data %>%
    select(id, type) %>% 
    group_by(type) %>%
    sample_n(1) %>% 
    ungroup()
  
  # separate non-atention questions and scramble 
  # scramble to ensure order of questions is different
  (ids_legit <- 
    ids_table %>%
    filter(!type %in% attention_test) %>% 
    pull(id) %>% 
    sample(., length(.)))
  
  # separate attention questions and sample
  # sample to ensure attention questions also do not have a set order 
  (ids_attention <- 
    ids_table %>%
    filter(type %in% attention_test) %>% 
    pull(id) %>% 
    sample(., length(.)))

  
  # create tables by assigning pages 1 - 6 for both the ids
  # bind the tables, and scramble withig a page to ensure attention questions not always the last in page
  # ungroup and add question number to later sort the sample by
  # remove page to avoid confusion
  (lookup_scrambled <- 
      tibble(id = ids_legit, page = rep(seq(1,6), each = 5)) %>% 
      bind_rows(tibble(id = ids_attention, page = seq(1,6))) %>% 
      group_by(page) %>% 
      sample_n(6) %>% 
      ungroup() %>%
      mutate(qnum = row_number()) %>%
      select(-page))

  # extract the data corresponding to the ids we filtered in step 1
  # this table is obviously not scrambled
  (sample_i <- 
      starred_data %>% filter(id %in% ids_table$id))
  
  
  # number and arrange by lookup
  sample_i_scrambled <- 
    sample_i %>%
    left_join(lookup_scrambled, by = "id") %>%
    arrange(qnum) %>% 
    select(-qnum) 
  
  #extract everything but those ids for section 2
  (section2  <- 
    starred_data %>%
    filter(!(id %in% ids_table$id)) %>%
    filter(!(type %in% attention_test)))
  
  (sec2_ids_scrambled <- 
    section2 %>%
    pull(id) %>%
    unique() %>% 
    sample(., length(.)))
  
  #we create a lookup for those gids
  (lookup_sec2 <- 
    tibble(id = sec2_ids_scrambled) %>%
    mutate(qnum = 1:n()))
  
  section2_scrambled <- 
    section2 %>%
    left_join(lookup_sec2, by = "id") %>%
    arrange(qnum) %>% 
    select(-qnum)

  # #make the names standard
  # names(sample_i) <- col_names
  # names(section2) <- col_names
  # names(sample_i_scrambled) <- col_names
  # names(section2_scrambled) <- col_names
  
  sample_i %>%
    write_csv(paste0("./data_output/samples_ordered/section1_",i,".csv"), col_names = F)
  section2 %>%
    write_csv(paste0("./data_output/samples_ordered/section2_",i,".csv"), col_names = F)
  
  sample_i_scrambled %>%
    write_csv(paste0("./data_output/samples_scrambled/section1_",i,".csv"), col_names = F)
  section2_scrambled %>%
    write_csv(paste0("./data_output/samples_scrambled/section2_",i,".csv"), col_names = F)
}

names(starred_data) <- col_names
write_csv(starred_data,"./data_output/main_section_full.csv", col_names = F)

starred_data %>%
  sample_n(nrow(.)) %>%
  write_csv("./data_output/section2.csv",col_names = F)
