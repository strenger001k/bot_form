def add(dict, messege_text):
    dict.append(messege_text)


def replace(dict, chat_id, messege_text, index):
    dict[chat_id][index] = (messege_text)
