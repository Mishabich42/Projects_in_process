from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
from time import sleep
from requests import get
from reportlab.pdfgen import canvas
from PIL import Image as PilImage
import re
import difflib

url = 'https://manga.in.ua'


def download_images(name_manga, select_page, end_page):
    # Create a PDF file
    pdf_file = f'{name_manga + " " + str(select_page) + "-" + str(end_page)}.pdf'
    c = canvas.Canvas(pdf_file, pagesize=letter)
    # Initialize the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Activate headless mode
    driver = webdriver.Chrome(options=options)

    # Navigate to the webpage
    driver.get(url)
    sleep(1)
    # Find and click the search button
    button_search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='header__auth']"))
    )
    button_search.find_element(By.XPATH, ".//button").click()
    sleep(1)
    # Enter the manga name into the search input field
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search' and contains(@id, 'story')]"))
    )
    search.send_keys(name_manga)

    # Click on the search result
    list_res = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='search-result-box']")))
    for res in list_res:
        title_elements = res.find_elements(By.XPATH, ".//div/a/span/span[@class='s-title']")
        for title_element in title_elements:
            title_text = title_element.text.strip().lower()
            name_manga_cleaned = ''.join(re.findall(r'\b\w+\b', name_manga)).lower()

            similarity = difflib.SequenceMatcher(None, name_manga_cleaned, title_text).ratio()
            print(title_text)
            print(name_manga_cleaned)
            print(similarity)
            if similarity >= 0.6:
                print(title_text)
                print(name_manga)
                title_element.click()
                break
    sleep(1)

    try:
        age_check = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@id='over18']")))
        age_check.click()
    except:
        print("")
    # Click on the read button
    button_read = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[@onclick]"))
    )
    button_read.click()

    # Navigate to the selected page if specified
    if select_page != '':
        pages = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//option"))
        )
        for page in pages:
            option_text = page.text
            match = re.search(r'Розділ (\d+)', option_text)
            if match:
                page_number = int(match.group(1))
                if page_number == int(select_page):
                    page.click()
                    break

    while True:
        sleep(1)
        button_start = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@id='startloadingcomicsbuttom']"))
        )
        button_start.click()
        sleep(10)

        step = 1000  # Set the desired scroll step size
        current_scroll_position = 0

        # Scroll through the page until reaching the bottom
        while True:
            page_height = driver.execute_script("return document.body.scrollHeight;")
            # Scroll the page
            for i in range(current_scroll_position, page_height, step):
                driver.execute_script(f"window.scrollTo(0, {i});")
                sleep(0.4)
                current_scroll_position = i
            # Check if the entire page has been scrolled
            new_page_height = driver.execute_script("return document.body.scrollHeight;")
            if new_page_height == page_height:
                break

        sleep(5)  # Wait for a few seconds for the page to load completely

        # Find all images on the page
        images = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='comics']"))
        )
        images = images.find_elements(By.XPATH, ".//img")

        # Download and add images to the PDF
        for img in images:
            img_url = img.get_attribute('src')
            if img_url:
                try:
                    response = get(img_url)
                    img_data = BytesIO(response.content)
                    pil_image = PilImage.open(img_data)
                    img_width, img_height = pil_image.size
                    pdf_width, pdf_height = img_width, img_height  # Set PDF page size based on image size
                    c.setPageSize((pdf_width, pdf_height))  # Set the PDF page size
                    c.drawImage(ImageReader(img_data), 0, 0, pdf_width, pdf_height)  # Add image to PDF
                    c.showPage()  # Add a new page to the PDF
                except Exception as e:
                    print(f"Error adding image to PDF: {e}")

        # Check if the current page matches the end_page
        page = driver.current_url
        page_check = page[page.index("rozdil-"):]
        page_check = int(''.join(filter(str.isdigit, page_check)))
        print(page_check)
        if page_check == int(end_page):
            print("Session ended page")
            break

        driver.execute_script(f"window.scrollTo(0, 0);")
        sleep(1)
            # Click on the next page button
        button_next = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[@id='fwdTop']"))
        )
        button_next.click()


    c.save()

    # Quit the webdriver
    driver.quit()
