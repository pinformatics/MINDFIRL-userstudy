import data_model as dm
from global_data import r, DATASET, DATASET2, DATA_SECTION1, DATA_SECTION2, DATA_SECTION3, DATA_SECTION4, DATA_SECTION5, DATA_SECTION6, DATA_SECTION7, DATA_SECTION8, DATA_SECTION9, DATA_SECTION10


def get_main_section_data(uid, section):
    sample = int(uid)%10
    if sample == 0:
        sample = 10
    sample -= 1

    if section == 1:
        return DATA_SECTION1[sample]
    elif section == 2:
        return DATA_SECTION2[sample]
    elif section == 3:
        return DATA_SECTION3[sample]
    elif section == 4:
        return DATA_SECTION4[sample]    
    elif section == 5:
        return DATA_SECTION5[sample]
    elif section == 6:
        return DATA_SECTION6[sample]
    elif section == 7:
        return DATA_SECTION7[sample]    
    elif section == 8:
        return DATA_SECTION8[sample]
    elif section == 9:
        return DATA_SECTION9[sample]
    elif section == 10:
        return DATA_SECTION10[sample]


out = list()
out.append('uid,section,moderate,minimum')
for uid in range(10):
    for section in range(1, 10):
        working_data = get_main_section_data(uid, section)
        kapr_limit_moderate = dm.get_kaprlimit(DATASET, working_data, 'moderate')
        kapr_limit_minimum = dm.get_kaprlimit(DATASET, working_data, 'minimum')
        out.append('%d,%d,%f,%f' % (uid, section, kapr_limit_moderate, kapr_limit_minimum))

with open('kapr_limit.csv', 'w+') as fout:
    for line in out:
        fout.write(line+'\n')


