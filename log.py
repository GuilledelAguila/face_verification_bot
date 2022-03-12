import os
import pickle
import numpy as np
from datetime import datetime

data_dir = "./results_log"
data = []

with open(f"{data_dir}/result_log_v2.p", 'rb') as fp:
    try:
        while True:
            data.append(pickle.load(fp))
    except EOFError:
        pass 
# 1583062225
final_data = []

for i in data:
    if i['chat_id'] not in [1]:
        final_data.append(i)
    # print(f"Date: {i['datetime']} - Chat ID: {i['chat_id']} - Name: {i['name']}\t\t\t-\tSystem result: {i['sistem_result']} - Result is correct: {i['result_is_correct']}", )
        print("Date: {0:<25}- Chat ID: {1: <15} - User: {2:<20}- System result: {3: <10}- Is same person: {4: <10}- Difficulty: {5: <10}"
        .format(i['datetime'], i['chat_id'], str(i['name']), i['sistem_result'], i['is_same_person'], int(i['user_difficulty'])))



# for threshold in range(50, 51, 5):
#     corrects = 0
#     false_pos = 0
#     false_neg = 0
#     true_pos = 0
#     true_neg = 0
#     true_pos_r = 0
#     true_neg_r = 0
#     false_pos_r = 0
#     false_neg_r = 0
#     print(f'-------------------- THRESHOLD AT: {threshold} ----------------------')
#     for log in final_data:
#         if int(log['result_is_correct']) == 0 and float(log['sistem_result']) >= threshold:
#             false_pos += 1
#             false_pos_r += float(log['sistem_result'])
#         elif int(log['result_is_correct']) == 0 and float(log['sistem_result']) < threshold:
#             false_neg += 1
#             false_neg_r += float(log['sistem_result'])
#         elif int(log['result_is_correct']) == 1 and float(log['sistem_result']) >= threshold:
#             true_pos += 1
#             corrects += 1
#             true_pos_r += float(log['sistem_result'])
#         else:
#             corrects += 1
#             true_neg += 1 
#             true_neg_r += float(log['sistem_result'])


#     total_logs = len(final_data)
#     print('STATs - Total Logs: {:.2f} - Accuracy: {:.2f} - True Positives: {:.2f} - True Negatives {:.2f}- False Negatives: {:.2f} - False Positives {:.2f}'
#         .format(total_logs, (corrects/total_logs)*100,(true_pos/total_logs)*100, (true_neg/total_logs)*100, (false_neg/total_logs)*100, (false_pos/total_logs)*100))

#     print('Average Results - True Positives: {:.2f} - True Negatives {:.2f}- False Negatives: {:.2f} - False Positives {:.2f}'
#         .format(true_pos_r/true_pos, true_neg_r/true_neg, false_neg_r/ false_neg, false_pos_r/false_pos))

# new_log = {'chat_id': 0
# , 'datetime': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
# , 'arcface_sq_diff': np.array([])
# , 'facenet_sq_diff': np.array([])
# , 'sistem_result': 0
# , 'true_result': 1
# }

# f = open(f"{data_dir}/result_log.p", 'wb')
# f.close()

# with open(f"{data_dir}/result_log.p", 'a+b') as fp:
#     pickle.dump(new_log,fp)

# if os.path.exists('./data/Ralf_1583062225.p'):
#     print('removing')
    # os.remove(chat_file_name)