import hotshot
import hotshot.stats

for filename in ['editorsupport.hotshot']:
    hotshot.stats.load(filename).sort_stats('time').print_stats()


