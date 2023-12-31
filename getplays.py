import calendar
import pytz
import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

COOKIE = None

class Play:
  def __init__(self, name, mode, diff, score, grade, passed, plate, counts, date):
    self.name = name
    self.mode = mode
    self.diff = diff
    self.score = score
    self.grade = grade
    self.passed = passed
    self.plate = plate
    self.counts = counts
    self.date = date

  def pretty(self):
    s  = ''
    s += '%s %s%d\n' % (self.name, self.mode, self.diff)
    s += '%d %s %s %s\n' % (self.score, self.grade, ("Fail","Pass")[self.passed], self.plate)
    s += '%s\n' % ' / '.join(self.counts)
    s += '[%s]' % str(self.date.astimezone())
    return s

  def short(self):
    return '%s %s%d: %d' % (self.name, self.mode, self.diff, self.score)

def epoch(date):
  return calendar.timegm(date.astimezone(pytz.utc).timetuple())

def open_db(path):
  con = sqlite3.connect(path)
  cur = con.cursor()
  cur.execute('CREATE TABLE IF NOT EXISTS plays(uniq TEXT, name TEXT, mode TEXT, diff INT, score INT, grade TEXT, passed INT, plate TEXT, perfs INT, greats INT, goods INT, bads INT, misses INT, date INT, date_pretty TEXT)')
  return con

def play_already_saved(db, play):
  cur = db.cursor()
  cur.execute("SELECT rowid FROM plays WHERE date = ? AND score = ?", (epoch(play.date), play.score))
  data = cur.fetchone()
  return not (data is None)

def save_play(db, play):
  if play.mode[0] == 'U':
    uniq = '%s %s' % (play.name, play.mode)
  else:
    uniq = '%s %s%d' % (play.name, play.mode, play.diff)
  cur = db.cursor()
  cur.execute('INSERT INTO plays(uniq, name, mode, diff, score, grade, passed, plate, perfs, greats, goods, bads, misses, date, date_pretty) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (
    uniq,
    play.name,
    play.mode,
    play.diff,
    play.score,
    play.grade,
    play.passed,
    play.plate,
    play.counts[0],
    play.counts[1],
    play.counts[2],
    play.counts[3],
    play.counts[4],
    epoch(play.date),
    str(play.date.astimezone()),
  ))
  db.commit()

def save_plays(db, plays, debug=True):
  for play in plays[::-1]:
    if debug: print('*** Possibly saving %s...' % play.short())
    if not play_already_saved(db, play):
      print('*** Saving %s...' % play.short())
      save_play(db, play)

def fetch_page(page):
  global COOKIE
  if COOKIE == None:
    try:
      COOKIE = open('cookie.txt', 'rb').read().decode('utf-8')
    except:
      raise Exception('Failure to read cookie.txt; login at piugame.com and save the contents of document.cookie')
  x = requests.get('https://www.piugame.com/my_page/recently_played.php?&&page=%d' % page, headers={'Cookie':COOKIE})
  if x.history and x.history[0].headers['Location'] == '?&page=1':
    return None
  return x.text

def fetch_page_fake():
  return open('test_html.txt','rb').read().decode('utf-8')

