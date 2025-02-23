# Database Information
###### Just information regarding the DBs that I use

## Database Hosting
The database is hosted through **PebbleHost MYSQL**. It's called `customer_834000_DCBot1`.

### The tables I currently have:

---

#### **QuotesDB**  
*Used for the QOTD task in `bot.py`*  
```json
[
  {
    "id": "PRIMARY_KEY",
    "quotes": "TEXT"
  }
]
```
---
#### **UsedQuotesDB**  
*Used to hold used Quotes from QuotesDB to avoid dupes*  
```json
[
  {
    "id": "PRIMARY_KEY",
    "UsedQuotes": "TEXT"
  }
]
```
---

#### Users
*Table that holds user data for the AboutMe command*
```json
[
  {
    "user_discord_id": "BIGINT && PRIMARY_KEY", // pulled from API
    "user_name": "TINYTEXT", // pulled from API
    "user_gender": "TINYTEXT",
    "user_pronouns": "TINYTEXT",
    "user_age": "TINYINT",
    "user_date_of_birth": "DATE",
    "user_bio": "BIGTEXT", // Optional
    "user_joined_at": "DATE", // pulled from API
    "user_created_at": "DATE" // pulled from API
  }
]
```
---

#### **Christmas** (DEPRECATED)
*Previously used for Christmas related questions*
```json
[
  {
    "id": "PRIMARY_KEY",
    "questions": "TEXT"
  }
]
```
