def declension(num,one,two,three):
    if num >= 5 and num <= 20:
        text = three
    elif int(str(num)[-1]) == 0:
        text = three
    elif int(str(num)[-1]) == 1:
        text = one
    elif int(str(num)[-1]) >= 5:
        text = three
    elif int(str(num)[-1]) <= 4:
        text = two
    return text

def get_id(text):
    pass