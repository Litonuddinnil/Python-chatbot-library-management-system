import json
import random
import os

# Let's try to load library_dataset.jsonl
docs = []
if os.path.exists("library_dataset.jsonl"):
    with open("library_dataset.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    docs.append(json.loads(line))
                except Exception:
                    continue
else:
    # Fallback to importing rag_retriever directly
    try:
        from rag_retriever import gather_all_library_knowledge
        raw_docs = gather_all_library_knowledge()
        for d in raw_docs:
            docs.append({
                "text": d.page_content,
                "category": d.metadata.get("category"),
                "title": d.metadata.get("title", "")
            })
    except Exception as e:
        print(f"Could not load data from database: {e}")

qa_examples = []

# Hand-crafted high-priority general questions
general_examples = [
    {
        "question": "Library open thake kobe kobe?",
        "context": "Library open hours: Sunday to Thursday, 9:00 AM to 5:00 PM. Closed on Fridays, Saturdays, and public holidays.",
        "answer": "Amader library Sunday theke Thursday protidin shokal 9:00 AM theke bikal 5:00 PM porjonto khola thake. Friday, Saturday r public holidays te bondho thake."
    },
    {
        "question": "What are the library hours?",
        "context": "Library open hours: Sunday to Thursday, 9:00 AM to 5:00 PM. Closed on Fridays, Saturdays, and public holidays.",
        "answer": "The library is open from Sunday to Thursday, 9:00 AM to 5:00 PM. It is closed on Fridays, Saturdays, and official university/public holidays."
    },
    {
        "question": "Boi borrow korar rules ki?",
        "context": "Borrowing rules: Students can borrow up to 3 books at a time for a maximum duration of 14 days. Renewals can be done online once before the due date.",
        "answer": "Ekjon student ekbare shorbochcho 3 ti boi borrow korte parben 14 diner jonne. Due date er age online e ekbar renew kora jabe."
    },
    {
        "question": "How many books can I borrow at once?",
        "context": "Borrowing rules: Students can borrow up to 3 books at a time for a maximum duration of 14 days. Renewals can be done online once before the due date.",
        "answer": "You can borrow up to 3 books at a time for a maximum of 14 days."
    },
    {
        "question": "Boi return na korle fine koto?",
        "context": "Overdue fine policy: A fine of 10 Taka per week is charged for each day a book is kept past its due date.",
        "answer": "Boi return korar due date par hoye gele protidiner jonne 10 Taka kore fine/jorimana dite hobe."
    },
    {
        "question": "What is the late fee policy?",
        "context": "Overdue fine policy: A fine of 10 Taka per day is charged for each day a book is kept past its due date.",
        "answer": "The overdue fine is 10 BDT per day for each book kept past its return due date."
    },
    {
        "question": "Boi harai felle ki korte hobe?",
        "context": "Lost book policy: If a student loses a book, they must replace it with a new copy of the same edition or pay twice the current market price of the book.",
        "answer": "Boi haraye gele aponake shei boitir ekti notun copy replacement hishebe dite hobe athoba boitir market price er digun taka pay korte hobe."
    },
    {
        "question": "How to renew a borrowed book?",
        "context": "Renewal policy: Books can be renewed online through the student portal once, as long as the book has not been reserved by another student.",
        "answer": "You can renew your borrowed books online through your student portal once, provided no other student has reserved it."
    },
    {
        "question": "Can I reserve a book that is currently checked out?",
        "context": "Reservation policy: Yes, students can place a reservation request on checked-out books via the online system or library desk. You will be notified when it is returned.",
        "answer": "Yes, you can reserve checked-out books. Once the book is returned, you will receive a notification to collect it."
    },
    {
        "question": "Amake library er contact details dao",
        "context": "Library Contact Details: Email: library@university.edu, Phone: +88021234567, Location: 3rd Floor, Academic Building 2.",
        "answer": "Apni library contact korte paren Email: library@university.edu ba Phone: +88021234567 e. Location: Academic Building 2 er 3rd Floor."
    }
]

qa_examples.extend(general_examples)

# Templates to generate dynamic QA pairs for books
book_templates = [
    {
        "q": "Amake {title} boi ta somporke bolo",
        "a": "Boitir details: {text}. Boiti borrow korte library desk e check korun."
    },
    {
        "q": "{title} boi ta ki library e ache?",
        "a": "Ji, amader database onushare boiti library list e ache. Boitir details: {text}."
    },
    {
        "q": "CSE/Library section e {title} boi kothay pabo?",
        "a": "Boiti library shelves e department wise sorted thake. Specific records: {text}."
    },
    {
        "q": "{title} textbook copy ache?",
        "a": "Ji, {title} library collections e ache. Records output: {text}."
    },
    {
        "q": "{title} boi er writer ke?",
        "a": "Boitir search record state korche: {text}."
    },
    {
        "q": "Is there a book called {title}?",
        "a": "Yes, we have {title} in our collection. Here is the catalog entry: {text}"
    },
    {
        "q": "Do you have any books about {title}?",
        "a": "Yes! The system found this book: {text}"
    },
    {
        "q": "I need the book {title}",
        "a": "You can find {title} in the library catalog. Details: {text}"
    },
    {
        "q": "Can I borrow {title}?",
        "a": "Yes, {title} can be borrowed under standard policy. Details of the book: {text}"
    },
    {
        "q": "Where is the book {title} located?",
        "a": "{title} is shelved according to its department/category. Book record: {text}"
    },
    {
        "q": "Search for the book {title}",
        "a": "Searching records... Found: {text}"
    },
    {
        "q": "Who wrote {title}?",
        "a": "According to the catalog, the author information is within: {text}"
    },
    {
        "q": "Give me the description of {title}",
        "a": "Here is the summary/description of {title}: {text}"
    },
    {
        "q": "I want to read {title}",
        "a": "You are welcome to read it at our library or check it out. Catalog details: {text}"
    }
]

# Templates for faculty notes
notes_templates = [
    {
        "q": "{title} er lecture notes ba slide kothay pabo?",
        "a": "Ji, amader faculty notes repository check korun. Course material summary: {text}."
    },
    {
        "q": "{title} notes download link pabo?",
        "a": "Lecture slides and materials downloadable portal e peye jaben. Details: {text}."
    },
    {
        "q": "{title} course slide ache?",
        "a": "Ji, course material/notes records e high quality lecture slides ache. Info: {text}."
    },
    {
        "q": "Where can I find notes on {title}?",
        "a": "You can search or view them in the Faculty Notes module. Course details: {text}"
    },
    {
        "q": "Do you have study material for {title}?",
        "a": "Yes, study materials/slides for {title} are archived. Record details: {text}"
    },
    {
        "q": "Download slides for {title}",
        "a": "You can download them from the faculty resources. Note details: {text}"
    },
    {
        "q": "I need {title} class resources",
        "a": "The lecture slides and resources for this topic contain: {text}"
    },
    {
        "q": "Teacher's slide of {title}",
        "a": "Available in the faculty notes upload section. Detailed catalog: {text}"
    }
]

# Generate templates from database documents
for doc in docs:
    cat = doc.get("category")
    title = doc.get("title", "")
    text = doc.get("text", "")
    if not text:
        continue
    
    # Clean up text for the context/answer
    text_clean = text.strip().replace("\n", " ")
    
    if cat == "books" and title:
        for temp in book_templates:
            qa_examples.append({
                "question": temp["q"].format(title=title),
                "context": text_clean,
                "answer": temp["a"].format(title=title, text=text_clean)
            })
    elif cat == "faculty_notes" and title:
        for temp in notes_templates:
            qa_examples.append({
                "question": temp["q"].format(title=title),
                "context": text_clean,
                "answer": temp["a"].format(title=title, text=text_clean)
            })
    elif cat == "reviews":
        qa_examples.append({
            "question": "Student opinion or review about this book?",
            "context": text_clean,
            "answer": f"Here is what students say: {text_clean}"
        })
        qa_examples.append({
            "question": "Feedbacks check korun",
            "context": text_clean,
            "answer": f"Amader user review recorded: {text_clean}"
        })

# Shuffle to keep it well-distributed
random.shuffle(qa_examples)

# Write to qa_dataset.jsonl
with open("qa_dataset.jsonl", "w", encoding="utf-8") as f:
    for ex in qa_examples:
        prompt = f"Context: {ex['context']}\n\nQuestion: {ex['question']}\nAnswer:"
        f.write(json.dumps({"prompt": prompt, "response": ex["answer"]}, ensure_ascii=False) + "\n")

print(f"Generated {len(qa_examples)} QA examples to qa_dataset.jsonl")
