if inPuTMsG.strip().startswith('/bundle'):
    parts = inPuTMsG.strip().split()

    if len(parts) != 2:
        msg = (
            "[B][C][ff0000]Sai cú pháp!\n\n"
            "[ffffff]Ví dụ:\n"
            "[00ff00]/bundle ob52"
        )
        P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
        continue

    item_name = parts[1].lower()

    if item_name not in BUNDLE_ITEMS:
        msg = (
            "[B][C][ff0000]Không tìm thấy bundle!\n\n"
            "[ffffff]Danh sách có sẵn:\n"
            "[00ff00]" + ", ".join(BUNDLE_ITEMS.keys())
        )
        P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
        continue

    bundle_id = BUNDLE_ITEMS[item_name]

    start_msg = (
        f"[B][C][00ff00]『 ACTIVE 』\n"
        f"[ffffff]Đang gửi bundle: [00ffb3]{item_name}\n"
        f"[ffffff]ID: [00ffb3]{bundle_id}"
    )
    P = await SEndMsG(response.Data.chat_type, start_msg, uid, chat_id, key, iv)
    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

    try:
        B = await bundle_packet(bundle_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', B)

        done_msg = (
            "[B][C][00ff00]Thành công!\n"
            f"[ffffff]Đã gửi bundle [00ffb3]{item_name}"
        )
        P = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

    except Exception as e:
        err = f"[B][C][ff0000]Lỗi gửi bundle: {e}"
        P = await SEndMsG(response.Data.chat_type, err, uid, chat_id, key, iv)
        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)