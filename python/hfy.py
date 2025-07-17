import praw
import sys
import requests
import re
import copy

from lxml import etree

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text

REDDIT_CLIENT_ID='CLIENT_ID_HERE'
REDDIT_CLIENT_SECRET='SECRET_HERE'
REDDIT_CLIENT_UA='linux:hfy_ebook_creator:v0.0.1 (by /u/Nv1diot)'
REDDIT = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_CLIENT_UA)


class Chapter(object):
    author = None
    series = None
    title = None
    url = None

    def __repr__(self):
        return "Chapter(author='%s', series='%s', title='%s', url='%s')" % (self.author, self.series, self.title, self.url)


def get_hfy_etree(url):
    wiki_ref = url.split("wiki/")[1].rstrip().rstrip("/")
    print(wiki_ref)
    hfy_all_html = REDDIT.subreddit('hfy').wiki[wiki_ref].content_html
    hfy_all_html = hfy_all_html.replace(u'\u2019', u"'")
    hfy_all_html = hfy_all_html.replace(u'\u2013', u"-")
    return etree.fromstring(hfy_all_html)


user_url=''
if len(sys.argv) == 2:
    user_url = sys.argv[1]
else:
    print("""
Enter a wiki URL as the first and only argument, it is used to get the list of items.  Try one of these:

          https://www.reddit.com/r/HFY/wiki/ref/universes/jenkinsverse/chronological_reading_order/

          https://www.reddit.com/r/HFY/wiki/ref/universes/jenkinsverse/timeline_reading_order/

          https://www.reddit.com/r/HFY/wiki/ref/universes/jenkinsverse/all_works/

NOTE: The all_works option WILL NOT WORK CORRECTLY because it, for
example, lists only part 1/4 of "Baptisms", meaning you'll miss a
bunch of content.  I'm not fixing it because it's going to be real
work and I have no interest in making an all_works book, but if you
do, feel free to ping robinleepowell@gmail.com if you need help.

""")
    sys.exit(1)

user_url_slug = user_url.rstrip().rstrip('/').split('/')[-1]

tree = get_hfy_etree(user_url)
all_chapters = []
# get all links
for a_tag in tree.xpath("//a"):
    # print(etree.tostring(a_tag, pretty_print=True, encoding="utf-8").decode("utf-8"))
    if '/wiki/' in a_tag.attrib['href'] and 'Origins' not in a_tag.text:
        # print("SKIPPING")
        continue
    if 'http' not in a_tag.attrib['href']:
        # print("SKIPPING")
        continue

    c = Chapter()

    c.title = a_tag.text
    c.url = a_tag.attrib['href']

    all_chapters.append(c)

