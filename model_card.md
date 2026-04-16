# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0**

A rule-based music recommender simulation built as a classroom project to explore how
scoring algorithms turn user preferences into ranked song suggestions.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *"Given what a listener says they like, which
songs in the catalog are the best match?"*

It does not predict listening history or learn from past behavior. Instead it takes four
explicit preferences — favorite genre, preferred mood, target energy level, and emotional
positivity (valence) — and scores every song in the catalog against them. The output is a
ranked list of the top five songs along with a plain-English explanation of why each one
was chosen.

The "prediction" is a score, not a probability. The system is not guessing what you might
like based on patterns — it is measuring distance between what you said you want and what
each song offers.

---

## 3. Data Used

- **Catalog size:** 20 songs stored in `data/songs.csv`
- **Features per song:** title, artist, genre, mood, energy (0.0–1.0), tempo_bpm,
  valence (0.0–1.0), danceability (0.0–1.0), acousticness (0.0–1.0)
- **Genres covered:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, country,
  electronic, k-indie, folk, funk, metal, soul, classical, punk, r&b
- **Moods covered:** happy, chill, intense, relaxed, moody, focused, melancholic,
  peaceful, sad, angry

**Limits and gaps:**
- Most genres have only **one** song. If your favorite genre is "folk," there is exactly
  one folk song in the entire catalog and the system has no alternatives to offer.
- Hip-hop, reggae, Latin, and gospel are completely absent. Users whose tastes fall in
  these areas will always get poor matches.
- Only the mood label "sad" appears on one song in the entire catalog (Rainy Seoul),
  meaning sad-preference listeners almost never get a mood match.
- The dataset was manually curated and reflects a Western, English-language perspective.
  It does not represent the diversity of global music.

---

## 4. Algorithm Summary

Think of the recommender as a friend who goes through every song in a pile and gives it
a score on a piece of paper before handing you the top five.

For each song, the friend adds up four things:

1. **Genre bonus (+2.0):** If the song's genre exactly matches what you said you like,
   it gets 2 points. This is the biggest single factor in the whole system.

2. **Mood bonus (+1.0):** If the song's mood exactly matches what you said you prefer,
   it gets 1 point. There is no partial credit — "focused" and "chill" count as
   completely different even if they feel similar.

3. **Energy closeness (0 to +2.0):** The closer the song's energy level is to your
   target, the more points it earns. A perfect match earns the full 2 points; a song on
   the completely opposite end earns close to zero.

4. **Valence closeness (0 to +1.0):** Same idea for emotional positivity — how happy
   vs. melancholic the song sounds. A perfect match earns 1 point; a mismatch earns
   close to zero.

The **highest possible score is 6.0**. Once every song has a number, the pile is sorted
and the top five are returned. The weights are stored in `DEFAULT_WEIGHTS` in
`src/recommender.py` and can be changed to run experiments without touching the core
logic.

---

## 5. Observed Behavior / Biases

**Genre dominates everything.**
Because genre is worth +2.0 and the maximum from mood is only +1.0, any song in the
matching genre will outscore almost any song outside of it — even if the outside song
matches every other preference better. In testing, "Gym Hero" (pop, but mood=*intense*)
ranked #2 for a happy pop listener, beating songs that matched the listener's happy mood
but belonged to a different genre. A real listener would have found those mood-matched
songs more satisfying.

**The system cannot detect contradictory preferences.**
The adversarial test profile asked for genre=metal, mood=sad, and energy=0.90. In the
real world, metal songs are almost never sad — they are angry or intense. The system did
not notice the contradiction. It returned Hollow Crown (metal, angry) at the top because
the genre matched, and Rainy Seoul (k-indie, sad, energy=0.31) at #2 because the mood
matched — despite Rainy Seoul being a quiet, low-energy track that sounds nothing like
what a metal fan wants. The system just picks the least-wrong answer rather than flagging
the conflict.

**Mood matching is all-or-nothing.**
"Angry" and "intense" are scored as completely different moods. "Peaceful" and "relaxed"
are completely different. In reality these are close neighbors, and listeners who prefer
one would often accept the other. The binary match/no-match design misses this nuance.

**Small catalog = forced filler.**
With only 20 songs across 17 genres, most top-5 lists include 3 or 4 songs that do not
match the genre at all. They are filler — the system has no better options. This makes
recommendations feel generic for any listener whose favorite genre has only one
representative in the catalog.

---

## 6. Evaluation Process

Four user profiles were tested by running `python -m src.main` and reading the output:

