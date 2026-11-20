# D1 – Project Proposal (one page, due end of Week 9)

**Team:** see main README
**Track:** D – Cybersecurity
**Service:** Password Strength Checker

## Problem and users
Weak and reused passwords remain a leading cause of account compromise. Students and staff need a quick way to check whether a password is strong, but typing a password into an unknown website is itself a risk. Our service evaluates password strength **without ever storing the password**, and gives aggregate, anonymous statistics that an IT/security team could use for awareness campaigns.

**Users:** students and staff (check a password); the IT/security team (view anonymous statistics).

## Two components
1. **Web application (Flask):** scores the password on length, character variety and patterns, and checks it against a list of known common passwords.
2. **Data store (PostgreSQL):** holds hashes of a public common-password list for lookup, plus anonymous check results (score, length, rules passed). The password and its hash are never stored.

## Roles
_To be filled once assigned._

## Architecture sketch
See [`architecture.md`](architecture.md).
