import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException, NoSuchElementException


class ScraperMetacritics:
    wait_time = 1

    def __init__(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        #options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        self.driver.get(url)
        time.sleep(self.wait_time)

        WebDriverWait(self.driver, self.wait_time).until(
            EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "onetrust-accept-btn-handler"]'))).click()
        time.sleep(self.wait_time / 1)



    def scrap(self):

        dados = []
        pagina_atual = 1

        while pagina_atual <= 56:
            itens = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'c-finderProductCard_container')))

            links = [item.get_attribute('href') for item in itens]

            for link in links:
                self.driver.get(link)

                try:
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                except WebDriverException:
                    print('Webdriver foi fechado manualmente!')
                    return dados

                div_list = soup.find_all('div', {
                    'class': 'c-productHero_score-container u-flexbox u-flexbox-column g-bg-white'})

                for d in div_list:
                    name = d.find('div', {'class': 'c-productHero_title g-inner-spacing-bottom-medium g-outer-spacing-top-medium'}).text.strip()

                    release_date = d.find('span', {'class': 'u-text-uppercase'}).text.strip()

                    console_game = d.findNext('ul', {'class': 'g-outer-spacing-left-medium-fluid'}).text.strip()

                    gender_game = d.findNext('li', {'class': 'c-genreList_item'}).text.strip()

                    meta_rating = d.find('div', {'class': 'c-siteReviewScore'})
                    meta_rating_value = meta_rating.find('span').text.strip() if meta_rating else ''

                    user_rating = d.find('div', {'class': 'c-siteReviewScore_user'})
                    user_rating_value = user_rating.find('span').text.strip() if user_rating else ''

                row = {
                    'Nome': name,
                    'Data de Lançamento': release_date,
                    'Console': console_game,
                    'Genero': gender_game,
                    'Metascore': meta_rating_value,
                    'UserScore': user_rating_value
                }
                dados.append(row)

            # Navegue para a próxima página
            self.driver.get(
                f'https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2024&page={pagina_atual + 1}')
            pagina_atual += 1

        self.driver.quit()
        return dados

    def salvar_df(self, dados):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        df = pd.DataFrame(dados)
        df.to_csv('teste_dados_metacritics_games.csv', sep=',')
        print(df)


S = ScraperMetacritics('https://www.metacritic.com/browse/game/?releaseYearMin=1958&releaseYearMax=2024&page=1')
dados = S.scrap()
S.salvar_df(dados)

