from bs4 import BeautifulSoup
import shutil
import pathlib
import logging
import streamlit as st

def add_analytics():
    GA_ID = "GTM-NBHTFL6M"  # Your Google Analytics ID
    analytics_js = f"""
    <!-- Google Tag Manager -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
    <div id="{GA_ID}"></div>
    """
    
    # Identify html path of streamlit
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if id not found within html file
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # backup recovery
        else:
            shutil.copy(index_path, bck_index)  # save backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + analytics_js)
        index_path.write_text(new_html)  # insert analytics tag at top of head