for c in all_chapters:
    # Detect correct series per chapter

    # The default
    c.series = "The Deathworlders"

    if 'Kevin Jenkins Experience' in c.title:
        c.series = 'The Deathworlders'
    if "Humans don't Make Good Pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans don't Make Good Pets ", "")
    if "Humans don't make good pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans don't make good pets ", "")
    if "Humans Don't Make Good Pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans Don't Make Good Pets ", "")
    if "The Lost Minstrel" in c.title:
        c.series = "The Lost Minstrel"
        c.title = c.title.replace("The Lost Minstrel - ", "")
        c.title = c.title.replace("The Lost Minstrel -", "")
    if c.title.startswith('MIA'):
        c.series = "MIA"
        c.title = c.title.replace("MIA - ", "")
        c.title = c.title.replace("MIA ", "")
    if "Deathworld Origins" in c.title:
        c.series = "Deathworld Origins"
        c.title = c.title.replace("Deathworld Origins: ", "")
    if "Salvage - " in c.title:
        c.series = "Salvage"
        c.title = c.title.replace("Salvage - ", "")
    if "Salvage " in c.title:
        c.series = "Salvage"
        c.title = c.title.replace("Salvage ", "")
    if "Good Training" in c.title:
        c.series = "Good Training"
        c.title = c.title.replace("Good Training: ", "")
        if c.title == "":
            c.title = "0"
    if "Henosis " in c.title:
        c.series = "Henosis"
        c.title = c.title.replace("Henosis ", "")
    if "Monkeys Reaches Stars" in c.title:
        c.series = "Xiu Chang Saga"
    if "The Tiger's Cub" in c.title:
        c.series = "Xiu Chang Saga"
    if "The Tigers Cub" in c.title:
        c.series = "Xiu Chang Saga"
    if "Rat in Sheep's Clothing" in c.title:
        c.series = "Xiu Chang Saga"
    if "The Ox's Plan" in c.title:
        c.series = "Xiu Chang Saga"
    if "A Wounded Rabbit" in c.title:
        c.series = "Xiu Chang Saga"
    if "Waters of Babylon" in c.title:
        c.series = "Waters of Babylon"
        c.title = c.title.replace("Waters of Babylon - ", "")

    # Manually clean up some titles to match easier with Deathworlders website
    if c.title == "5.5: Interlude and Ultimatum":
        c.title = "5.5: Interlude/Ultimatum"
    if c.title == "21.5: d4 d5, c4 dxc4.":
        c.title = "Interlude/d4 d5, c4 dxc4"
    if c.title == "22.5: Outlets":
        c.title = "Interlude/Outlets"
    if "War on Two Worlds" in c.title:
        c.title = c.title.replace(" pt.1 - ", ", Part 1-")
        c.title = c.title.replace(" pt.2 - ", ", Part 2-")
        c.title = c.title.replace(" pt.3 - ", ", Part 3-")
        c.title = c.title.replace(" pt.4 - ", ", Part 4-")
        c.title = c.title.replace(" pt.5 - ", ", Part 5-")


    # Store reference to Deathworlders: Warhorse. This needs to be replaced by 6 new ones
    if "Warhorse" in c.title and c.series == "The Deathworlders":
        warhorse_chapter = c

    # Similar situation for Origins
    if "Deathworld Origins 1-8" in c.title and c.series == "Deathworld Origins":
        origins_chapter = c

    # Deal with un-follow-able URLs; this is silly, better would be
    # to update the wiki, but that seems like a silly request to
    # make too
    if 'redd.it/2s100t' in c.url:
        c.url = 'https://www.reddit.com/r/HFY/comments/2s100t/oc_humans_dont_make_good_pets_xxiii/'
    if 'redd.it/2sddv4' in c.url:
        c.url = 'https://www.reddit.com/r/HFY/comments/2sddv4/oc_humans_dont_make_good_pets_xxiv/'
    if 'redd.it/2t5gfl' in c.url:
        c.url = 'https://www.reddit.com/r/HFY/comments/2t5gfl/oc_humans_dont_make_good_pets_xxv/'
    if 'redd.it/2u4hpo' in c.url:
        c.url = 'https://www.reddit.com/r/HFY/comments/2u4hpo/oc_humans_dont_make_good_pets_xxvi/'


# Remove art links
to_remove = []
for c in all_chapters:
    if 'Concept Art' in c.title:
        to_remove.append(c)
for c in to_remove:
    all_chapters.remove(c)


# Fetch all Deathworlders titles + series
deathworlders = []
# FIXME: auto-detect how many pages there are; 25 is *way* more than
# the current (March 2025) count of 15, though, so it should be fine
for i in range(1,25):
    if i == 1:
        page = requests.get('https://deathworlders.com/')
    else:
        page = requests.get('https://deathworlders.com/page/' + str(i) + '/')

    page_text = page.text
    page_text = page_text.replace(u"\u2014", "-")
    page_text = page_text.replace(u"\u2019", "'")

    tree = etree.HTML(page_text)
    for a_tag in tree.xpath("//main/section/ul/li/a"):
        c = Chapter()
        c.series = a_tag.text
        c.title = a_tag.getchildren()[0].tail.replace(u"\u2019", "'")
        c.url = 'https://deathworlders.com' + a_tag.attrib['href']
        deathworlders.append(c)

# Splice in Warhorse chapters
warhorse_chapters_dw = []
for c in deathworlders:
    if c.series == "The Deathworlders" and 'Warhorse' in c.title:
        warhorse_chapters_dw.append(c)
