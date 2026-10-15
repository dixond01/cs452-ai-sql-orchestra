# More Examples

All from the `openai/gpt-oss-120b` runs in [`responses/`](responses/). I checked each result against the data by hand.

## 1. How many players are in each ensemble?

**Strategy**: zero-shot

```sql
SELECT e.ensemble_id,
       e.name,
       COUNT(m.player_id) AS player_count
FROM ensemble AS e
LEFT JOIN membership AS m ON e.ensemble_id = m.ensemble_id
GROUP BY e.ensemble_id, e.name;
```

**Result**: `[(1, 'Symphony Orchestra', 10), (2, 'Wind Ensemble', 5), (3, 'String Quartet', 4), (4, 'Jazz Band', 7), (5, 'Chamber Strings', 6)]`

**Friendly response**: Here's how many players are in each ensemble: Symphony Orchestra: 10 players, Wind Ensemble: 5 players, String Quartet: 4 players, Jazz Band: 7 players, Chamber Strings: 6 players.

## 2. Who is the first chair cellist in the Symphony Orchestra?

**Strategy**: single-domain

```sql
SELECT p.first_name, p.last_name
FROM membership m
JOIN ensemble e ON m.ensemble_id = e.ensemble_id
JOIN section s ON m.section_id = s.section_id
JOIN player p ON m.player_id = p.player_id
WHERE e.name = 'Symphony Orchestra'
  AND s.instrument = 'Cello'
  AND m.chair_number = 1;
```

**Result**: `[('Ethan', 'Nguyen')]`

**Friendly response**: The first chair cellist in the Symphony Orchestra is Ethan Nguyen.

## 3. Which players play more than one instrument?

**Strategy**: cross-domain

Violin I and Violin II are different sections but the same instrument. It correctly counted distinct `instrument` values rather than distinct sections.

```sql
SELECT p.player_id, p.first_name, p.last_name
FROM player p
JOIN membership m ON p.player_id = m.player_id
JOIN section s ON m.section_id = s.section_id
GROUP BY p.player_id
HAVING COUNT(DISTINCT s.instrument) > 1;
```

**Result**: `[(1, 'Emma', 'Larsen'), (7, 'Sophia', 'Martinez'), (8, 'Mason', 'Clark'), (13, 'Charlotte', 'Davis'), (15, 'Amelia', 'Garcia')]`

**Friendly response**: Here are the players who play more than one instrument: Emma Larsen (ID 1), Sophia Martinez (ID 7), Mason Clark (ID 8), Charlotte Davis (ID 13), Amelia Garcia (ID 15).

## 4. Which parents have more than one child in the program?

**Strategy**: single-domain

Laura Davis is the tricky one: her children have different last names (Charlotte Davis and Henry Wilson).

```sql
SELECT p.name, p.phone, p.email, COUNT(DISTINCT pp.player_id) AS child_count
FROM parent p
JOIN player_parent pp ON p.parent_id = pp.parent_id
GROUP BY p.parent_id
HAVING COUNT(DISTINCT pp.player_id) > 1;
```

**Result**: `[('Karen Larsen', '801-555-0101', 'karen.larsen@example.com', 2), ('Erik Larsen', '801-555-0102', 'erik.larsen@example.com', 2), ('Laura Davis', '801-555-0112', 'laura.davis@example.com', 2)]`

**Friendly response**: Here are the parents who have more than one child in the program: Karen Larsen – 801‑555‑0101 – karen.larsen@example.com (2 children), Erik Larsen – 801‑555‑0102 – erik.larsen@example.com (2 children), Laura Davis – 801‑555‑0112 – laura.davis@example.com (2 children).

## 5. Who is the youngest player in the Wind Ensemble?

**Strategy**: zero-shot

```sql
SELECT p.first_name,
       p.last_name,
       p.birth_date
FROM   membership m
JOIN   player p        ON p.player_id = m.player_id
JOIN   ensemble e      ON e.ensemble_id = m.ensemble_id
WHERE  e.name = 'Wind Ensemble'
ORDER BY p.birth_date DESC
LIMIT 1;
```

**Result**: `[('Henry', 'Wilson', '2012-09-15')]`

**Friendly response**: The youngest player in the Wind Ensemble is Henry Wilson, born 2012‑09‑15.

## 6. Which ensembles have rehearsals that overlap in time?

**Strategy**: single-domain

It wrote a correct interval-overlap self-join on its own, and `e1.ensemble_id < e2.ensemble_id` avoids listing each pair twice.

```sql
SELECT e1.name AS ensemble1,
       e2.name AS ensemble2,
       e1.rehearsal_day
FROM ensemble e1
JOIN ensemble e2
  ON e1.ensemble_id < e2.ensemble_id
 AND e1.rehearsal_day = e2.rehearsal_day
 AND e1.start_time < e2.end_time
 AND e2.start_time < e1.end_time;
```

**Result**: `[('Symphony Orchestra', 'Wind Ensemble', 'Saturday'), ('String Quartet', 'Chamber Strings', 'Tuesday')]`

**Friendly response**: Saturday: Symphony Orchestra and Wind Ensemble. Tuesday: String Quartet and Chamber Strings.

## 7. Which other ensembles could Emma Larsen join without a schedule conflict?

**Strategy**: zero-shot

The SQL is correct, and so is the empty result: Emma is in the Symphony Orchestra, Jazz Band and Chamber Strings, and the only other two ensembles each overlap one of hers. But the friendly answer is useless for a person: it doesn't explain *why* nothing matched.

```sql
SELECT e.*
FROM ensemble e
WHERE e.ensemble_id NOT IN (
        SELECT m.ensemble_id
        FROM membership m
        WHERE m.player_id = 1
      )
  AND NOT EXISTS (
        SELECT 1
        FROM membership m
        JOIN ensemble em ON m.ensemble_id = em.ensemble_id
        WHERE m.player_id = 1
          AND e.rehearsal_day = em.rehearsal_day
          AND e.start_time < em.end_time
          AND e.end_time   > em.start_time
      );
```

**Result**: `[]`

**Friendly response**: Nothing matched.

Interesting detail: zero-shot hard-coded `player_id = 1`, which it could only know from the sample rows in the prompt. The other two strategies looked her up by name.

## 8. Do any orchestras have the same conductor? Which ones?

The result depended on the strategy.

**Single-domain** took "orchestras" literally:

```sql
SELECT
    c.name AS conductor,
    GROUP_CONCAT(e.name, ', ') AS orchestras
FROM ensemble e
JOIN conductor c ON e.conductor_id = c.conductor_id
WHERE e.name LIKE '%Orchestra%'
GROUP BY c.conductor_id
HAVING COUNT(*) > 1;
```

**Result**: `[]`

**Friendly response**: Nothing matched.

**Zero-shot** treated every ensemble as an orchestra:

```sql
SELECT e.conductor_id,
       c.name AS conductor_name,
       GROUP_CONCAT(e.name, ', ') AS ensembles
FROM ensemble e
JOIN conductor c ON e.conductor_id = c.conductor_id
GROUP BY e.conductor_id
HAVING COUNT(*) > 1;
```

**Result**: `[(1, 'Maria Alvarez', 'Symphony Orchestra, Chamber Strings'), (2, 'David Chen', 'Wind Ensemble, Jazz Band')]`

**Friendly response**: Yes! Maria Alvarez conducts Symphony Orchestra and Chamber Strings. David Chen conducts Wind Ensemble and Jazz Band.

Cross-domain gave the same correct answer as zero-shot.
