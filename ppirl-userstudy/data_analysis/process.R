library(tidyverse)

raw_user_data <- read_csv("raw_data.csv")
actual_question_data <- read_csv("main_section_full.csv", col_names = F)

raw_user_data %>% pull(type) %>% unique()


raw_user_data %>% 
  filter(type == "answer") %>% 
  separate(value, into = c("question", "choice"), sep = "a", convert = T) %>% 
  mutate(question = question %>% str_replace("p", "") %>% as.integer(),
         confidence = if_else(choice > 3, choice - 3, abs(choice - 4)),
         user_answer = if_else(choice > 3, 1, 0)) %>% 
  
  # group_by(uid) %>% 
  