warhorse_chapters_dw.reverse()
loc = all_chapters.index(warhorse_chapter)
all_chapters = all_chapters[0:loc] + warhorse_chapters_dw + all_chapters[loc+1:]

origins_chapters = []
page = requests.get('https://web.archive.org/web/20180610041631/http://captainmeta4.me/books/deathworld_origins/')

page_text = page.text
page_text = page_text.replace(u"\u2014", "-")
page_text = page_text.replace(u"\u2019", "'")

tree = etree.HTML(page_text)
for a_tag in tree.xpath("//section//li/a"):
    c = Chapter()
    c.series = "Deathworld Origins"
    c.title = a_tag.text
    c.url = 'https://web.archive.org/web/20180610041631/http://captainmeta4.me/books/deathworld_origins/' + a_tag.attrib['href']
    origins_chapters.append(c)

# Splice in Origins chapters
loc = all_chapters.index(origins_chapter)
all_chapters = all_chapters[0:loc] + origins_chapters + all_chapters[loc+1:]

for c in all_chapters:
    if c.series == 'The Deathworlders':
        for dw in deathworlders:
            if dw.series == 'The Deathworlders':
                dw_title = dw.title.split(":", 1)[1]
                if slugify(dw_title.lower()) in slugify(c.title.lower()):
                    c.url = dw.url
    if c.series == "Waters of Babylon":
        c.title = c.title.replace(".", "")
        for dw in deathworlders:
            if dw.series == "Waters of babylon":
                # No capital 'b' in Deathworlders site
                if dw.title.lower() in c.title.lower():
                    c.url = dw.url

# Stick missing chapters of the main series, if any, at the end
missing_chapters = []
for c in reversed(deathworlders):
    if c.series == "The Deathworlders":
        found = False
        for ac in all_chapters:
            if ac.series == "The Deathworlders":
                if ac.url == c.url:
                    found=True
                    break

        if not found:
            # Two interludes are known to not match but also
            # known to be present
            if "chapter-22.5-interlude-outlets" in c.url or "chapter-21.5-interlude-d4-d5-c4-dxc4" in c.url:
                continue

            c.title = c.title.split(": ", 1)[1]
            # print("not found")
            # print(c)
            all_chapters.append(c)

# This might be necessary on the all_works page?
#
# # First part of 'Good Training'
# for c in all_chapters:
#     if c.series == "Good Training" and "Good Training" in c.title and "Champions" not in c.title:
#         gt = c
# gt_chapters_dw = []
# for c in deathworlders:
#     if c.series == "Good Training" and "Chapter" in c.title:
#         gt_chapters_dw.append(c)
# loc = all_chapters.index(gt)
# all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]
# 
# # Good Training: The Champions
# for c in all_chapters:
#     if c.series == "Good Training" and "Good Training Champions 1" in c.title:
#         gt = c
# gt_chapters_dw = []
# for c in deathworlders:
#     if c.series == "Good Training: the Champions Part I":
#         gt_chapters_dw.append(c)
# loc = all_chapters.index(gt)
# all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]
# 
# # Good Training: The Champions part 2
# for c in all_chapters:
#     if c.series == "Good Training" and "Good Training Champions 2" in c.title:
#         gt = c
# gt_chapters_dw = []
# for c in deathworlders:
#     if c.series == "Good Training: the Champions Part II":
#         gt_chapters_dw.append(c)
# loc = all_chapters.index(gt)
# all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]

# # Deathworld Origins
# for c in all_chapters:
#     if c.series == "Deathworld Origins":
#         c.url = "https://captainmeta4.me/books/deathworld_origins/" + c.title

# Filter duplicate urls; this will effectively prune multi-part
# Deathworlders entries that are a single part on the main website
prev = None
to_delete = []
for c in all_chapters:
    if prev and c.url == prev.url:
        # Clean up the name of the first chapter to remove like
        # "(part 1/2)" at the end
        prev.title = prev.title.split("(")[0].rstrip()
        to_delete.append(c)
    prev = c
for c in to_delete:
    all_chapters.remove(c)


