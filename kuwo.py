import re

import os
import requests
import bs4


class Kuwo:
    search_url = 'http://sou.kuwo.cn/ws/NSearch?type=all&catalog=yueku2016&key={}'

    def __init__(self):
        self.songs = []

    def search_song(self, song_name):
        res = requests.get(self.search_url.format(song_name))
        res.raise_for_status()

        if '很抱歉，没有找到相关的结果' in res.text:
            return

        soup = bs4.BeautifulSoup(res.text)
        lists = soup.find_all('li', class_="clearfix")
        for li in lists:
            song_info = li.find('a')
            song_href = song_info.attrs.get('href')
            song_id = re.search('\d+', song_href).group()

            singer = li.find_all('a')[2]
            singer_title = singer.attrs.get('title')

            self.songs.append(Song(song_name, song_id, singer_title))
        return self.songs


class Song:
    player_url = 'http://player.kuwo.cn/webmusic/st/getNewMuiseByRid?rid=MUSIC_{}'

    def __init__(self, song_name, song_id, singer):
        self.song_name = song_name
        self.id = song_id
        self.singer = singer

    def download(self, save_path='./result'):
        res = requests.get(self.player_url.format(self.id))
        res.raise_for_status()
        data = res.text
        mp3path = re.search(r'<mp3path>(.*)</mp3path>', data).group(1)
        mp3dl = re.search(r'<mp3dl>(.*)</mp3dl>', data).group(1)
        download_url = 'http://' + mp3dl + '/resource/' + mp3path

        download_data = requests.get(download_url)
        download_data.raise_for_status()

        if not os.path.exists(save_path):
            os.mkdir(save_path)

        i = 1
        file_path = os.path.join(save_path, self.song_name)
        while os.path.exists(file_path):
            file_path = os.path.join(save_path, self.song_name + '({})'.format(i))
            i += 1

        with open(file_path, 'wb') as f:
            f.write(download_data.content)

        print('download [{}] success'.format(self.song_name))


if __name__ == '__main__':
    ku = Kuwo()
    ku.search_song('七里香')[0].download()