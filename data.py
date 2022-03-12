import os
import pickle
import numpy as np
import tensorflow as tf
from datetime import datetime

data_dir = "./data"
model = tf.keras.models.load_model('./models/gan_lfw_model',  compile=True) 

def get_file(chat_id):
    chat_file_name = ''
    for _, _, files in os.walk(data_dir):
        for file in files:
            if chat_id in file:
                chat_file_name = file
    return str(chat_file_name)

def load_data(chat_info):
    chat_id = str(chat_info['id'])
    chat_file_name = get_file(chat_id)

    # This chat has no previous data
    if not chat_file_name:
        # Generate initial dictionary
        data = {
        'first_name': chat_info['first_name']
        , 'awaiting_confirmation': False
        , 'awaiting_difficulty': False
        , 'num_photos': 0
        , 'total_verifications': 0
        , 'last_result': 0
        , 'was_same_person': 0
        , 'last_verification': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        , 'arcface_emb_1': np.array([])
        , 'arcface_emb_2': np.array([])
        , 'facenet_emb_1': np.array([])
        , 'facenet_emb_2': np.array([])
        , 'arcface_sq_diff' : np.array([])
        , 'facenet_sq_diff' : np.array([])
        }
        # save initial dictionary
        with open(f"{data_dir}/{chat_info['first_name']}_{str(chat_id)}.p", 'wb') as fp:
            pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)
        print(f'LOG - {data["last_verification"]} - CHAT: {chat_id} - USER NAME: {data["first_name"]} - TYPE: New User - ACTION: Create Profile')
        return data
    # We have previous data about this chat
    else:
        with open(f'{data_dir}/{chat_file_name}', 'rb') as fp:
            data = pickle.load(fp)
        # print(f'LOG - {data["last_verification"]} - TYPE: New Message - CHAT: {chat_id} - USER NAME: {data["first_name"]} - ACTION: Load Profile')

        return data

def save_data(chat_info, chat_data):
    chat_id = str(chat_info['id'])
    chat_file_name = get_file(chat_id)

    with open(f"{data_dir}/{chat_file_name}", 'wb') as fp:
        pickle.dump(chat_data, fp, protocol=pickle.HIGHEST_PROTOCOL)

def delete_data(chat_info):
    chat_id = str(chat_info['id'])
    chat_file_name = get_file(chat_id)
    data_path = f'{data_dir}/{chat_file_name}'
    if os.path.exists(data_path):
        print(f'LOG - TYPE: Chat Data Load Error - CHAT: {chat_info["id"]} - ACTION: Removing Data')
        os.remove(data_path)

def verify_data(chat_info):
    chat_data = load_data(chat_info)
    # Get user emebddings
    arcface_emb_1, arcface_emb_2 = chat_data['arcface_emb_1'], chat_data['arcface_emb_2']
    facenet_emb_1, facenet_emb_2 = chat_data['facenet_emb_1'], chat_data['facenet_emb_2']

    # print("Embeddings for verification: ", arcface_emb_1.shape, arcface_emb_2.shape, facenet_emb_1.shape, facenet_emb_2.shape)
    #Calculate squared diff
    arcface_sq_diff = np.array([np.square(np.subtract(arcface_emb_1, arcface_emb_2))])
    facenet_sq_diff = np.array([np.square(np.subtract(facenet_emb_1, facenet_emb_2))])

    # load model

    # make prediction
    preds = model.predict([arcface_sq_diff, facenet_sq_diff])
    #format result to 2 decimal points
    result = '{:.2f}'.format(preds[0][0]*100)

    # Update user data
    chat_data['last_result'] = result
    chat_data['total_verifications'] += 1
    chat_data['num_photos'] = 0
    chat_data['last_verification'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    chat_data['awaiting_confirmation'] = True
    chat_data['awaiting_difficulty'] = True
    chat_data['arcface_sq_diff'] = arcface_sq_diff
    chat_data['facenet_sq_diff'] = facenet_sq_diff
    # save updated user data
    save_data(chat_info, chat_data)
    # log verification result
    print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: Verification Result - RESULT: {result} - TOTAL VERIFICATIONS: {chat_data["total_verifications"]}')
    
    return result

def log_result(chat_info, chat_data, user_input):
    result_is_correct = 1 if user_input == 'y' else 0

    new_log = {'chat_id': chat_info['id']
    , 'name':  chat_info['first_name']
    , 'datetime': chat_data['last_verification']
    , 'arcface_sq_diff': chat_data['arcface_sq_diff']
    , 'facenet_sq_diff': chat_data['facenet_sq_diff']
    , 'sistem_result': chat_data['last_result']
    , 'result_is_correct': result_is_correct
    }

    with open(f"./results_log/result_log.p", 'a+b') as fp:
        pickle.dump(new_log,fp)
    print(f'LOG - {chat_data["last_verification"]} - TYPE: User Feedback 1 - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - RESULT IS CORRECT: {user_input}')

def log2_result(chat_info, chat_data, user_input):
    user_difficulty = int(user_input)
    is_same_person = chat_data['was_same_person']

    new_log = {'chat_id': chat_info['id']
    , 'name':  chat_info['first_name']
    , 'datetime': chat_data['last_verification']
    , 'arcface_sq_diff': chat_data['arcface_sq_diff']
    , 'facenet_sq_diff': chat_data['facenet_sq_diff']
    , 'sistem_result': chat_data['last_result']
    , 'is_same_person': is_same_person
    , 'user_difficulty': user_difficulty
    }

    with open(f"./results_log/result_log_v2.p", 'a+b') as fp:
        pickle.dump(new_log,fp)
    is_same_person = chat_data['was_same_person']
    print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: Feedback - IS SAME PERSON: {is_same_person} - DIFFICULTY: {user_difficulty}/3')