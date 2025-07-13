"""
Basic dataset of words and responses for the Naira chatbot, specialized for IT students.
"""

import random
import re

# IT Subjects with their codes
IT_SUBJECTS = {
    "IT01": {
        "name": "Programming Fundamentals",
        "topics": [
            "Variables and Data Types",
            "Control Structures",
            "Functions and Methods",
            "Object-Oriented Programming",
            "Basic Algorithms"
        ],
        "resources": [
            "Python Documentation",
            "Java Tutorial for Beginners",
            "C++ Reference Guide"
        ],
        "common_questions": {
            "what is a variable": "A variable is a container for storing data values. Think of it like a labeled box where you can store different types of information.",
            "explain loops": "Loops are control structures that repeat a block of code. Common types are for loops (iterate over a sequence) and while loops (continue while a condition is true).",
            "what is oop": "Object-Oriented Programming (OOP) is a programming paradigm based on 'objects' containing data and code. The main concepts are classes, objects, inheritance, and polymorphism."
        }
    },
    "IT02": {
        "name": "Database Management",
        "topics": [
            "SQL Fundamentals",
            "Database Design",
            "Normalization",
            "Query Optimization",
            "Database Security"
        ],
        "resources": [
            "MySQL Documentation",
            "PostgreSQL Tutorials",
            "Database Design Best Practices"
        ],
        "common_questions": {
            "what is sql": "SQL (Structured Query Language) is a standard language for managing and manipulating relational databases.",
            "explain joins": "Joins combine rows from two or more tables based on a related column. Common types are INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN.",
            "what is normalization": "Normalization is the process of organizing data to reduce redundancy and improve data integrity through a series of normal forms."
        }
    },
    "IT03": {
        "name": "Web Development",
        "topics": [
            "HTML5 & CSS3",
            "JavaScript",
            "Frontend Frameworks",
            "Backend Development",
            "RESTful APIs"
        ],
        "resources": [
            "MDN Web Docs",
            "W3Schools Tutorials",
            "React Documentation"
        ],
        "common_questions": {
            "what is html": "HTML (HyperText Markup Language) is the standard markup language for creating web pages and web applications.",
            "explain css": "CSS (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML.",
            "what is api": "API (Application Programming Interface) allows different software applications to communicate with each other."
        }
    },
    "IT04": {
        "name": "Cybersecurity",
        "topics": [
            "Network Security",
            "Cryptography",
            "Security Protocols",
            "Ethical Hacking",
            "Security Auditing"
        ],
        "resources": [
            "OWASP Guidelines",
            "Cybersecurity Best Practices",
            "Network Security Fundamentals"
        ],
        "common_questions": {
            "what is encryption": "Encryption is the process of converting information into a code to prevent unauthorized access.",
            "explain firewall": "A firewall is a network security device that monitors and filters incoming and outgoing network traffic.",
            "what is vulnerability": "A vulnerability is a weakness in a system that could be exploited by threats to gain unauthorized access."
        }
    },
    "IT05": {
        "name": "Cloud Computing",
        "topics": [
            "Cloud Services",
            "Virtualization",
            "Cloud Security",
            "Deployment Models",
            "Cloud Platforms"
        ],
        "resources": [
            "AWS Documentation",
            "Azure Learning Path",
            "Google Cloud Guides"
        ],
        "common_questions": {
            "what is cloud": "Cloud computing is the delivery of computing services over the internet, including servers, storage, databases, and software.",
            "explain saas": "SaaS (Software as a Service) is a software distribution model where applications are hosted by a provider and made available to customers over the internet.",
            "what is scaling": "Scaling is the ability to handle growing amounts of work by adding resources to the system."
        }
    },
    "IT06": {
        "name": "Artificial Intelligence",
        "topics": [
            "Machine Learning",
            "Neural Networks",
            "Natural Language Processing",
            "Computer Vision",
            "AI Ethics"
        ],
        "resources": [
            "TensorFlow Documentation",
            "PyTorch Tutorials",
            "AI Ethics Guidelines"
        ],
        "common_questions": {
            "what is ml": "Machine Learning is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
            "explain neural network": "A neural network is a computing system inspired by biological neural networks, designed to recognize patterns in data.",
            "what is nlp": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret, and manipulate human language."
        }
    }
}

