#! /usr/bin/env python3
'''
Convert an EmulationStation folder of NES ROMs and covers to work with NES Switch. The folder must contain gamelist.xml with local paths.
'''
from glob import glob
from gzip import open as gopen
from os import chdir,mkdir,remove
from os.path import abspath,expanduser,isdir,isfile
from PIL import Image
from progress.counter import Countdown
from subprocess import call
from tempfile import NamedTemporaryFile
from unidecode import unidecode
from xml.etree.ElementTree import parse
from zlib import compress
import argparse

def convert_date(old):
    return '%s-%s-%s' % (old[:4], old[4:6], old[6:8])

# parse args
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--input', required=True, type=str, help="Input EmulationStation Folder")
parser.add_argument('-o', '--output', required=True, type=str, help="Output Folder")
parser.add_argument('-N', '--NvnTexpkg', required=True, type=str, help="Path to NvnTexpkg.exe executable")
args = parser.parse_args()
INDIR = abspath(expanduser(args.input)).rstrip('/')
GAMELIST = '%s/gamelist.xml' % INDIR
OUTDIR = abspath(expanduser(args.output)).rstrip('/')
assert isdir(INDIR), "Non-existant input folder: %s" % INDIR
assert isfile(GAMELIST), "Non-existant gamelist: %s" % GAMELIST
assert not isdir(OUTDIR), "Output folder exists: %s" % OUTDIR

# perform conversion
gamelist = parse(GAMELIST).getroot()
progbar = Countdown('Remaining: ', max=len(gamelist.findall('game')))
mkdir(OUTDIR)
db = open('%s/lclassics.titlesdb' % OUTDIR, 'w')
db.write('{\n\t"titles": [')
for i,game in enumerate(gamelist):
    game_data = {attr.tag: unidecode(attr.text) for attr in game}
    game_data['name'] = game_data['name'].replace('"','').replace(':','').replace('\n',' ').replace('-',' ').replace("'",'').replace('?','').replace('!','').replace('+','and').replace('$','S').replace('.','')
    if 'developer' not in game_data:
        game_data['developer'] = game_data['publisher']
    if 'releasedate' not in game_data:
        game_data['releasedate'] = '19850913T000000'
    if 'players' not in game_data:
        game_data['players'] = 1
    elif isinstance(game_data['players'], str):
        game_data['players'] = int(game_data['players'].replace('1-2','2').replace('+',''))
    assert game_data['path'][:2] == './' and game_data['image'][:2] == './', "gamelist.xml must have local paths starting with './'"
    GAMEDIR = '%s/%s' % (OUTDIR, game_data['name'].replace(':',' -').replace('?',' -'))
    mkdir(GAMEDIR)
    ROM_PATH = '%s/%s.nes' % (GAMEDIR, game_data['name'].replace(':',' -').replace('?',''))
    COVER_PATH = '%s/%s.xtx.z' % (GAMEDIR, game_data['name'].replace(':',' -').replace('?',''))
    rom = open(ROM_PATH, 'wb')
    if game_data['path'].lower().endswith('.gz'):
        rom.write(gopen('%s/%s' % (INDIR, game_data['path'][2:])).read())
    else:
        rom.write(open('%s/%s' % (INDIR, game_data['path'][2:]), 'rb').read())
    rom.close()
    Image.open('%s/%s' % (INDIR, game_data['image'][2:])).save('%s/%s.tga' % (INDIR, game_data['image'][2:]))
    call([args.NvnTexpkg, '-i', '%s/%s.tga' % (INDIR, game_data['image'][2:]), '--mip-filter', 'box', '--minmip', '5', '-f', 'rgba8', '-o', '%s/%s.xtx' % (INDIR, game_data['image'][2:])])
    assert isfile('%s/%s.xtx' % (INDIR, game_data['image'][2:])), "NvnTexpkg didn't create xtx file for game: %s" % game_data['name']
    cover = open(COVER_PATH, 'wb')
    cover.write(compress(open('%s/%s.xtx' % (INDIR, game_data['image'][2:]), 'rb').read(), 9))
    remove('%s/%s.tga' % (INDIR, game_data['image'][2:]))
    remove('%s/%s.xtx' % (INDIR, game_data['image'][2:]))
    cover.close()
    if i != 0:
        db.write(',')
    db.write('\n\t\t{\n')
    db.write('\t\t\t"sort_title": "%s",\n' % game_data['name'])
    db.write('\t\t\t"publisher": "NINTENDO",\n') #db.write('\t\t\t"publisher": "%s",\n' % game_data['publisher'])
    db.write('\t\t\t"code": "%s",\n' % game_data['name'])
    db.write('\t\t\t"rom": "%s",\n' % ROM_PATH.replace(OUTDIR,'/titles'))
    db.write('\t\t\t"copyright": "NINTENDO",\n') #db.write('\t\t\t"copyright": "%s",\n' % game_data['developer'])
    db.write('\t\t\t"title": "%s",\n' % game_data['name'])
    db.write('\t\t\t"volume": 74,\n')
    db.write('\t\t\t"release_date": "%s",\n' % convert_date(game_data['releasedate']))
    db.write('\t\t\t"players_count": %d,\n' % game_data['players'])
    db.write('\t\t\t"cover": "%s",\n' % COVER_PATH.replace(OUTDIR,'/titles'))
    db.write('\t\t\t"overscan": [0, 0, 9, 3],\n')
    db.write('\t\t\t"armet_version": "v1",\n')
    db.write('\t\t\t"lcla6_release_date": "2018-09-01",\n')
    db.write('\t\t\t"save_count": 0,\n')
    db.write('\t\t\t"simultaneous": false,\n')
    db.write('\t\t\t"fadein": [3, 2],\n')
    db.write('\t\t\t"details_screen": "",\n') #db.write('\t\t\t"details_screen": "%s",\n' % game_data['desc'])
    db.write('\t\t\t"armet_threshold": 80,\n')
    db.write('\t\t\t"sort_publisher": "nintendo"\n') #db.write('\t\t\t"sort_publisher": "%s",\n' % game_data['publisher'])
    db.write('\t\t}')
    progbar.next()
db.write('\n\t]\n}\n')
db.close()
