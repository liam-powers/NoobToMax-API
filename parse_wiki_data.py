import requests
import json
import mwparserfromhell
import typing
import threading

headers = {
    'user-agent': 'NoobToMax/0.1 (MacOS; Sonoma 14.5)    Contact: liampowers@u.northwestern.edu    Repo: https://github.com/liam-powers/NoobToMax-API'
}

def get_all_quests() -> typing.List[str]:
    all_quests = []
    query_quests_url = 'https://oldschool.runescape.wiki/api.php?action=query&list=categorymembers&cmtitle=Category:Quests&cmlimit=500&format=json&formatversion=2'
    response = requests.get(query_quests_url, headers=headers)

    if response.status_code != 200:
        print('Status code not equal to 200! Uh oh!')

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
    if quest_template:
        for param in quest_template.params:
            if param.name.strip() == "requirements":
                quest_prereqs = [
                    str(quest.title)
                    for quest in param.value.filter_wikilinks()
                    if str(quest.title) in all_quests
                ]

    with lock:
        quest_to_prereqs[quest_name] = quest_prereqs

if __name__ == "__main__":
    all_quests = get_all_quests()
    print('all quests: ', all_quests)

    quest_to_prereqs = { quest: [] for quest in all_quests }

    lock = threading.Lock()

    id = 0
    while id < len(all_quests):
        threads = []
        for tid in range(id, min(id + 5, len(all_quests))):
            threads.append(threading.Thread(target=get_quest_prereqs, args=(all_quests[tid], tid, quest_to_prereqs, lock, all_quests)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        id += 5

    print("quest data: ")
    for key, value in quest_to_prereqs.items():
        print(key, ":", value)
