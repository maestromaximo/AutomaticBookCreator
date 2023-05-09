import openai
import re
from tqdm import tqdm
import time
import threading
from datetime import date
from pylatexenc.latex2pdf import pdflatex


openai.api_key = "YOUR TOKEN HERE"

def simulate_api_call(stop_event):
    progress_bar = tqdm(range(150), desc="Estimated API call Time")
    for _ in progress_bar:
        if stop_event.is_set():
            break
        time.sleep(1)
    progress_bar.close()

def compile_latex_to_pdf(tex_file, pdf_file):
    try:
        with open(tex_file, 'r') as infile:
            latex_src = infile.read()
        pdf_data = pdflatex(latex_src)
        with open(pdf_file, 'wb') as outfile:
            outfile.write(pdf_data)
        print(f"{tex_file} successfully compiled to {pdf_file}.")
    except Exception as e:
        print(f"Error during compilation of {tex_file}:")
        print(str(e))

def generate_code(prompt):
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=simulate_api_call, args=(stop_event,))
    progress_thread.start()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=3700,
        n=1,
        stop=None,
        temperature=0.7,
    )

    stop_event.set()
    progress_thread.join()

    message = response.choices[0].message["content"].strip()
    return message

def generate_code_GPT4(prompt):
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=simulate_api_call, args=(stop_event,))
    progress_thread.start()

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=7680,
        n=1,
        stop=None,
        temperature=0.7,
    )

    stop_event.set()
    progress_thread.join()

    message = response.choices[0].message["content"].strip()
    return message



def get_subject():
    subject = input("Enter the subject you want to learn: ")
    return subject

def get_lists(subject, gpt4, long_book):
    if long_book:
        num_prerequisites = 10
        num_core_topics = 25
    else:
        num_prerequisites = 8
        num_core_topics = 8

    prompt = f"I am trying to learn the subject {subject}. Please provide me with 2 lists and label them List 1: and List 2:. The first list should contain {num_prerequisites} specific topics that I need to know in order to understand this subject. The second list should contain {num_core_topics} essential topics about the subject that if I were to grasp them I should be able to understand the subject."

    if(gpt4 == False):
        print("Generating lists of topics...")
        response = generate_code(prompt)
    else:
        print("Generating lists of topics...")
        response = generate_code_GPT4(prompt)
    
    ##print(f"API Response: {response}")

    prerequisites = re.findall(r'(?<=List 1:)(.*?)(?=List 2:)', response, re.DOTALL)
    core_topics = re.findall(r'(?<=List 2:)(.*)', response, re.DOTALL)

    return prerequisites[0].strip(), core_topics[0].strip()



def generate_long_book_content(subject, prerequisites, core_topics, gpt4):
    prerequisites_list = [topic.strip() for topic in prerequisites.split('\n') if topic.strip()]
    core_topics_list = [topic.strip() for topic in core_topics.split('\n') if topic.strip()]

    topics_list = prerequisites_list + core_topics_list

    explanations = ""
    examples = ""

    for topic in topics_list:
        words = 2800 if gpt4 else 2800
        prompt = f"Please generate a long, logical, and summarized explanation of the topic '{topic}' in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.). Please provide approximately {words} words."
        #print(f"DEBUG: {topic} and this is the list {topics_list}")
        print(f"Generating explanation of {topic}...")
        explanation = generate_code_GPT4(prompt) if gpt4 else generate_code(prompt)

        print("Generating examples and solutions...")
        prompt = f"Generate 5 logical examples with solutions for the topic '{topic}' in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.)."
        example = generate_code_GPT4(prompt) if gpt4 else generate_code(prompt)

        explanations += f"\\section{{{topic}}}\n{explanation}\n"
        examples += f"{example}\n"

    return explanations, examples


def get_explanations_and_examples(subject, lists, gpt4):
    
    if(gpt4 == False):

        words = 2800
        prompt = f"Please generate me an extensive, long, logical, and summarized explanation of each subject on this list in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.). The list contains subjects I need to know and topics of a subject I need to learn. The subject is {subject}, and the list is {lists}. Please provide approximately {words} words."

        print("Generating short explinations...")
        explanations = generate_code(prompt)

        prompt = f"Given this list of topics, generate many logical examples with solutions for them in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.). Write as many as you can for each, and make it reach {words} words, make it look good. The list is {lists}."
        print("Generating problems and solutions...")
        examples = generate_code(prompt)
    else:
        words = 2800
        prompt = f"Please generate me an extensive, long, logical, and summarized explanation of each subject on this list in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.). The list contains subjects I need to know and topics of a subject I need to learn. The subject is {subject}, and the list is {lists}. Please provide approximately {words} words."

        print("Generating short explinations...")
        explanations = generate_code_GPT4(prompt)

        prompt = f"Given this list of topics, generate many logical examples with solutions for them in LaTeX format, but without the document preamble (\\documentclass, \\usepackage, etc.). Write as many as you can for each, and make it reach {words} words, make it look good. The list is {lists}."
        print("Generating problems and solutions...")
        examples = generate_code_GPT4(prompt)

    return explanations, examples

