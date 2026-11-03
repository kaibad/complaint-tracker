# Documentation Guide for a Junior Developer

How to document a software project well, how to explain it, and the interview and written-test questions you are likely to face for the Junior Developer post.

This guide uses the Citizen Complaint Tracker API as the running example, so every technique here points to something real in your project.

---

## Contents

1. [Why documentation is part of the job](#1-why-documentation-is-part-of-the-job)
2. [The seven kinds of documentation](#2-the-seven-kinds-of-documentation)
3. [How to write a README](#3-how-to-write-a-readme)
4. [Code comments and docstrings](#4-code-comments-and-docstrings)
5. [Documenting an API](#5-documenting-an-api)
6. [Writing setup instructions that work](#6-writing-setup-instructions-that-work)
7. [Git: commits, branches and pull requests](#7-git-commits-branches-and-pull-requests)
8. [Issues and bug reports](#8-issues-and-bug-reports)
9. [Progress updates and raising blockers](#9-progress-updates-and-raising-blockers)
10. [Writing rules that make documentation good](#10-writing-rules-that-make-documentation-good)
11. [Pre-submission checklist](#11-pre-submission-checklist)
12. [Interview questions with model answers](#12-interview-questions-with-model-answers)
13. [Written test practice](#13-written-test-practice)
14. [Practice tasks for your 22 hours](#14-practice-tasks-for-your-22-hours)
15. [Presenting your project honestly](#15-presenting-your-project-honestly)

---

## 1. Why documentation is part of the job

The job post lists documentation as a required skill and as a named responsibility. Read how it appears:

| Responsibility in the post | What it means for documentation |
|---|---|
| "Update code comments, setup instructions and technical documentation for assigned work" | Whenever you change code, you also change the words that describe it. Work is not finished until the docs match. |
| "Use version control and issue tracking correctly" | Commit messages, branch names and issue descriptions are documentation that other people read. |
| "Provide clear progress updates and raise blockers early" | Short written updates are documentation of your work. |
| "Write basic automated tests" | Tests are executable documentation: they show how the code is supposed to behave. |
| "Fix reproducible defects" | You must be able to read a bug report, and write one, with exact steps to reproduce. |
| "Follow access, confidentiality and data-handling rules" | Documentation must never contain passwords, real citizen data or internal details that should not be shared. |

You will work under a senior developer with five mid-level developers around you. Nobody on a team of seven has time to answer the same question repeatedly. Good documentation is how a junior developer becomes useful quickly and visibly.

**The test of good documentation:** a competent stranger can set up, run, understand and safely change your project using only what you wrote.

---

## 2. The seven kinds of documentation

| # | Kind | Audience | Where it lives | Answers the question |
|---|------|----------|----------------|----------------------|
| 1 | README | Anyone opening the repository | `README.md` | What is this, and how do I run it? |
| 2 | Code comments and docstrings | The next developer reading the code | Inside the source files | Why is the code written this way? |
| 3 | API documentation | Developers calling the API | `/docs` plus the README | How do I call this, and what comes back? |
| 4 | Setup and troubleshooting notes | A new team member | README sections | Why is it not working on my machine? |
| 5 | Commit messages and pull requests | Reviewers and future maintainers | Git history | What changed, and why? |
| 6 | Issues and bug reports | The person fixing the problem | Issue tracker | What exactly is broken, and how do I see it? |
| 7 | Progress updates | Senior developer and project manager | Chat, email, stand-up | Where are you, and what is blocking you? |

Beginners usually write only the README. Employers notice when you do all seven.

---

## 3. How to write a README

A README is the front door of the project. Decide who is reading: a developer who knows Python but has never seen your project and wants to run it in five minutes.

### The structure that works

1. **Title and one-sentence description.** What the project is, in plain words.
2. **Stack.** The main technologies, on one line.
3. **Quick start.** The exact commands to install and run. Put this near the top.
4. **How it works.** Structure of the project and the reasoning behind it.
5. **Reference.** Endpoints, data model, configuration.
6. **Testing.** How to run the tests and what they cover.
7. **Troubleshooting.** The problems a newcomer will actually hit.
8. **Limitations and future work.** Honest and specific.

Open the project's `README.md` and compare it with this list. Every item is there, and you should be able to say why each part exists.

### Principles

- **Lead with what the reader needs first.** People decide in ten seconds whether to continue. The description and quick start come before the history and theory.
- **Every command must be copy-and-paste ready.** Put commands in code blocks and specify the language (`bash`, `json`, `python`).
- **Show real output.** The sample responses in the project README were captured from the running application, not typed from imagination. Invented examples drift away from the truth.
- **Explain decisions, not just facts.** "I used `PATCH` because the request changes part of the resource" teaches more than "uses PATCH".
- **State limitations openly.** A README that says "there is no authentication yet" earns more trust than one that hides it.
- **Use tables for comparisons and lists of fields.** Use prose for reasoning.
- **Keep one idea per paragraph.** Short paragraphs are easier to scan.
- **Use relative structure, not screenshots of text.** Text can be copied and searched; screenshots cannot.

### A reusable skeleton

```markdown
# Project Name

One sentence describing what it does and for whom.

**Stack:** Python, FastAPI, ...

## Quick Start
(prerequisites, install, run, first request)

## Project Structure
(folder tree, one line per file, and why it is organised this way)

## API Reference / Usage
(endpoints, parameters, example request and response)

## Testing
(how to run, what is covered)

## Troubleshooting
(symptom -> cause -> fix)

## Known Limitations and Future Work
```

### Common README mistakes

- Instructions that were never tested on a clean machine.
- Missing Python version or missing dependency list.
- Describing features that do not exist yet.
- Screenshots with no text explanation.
- Leaving template text such as "TODO" or "Lorem ipsum".
- Putting passwords, API keys or real personal data in examples.

---

## 4. Code comments and docstrings

### Comment the why, not the what

The code already says what it does. Comments should explain what the code cannot: the reason.

```python
# Bad: repeats the code
# increase skip by 10
skip += 10

# Good: explains a decision
# Closed complaints are final so that statistics built on them stay reliable.
if complaint.status in FINAL_STATUSES:
    raise ClosedComplaintError(...)
```

### Docstrings

A docstring is a string placed directly under a function, class or module definition. Tools and editors display it, and FastAPI shows route docstrings in `/docs`.

Write one short sentence in the imperative mood ("Return...", "Create...", "Raise...") that says what the function does and anything surprising about it.

```python
def update_status(db, complaint, data):
    """Change a complaint's status and remarks.

    Raises ClosedComplaintError if the complaint is already resolved or rejected.
    """
```

For a longer function, add what the arguments mean, what is returned and what errors can be raised.

### Other rules

- Use meaningful names first. `complaint_id` needs no comment; `x` does.
- Delete commented-out code. Git remembers old versions.
- Update comments when you change code. A wrong comment is worse than none.
- Use `TODO` comments only with an explanation, and track the real work in an issue.
- Use type hints (`def get(db: Session, complaint_id: int) -> Complaint | None`). They document the expected input and output and let tools catch mistakes.

---

## 5. Documenting an API

For every endpoint, a reader needs six things.

| Item | Example |
|------|---------|
| Method and URL | `PATCH /complaints/{id}/status` |
| Purpose | Change a complaint's status |
| Inputs (path, query, body) | Path `id`; body `status`, `remarks` |
| Example request | A complete JSON body or `curl` command |
| Example response | A complete JSON body |
| Possible errors | `400` closed complaint, `404` not found, `422` invalid body |

### Where each piece comes from in FastAPI

- **Type hints and Pydantic models** document the inputs and outputs and are shown automatically in `/docs`.
- **Docstrings** on route functions become the endpoint descriptions.
- **`tags`** group endpoints in `/docs`.
- **The README** adds what `/docs` does not: the reasoning, the lifecycle, the status-code policy and real examples.

Document error responses as carefully as success responses. A developer integrating with your API will spend most of their time handling the errors.

---

## 6. Writing setup instructions that work

Untested instructions are the most common documentation failure. Follow this routine.

1. Delete your virtual environment and the database file.
2. Clone the repository into a new folder, or ask a friend to try.
3. Follow your README exactly, line by line, doing nothing that is not written down.
4. Every time you have to improvise, add the missing step to the README.
5. Repeat until it works with no improvisation.

Also record:

- The Python version.
- The operating system differences (for example, the Windows command for activating the virtual environment).
- Any environment variable or configuration file needed. Provide an example file such as `.env.example` with fake values. Never commit the real one.

---

## 7. Git: commits, branches and pull requests

Version control history is documentation. A reviewer reads your commit messages to understand your work.

### Commit messages

Use a short summary line in the imperative mood, under about 70 characters, optionally followed by a blank line and a longer explanation.

```
Add pagination to complaint listing

Limit is capped at 100 to avoid very large responses.
Default is 20. Results are ordered newest first.
```

| Weak | Strong |
|------|--------|
| `update` | `Reject status changes on closed complaints` |
| `fix bug` | `Fix 500 error when phone is an empty string` |
| `changes` | `Add tests for category filter` |

Rules of thumb:

- One logical change per commit.
- The summary completes the sentence "If applied, this commit will..."
- Commit often in small steps rather than once at the end. A history of 15 meaningful commits shows how you work; one commit called "final" shows nothing.

You can use a prefix convention such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:` (called Conventional Commits) if your team uses it. Follow whatever the team already does.

### Branches

Do your work on a branch, not directly on `main`.

```bash
git checkout -b feature/complaint-search
# work, commit
git push -u origin feature/complaint-search
```

Name branches by purpose: `feature/...`, `fix/...`, `docs/...`.

### Pull request description

A reviewer should understand the change without opening every file.

```markdown
## What
Adds keyword search to GET /complaints via a new `q` parameter.

## Why
Officers need to find complaints without scrolling through pages.

## How to test
1. Run `pytest`
2. Create a complaint titled "Water leak"
3. GET /complaints?q=leak -> returns that complaint

## Notes
Search is case-insensitive and matches title and description.
```

### Useful commands you should be able to explain

```bash
git status          # what has changed
git add <file>      # stage changes
git commit -m "..."  # record staged changes
git log --oneline   # short history
git diff            # unstaged changes
git pull            # fetch and merge remote changes
git stash           # temporarily set work aside
git revert <hash>   # undo a commit by creating a new one
```

---

## 8. Issues and bug reports

The job says you will "fix reproducible defects". Reproducible means someone can follow steps and see the problem. A good bug report makes that possible.

### Bug report template

```markdown
**Title:** Updating a resolved complaint returns 500 instead of 400

**Environment:** Python 3.12, commit a1b2c3d

**Steps to reproduce**
1. POST /complaints (valid body)
2. PATCH /complaints/1/status with {"status": "resolved"}
3. PATCH /complaints/1/status with {"status": "in_progress"}

**Expected result:** 400 with "Complaint is already resolved"
**Actual result:** 500 Internal Server Error

**Evidence:** error log or response body pasted here
```

### Fixing a bug in the right order

1. **Reproduce it.** If you cannot reproduce it, you cannot know you fixed it.
2. **Write a failing test** that captures the bug.
3. **Find the cause** with the traceback, print statements or a debugger.
4. **Fix the code** with the smallest change that works.
5. **Run all the tests**, not only the new one.
6. **Commit** with a message that references the issue.

### Reading a traceback

Read from the bottom up. The last line names the error and the message. The lines above it show where it happened. Find the first line that points to your own code, not to a library.

---

## 9. Progress updates and raising blockers

Your senior developer and the project manager cannot see inside your head. A short, regular update solves that.

### A simple daily format

```
Done:     Added status filter and tests for GET /complaints.
Next:     Add keyword search.
Blocked:  Unsure whether search should include the remarks field. Need a decision.
```

### Raising a blocker well

Raise it early. A blocker mentioned after two days of silence has already cost the team time.

1. State what you are trying to do.
2. State what you already tried.
3. State exactly what you need (a decision, access, a review, an explanation).

```
I'm adding search to the complaints endpoint. I tried matching on title only and
it works, but I'm not sure if remarks should be searched too. Could you confirm
which behaviour is wanted? I'll continue with the title-only version meanwhile.
```

This shows effort, makes the question easy to answer, and keeps you moving.

---

## 10. Writing rules that make documentation good

1. **Know your reader.** Write for someone intelligent who does not know your project.
2. **Be specific.** "Run `pytest -v` from the project root" beats "run the tests".
3. **Use plain words and short sentences.** Technical writing is judged on clarity, not on how impressive it sounds.
4. **Use active voice.** "The route returns 404" rather than "404 is returned by the route".
5. **Be consistent.** Choose one name for each concept ("complaint", not sometimes "ticket" or "case") and one format for each kind of example.
6. **Show, then explain.** Give a code example, then say what it demonstrates.
7. **Keep it current.** Update documentation in the same commit as the code change.
8. **Protect confidential data.** Never put real names, phone numbers, passwords, tokens or internal addresses in documentation or examples. Use clearly fake values.
9. **Proofread.** Spelling errors in documentation suggest carelessness in code.
10. **Delete what is no longer true.** Outdated documentation misleads.

---

## 11. Pre-submission checklist

**Project**

- [ ] The project runs from a clean clone following only the README
- [ ] `pytest` passes
- [ ] No secrets, `.venv`, `__pycache__` or database file in the repository
- [ ] `.gitignore` and `requirements.txt` are present and correct

**Documentation**

- [ ] README has a description, stack, quick start, structure, API reference, testing, troubleshooting and limitations
- [ ] Every endpoint has a documented request, response and error codes
- [ ] Every route and function has a docstring
- [ ] Examples use fake data
- [ ] No placeholder text remains

**Git**

- [ ] At least 10 meaningful commits with clear messages
- [ ] Repository is public (or accessible to the reviewer) and the link works

**You**

- [ ] You can explain every file and every function
- [ ] You can answer the questions in section 12 in your own words

---

## 12. Interview questions with model answers

The answers below are short models. Learn the ideas, then say them in your own words, using examples from your own project. Interviewers can tell memorised answers from understood ones.

### A. Your project

**1. Walk me through your project.**
It is a REST API built with FastAPI where citizens file public-service complaints and officers move them through pending, in progress, resolved or rejected. It has create, read, list, update-status and delete endpoints, filtering and pagination, input validation and a statistics endpoint. The code is split into routes, business logic, models and schemas, and it has 12 automated tests.

**2. Why did you choose this project?**
It matches the kind of systems a government office actually runs: public requests, status tracking and records that must stay reliable. It was also small enough for me to understand completely while covering validation, error handling, testing and documentation.

**3. What was the hardest part?**
Name something true for you. For example: understanding how dependency injection supplies a database session, or how to make the tests use a separate database. Describe what confused you, how you investigated it, and what you learned.

**4. What would you improve with more time?**
Authentication with citizen and officer roles, a status-history table, database migrations with Alembic, soft delete, PostgreSQL and automated tests on every push.

**5. Why did you separate `crud.py` from `main.py`?**
So that business rules and database access do not depend on the web framework. The rule that closed complaints cannot be changed lives in `crud.py` and raises an exception. `main.py` converts that into a 400 response. This makes the logic easier to test and change.

**6. Why do you have both `models.py` and `schemas.py`?**
`models.py` describes how data is stored in the database. `schemas.py` describes what the API accepts and returns. They differ: for example, the client does not send `id` or `status` when creating a complaint, but the database stores them. Keeping them separate lets the API and the database change independently.

### B. Python

**7. What is the difference between a list and a tuple?**
A list is mutable (can be changed after creation); a tuple is immutable. Tuples can be used as dictionary keys and signal data that should not change.

**8. What is a dictionary?**
A collection of key-value pairs with fast lookup by key. Keys must be hashable, such as strings, numbers or tuples.

**9. What is a virtual environment and why use one?**
An isolated folder with its own Python packages. It keeps each project's dependencies separate so that versions do not conflict.

**10. What are type hints?**
Annotations such as `def get(id: int) -> str | None`. Python does not enforce them at run time, but editors and tools use them to catch mistakes, and FastAPI and Pydantic use them to validate data.

**11. What is a decorator?**
A function that wraps another function to add behaviour. `@app.get("/complaints")` registers the function below it as the handler for that URL.

**12. What is a generator, and where did you use one?**
A function that uses `yield` to produce values one at a time. `get_db` uses `yield` so FastAPI can give a session to the route and run the cleanup code after the request finishes.

**13. What does `with` do?**
It sets up a resource and guarantees cleanup afterwards, such as closing a file, even if an error occurs.

**14. What is the difference between `==` and `is`?**
`==` compares values; `is` checks whether two names refer to the same object. Use `is None` to compare with `None`.

**15. How does exception handling work?**
Code that might fail goes in `try`; the `except` block handles a specific error; `finally` runs regardless. In my project `crud.py` raises `ClosedComplaintError` and `main.py` catches it and returns a 400.

**16. What is a mutable default argument, and why is it a bug?**
`def f(items=[])` creates the list once, and every call shares it. Use `items=None` and create a new list inside the function.

### C. APIs and HTTP

**17. What is a REST API?**
An API that uses HTTP methods on resources identified by URLs: GET reads, POST creates, PUT or PATCH updates, DELETE removes. It is stateless, meaning each request carries everything needed to process it, and it usually exchanges JSON.

**18. Explain the common HTTP methods.**
GET retrieves data and changes nothing. POST creates a resource. PUT replaces a resource entirely. PATCH changes part of a resource. DELETE removes it.

**19. What is the difference between PUT and PATCH?**
PUT sends the complete resource to replace the existing one. PATCH sends only the fields to change. I used PATCH for the status update because only the status and remarks change.

**20. Which status codes do you know and when do you use them?**
200 success, 201 created, 204 success with no body, 400 bad request, 401 not authenticated, 403 not allowed, 404 not found, 422 validation failed, 500 server error.

**21. What is the difference between 400 and 422?**
In my project, 422 means the request does not match the expected shape (a field is missing or invalid). 400 means the request is valid in shape but not allowed given the current data, such as updating a closed complaint.

**22. What is JSON?**
A text format for structured data made of objects (key-value pairs), arrays, strings, numbers, booleans and null. Almost every web API uses it.

**23. What is the difference between a path parameter and a query parameter?**
A path parameter identifies a specific resource: `/complaints/5`. A query parameter filters or modifies a request: `/complaints?status=pending`.

**24. What does idempotent mean?**
Repeating the same request gives the same result as sending it once. GET, PUT and DELETE are idempotent. POST is not, because repeating it creates another resource.

**25. What is pagination and why is it needed?**
Returning data in pages using `skip` and `limit`. Without it a request for a large table could return huge responses, slow the server and overload the client.

**26. What is the difference between authentication and authorisation?**
Authentication checks who you are. Authorisation checks what you are allowed to do. My project has neither yet, and I would add both before real use.

### D. FastAPI and Pydantic

**27. Why FastAPI?**
It validates requests automatically from type hints, generates interactive documentation, and needs little boilerplate.

**28. What does Pydantic do?**
It defines data models with types and rules, validates incoming data against them and returns clear errors when the data is wrong.

**29. What is dependency injection?**
Instead of a function creating what it needs, the framework supplies it. `Depends(get_db)` gives each route a database session, which also lets tests substitute a different database.

**30. What does `response_model` do?**
It tells FastAPI the shape of the response. FastAPI filters the output to match it and documents it in `/docs`.

**31. What is the difference between `def` and `async def` routes?**
`async def` lets the server handle other requests while waiting on slow operations such as network calls, if the code inside uses `await`. I used plain `def` because my database calls are synchronous, and FastAPI runs those routes in a thread pool.

### E. Databases and SQL

**32. What is an ORM?**
Object-Relational Mapper. It lets you work with database rows as Python objects instead of writing raw SQL. SQLAlchemy is one.

**33. What is a primary key?**
A column whose value uniquely identifies each row. In my project it is `id`.

**34. What is SQL injection and how is it prevented?**
An attack where user input is inserted into a SQL string and changes the query. It is prevented by using parameterised queries, which SQLAlchemy does, and by never building SQL with string concatenation.

**35. What does an index do?**
It speeds up lookups on a column at the cost of extra storage and slower writes. I indexed `status` and `category` because they are used for filtering.

**36. What is the difference between `DELETE` and `DROP`?**
`DELETE` removes rows from a table. `DROP` removes the table itself.

**37. What does `GROUP BY` do?**
It groups rows that share a value and lets you aggregate each group, for example counting complaints per status.

### F. Testing

**38. Why write tests?**
They prove the code does what it should, catch regressions when something changes, and describe the expected behaviour. They give confidence to change code safely.

**39. What is a unit test, and how does it differ from an integration test?**
A unit test checks one small piece in isolation. An integration test checks that several parts work together. My tests call the API endpoints with a test database, so they sit between the two.

**40. What is a fixture?**
Reusable set-up code that tests receive as an argument. My `client` fixture creates a clean in-memory database and a test client for each test.

**41. Why do your tests use an in-memory database?**
It is fast, isolated and leaves no data behind, and it can never damage real data.

**42. What makes a good test?**
It checks one behaviour, has a name that describes it, does not depend on other tests, and fails for a clear reason.

**43. What did you test and what did you not?**
I tested success paths, validation errors, missing records, filtering, pagination and the closed-complaint rule. I did not test authentication because it does not exist yet, and I did not test performance with large amounts of data.

### G. Git

**44. What is Git and why is it used?**
A distributed version control system. It records the history of changes, allows several people to work in parallel, and lets you return to an earlier state.

**45. What is the difference between Git and GitHub?**
Git is the tool on your machine. GitHub is a hosting service for Git repositories that adds collaboration features such as pull requests and issues.

**46. What is a branch and why use one?**
An independent line of development. Branches let you work on a feature without disturbing the stable code on `main`.

**47. What is a merge conflict and how do you resolve it?**
It happens when two changes touch the same lines and Git cannot combine them automatically. You open the file, choose or combine the correct content, remove the conflict markers, then add and commit.

**48. What is the difference between `git fetch` and `git pull`?**
`fetch` downloads remote changes without applying them. `pull` fetches and then merges them into the current branch.

**49. What is the difference between `git revert` and `git reset`?**
`revert` creates a new commit that undoes an earlier one, so history is preserved. `reset` moves the branch pointer and can discard history, so it should not be used on shared branches.

**50. What is a pull request?**
A request to merge your branch into another, which lets teammates review the code and discuss it first.

### H. Debugging

**51. How do you debug a problem?**
I reproduce it reliably, read the error message and traceback from the bottom up, narrow down where the wrong value appears using print statements or a debugger, form a hypothesis, test it, fix the smallest thing, and then add a test so it cannot return.

**52. What do you do when you are stuck?**
I spend a fixed, reasonable time on it first. I write down what I expect, what happens, and what I tried. If I am still stuck, I ask my senior developer with that summary, so the question is easy to answer, and I tell them early instead of waiting.

### I. Documentation

**53. Why does documentation matter?**
It lets other people use and maintain the work without asking me, it speeds up onboarding, and it records the reasons behind decisions that code alone cannot show.

**54. What goes in a good README?**
A description, the stack, quick-start commands, project structure, usage or API reference, testing instructions, troubleshooting and known limitations.

**55. How do you keep documentation up to date?**
I update it in the same commit as the code change, and I treat a pull request as incomplete if the related documentation is wrong.

**56. What is the difference between a code comment and a docstring?**
A comment explains a specific line or decision and is ignored by Python. A docstring describes what a function, class or module does and is available to tools and to `help()`.

**57. How would you document a change you just made?**
Update the docstring and comments, adjust the README or API reference if behaviour changed, write a clear commit message and a pull request description with how to test it.

### J. Security and data handling

**58. How do you handle sensitive data?**
I collect only what is needed, keep real data out of the repository and documentation, do not log or hard-code secrets, restrict access to people who need it, and follow the organisation's rules on confidentiality.

**59. Where should passwords and API keys be stored?**
In environment variables or a secrets manager, never in the source code or Git. A `.env.example` file with fake values documents what is needed.

**60. What security gaps does your project have?**
There is no authentication or authorisation, phone numbers are stored and returned in plain text, and there is no rate limiting or HTTPS configuration. I documented these in the README.

### K. Teamwork and behaviour

**61. How do you respond to code review feedback?**
I read it carefully, ask if something is unclear, apply the changes, and learn the pattern so I do not repeat the mistake. Reviews are how I improve the fastest.

**62. How do you manage your time on several tasks?**
I list them, confirm priorities with my senior developer, start with the most important or blocking one, and give regular updates.

**63. Describe a time you learned something quickly.**
Use a true example. Your DevOps training and internship, or this project, are good sources. Use the structure: situation, what you did, result, what you learned.

**64. Why do you want this job?**
Give a genuine answer. For example: you want to grow as a developer in a structured team, learn from senior engineers, and contribute to systems that serve the public.

**65. Where do you see yourself in two years?**
The post is a two-year term. A good answer shows commitment to growing within it: taking on larger components, reviewing others' code, and becoming a dependable mid-level developer.

### L. Scenario questions

**66. A reviewer says your function has no validation. What do you do?**
Ask what inputs concern them, add validation (for example Pydantic rules), add tests for the invalid cases, and update the documentation.

**67. You find a bug in a teammate's code. What do you do?**
Reproduce it, write a clear bug report with steps, expected and actual results, and share it respectfully with them or raise an issue. I do not fix it silently or criticise them publicly.

**68. Your deadline is tomorrow but the task will take two more days. What do you do?**
Tell my senior developer immediately, explain what is done, what remains and why, and propose options such as reducing scope or extending the date.

**69. You are asked to use a technology you do not know.**
I say honestly that I have not used it, read the official documentation, build a small example, and ask for guidance on conventions. I ask for review of my first piece of work.

**70. You accidentally committed a password to Git.**
I tell my senior developer immediately, change the password straight away because it must be treated as exposed, remove it from the repository, and add the file to `.gitignore`. Deleting it in a later commit is not enough because it remains in the history.

---

## 13. Written test practice

Government and public-sector written tests usually mix short theory questions, small coding tasks and tasks that check your writing. Try each question first, then read the answer.

### Part 1: Short theory

1. Write the HTTP status code for each: resource created; resource not found; invalid input; server error; success with no content.
2. List four HTTP methods and one use of each.
3. Explain the difference between a list and a tuple in two sentences.
4. State two benefits of automated tests.
5. What is the purpose of `.gitignore`?

<details>
<summary>Answers</summary>

1. 201; 404; 422 (or 400); 500; 204.
2. GET reads data; POST creates; PATCH or PUT updates; DELETE removes.
3. A list is mutable, so its contents can change after creation. A tuple is immutable and cannot be changed, which makes it safe as a dictionary key.
4. They catch regressions early, and they document expected behaviour and make changes safer.
5. It lists files and folders Git should not track, such as virtual environments, caches, secrets and database files.

</details>

### Part 2: Read and predict

**Question A.** What does this print?

```python
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))
print(add_item("b"))
```

**Question B.** What does this print?

```python
numbers = [1, 2, 3, 4, 5, 6]
print([n * 2 for n in numbers if n % 2 == 0])
```

**Question C.** What is the problem?

```python
if user_input == None:
    print("empty")
```

<details>
<summary>Answers</summary>

A. `['a']` and then `['a', 'b']`. The default list is created once and shared between calls. The fix is `items=None`, then `if items is None: items = []`.

B. `[4, 8, 12]`.

C. `None` should be compared with `is`, not `==`: `if user_input is None:`.

</details>

### Part 3: Find the bug

```python
def get_page(items, page, page_size):
    start = page * page_size
    end = start + page_size
    return items[start:end]

# The user asks for page 1 and expects the first 10 items
print(get_page(list(range(100)), 1, 10))
```

<details>
<summary>Answer</summary>

Pages are numbered from 1, but the code treats the first page as 0, so page 1 returns items 10 to 19. The fix is `start = (page - 1) * page_size`. This is an off-by-one error. A test would be: `get_page(list(range(100)), 1, 10) == list(range(10))`.

</details>

### Part 4: Write code

**Task 1.** Write a function `is_valid_phone(phone)` that returns `True` if the string contains 7 to 15 digits and nothing else.

**Task 2.** Write two pytest tests for it.

**Task 3.** Write a FastAPI route `GET /health` that returns `{"status": "ok"}`.

**Task 4.** Write a SQL query that counts complaints per status.

<details>
<summary>Answers</summary>

```python
# Task 1
def is_valid_phone(phone: str) -> bool:
    """Return True if phone is 7 to 15 digits and nothing else."""
    return phone.isdigit() and 7 <= len(phone) <= 15

# Task 2
def test_valid_phone():
    assert is_valid_phone("9800000000") is True

def test_invalid_phone():
    assert is_valid_phone("98-000") is False
    assert is_valid_phone("") is False

# Task 3
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

```sql
-- Task 4
SELECT status, COUNT(*) AS total
FROM complaints
GROUP BY status;
```

</details>

### Part 5: Git scenarios

1. Write the commands to create a branch called `fix/phone-validation`, commit a change, and push it.
2. You committed to the wrong branch. What are your options?
3. Two people edited the same line. What happens, and what do you do?

<details>
<summary>Answers</summary>

1.
```bash
git checkout -b fix/phone-validation
git add .
git commit -m "Reject phone numbers containing letters"
git push -u origin fix/phone-validation
```
2. If the commit is not pushed, create the correct branch from there, move to it, then reset the wrong branch back, or use `git cherry-pick` to copy the commit to the right branch. If it is already pushed and shared, use `git revert` on the wrong branch rather than rewriting history.
3. Git reports a merge conflict and marks the file. Open it, decide the correct final content, delete the conflict markers, run the tests, then `git add` and commit.

</details>

### Part 6: Writing tasks

Written tests for this post will almost certainly ask you to write something, because documentation is a required skill.

**Task 1.** Write a bug report for this problem: when a user submits a complaint with a phone number containing letters, the API crashes.

**Task 2.** Write a commit message for adding a status filter to the list endpoint.

**Task 3.** Write a progress update for a day when you finished two tasks and are blocked on a third.

**Task 4.** Write setup instructions for a new developer in five steps or fewer.

<details>
<summary>Model answers</summary>

**Task 1**
```
Title: Complaint creation fails when phone contains letters

Steps to reproduce:
1. POST /complaints with "phone": "98abc00000" and otherwise valid data

Expected: 422 with a message that phone must contain digits only
Actual: 500 Internal Server Error

Notes: occurs on every request with non-digit characters
```

**Task 2**
```
Add status filter to GET /complaints

Allows officers to list only pending, in_progress, resolved or
rejected complaints. Includes a test for the filter.
```

**Task 3**
```
Done: Added the category filter and wrote tests for it. Updated the README
API table.
Done: Fixed the 404 response for unknown ids.
Blocked: Keyword search. I need to know whether remarks should be searched
as well. I will start with title only and adjust once confirmed.
```

**Task 4**
```
1. Install Python 3.10 or newer.
2. Clone the repository and open the project folder.
3. Create and activate a virtual environment, then run
   pip install -r requirements.txt
4. Start the server with uvicorn app.main:app --reload
5. Open http://127.0.0.1:8000/docs and run pytest to check everything works.
```

</details>

### Part 7: Explain in your own words (practise writing 4 to 6 sentences)

- Explain REST to someone who has never programmed.
- Explain why we write tests.
- Explain why you would never commit a password.
- Explain what your project does and who would use it.

Good written answers state the idea in the first sentence, add one concrete example, and avoid unexplained jargon.

---

## 14. Practice tasks for your 22 hours

Do these in order. Each builds a skill the post asks for.

1. **Run and break the project (1 hour).** Send invalid requests on purpose and read each error. Learn what each status code looks like.
2. **Trace one request (1 hour).** Pick `PATCH /complaints/{id}/status`. Follow it from `main.py` to `crud.py` to the database and back, writing down every function it touches.
3. **Test the README (1 hour).** Follow the setup instructions on a clean copy and fix anything unclear.
4. **Add three tests (2 hours).** Status filter, empty `citizen_name`, `updated_at` changes after an update. Make one fail first on purpose and watch the message.
5. **Add one feature yourself (3 hours).** Keyword search is a good choice. Use a branch, small commits, tests and a documentation update. Treat it as a real task from your senior developer.
6. **Write a bug report and fix it (1 hour).** Introduce a small bug, write the report in the template, reproduce it, write a failing test, fix it, commit.
7. **Update the README (1 hour).** Document your feature in the API table, add an example, and update the test list.
8. **Practise the answers aloud (3 hours).** Say questions 1 to 6 and 17 to 26 out loud without notes. Record yourself if you can.
9. **Do the written practice (2 hours).** Parts 1 to 6 of section 13 with a timer and no notes.

---

## 15. Presenting your project honestly

Be clear about what is yours.

- You received a working starting point, and the value you add is in understanding it, extending it and documenting it. Make your own changes visible in your commits: a new feature, new tests and an improved README.
- If an interviewer asks "Did you write this yourself?", the safe answer is the true one. Say which parts you built, which you started from, what you learned, and how you extended it. An honest answer with real understanding is stronger than a claim you cannot support.
- Never describe a feature that does not exist. State the limitations yourself before you are asked.
- You will probably be asked to change something live or explain a function on screen. This is why section 14 requires you to trace the code and add a feature on your own.

### A 60-second summary to adapt

> I built a REST API with FastAPI for tracking public-service complaints. Citizens file a complaint and officers move it through pending, in progress, resolved or rejected. I separated the routes, the business rules and the data layer, validated all input with Pydantic, and wrote automated tests using a separate in-memory database. I added [your feature] myself. I documented the project with a full README, docstrings and a troubleshooting section. The main gap is authentication, which I would add next.

Replace the bracket with something you really did. Practise until it sounds like you.

---

*Finish by re-reading the project README one more time, as if you were the interviewer. Any sentence you cannot explain, study until you can.*
