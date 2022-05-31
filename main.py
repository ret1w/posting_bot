from bs4 import BeautifulSoup as bs
from time import sleep
import requests
import telebot
import vk_api
import json


class BotNews:

    def __init__(self):
        self.path = 'settings.json'
        self.data = self.load_settings()
        self.bot = None

    def auth_bot(self):
        self.bot = telebot.TeleBot(self.data['token'], parse_mode=None)

    def load_settings(self):
        with open(self.path, 'r', encoding="UTF-8") as f:
            data = json.load(f)

        return data

    def save_settings(self):
        with open(self.path, "w", encoding="UTF-8") as f:
            json.dump(self.data, f, sort_keys=True, indent=4, ensure_ascii=False)

    def main(self):
        posts = self.parse_news()
        if posts:
            for post in posts:
                self.send_post_tg(post)
                sleep(1)
                if self.data['vk_token']:
                    self.send_post_vk(post)
                    sleep(1)

    def send_post_tg(self, post):
        self.auth_bot()
        txt = f'<a href="{post["link_news"]}">{post["title"]}</a>\n'
        self.bot.send_photo(self.data['channel_id'], post['link_photo'], caption=txt, parse_mode="HTML")

    def parse_news(self):
        url = ''
        response = requests.get(url=url)
        html = bs(response.content, 'html.parser')

        posts = []
        blocks = html.select('.front-page-masonry > li')
        last_news_link = None
        for i, block in enumerate(blocks):
            link_news = block.select(".image-link")[0]['href']
            # print(link_news)
            # print(self.data['last_news_link'])
            # print('---------------------')
            if link_news == self.data['last_news_link']:
                break

            if i == 0:
                last_news_link = link_news

            link_photo = block.select(".frame")[0]['style'].replace('background-image: url(', '').replace(')', '')
            title = block.select(".title")[0].text

            posts.append({
                'title': title,
                'link_news': link_news,
                'link_photo': link_photo
            })

        if last_news_link:
            self.data['last_news_link'] = last_news_link
            self.save_settings()

        return posts

    def send_post_vk(self, post):
        vk = vk_api.VkApi(token=self.data['vk_token'])

        txt = post['title'] + '\n'

        try:
            vk.method("wall.post",
                           {
                               "owner_id": self.data['vk_group_id'] * -1,
                               "message": txt,
                               "from_group": 1,
                               "attachments": post['link_news']
                           })
        except Exception as message:
            pass

        sleep(1)


if __name__ == '__main__':
    bot = BotNews()
    while True:
        try:
            bot.main()
            sleep(10)
        except Exception as message:
            bot = BotNews()