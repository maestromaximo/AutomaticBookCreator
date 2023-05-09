import openai
import re
import threading
from datetime import date
from tqdm import tqdm
import time
import re


openai.api_key = "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"

def get_user_input():
    prompt = input("Enter the story prompt: ")
    num_chapters = int(input("Enter the number of chapters: "))
    return prompt, num_chapters

def simulate_api_call(stop_event):
    progress_bar = tqdm(range(31), desc="Estimated API call Time")
    for _ in progress_bar:
        if stop_event.is_set():
            break
        time.sleep(1)
    progress_bar.close()

def generate_chatGPT_response(prompt):
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=simulate_api_call, args=(stop_event,))
    progress_thread.start()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=3500,
        n=1,
        stop=None,
        temperature=0.9,
    )

    stop_event.set()
    progress_thread.join()

    message = response.choices[0].message["content"].strip()
    return message

def generate_latex_without_preamble(text):
    return re.sub(r"\\(?:documentclass|usepackage|begin{document}|end{document}).*?\n", "", text)

def create_latex_document(book_title, user_prompt, story_outline, table_of_contents, chapters):
    latex_preamble = (
        "\\documentclass{book}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{amssymb}\n"
        "\\usepackage{graphicx}\n"
        "\\begin{document}\n"
    )
    latex_end = "\\end{document}"

    latex_document = f"{latex_preamble}\\title{{{book_title}}}\n\\maketitle\n\n"
    latex_document += f"\\chapter*{{Original Prompt}}\n{user_prompt}\n\n"
    latex_document += f"\\chapter*{{Story Outline}}\n{story_outline}\n\n"
    latex_document += f"\\tableofcontents\n\n{table_of_contents}"
    latex_document += f"{chapters}\n{latex_end}"
    return latex_document

def count_words(text):
    words = text.split()
    return len(words)

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', '', filename)

def main():
    user_prompt, num_chapters = get_user_input()

    story_outline_prompt = f"Create a detailed story outline based on this prompt: {user_prompt}"
    print("Generating outline...")
    story_outline = generate_chatGPT_response(story_outline_prompt)

    chapter_titles_prompt = f"Generate a list of {num_chapters} creative chapter titles for the story based on this outline: {story_outline}"
    print("Generating chapter list...")
    chapter_titles_str = generate_chatGPT_response(chapter_titles_prompt)
    chapter_titles = chapter_titles_str.split("\n")

    chapters = ""
    for i, title in enumerate(chapter_titles, start=1):
        # Break the chapter into smaller sections
        num_sections = 3  # Adjust the number of sections as needed
        sections = ""
        for j in range(num_sections):
            section_prompt = f"Generate content for Chapter {i}, Section {j + 1}, titled '{title}', based on this story outline: {story_outline}. Please make it creative and unique, and ensure that it naturally flows as a story, without dividing it into acts."
            print(f"Generating Chapter {i}, Section {j + 1}...") 
            section_content = generate_chatGPT_response(section_prompt)
            sections += section_content + "\n\n"

        chapters += f"\\chapter{{{title}}}\n{sections}\n\n"

    book_title_prompt = f"Create a cool book title using the original prompt: {user_prompt}"
    print("Generating Title...")
    book_title = generate_chatGPT_response(book_title_prompt)

    latex_document = create_latex_document(book_title, user_prompt, story_outline, "", chapters)

    sanitized_book_title = sanitize_filename(book_title)
    with open(f"{sanitized_book_title}_Light_Novel.tex", "w") as outfile:
        outfile.write(latex_document)
    print(f"The LaTeX document has been saved as {sanitized_book_title}_Light_Novel.tex")
    wordCount = count_words(latex_document)
    print("Total words: " + str(wordCount) + ", approximated cost: " + str(wordCount*0.75/1000*0.002) + "$")

if __name__ == "__main__":
    main()
       


# def main():
#     user_prompt, num_chapters = get_user_input()

#     story_outline_prompt = f"Create a detailed story outline based on this prompt: {user_prompt}"
#     print("Generating outline...")
#     story_outline = generate_chatGPT_response(story_outline_prompt)

#     chapter_titles_prompt = f"Generate a list of {num_chapters} creative chapter titles for the story based on this outline: {story_outline}"
#     print("Generating chapter list...")
#     chapter_titles_str = generate_chatGPT_response(chapter_titles_prompt)
#     chapter_titles = chapter_titles_str.split("\n")

#     chapters = ""
#     for i, title in enumerate(chapter_titles, start=1):
#         words = (3500 - (5 + (count_words(title) + count_words(story_outline))*0.75))/0.68
#         chapter_content_prompt = f"Generate content for Chapter {i}, titled '{title}', based on this story outline: {story_outline}, make it long and creative and it must be at least 3000 words long"
#         print("Generating Chapter " + str(i) + "..." + " word count:" + str(words))
#         chapter_content = generate_chatGPT_response(chapter_content_prompt)
#         chapters += f"\\chapter{{{title}}}\n{chapter_content}\n\n"

#     book_title_prompt = f"Create a cool book title using the original prompt: {user_prompt}"
#     print("Generating Title...")
#     book_title = generate_chatGPT_response(book_title_prompt)

#     latex_document = create_latex_document(book_title, user_prompt, story_outline, "", chapters)

#     sanitized_book_title = sanitize_filename(book_title)
#     with open(f"{sanitized_book_title}_Light_Novel.tex", "w") as outfile:
#         outfile.write(latex_document)
#     print(f"The LaTeX document has been saved as {sanitized_book_title}_Light_Novel.tex")

# if __name__ == "__main__":
#     main()

