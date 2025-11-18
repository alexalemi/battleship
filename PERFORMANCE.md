# Performance Notes

## Player Bot Performance

Different player bots have significantly different computational requirements:

### Fast Bots (<0.1s per move)
- `randguess.py` - Pure random, instant
- `tile.py` - Sequential tiling, instant
- `hunter.py` - Hunt and target, very fast
- `hunter_parity.py` - Hunt and target with parity, very fast

### Medium Bots (0.1-0.5s per move)
- `ethan.py` - Probabilistic strategy, moderately fast
- `frederic.py` - Monte Carlo with 1000 iterations, ~0.5s per move

### Slow Bots (>1.5s per move)
- `maxime.py` - Heavy Monte Carlo simulation, ~1.9s per move

## Running Tournaments

### Default Timeout (2s)
The default 2-second timeout works for most bots except `maxime.py`:

```bash
# Works well for fast/medium bots
battleship --leaderboard players/hunter.py players/frederic.py players/ethan.py -n 25
```

### Higher Timeout (5s)
For including `maxime.py` or running on slower systems, increase the timeout:

```bash
# Include slow bots with higher timeout
battleship --leaderboard --timeout 5 -n 25

# Or specifically for maxime.py
battleship --tournament players/maxime.py players/frederic.py --timeout 5 -n 10
```

### Tournament Duration Estimates

With 7 players and N games per matchup:
- Total matchups: C(7,2) = 21 matchup pairs
- Total games: 21 × 2 × N = 42N games
- Average game length: ~50-80 turns

**Time estimates:**
- Fast bots only (N=25): ~2-5 minutes
- With frederic.py (N=25): ~5-10 minutes
- With maxime.py (N=25, timeout=5): ~20-30 minutes

### Recommendations

1. **Quick testing**: Use `--timeout 2` and exclude `maxime.py`
2. **Full tournament**: Use `--timeout 5` to include all bots
3. **Benchmarking**: Use `-n 1` or `-n 2` for rapid iteration
4. **Production**: Use `-n 100` or more for stable rankings

### Excluding Slow Bots

To exclude maxime.py from auto-discovery, make it non-executable:

```bash
chmod -x players/maxime.py
```

Or specify players explicitly:

```bash
battleship --leaderboard players/{hunter,frederic,ethan}.py -n 50
```
