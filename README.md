![OSRS Banner](https://upload.wikimedia.org/wikipedia/en/a/a7/Old_School_Runescape_Logo.png)

# Noob To Max API

Python Flask back-end acting as an HTTP server to receive API requests for Noob to Max.

- Noob to Max is a project serving the Old School RuneScape playerbase by providing a website with a simple user interface to create aesthetic and easily shareable goal graphs.
- This back-end implements an adjacency list implementation of unweighted directed graphs. Goals come in the form of quests, items, and levels, and often come with many chained prerequisites, and there are many connections between them (not sparse), so an adjacency list makes the most sense.
- If you're an OSRS Wiki mod and you're reading this, feel free to reach out to me at liampowers@u.northwestern.edu. I'm happy to chat about rate limiting or any gripes about my use of MediaWiki API for your site. Since the project is in early development right now, expect requests to become more consistent but lesser in volume per in the coming weeks.

Thanks for reading!

Special thanks to [earwig](https://github.com/earwig) and many other contributors for the excellent [MediaWiki Parser from Hell package](https://github.com/earwig/mwparserfromhell).
