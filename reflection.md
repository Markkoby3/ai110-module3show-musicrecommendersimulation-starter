# Reflection: Comparing User Profile Outputs

This file compares what the recommender returned for each profile tested and explains
why the differences make sense — written for a non-programmer audience.

---

## Profile 1 vs. Profile 2: High-Energy Pop vs. Chill Lofi

**High-Energy Pop** (genre=pop, mood=happy, energy=0.80, valence=0.85) got upbeat,
fast songs — Sunrise City at the top with a score of 5.95/6.0. The results feel exactly
right: they are bright, positive tracks that you would hear in a workout playlist or a
feel-good movie montage.

**Chill Lofi** (genre=lofi, mood=chill, energy=0.38, valence=0.58) got quiet, slow
background music — Library Rain and Midnight Coding, both near-silent bedroom-producer
tracks. These are songs you put on when studying or winding down.

**Why they differ:** The energy preference is doing most of the work here. A song like
Sunrise City (energy=0.82) scores nearly 2.0 out of 2.0 for the Pop listener but scores
close to 0 for the Lofi listener who targets energy=0.38. The math is just measuring
distance: how far is this song from what you asked for? A high-energy song is very far
from a low-energy target, so it sinks to the bottom automatically.

---

## Profile 2 vs. Profile 3: Chill Lofi vs. Deep Intense Rock

**Chill Lofi** surfaced soft, instrumental tracks with energy below 0.45. The top two
were nearly identical in score (5.92 vs 5.90) because both Library Rain and Midnight
Coding match the genre, mood, and energy target almost perfectly.

**Deep Intense Rock** (genre=rock, mood=intense, energy=0.92, valence=0.45) surfaced
Storm Runner at the top, followed by punk and electronic tracks. The system correctly
identified that a rock listener who wants intensity would also accept punk and electronic
music — those genres share the "intense" mood tag even though they sound very different
in practice.

**Why they differ:** These two profiles are nearly opposite on every dimension — the
Lofi listener wants 0.38 energy, the Rock listener wants 0.92. Songs that score well for
one profile score terribly for the other, which is exactly what you want from a
recommender. The system correctly sorted them into completely non-overlapping lists.

---

## Profile 3 vs. Profile 4: Deep Intense Rock vs. Adversarial

**Deep Intense Rock** produced a clean, consistent top 5: all five songs are genuinely
intense, high-energy tracks. The #1 result (Storm Runner) matched on genre, mood, energy,
and valence — a near-perfect result.

**Adversarial** (genre=metal, mood=sad, energy=0.90, valence=0.20) produced a messy,
contradictory list. The #1 result was Hollow Crown (metal, angry) — not sad at all — and
the #2 result was Rainy Seoul (k-indie, sad, energy=0.31) — not energetic at all. The
system could not find a single song that is simultaneously metal, sad, and high-energy,
because no such song exists in the catalog.

**Why the adversarial profile "tricks" the system:** Metal music tends to be intense and
angry, not sad. Sad music tends to be slow and quiet. Asking for metal AND sad AND high
energy is like asking for a quiet explosion — the preferences pull in opposite directions.
The system has no way to notice this conflict; it just picks the song that scores best on
whatever signals align, which in this case was the genre bonus for metal. The result
feels wrong because the input was contradictory, and the system had no mechanism to say
"these preferences don't go together."

---

## Experiment: What Happened When We Changed the Weights

We ran **Deep Intense Rock** twice — once with the default weights (genre +2.0, energy
+2.0 max) and once with the genre weight halved to +1.0 and the energy weight doubled to
+4.0 max.

**The ranking did not change.** Storm Runner was still #1, Chasing Sparks was still #2.

This tells us something important: when a song genuinely matches on all dimensions (as
Storm Runner does), the ordering is stable no matter how you adjust the weights. Weight
tuning matters most when songs are close competitors — for example, when you have two
songs where one has a genre match and the other has a better energy match. In this
dataset, those close calls mostly did not exist for the rock profile, so the experiment
had no visible effect on ranking order.

The practical lesson: if you want to test whether your weights are doing anything
meaningful, you need a larger catalog where many songs compete closely on multiple
dimensions. With only one rock song in the catalog, the system was always going to rank
Storm Runner first regardless of the weights.

---

## Summary: What the Profiles Reveal About the System

The outputs across all four profiles show that the recommender works well when:
- The user's genre exists in the catalog
- There are at least two songs in that genre to compare
- The mood and energy preferences are internally consistent

It struggles when:
- The user's preferences contradict each other (Adversarial profile)
- The genre has only one representative in the catalog (the system has no choice)
- The user's mood preference is rare — "sad" appears on only one song in the catalog,
  meaning no mood match is possible for most sad-preference users

In plain terms: the system is as good as the data it has to work with. A recommender
that knows about 20 songs will always feel limited, because a real music listener's taste
is shaped by thousands of songs they have heard over a lifetime.