def get_subject_info(subject_code):
    """Get information about a specific IT subject."""
    if subject_code in IT_SUBJECTS:
        return IT_SUBJECTS[subject_code]
    return None

def get_subject_topics(subject_code):
    """Get topics for a specific IT subject."""
    subject = get_subject_info(subject_code)
    if subject:
        return subject["topics"]
    return None

def get_subject_resources(subject_code):
    """Get learning resources for a specific IT subject."""
    subject = get_subject_info(subject_code)
    if subject:
        return subject["resources"]
    return None

def get_subject_question_answer(subject_code, question):
    """Get answer to a common question about a specific IT subject."""
    subject = get_subject_info(subject_code)
    if subject and question.lower() in subject["common_questions"]:
        return subject["common_questions"][question.lower()]
    return None

STUDY_TIPS = {
    "general": [
        "Break your study sessions into 25-minute chunks with 5-minute breaks",
        "Find a quiet, well-lit place to study",
        "Stay hydrated and take regular breaks",
        "Review your notes within 24 hours of taking them",
        "Teach the material to someone else to better understand it"
    ],
    "programming": [
        "Practice coding every day, even if just for 30 minutes",
        "Work on real projects to apply what you learn",
        "Use version control (like Git) for your code",
        "Read and understand others' code",
        "Debug systematically using print statements or a debugger"
    ],
    "database": [
        "Practice writing SQL queries regularly",
        "Design databases starting with requirements",
        "Learn to read and create ERD diagrams",
        "Practice database normalization",
        "Use sample databases for learning"
    ],
    "web_development": [
        "Build responsive designs from the start",
        "Test your websites across different browsers",
        "Learn to use browser developer tools",
        "Keep up with web standards and best practices",
        "Practice both frontend and backend development"
    ]
}

greetings_input = ["hi", "hello", "hey", "greetings", "hi there", "hello there", "hey there"]
greetings_response = [
    "Hello! I'm Naira, your educational assistant. How can I help you today?",
    "Hi there! How can I support your learning today?",
    "Welcome! What would you like to learn or work on?",
    "Hello! Need help with a subject, study tips, or organizing your tasks? Just ask!"
]

motivation_responses = [
    "Remember, every expert was once a beginner. Keep going!",
    "Stay positive and keep pushing forward—you can do it!",
    "Learning is a journey. Celebrate your progress!",
    "Don't give up. Every step you take brings you closer to your goal."
]

greeting_message = (
    "Hello! I'm Naira, your study assistant. How can I help you today? You can ask me about:\n"
    "• Study techniques\n"
    "• Time management\n"
    "• Exam preparation\n"
    "• Setting study goals"
)

