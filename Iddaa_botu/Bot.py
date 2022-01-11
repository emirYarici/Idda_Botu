from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import numpy as np
import mysql.connector
import requests
import datetime
def mysql_veri_cek():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Emireren1",
        database="ysa_proje"
    )
    cur = mydb.cursor()
    cur.execute("select * from tbl_maclar")
    records = cur.fetchall()
    records = list(records)
    array = []
    for record in records:
        record = record[6:]
        array.append(record)
    train_samples = array
    cur.close()
    mydb.close()
    return train_samples



samples=mysql_veri_cek()
gecilen_mac = 0
tutma_orani = 0.60
date = datetime.datetime(2022,1,11)
url = 'https://www.mackolik.com/futbol/canli-sonuclar'
driver = webdriver.Chrome(executable_path="C:\\Users\\Hp\\Desktop\\chromedriver")
driver.get(url)
iddaa_kodlari = {'1': 3, '4': 3, '6-11': 3, '611': 3, '11': 2, '15': 28, '62': 6, '14': 9, '18': 2}
str_date = date.strftime('%Y-%m-%d')
model = load_model('models/iddaa_botu_modeli.h5')
#istenen güne tıklandı
while 1:
    try:
        #gun degerine tiklamayı dene
        driver.find_element_by_xpath('//*[@id="widget-dateslider-day-' + str_date + '"]').click()
        break
        #araya reklam girerse
    except ElementClickInterceptedException:
        driver.find_element_by_xpath('//*[@id="close47559333074953319"]').click()
        #tarih listesinde istedigin gun yoksa
    except NoSuchElementException:
        try:
            #previous tusuna basmayı dene
            driver.find_element_by_xpath(
                "/html/body/div[4]/div/main/div/div[1]/div[1]/div[1]/div[1]/button[1]").click()
        #reklam cıkarsa
        except:

            driver.find_element_by_xpath('//*[@id="close47559333074953319"]').click()
        #sayfa dinamik olarak yuklendiğinden biraz beklemek gerekiyor
        try:
            myElem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'id="widget-dateslider-day-' + str_date + "'")))
            print("Page is ready!")
        except TimeoutException:
            print("Loading took too much time!")
try:
    myElem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'id="widget-dateslider-day-' + str_date + "'")))
    print("Page is ready!")
except TimeoutException:
    print("Loading took too much time!")
#simdi selenium u bırakıp BeautifulSoup kullanmaya başladık
soup = BeautifulSoup(driver.page_source, 'html.parser')
#gunun tum maç adreslerini veren href adresleri su an mac_html_adresleri degiskenine atandı
mac_html_adresleri = soup.find_all('a', class_="match-row__score", href=True)

#o gunun her macı icin asağıdaki islemler yapılacak, ancak istenen 67 ozniteliğe sahip degilse bu mac
#gecilecek
for adres in mac_html_adresleri:
    train_samples = []
    istenen_yok = False
    bolumler = str(adres['href']).split("/")
    mac_ismi = bolumler[4]  # 7422395 7428335 7428328 7428149 7531691 7428338 7428340
    del bolumler[5]
    bolumler.insert(-1, "iddaa")
    iddaa_html_adress = "/".join([str(item) for item in bolumler])
    iddaa_html_adress = requests.get(iddaa_html_adress).text
    iddaa_sayfasi_soup = BeautifulSoup(iddaa_html_adress, "lxml")
    # iddaa disabletse geç , 50 den fazla arka arkaya disable olayı olmussa sayfayı degistir
    if iddaa_sayfasi_soup.find('a',
                               class_="widget-match-detail-submenu__icon widget-match-detail-submenu__icon--iddaa   widget-match-detail-submenu__icon--disabled  ") != None:
        gecilen_mac += 1
        print(str(gecilen_mac), mac_ismi)
        if gecilen_mac > 30:
            break
        continue

    for data_id in list(iddaa_kodlari):
        aranan = None
        if data_id == '18':
            ustler = iddaa_sayfasi_soup.find_all("li", {"data-market": data_id})
            for ust in ustler:
                if ust.find("span", class_="widget-iddaa-markets__header-text").text == " 2,5 Alt/Üst ":
                    aranan = ust
                    break
        else:
            aranan = iddaa_sayfasi_soup.find("li", {"data-market": data_id})
        if aranan == None:
            istenen_yok = True
            break
        icerik_sayisi = len(aranan.find_all('a', class_="widget-iddaa-markets__link"))
        if icerik_sayisi != iddaa_kodlari[data_id]:
            istenen_yok = True
            break
    if istenen_yok == True:
        gecilen_mac += 1
        print(str(gecilen_mac), mac_ismi)
        if gecilen_mac > 30:
            break
        continue
    else:
        gecilen_mac = 0
    print(mac_ismi)
    containers = iddaa_sayfasi_soup.find_all('li', class_="widget-iddaa-markets__market-item")
    try:
        ev_skor = int(
            iddaa_sayfasi_soup.find("span", class_="p0c-soccer-match-details-header__score-home").text)
        continue
    except ValueError:
        pass
    except AttributeError:
        pass

    mac_oran_listesi = []
    for container in containers:
        data_kodu = container.get('data-market')

        iddaa_icerikleri = container.find_all('a', class_="widget-iddaa-markets__link")
        if data_kodu in list(iddaa_kodlari):
            if data_kodu == '18':
                if container.find("span",
                                  class_="widget-iddaa-markets__header-text").text != " 2,5 Alt/Üst ":
                    continue
            for iddaa_icerigi in iddaa_icerikleri:

                value = float(iddaa_icerigi.find("span", class_="widget-iddaa-markets__value").contents[
                                      0].strip())
                train_samples.append(value)
    samples.append(train_samples)
    samples_np = np.array(samples)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_train_samples = scaler.fit_transform(samples_np)
    scaled_train_samples=scaled_train_samples[-1].reshape(-1,59)
    print(train_samples)
    prediction=model.predict(x =scaled_train_samples , batch_size=64,verbose=0)
    print(prediction)
    print("****"*30)