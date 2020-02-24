def sticker_send():
    sticker_ids = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 21, 100, 101, 102, 103, 106, 107, 110, 114, 116, 117, 119, 120, 122, 124, 125, 130, 134, 136, 137, 138, 139, 402, 20, 22, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 156, 157, 158, 159, 160, 151, 164, 166, 167, 171, 172, 176, 179, 501, 504, 505, 506, 508, 509, 511, 512, 513, 514, 516]    
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print("index_id = ",index_id)
    if index_id < 34:
        sticker_message = StickerSendMessage(
            package_id='1',
            sticker_id=sticker_id
            )
    else:
        sticker_message = StickerSendMessage(
            package_id='2',
            sticker_id=sticker_id
            )