def get_response(message):
    message = message.lower().strip()

    # Friendly small talk
    if "how are you" in message or "how's it going" in message:
        return "I'm just a bot, but I'm here and ready to help you with your studies. How can I assist you today?"
    if "who are you" in message or "what is your name" in message:
        return "I'm Naira, your educational assistant chatbot. I'm here to help you with IT topics, study tips, and productivity."
    if "what can you do" in message or "what do you do" in message:
        return (
            "I can answer questions about IT subjects, provide study tips, help with motivation, recommend resources, and assist with productivity. Please ask me anything related to your studies."
        )
    if "joke" in message:
        return "Why do programmers prefer dark mode? Because light attracts bugs."
    if "weather" in message:
        return "I'm sorry, I don't have weather information. You can check a weather website or app for the latest updates."
    if "good morning" in message:
        return "Good morning! I hope you have a productive and positive day. How can I help you today?"
    if "good night" in message:
        return "Good night! Rest well and recharge for tomorrow. If you need any study tips before bed, just ask."
    if "bye" in message or "goodbye" in message or "see you" in message:
        return "Goodbye! If you need help again, just come back and chat with me. Have a great day!"

    # Greetings
    if any(greet in message for greet in greetings_input):
        return greeting_message

    # Study tips
    if "study tips" in message or "how to study" in message:
        if "programming" in message:
            return "Here are some programming study tips: " + ", ".join(STUDY_TIPS["programming"]) + "."
        elif "database" in message:
            return "Here are some database study tips: " + ", ".join(STUDY_TIPS["database"]) + "."
        elif "web" in message:
            return "Here are some web development study tips: " + ", ".join(STUDY_TIPS["web_development"]) + "."
        else:
            return "Here are some general study tips: " + ", ".join(STUDY_TIPS["general"]) + "."

    # Time management and productivity
    if "time management" in message or "manage my time" in message or "productivity" in message:
        return (
            "Here are some time management tips: Use a planner or digital calendar to organize your tasks, prioritize important assignments first, break large tasks into smaller steps, set specific goals for each study session, and avoid multitasking—focus on one thing at a time."
        )

    # Exam preparation
    if "exam" in message or "test" in message or "prepare for" in message:
        return (
            "Exam preparation tips: Start studying early and review regularly, practice with past exam papers, teach concepts to a friend or yourself, take care of your health—sleep and eat well, and stay calm and confident during the exam."
        )

    # Assignment and project help
    if "assignment" in message or "project" in message or "homework" in message:
        return (
            "For assignments and projects: Read the instructions carefully, break the work into smaller tasks, set deadlines for each part, ask your instructor or classmates if you're stuck, and review your work before submitting."
        )

    # Motivation
    if "motivate" in message or "encourage" in message or "inspire" in message:
        return random.choice(motivation_responses)

    # Resource recommendations
    if "resource" in message or "recommend" in message or "where can i learn" in message:
        return (
            "I can recommend resources for IT subjects. Please specify the topic or subject code, for example, IT01 for Programming Fundamentals."
        )

    # Polite/Thank you responses
    if "thank" in message or "thanks" in message or "appreciate" in message:
        return "You're welcome! If you have more questions or need help, just ask."

    # Help command
    if "help" in message or "can you help" in message or "assist" in message:
        return (
            "Of course! I can help you with information about IT subjects (codes IT01-IT06), study tips for different fields, explanations of technical concepts, resource recommendations, and motivation or productivity advice. Just ask your question or tell me what you need."
        )

    # Subject code queries
    for code in IT_SUBJECTS:
        if code.lower() in message:
            subject = IT_SUBJECTS[code]
            return f"Subject: {subject['name']} ({code}). Topics covered: " + ", ".join(subject['topics']) + ". Available resources: " + ", ".join(subject['resources']) + f". Ask me specific questions about any topic in {subject['name']}."

    # Specific questions about subjects
    for code, subject in IT_SUBJECTS.items():
        for question, answer in subject["common_questions"].items():
            if question in message or any(word in message for word in question.split()):
                return f"{answer} This is related to {subject['name']} ({code}). Would you like to know more about this subject?"

    # If the message is ambiguous (very short or unclear)
    if len(message.split()) <= 2:
        return "Could you please clarify your question or provide more details so I can assist you better?"

    # Fallback for unknown questions
    return greeting_message

# Simple rule-based response rules for demo/testing
response_rules = [
    (re.compile(r'^(hi|hello|hey)\b', re.IGNORECASE),
     "Hello! How can I help you today?"),
    (re.compile(r'\b(homework|assignment)\b', re.IGNORECASE),
     "Sure—what subject or topic are you working on?"),
    (re.compile(r'\b(thanks|thank you)\b', re.IGNORECASE),
     "You're welcome!"),
    (re.compile(r'\b(bye|goodbye)\b', re.IGNORECASE),
     "Goodbye! If you need more help, just let me know.")
]

def get_bot_response(text: str) -> str:
    for pattern, reply in response_rules:
        if pattern.search(text):
            return reply
    return "I'm sorry, I don't understand. Can you rephrase your question?"

def main():
    print("Naira: Hi! I'm Naira, your educational assistant. (Type 'exit' to quit.)")
    while True:
        user = input("You: ").strip()
        if user.lower() in ('exit','quit'):
            print("Naira: Goodbye!")
            break
        print("Naira:", get_response(user))

if __name__ == "__main__":
    main() 