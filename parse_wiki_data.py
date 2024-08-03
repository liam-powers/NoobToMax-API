import requests
import json
import mwparserfromhell
import typing
import threading
import re

headers = {
    'user-agent': 'NoobToMax/0.1 (MacOS; Sonoma 14.5)    Contact: liampowers@u.northwestern.edu    Repo: https://github.com/liam-powers/NoobToMax-API'
}

class Quest:
    def __init__(self, title):
        self.title = title
        self.direct_prereqs = []

    def set_direct_prereqs(self) -> None:
        quest_URL = 'https://oldschool.runescape.wiki/api.php?action=query&prop=revisions&rvprop=content&titles=' + self.title + '&format=json&formatversion=2'
        response = requests.get(quest_URL, headers=headers)

        py_response = response.json()
        if (response.status_code != 200):
            return

        quest_page_wikicontent = py_response['query']['pages'][0]['revisions'][0]['content']
        wikicode = mwparserfromhell.parse(quest_page_wikicontent)

        templates = wikicode.filter_templates()
        quest_template = None

        for template in templates:
            if template.name.strip() == 'Quest details':
                quest_template = template

        direct_prereqs = []
        if quest_template:
            for param in quest_template.params:
                if param.name.strip() == 'requirements':
                    quest_text = str(param.value)
                    unclean_quests = quest_text.split('\n')

                    for unclean_quest in unclean_quests:
                        num_stars = unclean_quest.count('*')
                        clean_quest = clean_quest_text(unclean_quest)
                        if not clean_quest:
                            continue
                        if num_stars == 2:
                            direct_prereqs.append(clean_quest)

        self.direct_prereqs = direct_prereqs

class QuestTree:
    def __init__(self):
        self.all_quest_titles = []
        self.idx_to_quest = {}

    def set_all_quest_titles(self) -> None:
        all_quest_titles = []
        query_quests_url = 'https://oldschool.runescape.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Quests&cmlimit=500&format=json&formatversion=2'
        response = requests.get(query_quests_url, headers=headers)

        if response.status_code != 200:
            return

        py_response = response.json()
        response_text_content = py_response['query']['categorymembers']

        for quest_dict in response_text_content:
            quest_title = quest_dict['title']
            if not (quest_title.startswith('Quest') or quest_title.startswith('Category') or quest_title.startswith('User')):
                all_quest_titles.append(quest_dict['title'])

        self.all_quest_titles = all_quest_titles

    def set_all_quest_objs(self) -> None:
        idx_to_quest = { i: Quest(title=self.all_quest_titles[i]) for i in range(len(self.all_quest_titles)) }
        id = 0
        while id < len(idx_to_quest):
            threads = []
            for tid in range(id, min(id + 2, len(self.all_quest_titles))):
                threads.append(threading.Thread(target=idx_to_quest[tid].set_direct_prereqs))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            id += 2

        self.idx_to_quest = idx_to_quest

def clean_quest_text(uncleaned_quest: str):
    pattern = r'\[\[(.*?)\]\]'
    matches = re.findall(pattern, uncleaned_quest)
    if len(matches) < 1:    # wasn't even quest text in the first place
        return False
    return matches[0]

if __name__ == '__main__':
    qt = QuestTree()
    qt.set_all_quest_titles()
    qt.set_all_quest_objs()

    print(qt.idx_to_quest[0])
