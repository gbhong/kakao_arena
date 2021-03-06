import json
import pandas as pd
import re
import khaiii as kh


def load_genre_list():
    genres = open('./all_data/melon_give_us/genre_gn_all.json', encoding='utf-8')
    gen = json.load(genres)
    gen_names = []
    for name in gen.items():
        if name[0][-2:] == '00':
            gen_names.append(name[1])

    gen_names = set(gen_names)

    genre = []
    for i in gen_names:
        if '/' in i:
            _ = i.replace('/', ' ').split()

            for j in _:
                genre.append(j)
        else:
            genre.append(i)

    return genre


def finding_top_artist(length):
    song_meta = open('./all_data/melon_give_us/song_meta.json', encoding='utf-8')
    s_meta = json.load(song_meta)
    artist_name_dict = {}

    for song in s_meta:
        for name in song["artist_name_basket"]:
            if name in artist_name_dict.keys():
                artist_name_dict[name] += 1
            else:
                artist_name_dict[name] = 1

    artist_name_ls = sorted(artist_name_dict.items(), reverse=True, key=lambda item: item[1])
    artist = []
    for t in artist_name_ls:
        if len(t[0]) == 1:
            continue
        else:
            if re.match('^[가-힣0-9]', t[0]) != None:
                artist.append(t[0])
            if len(artist) == length:
                break
    tmp = []
    for i in artist:
        if '(' in i:
            ls = i.split('(')

            for j in ls:
                tmp.append(j.strip().rstrip(')'))
        else:
            tmp.append(i)
    return tmp


def name_tokenize(sentence):
    api = kh.KhaiiiApi()
    api.open()
    x = re.sub('[-\.\$\+>#\}\{\*<&@%;\\\)\(="?!\[\]~\^/:,_\|]+', '.',
               str(sentence).replace("'", "")).replace('.', ' ')  # 특수 기호 제거

    res = []
    try:
        for word in api.analyze(x):
            if re.match('\d+', word.lex) != None:
                tmp = ''
                for m in word.morphs:  # '2000년대','2000년대의'에서 '2000년대'만 뽑아내는 코드
                    if m.tag in ['NNG', 'NNP', 'NNB', 'SN']:
                        tmp += m.lex
                res.append(tmp)
            else:
                a = len(res)
                for i in genre:
                    if i in word.lex:
                        res.append(i)  # '발라드', '메탈'처럼 장르명이 제목에 있으면 바로 리스트에 추가

                for j in artist:
                    if j in word.lex and len(j) > 1:  # 두 글자 이상의 아티스트 이름이 단어에 들어있으면 리스트에 추가
                        res.append(j)
                b = len(res)
                if a == b:
                    for m in word.morphs:
                        if m.tag in ['NNG', 'NNP', 'NNB', 'SN', 'SL']:  # 명사와 숫자, 외국어만 받습니다
                            res.append(m.lex)
    except:
        pass

    return ' '.join(res)


def plyst_title_tokenizing(length):
    if length == 300:
        train = pd.read_json('./all_data/melon_give_us/train.json', encoding='utf-8')
        val = pd.read_json('./all_data/melon_give_us/val.json', encoding='utf-8')

        train = train.drop(columns=['tags', 'songs', 'like_cnt', 'updt_date'])
        train['name_normalized'] = train.plylst_title.apply(name_tokenize)

        val = val.drop(columns=['tags', 'songs', 'like_cnt', 'updt_date'])
        val['name_normalized'] = val.plylst_title.apply(name_tokenize)

        train.to_csv('./all_data/train/train_names.csv', index=False)
        val.to_csv('./all_data/val/val_names.csv', index=False)

    else:
        test = pd.read_json('./all_data/melon_give_us/test.json', encoding='utf-8')
        test = test.drop(columns=['tags', 'songs', 'like_cnt', 'updt_date'])

        test['name_normalized'] = test.plylst_title.apply(name_tokenize)
        test.to_csv('./all_data/test/test_names.csv', index=False)


def tokenized_title_csv(length):
    if length == 300:
        tr = pd.read_csv('./all_data/train/train_names.csv')
        vl = pd.read_csv('./all_data/val/val_names.csv')

        tr.name_normalized = tr.name_normalized.astype('str').apply(lambda x: x.split())
        vl.name_normalized = vl.name_normalized.astype('str').apply(lambda x: x.split())

        rows = []

        df_train = tr.apply(lambda row: [rows.append([row.id, name]) for name in row.name_normalized if name != ''],
                            axis=1)
        pd.DataFrame(rows, columns=['pid', 'name']).to_csv('./all_data/train/train_playlists_name.csv', index=False)

        rows2 = []
        df_val = vl.apply(lambda row: [rows2.append([row.id, name]) for name in row.name_normalized if name != ''],
                          axis=1)
        pd.DataFrame(rows2, columns=['pid', 'name']).to_csv('./all_data/val/val_playlists_name.csv', index=False)

    else:
        ts = pd.read_csv('./all_data/test/test_names.csv')
        ts.name_normalized = ts.name_normalized.astype('str').apply(lambda x: x.split())

        rows = []
        df_test = ts.apply(lambda row: [rows.append([row.id, name]) for name in row.name_normalized if name != ''],
                           axis=1)
        pd.DataFrame(rows, columns=['pid', 'name']).to_csv('./all_data/test/test_playlists_name.csv', index=False)

# if __name__ == '__main__':
genre = load_genre_list()

##### Set1 - for making csv relatedt to train / validation'
artist = finding_top_artist(300)
plyst_title_tokenizing(300)
tokenized_title_csv(300)

##### Set2 - for making csv relatedt to test'
artist = finding_top_artist(10000)
plyst_title_tokenizing(10000)
tokenized_title_csv(10000)