import json, random

pairs = []
try:
    with open("library_dataset.jsonl", encoding="utf-8") as f:
        docs = [json.loads(l) for l in f]
except FileNotFoundError:
    print("library_dataset.jsonl not found! Please run export_dataset.py first.")
    docs = []

templates_by_category = {
    "books": [
        "Is there a book called {title}?",
        "Do you have any books about {title}?",
        "I need the textbook for {title}",
        "Can I borrow {title}?",
        "Where is the book {title} located?",
        "Is {title} available in the library?",
        "Show me information about {title}",
        "Who wrote {title}?",
        "Search for the book {title}",
        "Amake {title} boi ta dao",
        "{title} boi ta ki library e ache?",
        "CSE er library section e {title} boi kothay pabo?",
        "{title} textbook copy ache?",
        "I want to read {title}",
        "Find {title} in books list",
        "Give me the author details of {title}",
        "Who is the writer of {title}?",
        "{title} book availability check",
        "Borrowing policy for {title}"
    ],
    "faculty_notes": [
        "Where can I find notes on {title}?",
        "Lecture notes for {title}",
        "Download slides for {title}",
        "Do you have notes or material for {title}?",
        "Where is the study material for {title}?",
        "I need {title} class resources",
        "Teacher's slide or note of {title}",
        "{title} er lecture notes kothay?",
        "{title} er slide ba note pabo?",
        "Faculty slides on {title}",
        "Amake {title} lecture notes download link dao",
        "{title} class notes are available?",
        "{title} course content materials",
        "Slides for course {title}"
    ],
    "submissions": [
        "Status of my request for {title}",
        "When is {title} due back?",
        "Return deadline for {title}",
        "Is my submission for {title} complete?",
        "Did you receive my return of {title}?",
        "When do I need to return {title}?",
        "Due date of {title}",
        "{title} book return due kobe?",
        "{title} renewal schedule",
        "How many days left for {title}?",
        "Submit status for {title}",
        "Pending issue of {title}"
    ],
    "reviews": [
        "Review for {title}",
        "What do people think about {title}?",
        "Student comments on {title}",
        "Is {title} recommended?",
        "Rating or review for {title}",
        "{title} er reviews kemon?",
        "Feedback on the book {title}"
    ]
}

# Generic templates that apply to any category with a title
generic_templates = [
    "Details of {title}",
    "Information about {title}",
    "I want to know about {title}",
    "{title} somporke bolo",
    "Tell me about {title}",
    "Query regarding {title}"
]

for d in docs:
    cat = d.get("category")
    title = d.get("title", "")
    if not title:
        continue
        
    # 1. Add category-specific templates
    if cat in templates_by_category:
        for t in templates_by_category[cat]:
            pairs.append({"query": t.format(title=title), "passage": d["text"]})
            
    # 2. Add generic templates to guarantee query diversity
    for t in generic_templates:
        pairs.append({"query": t.format(title=title), "passage": d["text"]})

random.shuffle(pairs)
if pairs:
    with open("train_pairs.jsonl", "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"Generated {len(pairs)} training pairs")
else:
    print("No training pairs generated.")

