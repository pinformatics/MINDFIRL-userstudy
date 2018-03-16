pacman::p_load(tidyverse, rebus)

raw_user_data <- read_csv("raw_data.csv")
actual_questions_data <- read_csv("main_section_full.csv")

raw_user_data %>% pull(type) %>% unique()

questions_info <- 
  actual_questions_data %>% 
  select(question = `Group ID`, 
         actual_answer = Same,
         question_type = `Record ID`) %>% 
  mutate_all(as.integer)

# user_kapr <- 
  raw_user_data %>% 
  filter(type %in% c("open_cell", "kapr")) %>% 
  group_by(uid) %>% 
  arrange(timestamp) %>% 
  spread(type, value) %>% 
  mutate(timedelta = lead(timestamp) - (timestamp),
         group_kapr = if_else((timedelta < 50), 1, 0) %>% if_else(is.na(.), 0, .) %>% cumsum()) %>% 
  group_by(uid, group_kapr) %>% 
  separate(open_cell, into = c("question", "cell"), sep = "-", convert = T) %>% 
  mutate(open_cell = str_c(question, cell)) %>% 
  summarise(kapr = last(kapr[!(kapr %>% is.na())]),
            cell = first(open_cell) %>% str_extract(one_or_more(DIGIT)),
            timestamp = first(timestamp),
            timedelta = first(timedelta)) %>% 
  ungroup() %>% 
  mutate(kapr = lead(kapr) - kapr)  
  
user_questions_data <- 
  raw_user_data %>% 
  filter(type == "final_answer") %>% 
  separate(value, into = c("question", "choice"), sep = "a", convert = T) %>% 
  mutate(question = question %>% str_replace("p", "") %>% as.integer(),
         confidence = if_else(choice > 3, choice - 3, abs(choice - 4)),
         user_answer = if_else(choice > 3, 1, 0)) %>% 
  left_join(questions_info, by = "question") %>% 
  mutate(grade = ifelse(user_answer == actual_answer, 1, 0),
         sample = as.integer(uid)%%10) %>% 
  select(-type, -timestamp, -extra) %>% 
  mutate_all(as.integer)

attention_test = c(1,7,13,19,25,31)

user_questions_data %>% 
  group_by(uid, sample) %>% 
  summarise(grade36 = sum(grade),
            grade30 = sum(grade[!(question_type %in% attention_test)]),
            percent_attention = mean(grade[question_type %in% attention_test]),
            percent_attention = ifelse(is.nan(percent_attention), 1, 0),
            percent36 = mean(grade)*100,
            percent30 = grade30*100/30,
            mean_confidence = mean(confidence),
            mean_confidence_right = mean(confidence[grade == 1]),
            mean_confidence_wrong = mean(confidence[grade == 0]))

