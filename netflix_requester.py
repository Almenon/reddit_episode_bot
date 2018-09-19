__author__ = 'Almenon'

hardcoded_links = { # No netflix API availible, so I have to hardcode :(
    'bojack horseman': 'https://www.netflix.com/title/70300800',
    'orange is the new black': 'https://www.netflix.com/title/70242311',
    'my little pony': 'https://www.netflix.com/title/70234440',
    'black mirror': 'https://www.netflix.com/title/70264888',
    'agents of s.h.i.e.l.d.': 'https://www.netflix.com/title/70279852',
    'mad men':'https://www.netflix.com/title/70136135',
    'disenchantment':'https://www.netflix.com/title/80095697'
}

english_letters = "aeiouun"
accent_letters = b'\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xbc\xc3\xb1'.decode()
 # above is equivalent to "áéíóúüñ".encode().decode()
 # i should be able to just type "áéíóúüñ" and be done with it
 # probably has to do with the project encoding (file - settings - editor - file encodings in pycharm)
 # but it works so i'm not going to mess with it

def get_netflix_link(title):
    """
    Replaces accents in show title and tries to access dict of hardcoded netflix links
    :param title: of a show
    :return: link to instant watch show on Netflix.
    :raise:  KeyError if i don't have the link hardcoded
    """

    for accent, no_accent in zip(accent_letters, english_letters):
        title = title.replace(accent, no_accent)
    return hardcoded_links[title]

# this method used to be a lot fancier when I had a API I could call :/