| Profile | Genre | Mood | Energy | Valence | Top Result | Score |
|---|---|---|---|---|---|---|
| High-Energy Pop | pop | happy | 0.80 | 0.85 | Sunrise City | 5.95/6.0 |
| Chill Lofi | lofi | chill | 0.38 | 0.58 | Library Rain | 5.92/6.0 |
| Deep Intense Rock | rock | intense | 0.92 | 0.45 | Storm Runner | 5.95/6.0 |
| Adversarial | metal | sad | 0.90 | 0.20 | Hollow Crown | 4.86/6.0 |

**What felt right:** The first three profiles returned exactly what you would expect. When
a catalog song genuinely matched all four dimensions, it rose to the top with a score
above 5.8/6.0. The results were accurate enough that a real listener would likely
recognize the top pick as a good choice.

**What surprised me:** The adversarial profile returned Hollow Crown at #1 even though
its mood is "angry" not "sad." The genre weight alone was enough to win. Also surprising:
Gym Hero (#2 for pop/happy) kept showing up even though its mood was "intense" — a
reminder that the genre bonus is powerful enough to override mood mismatches.

**Experiment:** The Deep Intense Rock profile was run twice — once with default weights
and once with genre weight halved (1.0) and energy weight doubled (4.0). The ranking
order did not change. Storm Runner was still #1 because it matched on every dimension.
This showed that weight tuning only matters when songs are close competitors — in a
20-song catalog with one rock song, the weights barely matter.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Learning how scoring-based recommendation systems work
- Exploring how weight choices affect which results bubble to the top
- Classroom discussion about bias, fairness, and data representation in AI systems
- Experimentation: changing weights, adding songs, testing edge-case profiles

**Not intended for:**
- Making real music recommendations for actual listeners
- Replacing or comparing against production systems like Spotify, Apple Music, or YouTube
- Any application where the quality of recommendations affects a real person's experience
- Drawing conclusions about a user's actual taste — the profile is too simple and the
  catalog is too small to represent real musical preference

---

## 8. Ideas for Improvement

1. **Partial mood credit using mood families.** Group moods into clusters
   (e.g., {chill, relaxed, peaceful} and {intense, angry, energetic}) and award 0.5
   points for a within-family match instead of 0 for anything outside the exact label.
   This would make mood matching feel much more realistic.

2. **Contradiction detection before scoring.** Before running recommendations, check
   whether the user's genre and mood preferences are compatible based on the catalog
   data. If the combination has zero songs, warn the user and suggest adjustments rather
   than silently returning misleading results.

3. **Diversity enforcement in the top-k output.** After ranking all songs, check that
   the top five do not all come from the same genre. If they do, replace some lower-ranked
   same-genre songs with the highest-ranked songs from different genres. This prevents
   the list from feeling repetitive and gives listeners exposure to adjacent styles.

---

## 9. Personal Reflection

**Biggest learning moment:**
The moment that changed how I think about recommenders was running the adversarial
profile. I expected the system to struggle, but I did not expect it to be so confident
about a wrong answer. Hollow Crown (metal, angry) ranked #1 at 4.86/6.0 — a high score
— even though the user explicitly asked for sad music. The system was not confused; it
was certain. That is the danger of a simple scoring algorithm: it always produces an
answer, and the number looks authoritative even when the underlying logic cannot
represent what the user actually wants. Real recommenders earn trust by being right most
of the time, not by always producing an answer.

**How AI tools helped — and when I had to double-check:**
AI tools were genuinely useful for structuring the project quickly: generating the CSV
expansion, suggesting the `sorted()` vs `.sort()` distinction, and drafting the Mermaid
flowchart. But I had to verify the output myself. When I ran the profiles, I compared the
scores manually against the CSV data to confirm the math was correct — the code looked
right but the only way to trust the ranking was to trace through a few scores by hand.
AI tools produce plausible-looking output, and in a scoring system "plausible" is not
the same as "correct."

**What surprised me about simple algorithms feeling like recommendations:**
The output actually felt like recommendations. When I ran the Chill Lofi profile and saw
Library Rain and Midnight Coding at the top, it genuinely felt like the system "got it."
That was surprising — four arithmetic operations produced something that felt intelligent.
The lesson is that recommendation does not require understanding. It only requires
measurement. The system did not understand what "chill" means; it just measured how close
a number was to another number, and the pattern happened to match human intuition for
the cases where the catalog had good coverage. The feeling of intelligence was real; the
intelligence was not.

**What I would try next:**
The biggest gap in VibeFinder is that it treats all users the same way — one profile, one
answer, no history. The most interesting next step would be adding a simple feedback loop:
after showing the top five, ask the user to rate one or two songs, then adjust the weights
automatically based on those ratings. If the user says the energy match mattered more
than the genre, reduce the genre weight for the next run. That would move the system from
"rule-based" toward something closer to how real recommenders learn from behavior — and
it would make the bias experiments from this project far more meaningful, because you
could watch the weights shift in response to real input.