# Make sure to have no None values for series:
for c in all_chapters:
    if c.title == "The Brink":
        c.series = "The Brink"
    if c.title == "The Catechism of the Gricka":
        c.series = "The Catechism of the Gricka"


# Set authors
for c in all_chapters:
    if c.series == "The Deathworlders":
        c.author = "Hambone"
    elif c.series == "Humans don't Make Good Pets":
        c.author = "guidosbestfriend"
    elif c.series == "Xiu Chang Saga":
        c.author = "hume_reddit"
    elif c.series == "Salvage":
        c.author = "Rantarian"
    elif c.series == "MIA":
        c.author = "GoingAnywhereButHere"
    elif c.series == "Henosis":
        c.author = "hume_reddit"
    elif c.series == "The Lost Minstrel":
        c.author = "doules1071"
    elif c.series == "Good Training":
        c.author = "ctwelve"
    elif c.series == "Good Training: the Champions Part I":
        c.author = "ctwelve"
    elif c.series == "Good Training: the Champions Part II":
        c.author = "ctwelve"
    elif c.series == "Deathworld Origins":
        c.author = "captainmeta4"
    elif c.series == "The Brink":
        c.author = "slice_of_pi"
    elif c.series == "Waters of Babylon":
        c.author = "slice_of_pi"
    elif c.series == "The Catechism of the Gricka":
        c.author = "slice_of_pi"

        
# Create spec file
header = \
"""{
    "title": "Humanity - Fuck Yeah! - SLUGHERE",
    "creator": "Hambone, guidosbestfriend, hume_reddit, Rantarian, GoingAnywhereButHere, doules1071, ctwelve, slice_of_pi, captainmeta4",
    "filters": {
        "reddit": [
            "from-reddit-post",
            "clean-reddit",
            "custom-break-to-hr",
            "no-preamble",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "hfy-archive": [
            "from-hfy-archive",
            "clean-reddit",
            "custom-break-to-hr",
            "no-preamble",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "deathworld-origins": [
            "from-deathworld-origins",
            "clean-reddit",
            "custom-break-to-hr",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "humans-pets": [
                "from-reddit-post",
                "clean-reddit",
                "no-preamble",
                "jverse-hdmgp",
                "typography",
                "finalize"
        ],
        "mia": [
                "from-reddit-post",
                "clean-reddit",
                "no-preamble",
                "jverse-mia",
                "typography",
                "finalize"
        ],
        "salvage": [
                "from-reddit-post",
                "clean-reddit",
                "custom-break-to-hr",
                "no-preamble",
                "jverse-salvage",
                "typography",
                "finalize"
        ],
        "xiu": [
                "from-reddit-post",
                "clean-reddit", 
                "no-preamble",
                "jverse-txcs",
                "typography",
                "finalize"
        ]
    },
    "filename": "Humanity - Fuck Yeah - SLUGHERE",
    "output": ["epub", "latex", "html"],
    "contents":
    [
"""

header = header.replace('SLUGHERE', user_url_slug)

footer = \
"""
    ]
}
"""

spec_chapter = \
"""
        {
            "title": "%s",
            "filters": "%s",
            "src": "%s"
        }
"""

# Base the file name on the last part of the URL
spec_file = open('HFY_' + user_url_slug + '.spec', 'w')
spec_file.write(header)
chapter_list = []
for c in all_chapters:
    print("Adding " + c.title + " from " + c.series + " at " + c.url)
    if 'deathworlders.com' in c.url:
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "hfy-archive", c.url))
    elif c.series == "Humans don't Make Good Pets":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "humans-pets", c.url))
    elif c.series == "MIA":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "mia", c.url))
    elif c.series == "Salvage":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "salvage", c.url))
    elif c.series == "Xiu Chang Saga":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "xiu", c.url))
    elif c.series == "Deathworld Origins":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "deathworld-origins", c.url))
    else:
        if c.series:
            chapter_list.append(spec_chapter % (c.series + ": " + c.title, "reddit", c.url))

spec_file.write(",\n".join(chapter_list))
spec_file.write(footer)
spec_file.close()

