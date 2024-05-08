import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import pickle
from selenium.webdriver.common.action_chains import ActionChains
#import pickle

"""
#Fill the form 

def fill_the_form(driver, total_experiences):
    try:
        form = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
        question = form.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
        for questions in question:
            try:
                input_tag_main_class = questions.find_element(By.CLASS_NAME, "artdeco-text-input--container.ember-view")
                label_text = input_tag_main_class.find_element(By.TAG_NAME, "label").text
                print('Input Question: ', label_text)
                if "years of work experience" in label_text or "Total experience" in label_text:
                    input_tag = input_tag_main_class.find_element(By.TAG_NAME, "input")
                    if not input_tag.get_attribute('value'):
                        input_tag.send_keys(total_experiences)
                else:
                    print('No keyword found')
            except Exception as e:
                print('Input Part Not Working')

                try:
                    fieldset = questions.find_element(By.CSS_SELECTOR, "fieldset[data-test-form-builder-radio-button-form-component='true']")
                    fieldset_question = fieldset.find_element(By.CSS_SELECTOR, ' legend span[data-test-form-builder-radio-button-form-component__title]')
                    fieldset_question_span_text = fieldset_question.find_element(By.CLASS_NAME, 'visually-hidden').text
                    print("Question:", fieldset_question_span_text)
                    question = fieldset_question_span_text

                    options = fieldset.find_elements(By.CSS_SELECTOR, "label[data-test-text-selectable-option__label]")
                    for option in options:
                        print("Option:", option.text)
                        options = option.text
                except Exception as e:
                    print('Fieldset Not Working')
    except Exception as e:
        print('Form Tag not working')
"""
#Function of Clicking next page
def click_next_page(driver):
    try:
        # Find the active page and get its number
        active_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-pagination__indicator--number.active.selected'))
        )
        page_number = int(active_page.text)

        # Find the next page button and click on it
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Page " + str(page_number + 1) + "']"))
        )
        next_page_button.click()
        return True
    except TimeoutException as e:
        #logging.info(f"Error clicking next page: {e}")
        return False


