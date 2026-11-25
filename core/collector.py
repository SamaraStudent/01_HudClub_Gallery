import json
from core.parser import get_message_hashtags

def collect_user_data(json_files, target_hashtags_set, new_review_map, new_reviews):
    user_photos = {}
    potential_names = {}
    user_target_intervals = {}
    
    
    # 1. Собираем интервалы
    for jfile in json_files:
        try:
            with open(jfile, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [warn] Не удалось прочитать {jfile}: {e}")
            continue
        for msg in data.get("messages", []):
            if msg.get("type") != "message":
                continue
            f_id = str(msg.get("from_id", ""))
            if not f_id:
                continue
            msg_tags = get_message_hashtags(msg)
            found_tags = [t for t in msg_tags if t in target_hashtags_set]
            if found_tags:
                user_target_intervals.setdefault(f_id, []).append({
                    "time": int(msg.get("date_unixtime", 0)),
                    "tag": found_tags[0],
                })

   
    # 2. Собираем фото
    skipped_no_file = 0
    for jfile in json_files:
        chat_dir = jfile.parent
        try:
            with open(jfile, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"  [warn] Не удалось прочитать {jfile}: {e}")
            continue
        for msg in data.get("messages", []):
            if msg.get("type") != "message":
                continue
            f_id = str(msg.get("from_id", ""))
            if not f_id:
                continue

            potential_names[f_id] = msg.get("from", f"User_{f_id}")
            rel_path = msg.get("photo") or msg.get("file")
            if not rel_path or not rel_path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue

            abs_path = chat_dir / rel_path
            if not abs_path.exists():
                skipped_no_file += 1
                continue

            msg_tags = get_message_hashtags(msg)
            current_time = int(msg.get("date_unixtime", 0))
            matched_tag = None

            found_tags = [t for t in msg_tags if t in target_hashtags_set]
            if found_tags:
                matched_tag = found_tags[0]
            elif f_id in user_target_intervals:
                has_other_hashtag = any(t not in target_hashtags_set for t in msg_tags)
                if not has_other_hashtag:
                    best_tag = None
                    best_delta = 121
                    for interval in user_target_intervals[f_id]:
                        delta = abs(current_time - interval["time"])
                        if delta <= 120 and delta < best_delta:
                            best_delta = delta
                            best_tag = interval["tag"]
                    if best_tag is not None:
                        matched_tag = best_tag

            if matched_tag:
                new_idx = None
                new_color = None
                if matched_tag in new_review_map:
                    thr, color = new_review_map[matched_tag]
                    if current_time >= thr:
                        new_idx = next(
                            (i for i, r in enumerate(new_reviews) if r["tag"] == matched_tag),
                            None
                        )
                        new_color = color

                user_photos.setdefault(f_id, []).append({
                    "path": abs_path,
                    "tag": matched_tag,
                    "new_idx": new_idx,
                    "new_color": new_color,
                    "time": current_time,
                })



    for fid in user_photos:
        user_photos[fid].sort(key=lambda x: x["time"])
        
    return user_photos, potential_names