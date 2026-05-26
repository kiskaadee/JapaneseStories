# Japanese Glossary and Active recall review system: Architecture & Specification

## 1. High-Level Architecture

This was schemed after the classic modern web stack, utilizing a decoupled Client-Server model.

* **Frontend (Client):** A Single Page Application (SPA) using React or Vue. This allows for the snappy, app-like feel required for the "Lazy Search" and the "Review Game".

* **Backend (API):** FastAPI REST API. Handles business logic, SRS calculations, and proxies requests to external dictionaries.

* **Database:** PostgreSQL. Handles relational data (Users -> Collections -> Topics -> Terms) and complex full-text search queries.
* **Authentication:** Google OAuth 2.0 (handled via the backend using a library like `Authlib` or `FastAPI-Users`).

### Architecture Diagram

```text
[ Web Browser / Frontend SPA ]
       |             |
  (REST/JSON)    (OAuth Flow)
       |             |
[   FastAPI Backend Server   ] <---> [ External API (Jisho.org) ]
       |             |
[ PostgreSQL ]  [ Google Auth ]

```

---

## 2. Authentication Flow (Google OAuth)

Since you want minimal friction, Google Auth is ideal.

1. **User Clicks "Login with Google"** on the Frontend.
2. Frontend redirects to the FastAPI backend login route (`/auth/google/login`).
3. FastAPI redirects the user to Google's consent screen.
4. User approves, and Google redirects back to FastAPI (`/auth/google/callback`) with an authorization code.
5. FastAPI exchanges the code for the user's profile data, creates a User record in PostgreSQL (if they are new), and generates a secure **JWT (JSON Web Token)**.
6. FastAPI sends the JWT to the Frontend. The Frontend includes this JWT in the header of all future requests to prove identity.

---

## 3. Core User Flows

### Flow A: Adding a Term (The "Lazy Search")

This flow minimizes typing and friction.

```text
User Input: Types "tabe" in Katakana/Romaji input box.
   ↓
Frontend:   Sends debounce GET request -> /api/search?q=tabe
   ↓
Backend:    Queries Jisho.org API (or local cache).
            Formats top 3-5 results. Returns JSON.
   ↓
Frontend:   Displays dropdown of suggestions.
   ↓
User:       Clicks "食べる (to eat)".
   ↓
Frontend:   Auto-fills the 'Add Term' form (Word, Furigana, Meaning, POS).
   ↓
User:       Selects Collection/Topic. Modifies meaning if desired. Clicks "Save".
   ↓
Backend:    Saves to PostgreSQL under the user's ID. Initializes SRS tracking.

```

### Flow B: The Active Recall Review Session

This is the Pomodoro-style study loop.

```text
User:       Clicks "Review (15 Due)" on Dashboard.
   ↓
Backend:    Calculates terms where `next_review_date <= NOW()`.
            Returns a batch of up to 15 terms.
   ↓
Frontend:   Displays Term 1 (e.g., "Cloze Deletion" or "Meaning Match").
   ↓
User:       Answers the prompt. Clicks "Show Answer".
   ↓
Frontend:   Reveals correct answer. Shows grading buttons (Hard, Good, Easy).
   ↓
User:       Selects "Good".
   ↓
Backend:    Updates `practice_count`, `interval`, and `next_review_date`.
   ↓
Frontend:   Loads Term 2. (Repeats until batch is done).

```

---

## 4. UI / UX Sketches (Wireframes)

Here is a conceptual layout for the two most important screens in your application.

### Screen 1: The Dashboard (The Entry Point)

```text
=============================================================================
|  [Logo] Japanese Glossary                            [Search...]  [Profile] |
=============================================================================
|                                                                           |
|  👋 Welcome back! You have a 3-day streak.                                |
|                                                                           |
|  [🔥 REVIEW NOW (12 Terms Due) ] <-- Prominent Call to Action             |
|                                                                           |
|  -----------------------------------------------------------------------  |
|  | ADD NEW TERM                                                        |  |
|  | [ Input word, reading, or meaning... (Triggers Lazy Search) ]       |  |
|  -----------------------------------------------------------------------  |
|                                                                           |
|  📂 YOUR COLLECTIONS                                                      |
|  -------------------------      -------------------------                 |
|  | 📖 Genki Vol 1        |      | ✈️ Okinawa Trip        |  >> scroll >>   |
|  | 4 Topics, 120 Terms   |      | 2 Topics, 45 Terms    |                 |
|  -------------------------      -------------------------                 |
=============================================================================

```

### Screen 2: The Review Card (Active Recall Mode)

```text
=============================================================================
|  ⏳ 12:45 (Pomodoro)                                   Remaining: 4 / 12  |
=============================================================================
|                                                                           |
|                          [ Topic: Okinawa Food ]                          |
|                                                                           |
|                                                                           |
|                                  海葡萄                                   |
|                               (うみぶどう)                                |
|                                                                           |
|                        _______________________                            |
|                                                                           |
|  Select the correct meaning:                                              |
|                                                                           |
|  [ A: Seaweed ]     [ B: Sea Grapes ]     [ C: Fish ]     [ D: Salt ]     |
|                                                                           |
=============================================================================
(After Selection) -> UI reveals the answer and shows the SRS grading buttons:
           [ 🔴 HARD (< 1m) ]   [ 🟢 GOOD (2d) ]   [ 🔵 EASY (4d) ]

```

---

## 5. Spaced Repetition (SRS) Data Logic

To make the review game work, your `Term` model needs slightly different fields than we previously discussed. We should base this on a proven algorithm like **SuperMemo-2 (SM-2)** (which Anki uses).

We need to add these exact fields to your database:

1. **`interval` (int):** How many days until the next review.
2. **`ease_factor` (float):** A multiplier (default `2.5`). If they get it right easily, this goes up. If they fail, it goes down.
3. **`next_review_date` (datetime):** The exact timestamp when this term should appear in the queue again.

**The Backend Logic (Simplified SM-2):**
When a user clicks "Good":

* `new_interval = old_interval * ease_factor`
* `next_review_date = NOW() + new_interval`

When a user clicks "Hard" or gets it wrong:

* `interval = 1` (Reset back to 1 day)
* `ease_factor -= 0.15` (Make it show up more frequently in the future)
* `next_review_date = NOW() + 1 day`
