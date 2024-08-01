import requests
import json
import mwparserfromhell
import typing
import threading
import re

headers = {
    'user-agent': 'NoobToMax/0.1 (MacOS; Sonoma 14.5)    Contact: liampowers@u.northwestern.edu    Repo: https://github.com/liam-powers/NoobToMax-API'
}

def get_all_quests() -> typing.List[str]:
    all_quests = []
    query_quests_url = 'https://oldschool.runescape.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Quests&cmlimit=500&format=json&formatversion=2'
    response = requests.get(query_quests_url, headers=headers)

    if response.status_code != 200:
        print('Status code not equal to 200! Uh oh!')
        return all_quests

    py_response = response.json()
    response_text_content = py_response['query']['categorymembers']

    for quest_dict in response_text_content:
        quest_title = quest_dict['title']
        if not (quest_title.startswith('Quest') or quest_title.startswith('Category') or quest_title.startswith('User')):
            all_quests.append(quest_dict['title'])

    return all_quests

def get_quest_prereqs(quest_name: str, tid: int, quest_to_prereqs: dict, lock: threading.Lock, all_quests: typing.List[str]) -> None:
    print(f'thread {tid} in get_all_quests')
    quest_URL = 'https://oldschool.runescape.wiki/api.php?action=query&prop=revisions&rvprop=content&titles=' + quest_name + '&format=json&formatversion=2'
    response = requests.get(quest_URL, headers=headers)

    py_response = response.json()
    if (response.status_code != 200):
        print('Status code not equal to 200! Uh oh!')
        print(response.text)
        print(response.status_code)
        return

    sample_quest_textcontent = py_response['query']['pages'][0]['revisions'][0]['content']
    wikicode = mwparserfromhell.parse(sample_quest_textcontent)

    templates = wikicode.filter_templates()
    template_names = []
    quest_template = None

    for template in templates:
        template_names.append(template.name)
        if template.name.strip() == 'Quest details':
            quest_template = template

    quest_prereqs = []
    quest_prereqs_textcontent = None
    if quest_template:
        for param in quest_template.params:
            if param.name.strip() == "requirements":
                quest_prereqs_textcontent = param.value
                quest_prereqs = [
                    str(quest.title)
                    for quest in param.value.filter_wikilinks()
                    if str(quest.title) in all_quests
                ]

    with lock:
        quest_to_prereqs[quest_name]["prereqs"] = quest_prereqs
        quest_to_prereqs[quest_name]["prereqs_textcontent"] = quest_prereqs_textcontent

def clean_quest_text(uncleaned_quest: str) -> str:
    pattern = r'\[\[(.*?)\]\]'

    matches = re.findall(pattern, uncleaned_quest)
    return matches[0]

def tier_quests(quest_text: str) -> dict:   # pass JUST the quest text (between completion of the following quests and the next single star)
    tiered_quests = {}

    unclean_quests = quest_text.split('\n')
    ancestors = []

    for unclean_quest in unclean_quests:
        num_stars = unclean_quest.count('*')
        clean_quest = clean_quest_text(unclean_quest)
        if num_stars == 2:
            ancestors = []
        elif num_stars <= len(ancestors):
            ancestors = ancestors[:num_stars - 2]

        curr_parent = tiered_quests
        for ancestor in ancestors:
            curr_parent = curr_parent[ancestor]
        curr_parent[clean_quest] = {}
        ancestors.append(clean_quest)

    return tiered_quests

# test for getting all quests names then getting their prereqs
if __name__ == "__main__":
    requirements_text = "** [[Pirate's Treasure]]\n** [[Rum Deal]]\n*** [[Zogre Flesh Eaters]]\n**** [[Big Chompy Bird Hunting]]\n**** [[Jungle Potion]]\n***** [[Druidic Ritual]]\n*** [[Priest in Peril]]"

    print(tier_quests(requirements_text))
    # all_quests = get_all_quests()
    # print('all quests: ', all_quests)

    # quest_to_prereqs = { quest: { "prereqs": [], "prereqs_textcontent": None } for quest in all_quests }

    # lock = threading.Lock()

    # id = 0
    # while id < 10: # id < len(all_quests):
    #     threads = []
    #     for tid in range(id, min(id + 3, len(all_quests))):
    #         threads.append(threading.Thread(target=get_quest_prereqs, args=(all_quests[tid], tid, quest_to_prereqs, lock, all_quests)))
    #     for thread in threads:
    #         thread.start()
    #     for thread in threads:
    #         thread.join()
    #     id += 3


    # for key, value in quest_to_prereqs.items():
    #     if value['prereqs_textcontent']:
    #         print(f'{key}: {value['prereqs_textcontent']}')
