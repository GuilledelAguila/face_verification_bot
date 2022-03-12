from datetime import datetime
import data as data
import image_process as image_process
from io import BytesIO
from PIL import Image
import numpy as np
import os

def sample_responses(input_text, chat_info):
    # Get name of user
    chat_name = chat_info['first_name']
    # message from user (we dont really care about it)
    # user_message = str(input_text).lower()

    # load previous data from chat
    chat_data = data.load_data(chat_info)
    
    try:
        user_input = int(input_text)
    except ValueError:
        user_input = str(input_text).lower()

    # Check if we are waiiting for confirmation from previous verification
    if chat_data['awaiting_confirmation'] == True or chat_data['awaiting_difficulty'] == True:
        # Check if the user correctly indicated if the result was correct
        if chat_data['awaiting_confirmation'] == True and user_input in ('y','n'):
            # Update user status data
            chat_data['awaiting_confirmation'] = False
            chat_data['was_same_person'] =  1 if user_input == 'y' else 0
            data.save_data(chat_info, chat_data)
            
            return "Thanks! Now I need to know the difficulty of the verification. Please reply:\n\n\
1 - [EASY] If the pictures where high quality, aligned with the camera, no glasses or masks and a normal face expression\n\n\
2 - [MEDIUM] If the person wasn't looking into the camera, face was partially covered or the face expression in the pictures was very different\n\n\
3 - [DIFFICULT] If relatives like siblings were involved in the verification or there was a big age difference between the two pictures"
        elif chat_data['awaiting_difficulty'] == True and chat_data['awaiting_confirmation'] == False and user_input in (1,2,3):
            chat_data['awaiting_difficulty'] = False
            data.save_data(chat_info, chat_data)
            data.log2_result(chat_info, chat_data, user_input)
            return "Thanks for your feedback! you can now keep comparing pictures! 📸 📸"
        elif chat_data['awaiting_confirmation'] == True and user_input not in ('y','n'):
            return 'Please 🙏 let me know if the people in the last two pictures where the same person\n\nReply "Y" if yes or "N" if no'
        elif chat_data['awaiting_difficulty'] == True and chat_data['awaiting_confirmation'] == False and user_input not in (1,2,3):
            return 'Please 🙏 let me know the difficulty of the last verification\n\nReply a number from 1 to 3'
        else:
            return 'Uh'
    # If not waiting for result confirmation --> continue
    else:
        # user hasnt sent any pictures
        if chat_data['num_photos'] == 0:
            return f'Hi {chat_name} 👋, I need two pictures to verify your identity'
        # user has only sent 1 pic
        elif chat_data['num_photos'] == 1:
            return f'Hi {chat_name} 👋, I need one more picture'
        # this should never happen    
        else:
            data.delete_data(chat_info)
            return 'Error 🚨... Resolving... Please, start again'
        

def photo_responses(input_photo, chat_info):
    # load previous data from chat
    chat_data = data.load_data(chat_info)

    if chat_data['awaiting_confirmation'] == True or chat_data['awaiting_difficulty'] == True:
        if chat_data['awaiting_confirmation'] == True:
            return 'Please 🙏 let me know if the verification result was correct before we continue.\n\nReply "Y" if yes or "N" if no'
        else:
            return 'Please 🙏 let me know the difficulty of the last verification\n\nReply a number from 1 to 3'
    else:
        # Get name of user
        chat_name = chat_info['first_name']

        # Get byte stream and open as Image
        stream = BytesIO(input_photo.download_as_bytearray())
        image = Image.open(stream).convert("RGB")
        image.thumbnail((500,500))
        # image.show()
        stream.close()
        # image.show()

        # user hasnt sent any pictures
        if chat_data['num_photos'] == 0:
            embeddings = image_process.process(image)
            if len(embeddings) <= 1 or not embeddings.any():
                print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: Bad Image - ACTION: Process')
                if not embeddings.any() or embeddings[0] == -3:
                    return f'Sorry {chat_name} the picture is not suitable for verification, try with a different pic'
                elif embeddings[0] == -1:
                    return f'Please send pictures with only ONE face in them'
                elif embeddings[0] == -4:
                    return f'Sorry only one side of the face can be seen, look into the camera'
                else: 
                    return f'Sorry {chat_name}, no face was found ❌🔎 try with a different pic'
            else:
                chat_data['arcface_emb_1'] = embeddings[0]
                chat_data['facenet_emb_1'] = embeddings[1]
                chat_data['num_photos'] += 1
                data.save_data(chat_info, chat_data)

                print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: New Image - ACTION: Process')

                return f'Perfect, I need one more picture'

                # face = Image.fromarray(un_norm_face.astype(np.uint8))
                # face.show()


        # user has only sent 1 pic
        elif chat_data['num_photos'] == 1:
            embeddings = image_process.process(image)
            if len(embeddings) <= 1 or not embeddings.any():
                print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: Bad Image - ACTION: Process')
                if not embeddings.any() or embeddings[0] == -3:
                    return f'Sorry {chat_name} the picture is not suitable for verification, try with a different pic'
                elif embeddings[0] == -1:
                    return f'Please send pictures with only ONE face in them'
                elif embeddings[0] == -4:
                    return f'Sorry only one side of the face can be seen, look into the camera'
                else: 
                    return f'Sorry {chat_name}, no face was found ❌🔎 try with a different pic'
            else:
                chat_data['arcface_emb_2'] = embeddings[0]
                chat_data['facenet_emb_2'] = embeddings[1]
                chat_data['num_photos'] += 1
                data.save_data(chat_info, chat_data)
                print(f'LOG - {chat_data["last_verification"]} - CHAT: {chat_info["id"]} - USER NAME: {chat_data["first_name"]} - TYPE: New Image - ACTION: Process')

                return f"Okay, let's start verifying... 🤔"
        else:
            data.delete_data(chat_info)
            return 'Error 🚨... Resolving... Please, start again'            