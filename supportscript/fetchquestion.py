# define "fetch_question" function
def fetch_question(question_id_list) -> dict:
    # Importing Python Module:S1
    try:
        import requests
        from bs4 import BeautifulSoup
        import re
        import html as _html
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [FetchQuestion:S1] - {error}'}

    # Fetching Question IDs From Parameter And Constructing URLs:S2
    try:
        if (not question_id_list) or (len(question_id_list) == 0):
            return {'status': 'ERROR', 'message': 'ERROR - [FetchQuestion:S2] - Invalid Question ID List Provided'}
        question_map = {}
        for raw_id in question_id_list:
            question_map[raw_id] = {'url': f'https://stackoverflow.com/questions/{raw_id}', 'cleaned_html': None}
    except Exception as error:
        return {'status': 'ERROR', 'message': f'ERROR - [FetchQuestion:S2] - {error}'}

    # Looping Through Each Question URL And Fetching The Question Details
    for qid, qdata in question_map.items():
        # Fetching Question From Each URL And Extracting The Question Section Text:S3
        try:
            qurl = qdata['url']
            question_html = requests.get(qurl,headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.9',},timeout=20,).text
            question_html_soup_object = BeautifulSoup(question_html, 'lxml')
            question_section_text = question_html_soup_object.select_one('#question div.s-prose.js-post-body')
        except Exception as error:
            return {'status': 'ERROR', 'message': f'ERROR - [FetchQuestion:S3] - {error}'}

        # Clean HTML Tags From Question Text And Unescape HTML Entities:S4
        try:
            # 1) Unescape &lt; &gt; &amp; etc.
            cleaned_html = _html.unescape(question_section_text.decode_contents())
            # 2) Preserve readability by converting some block tags to newlines
            cleaned_html = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", cleaned_html)
            cleaned_html = re.sub(r"(?i)</\s*p\s*>", "\n", cleaned_html)
            cleaned_html = re.sub(r"(?i)</\s*div\s*>", "\n", cleaned_html)
            cleaned_html = re.sub(r"(?i)</\s*pre\s*>", "\n", cleaned_html)
            cleaned_html = re.sub(r"(?i)</\s*li\s*>", "\n", cleaned_html)
            # 3) Remove all remaining tags
            cleaned_html = re.sub(r"<[^>]+>", "", cleaned_html)
            # 4) Normalize whitespace
            cleaned_html = re.sub(r"\s+", " ", cleaned_html).strip()
            question_map[qid]['cleaned_html'] = cleaned_html
        except Exception as error:
            return {'status': 'ERROR', 'message': f'ERROR - [FetchQuestion:S4] - {error}'}

    # Return successful response with question data
    return {'status': 'SUCCESS', 'message': 'Successfully Fetched And Cleaned All Questions From Stack Overflow', 'data': {qid: qdata['cleaned_html'] for qid, qdata in question_map.items()}}