def parse_page(html, debug=True):
  soup = BeautifulSoup(html, 'html.parser')
  ul = soup.find('ul', re.compile('.*recently_playeList.*'))
  if ul == None:
    raise Exception('Play list not found on fetched page (are you logging in correctly?)')

  # For each score on the page...
  plays = []
  for li in ul.findChildren('li', recursive=False):
    if debug: print('*Score Element*')
 
   # Song name
    name = li.find('div', re.compile('.*song_name.*')).text
    if debug: print('  name = '+name)

    # Mode
    mode_img = li.find('div', 'tw').find('img')['src']
    if mode_img.endswith('d_text.png'):
      mode = 'D'
    elif mode_img.endswith('s_text.png'):
      mode = 'S'
    elif mode_img.endswith('c_text.png'):
      mode = 'C'
    elif mode_img.endswith('u_text.png'):
      bg_style = li.find('div', re.compile('.*cont.*'))['style']
      if '/s_bg.png' in bg_style:
        mode = 'US'
      elif '/d_bg.png' in bg_style:
        mode = 'UD'
      else:
        raise Exception('Unexpected UCS style: '+bg_style)
    else:
      raise Exception('Unexpected mode image src: '+mode_img)
    if debug: print('  mode = '+mode)

    # Difficulty
    diff_num = 0
    if mode[0] != 'U':
      diff_div = li.find('div', re.compile('.*numw.*'))
      diff = ''
      for img in diff_div.find_all('img'):
        diff_img = img['src']
        if diff_img.endswith('/c_icon.png'): continue
        if diff_img.endswith('/u_num_x.png'): continue
        x = re.match(r'.*/[dsc]_num_(\d)\.png$', diff_img)
        if x == None:
          raise Exception('Unexpected difficulty image src: '+diff_img)
        diff += x.group(1)
      if debug: print('  diff = '+diff)
      diff_num = int(diff)

    # Stage Break, Score, Grade, Passed, Plate
    grade_div = li.find('div', 'li_in ac')
    score_text = grade_div.text.strip()
    stage_break = (score_text == "STAGE BREAK")
    if debug: print('  stage_break = '+str(stage_break))
    if not stage_break:
      # Score
      score = score_text.replace(',','')
      if int(score) < 0 or int(score) > 1000000:
        raise Exception('Unexpected score: '+score)
      if debug: print('  score = '+score)

      # Grade, Passed
      grade_img = grade_div.find('img')['src']
      x = re.match(r'.*/grade/(x_)?(?:([a-z]+)(_p)?)\.png', grade_img)
      if x == None:
        raise Exception('Unexpected grade image src: '+grade_img)
      passed = (x.group(1) == None)
      if debug: print('  passed: '+str(passed))
      grade = x.group(2).upper()
      if x.group(3) == '_p':
        grade += '+'
      if grade not in ('SSS+', 'SSS', 'SS+', 'SS', 'S+', 'S', 'AAA+', 'AAA', 'AA+', 'AA', 'A+', 'A', 'B', 'C', 'D', 'F'):
        raise Exception('Unexpected grade: '+grade)
      if debug: print('  grade = '+grade)

      # Plate
      plate = ''
      plate_div = li.find('div', 'li_in st1')
      if plate_div:
        plate_img = plate_div.find('img')['src']
        x = re.match(r'.*/plate/(\w+)\.png', plate_img)
        plate = x.group(1).upper()
      if plate not in ('PG', 'UG', 'EG', 'SG', 'MG', 'TG', 'FG', 'RG', ''):
        raise Exception('Unexpected plate: '+plate)
      if debug: print('  plate = '+plate)
    else: # Stage break
      score = 0
      grade = ''  # <- A grade of '' indicates stage break
      passed = False
      plate = ''

    # Judgment Counts
    tbody = li.find('tbody')
    counts = []
    for td in tbody.find_all('td'):
      counts.append(td.text.replace(',','').strip())
    if len(counts) != 5:
      raise Exception('Unexpected judgment counts: '+str(counts))
    if debug: print('  counts = '+' / '.join(counts))

    # Date
    date_text = li.find('p', 'recently_date_tt').text.strip().replace('GMT+9', 'GMT+0900') # lazy
    date = datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S (%Z%z)')
    if debug: print('  date = %s (%d)' % (str(date.astimezone()), epoch(date)))

    play = Play(name, mode, diff_num, int(score), grade, passed, plate, counts, date)
    plays.append(play)
  return plays

def fetch_and_parse_all_pages(db=None, debug=True):
  all_plays = []
  page = 1
  while True:
    print('*** Fetching page %d...' % page)
    html = fetch_page(page)
    if html == None: break
    plays = parse_page(html)
    if db:
      # TODO: Check if we should stop fetching pages by using db queries
      pass
    all_plays.extend(plays)
    page += 1
  return all_plays

def full_update(db_path):
  db = open_db(db_path)
  plays = fetch_and_parse_all_pages(db)
  save_plays(db, plays)

if __name__ == '__main__':
  full_update('plays.db')
  #html = fetch_page_fake()
  #plays = parse_page(html)

# TODO: Option to fetch the cookie automatically given a hardcoded username/password

