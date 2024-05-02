from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import assignments


# driver = webdriver.Chrome('download path for where driver was installed')

def getPrairielearnAssignments(driver, email, password):
  url = "https://us.prairielearn.com/pl/auth/institution/3/saml/login"

  driver.get(url)

  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "loginfmt")))
  emailBox = driver.find_element(By.NAME, "loginfmt")
  emailBox.send_keys(email)

  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "idSIButton9")))
  nextButton = driver.find_element(By.ID, "idSIButton9")
  nextButton.click()

  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "passwd")))
  passwordBox = driver.find_element(By.NAME, "passwd")
  passwordBox.send_keys(password)

  WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "idSIButton9")))
  nextButton = driver.find_element(By.ID, "idSIButton9")
  nextButton.click()

  instances = driver.find_elements(By.XPATH, "//a[@href]")

  courses = []
  coursesLinks = []
  coursesNames = []

  for instance in instances:
    if "course_instance" in instance.get_attribute("href"):
      coursesLinks.append(instance.get_attribute("href"))
      print(instance.get_attribute("href"))
      courses.append(instance)
      print(instance.text)
      coursesNames.append(instance.text)

  coursesToAssessments = {}
  for i in range(len(coursesLinks)):
    driver.get(coursesLinks[i])
    for instance in driver.find_elements(By.XPATH, "//a[@href]"):
      if "assessment_instance" in instance.get_attribute("href"):
        if coursesNames[i] not in coursesToAssessments:
          coursesToAssessments[coursesNames[i]] = [instance.text]
          # driver.get(instance.get_attribute("href"))
          # soup = BeautifulSoup(driver.page_source, 'html.parser')
          # text = soup.get_text()
          # dueDate = "DEADLINE PASSED"
          # if "until" in text:
          #   dueDate = text[text.index("until") + 6 : text.index("until") + 20]
          # coursesToAssessments[coursesNames[i]][-1].append(dueDate)

        else:
          coursesToAssessments[coursesNames[i]].append(instance.text)
          # driver.get(instance.get_attribute("href"))
          # soup = BeautifulSoup(driver.page_source, 'html.parser')
          # text = soup.get_text()
          # dueDate = "DEADLINE PASSED"
          # if "until" in text:
          #   dueDate = text[text.index("until") + 6 : text.index("until") + 20]
          # coursesToAssessments[coursesNames[i]][-1].append(dueDate)

  assignments = []
  for key in coursesToAssessments.keys():
    assignments.append.assignment.Assignment(key, coursesToAssessments[key], datetime.min ,"PrairieLearn")

  driver.quit()

  return(assignments)