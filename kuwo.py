import re

import os
import requests
import bs4
import sys


class Kuwo:
    search_url = 'http://sou.kuwo.cn/ws/NSearch?type=all&catalog=yueku2016&key={}'

    def __init__(self):
        self.songs = []

    def search_song(self, song_name):
        res = requests.get(self.search_url.format(song_name))
        res.raise_for_status()

        if '很抱歉，没有找到相关的结果' in res.text:
            raise ValueError('have no such song [{}]'.format(song_name))

        soup = bs4.BeautifulSoup(res.text, 'lxml')
        lists = soup.find_all('li', class_="clearfix")
        for li in lists:
            song_info = li.find('a')
            song_href = song_info.attrs.get('href')
            song_title = song_info.attrs.get('title')
            song_id = re.search('\d+', song_href).group()

            album = li.find_all('a')[1]
            album_name = album.attrs.get('title')

            singer = li.find_all('a')[2]
            singer_title = singer.attrs.get('title')

            self.songs.append(Song(song_title, song_id, album_name, singer_title))
        return self.songs

    def show_songs(self):
        song_list = [map(len, song.get_list()) for song in self.songs]
        size = list(map(max, zip(*song_list)))
        formatter = '   '.join(['{%s:<%s}' % item for item in enumerate(size)])
        print('\n'.join([str(index+1)+'. '+formatter.format(*song.get_list()) for index, song in enumerate(self.songs)]))


class Song:
    player_url = 'http://player.kuwo.cn/webmusic/st/getNewMuiseByRid?rid=MUSIC_{}'

    def __init__(self, song_name, song_id, album_name, singer):
        self.song_name = song_name
        self.id = song_id
        self.singer = singer
        self.album_name = album_name

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
        file_path = os.path.join(save_path, self.song_name + '.mp3')
        while os.path.exists(file_path):
            file_path = os.path.join(save_path, self.song_name + '({})'.format(i) + '.mp3')
            i += 1

        with open(file_path, 'wb') as f:
            f.write(download_data.content)

        print('download [{}] success'.format(self.song_name))

    def __repr__(self):
        return '{} {} {}'.format(self.song_name, self.album_name, self.singer)

    def __str__(self):
        return self.__repr__()

    def get_list(self):
        return [self.song_name, self.album_name, self.singer]


if __name__ == '__main__':

    while True:
        ku = Kuwo()
        song = input('what song do you want to download: \n')
        try:
            ku.search_song(song)
        except ValueError:
            print('搜索不到歌曲')
            continue
        ku.show_songs()
        num = input('which one do you want to download: (1~10)\n')

        ku.songs[int(num)-1].download()