def word_count(text):
    return len(text.split())

# def create_latex_document(lists_latex, explanations, examples):
#     latex_preamble = (
#         "\\documentclass{article}\n"
#         "\\usepackage{amsmath}\n"
#         "\\usepackage{amssymb}\n"
#         "\\usepackage{graphicx}\n"
#         "\\begin{document}\n"
#     )
#     latex_end = "\\end{document}"

#     latex_document = f"{latex_preamble}{lists_latex}\n{explanations}\n{examples}\n{latex_end}"
#     return latex_document

def create_latex_document(subject, lists_latex, explanations, examples, total_word_count):
    today = date.today().strftime("%B %d, %Y")
    latex_preamble = (
        "\\documentclass{article}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{amssymb}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage{titling}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage{geometry}\n"
        "\\usepackage{titlesec}\n"
        "\\usepackage{newtxtext}\n"
        "\\usepackage{microtype}\n"
        "\\usepackage{xcolor}\n"
        "\\usepackage{booktabs}\n"
        "\\geometry{margin=1in}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\rfoot{\\thepage}\n"
        "\\lhead{\\theauthor}\n"
        "\\cfoot{}\n"
        "\\title{Lesson on: " + subject + "}\n"
        "\\author{" + today + "}\n"
        "\\titleformat*{\\section}{\\large\\bfseries}\n"
        "\\titleformat*{\\subsection}{\\normalsize\\bfseries}\n"
        "\\titleformat*{\\subsubsection}{\\small\\bfseries}\n"
        "\\definecolor{sectioncolor}{RGB}{0,0,0}\n"
        "\\titleformat{\\section}{\\color{sectioncolor}\\large\\bfseries}{\\thesection}{1em}{}\n"
        "\\begin{document}\n"
        "\\maketitle\n\n"
        "\\thispagestyle{empty}\n\n"
        "Total word count: " + str(total_word_count) + "\n\n"
        "\\newpage\n"
        "\\tableofcontents\n"
        "\\newpage\n"
    )
    latex_end = "\\end{document}"

    latex_document = f"{latex_preamble}{lists_latex}\n\\newpage\n{explanations}\n{examples}\n{latex_end}"
    return latex_document




def main():
    gpt4 = False
    words = 2800
    if (input("Would you like to use GPT4? (More expensive), yes or no:") == "yes"):
        gpt4 = True
        words = 2800
    else:
        gpt4 = False

    long_book = input("Would you like to generate a long book? (yes or no): ") == "yes"

    subject = get_subject()
    prerequisites, core_topics = get_lists(subject, gpt4, long_book)
    print("done list")

    if long_book:
        explanations, examples = generate_long_book_content(subject, prerequisites, core_topics, gpt4)
    else:
        explanations, examples = get_explanations_and_examples(subject, f"{prerequisites}, {core_topics}", gpt4)

    # Generate the Latex response for the lists
    prompt = f"Convert this to Latex, but without the document preamble (\\documentclass, \\usepackage, etc.): List of prerequisites: \n {prerequisites} \n List of Core topics: \n {core_topics} \n "
    response = generate_code(prompt)
    
    print("Lists in Latex: ")
    print(response)
    print("Explanations in Latex:")
    print(explanations)
    print("\nExamples in Latex:")
    print(examples)

    total_word_count = word_count(f"{subject}, {prerequisites}, {core_topics}, {explanations}, {examples}")

    if(gpt4 is True):
        cost = words*0.75/1000*0.06
    else:
        cost = words*0.75/1000*0.002

    latex_document = create_latex_document(subject, response, explanations, examples, total_word_count)

    with open(subject+"CHATGPTGENERATED_course.tex", "w", encoding='utf-8') as outfile:
        outfile.write(latex_document)


    print(f"The LaTeX document has been saved to {subject}CHATGPTGENERATED_course.tex")

    print(f"\nTotal word count: {total_word_count} the approximate cost is {cost}")

    tex_file = subject + "CHATGPTGENERATED_course.tex"
    pdf_file = subject + "CHATGPTGENERATED_course.pdf"
    compile_latex_to_pdf(tex_file, pdf_file)

if __name__ == "__main__":
    main()