def apply_job(conn, email, password, job, location,resume_filepath, total_experiences, user_id):
    driver = webdriver.Chrome()
    driver.maximize_window()
    time.sleep(1)

    driver.get("https://linkedin.com/")
    
    try:
        sign_in_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.LINK_TEXT,'Sign in')))
        sign_in_button.click()
    except TimeoutException:
        print(f'Timeout waiting')

    try:
        email_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
        email_field.send_keys(email)
        password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "password")))
        password_field.send_keys(password)
        sign_in_login_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[data-litms-control-urn="login-submit"]')))
        sign_in_login_button.click()
    except TimeoutException:
        print(f'Timeout waiting')
    time.sleep(15)
    try:
        target_url = 'https://www.linkedin.com/jobs/collections/recommended/?currentJobId=3900528116&discover=recommended&discoveryOrigin=JOBS_HOME_JYMBII'
        if driver.current_url != target_url:
            driver.get(target_url)
            time.sleep(5)
    except Exception as e:
        pass
    """
    try:
        job_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://www.linkedin.com/jobs/?']")))
        # Click the Jobs button
        job_button.click()
    except Exception as e:
        print('Job Button not working')
    """
    try:
        search_job = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.jobs-search-box__input--keyword .jobs-search-box__text-input')))
        search_job.clear()
        search_job.send_keys(job)

        search_location = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'.jobs-search-box__input--location .jobs-search-box__text-input')))
        search_location.clear()
        search_location.send_keys(location)
        #Press Enter
        #driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keypress', { 'key': 'Enter' }))", search_location)
        search_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "jobs-search-box__submit-button")))
        if "Search" in search_button.text:
            search_button.click()
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException) as e:
        pass
    try:
        main_filter_button = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'search-reusables__filter-list')))
        filter_buttons = main_filter_button.find_elements(By.CLASS_NAME, 'search-reusables__primary-filter')
        for buttons in filter_buttons:
            button_tag = buttons.find_element(By.CLASS_NAME, 'search-reusables__filter-pill-button')
            print('Main-Button: ', button_tag.text)
            if button_tag.text == 'Easy Apply':
                button_tag.click()
                time.sleep(3)
    except Exception as e:
        print('Button Not Working')
    #resume_file_path = 'E:/Smart-Apply/uploads/Saipranay_Masadi-Updated_Resume.pdf'
    #print("Resume Filepath:", resume_filepath)
    try:
        #Job Card Code
        Flag = True
        while Flag:
            job_cards = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobs-search-results__list-item')))
            for job_card in job_cards:
                job_card.click()
                driver.execute_script("arguments[0].scrollIntoView();", job_card)
                print('Job Card clicked')
                time.sleep(2)
                try:
                    job_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title")))
                    job_link = job_element.find_element(By.TAG_NAME, 'a')
                    link = job_link.get_attribute('href')
                    driver.execute_script("window.open(arguments[0], '_blank');", link)
                    print('Job Link opened in new tab')
                    driver.switch_to.window(driver.window_handles[-1])
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                    time.sleep(3)
                    try:
                        print("Waiting for the Easy Apply button...")
                        easy_aaply = driver.find_element(By.CLASS_NAME, 'jobs-apply-button--top-card')
                        print('Easy Apply tag', easy_aaply)
                        easy_aaply_button = easy_aaply.find_element(By.CLASS_NAME, 'jobs-apply-button.artdeco-button.artdeco-button--3.artdeco-button--primary.ember-view')
                        easy_aaply_button.click()

                        #easy_aaply_button.click()
                        print('Easy Apply Button Clicked')
                        continue_loop = True
                        while continue_loop:
                            try:
                                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view')))
                                #driver.execute_script("arguments[0].scrollIntoView();", next_button)

                                #Resume Upload from server
                                try:
                                    resume_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'js-jobs-document-upload__container')))
                                    resume_button_class = resume_button.find_element(By.CLASS_NAME, 'hidden')
                                    resume_filepath_modified = resume_filepath.replace("\\", "/")
                                    print("Sending keys:", resume_filepath_modified)
                                    resume_button_class.send_keys(resume_filepath_modified)
                                    time.sleep(3)
                                except Exception as e:
                                    print('Resume Button part not working')
                                driver.execute_script("arguments[0].scrollIntoView();", next_button)

                                #Form fill part 
                                """
                                try:
                                    fill_the_form(driver, total_experiences)
                                except Exception as e:
                                    print('Fill the form not working')
                                """
                                try:
                                    cursor = conn.cursor()
                                    form = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
                                    question = form.find_elements(By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
                                    for questions in question:
                                        try:
                                            input_tag_main_class = questions.find_element(By.CLASS_NAME, "artdeco-text-input--container.ember-view")
                                            label_text = input_tag_main_class.find_element(By.TAG_NAME, "label").text
                                            print('Input Question: ', label_text)
                                            if "years of work experience" in label_text or "Total experience" in label_text or "years of experience" in label_text:
                                                input_tag = input_tag_main_class.find_element(By.TAG_NAME, "input")
                                                if not input_tag.get_attribute('value'):
                                                    input_tag.send_keys(total_experiences)
                                            else:
                                                print('No keyword found')
                                        except Exception as e:
                                            print('Input Part Not Working')

                                            try:
                                                fieldset = questions.find_element(By.CSS_SELECTOR, "fieldset[data-test-form-builder-radio-button-form-component='true']")
                                                fieldset_question = fieldset.find_element(By.CSS_SELECTOR, ' legend span[data-test-form-builder-radio-button-form-component__title]')
                                                fieldset_question_span_text = fieldset_question.find_element(By.CLASS_NAME, 'visually-hidden').text
                                                print("Question:", fieldset_question_span_text)

                                                options = fieldset.find_elements(By.CSS_SELECTOR, "label[data-test-text-selectable-option__label]")
                                                option_text_list = []

                                                no_option_found = True
                                                for option in options:
                                                    print("Option:", option.text)
                                                    option_text_list.append(option.text)
                                                    option_text = option.text

                                                    if "No" in option_text:
                                                        option.click()
                                                        print("Clicked on the 'No' option radio button")
                                                        no_option_found = False
                                                        break
                                                if not no_option_found:
                                                    print("No 'No' option found in the available options.")

                                                option_text = ', '.join(option_text_list)
                                                cursor.execute("INSERT INTO job_questions (user_id, question_text, option_text) VALUES (%s, %s, %s)", (user_id, fieldset_question_span_text, option_text))
                                                conn.commit()  # Commit the transaction

                                            except Exception as e:
                                                print('Fieldset Not Working')

                                                try:
                                                    select = questions.find_element(By.CSS_SELECTOR, '[data-test-text-entity-list-form-component]')
                                                    select_label = select.find_element(By.TAG_NAME, 'label')
                                                    select_label_span_text = select_label.find_element(By.CLASS_NAME, 'visually-hidden').text
                                                    print("Dropdown Question: ", select_label_span_text)

                                                    cursor.execute("SELECT answer FROM user_answers WHERE user_id = %s AND question_text = %s", (user_id, select_label_span_text))
                                                    answer_row = cursor.fetchone()
                                                    if answer_row:
                                                        answer = answer_row[0]
                                                        print("Answer found in database:", answer)

                                                        select_tag = select.find_element(By.TAG_NAME, 'select')
                                                        select_tag_selector = Select(select_tag)

                                                        if answer in [option.text for option in select_tag_selector.options]:
                                                            select_tag_selector.select_by_visible_text(answer)
                                                            print("Answer selected:", answer)
                                                        else:
                                                            print("Answer not found in dropdown options")
                                                    else:
                                                        print("No answer found in database for this question")

                                                    options = [option.text for option in select_tag_selector.options]
                                                    print('Dropdown-Options: ', options)
                                                    #option_text_dropdown = ', '.join(options)
                                                    
                                                    cursor.execute("INSERT INTO job_questions (user_id, question_text, option_text) VALUES (%s, %s, %s)", (user_id, select_label_span_text, ', '.join(options)))
                                                    conn.commit()

                                                    print('Data Inserted in db')
                                                except Exception as e:
                                                    print('Dropdown not working')
                                except Exception as e:
                                    print('Form Tag not working')
                                finally:
                                    cursor.close()
                                next_button.click()
                                time.sleep(3)
                            
                                try:
                                    error = driver.find_element(By.CLASS_NAME, 'artdeco-inline-feedback__message')
                                    if error:
                                        continue_loop = False
                                        driver.close()
                                        time.sleep(2)
                                        driver.switch_to.window(driver.window_handles[0])
                                except Exception as e:
                                    print('Error Class Not here')
                            except Exception as e:
                                print('Next button not working')
                                continue_loop = False
                                driver.close()
                                time.sleep(2)
                                driver.switch_to.window(driver.window_handles[0])
                    except Exception as e:
                        print('Easy Apply Not Working')
                        driver.close()
                        time.sleep(2)
                        driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    print('Job Link Issue')
            if not click_next_page(driver):
                Flag = False

    except Exception as e:
        print('Not Working')
        Flag = False

    
    time.sleep(5)
    print('Closing Easy Apply Tool')
    driver.quit()  # Close the WebDriver instance
#print('Failed to log in with all browsers')
#kill_webdriver_sessions()

#apply_job()