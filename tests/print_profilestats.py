import hotshot
import hotshot.stats

for filename in ['paras.hotshot']:
    hotshot.stats.load(filename).sort_stats('time').print_stats()


