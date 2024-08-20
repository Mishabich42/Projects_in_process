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




def download_images(name_manga, select_page, end_page):
    # Create a PDF file
    pdf_file = f'{name_manga + " " + str(select_page) + "-" + str(end_page)}.pdf'
    c = canvas.Canvas(pdf_file, pagesize=letter)
    # Initialize the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Activate headless mode
    driver = webdriver.Chrome(options=options)

    # Navigate to the webpage
    url = 'https://honey-manga.com.ua'
    driver.get(url)
    sleep(1)
    # Find and click the search button
    button_search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='flex items-center gap-x-4']"))
    )
    button_search.find_element(By.XPATH, ".//div").click()
    sleep(1)
    # Enter the manga name into the search input field
    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Введіть пошуковий запит...']"))
    )
    search.send_keys(name_manga)
    list_res = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='mt-6 flex flex-col gap-y-6']")))
    for res in list_res:
        title_elements = res.find_elements(By.XPATH, ".//a/div[2]/div/p")
        for title_element in title_elements:
            title_text = title_element.text.strip().lower()
            name_manga_cleaned = ''.join(re.findall(r'\b\w+\b', name_manga)).lower()

            similarity = difflib.SequenceMatcher(None, name_manga_cleaned.replace(" ", ""), title_text.replace(" ", "")).ratio()
            if similarity >= 0.7:
                driver.execute_script("arguments[0].click();", title_element)
                break
    sleep(1)
    # Click on the read button
    select_page_href = None
    end_page_href = None
    next_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//ul[@class='MuiPagination-ul css-nhb8h9']"))
    )
    next_button = next_button.find_elements(By.XPATH, ".//li")
    while True:
        page_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='flex flex-col md:px-6 max-md:px-2 mt-4']"))
        )
        pages = page_list.find_elements(By.XPATH, ".//a")
        for page in pages:

            page_text = page.find_element(By.XPATH, ".//div/p").text
            page_number = page_text[page_text.index("Розділ "):].replace("Розділ ", "")
            page_number = ''.join(c for c in page_number if c.isdigit())
            if float(select_page) == float(page_number):
                select_page_href = page.get_attribute("href")
            if float(end_page) == float(page_number):
                end_page_href = page.get_attribute("href")
        if select_page_href and end_page_href:
            break
        try:
            next_button[-1].click()
            sleep(3)
        except:
            break
    driver.get(select_page_href)
    sleep(1)
    while True:
        sleep(1)
        list_images = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@class='max-w-4xl mx-auto md:mx-auto MuiBox-root css-0']/div/div/div"))
        )
        for image in list_images:
            driver.execute_script("arguments[0].scrollIntoView(true);", image)
            sleep(0.5)
            image = image.find_element(By.XPATH, ".//img")
            image_scr = image.get_attribute("src")
            try:
                response = get(image_scr)
                img_data = BytesIO(response.content)
                pil_image = PilImage.open(img_data)
                img_width, img_height = pil_image.size
                pdf_width, pdf_height = img_width, img_height  # Set PDF page size based on image size
                c.setPageSize((pdf_width, pdf_height))  # Set the PDF page size
                c.drawImage(ImageReader(img_data), 0, 0, pdf_width, pdf_height)  # Add image to PDF
                c.showPage()  # Add a new page to the PDF
            except Exception as e:
                print(f"Error adding image to PDF: {e}")
        driver.execute_script(f"window.scrollTo(0, 0);")
        end_url = driver.current_url
        if end_url == end_page_href:
            print("Session ended page")
            break
        try:
            buton_next = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='flex items-center justify-center md:gap-x-2']/a[2]"))
            )
            buton_next.click()
        except:
            print("Session ended button")
            break
    c.save()

    # Quit the webdriver
    driver.quit()
